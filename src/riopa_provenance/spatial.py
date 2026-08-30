"""Canonical spatial conversion and analytical materialisations.

The module intentionally keeps source bytes and canonical products separate.
It can transform ArcGIS JSON or GeoJSON into deterministic row ordering,
GeoParquet 1.1 metadata, a DuckDB analytical bundle, and a machine-readable
quality report.  Source assertions remain available through capture IDs and
source object IDs on every row.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq
from pyproj import CRS
from shapely import is_valid, make_valid, to_wkb
from shapely.geometry import (
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
    shape,
)
from shapely.geometry.base import BaseGeometry

from .hashing import sha256_file, sha256_json
from .validation import resolve_local_reference


@dataclass(frozen=True)
class SpatialMaterialization:
    geoparquet_path: Path
    duckdb_path: Path
    quality_report_path: Path
    feature_count: int
    geoparquet_sha256: str
    duckdb_sha256: str


class SpatialConversionError(ValueError):
    """Raised when source geometry cannot be represented safely."""


def _feature_identity(feature: Mapping[str, Any], identity_property: str | None) -> str:
    value = (
        feature.get("properties", {}).get(identity_property)
        if identity_property is not None
        else feature.get("id")
    )
    if value is None:
        raise SpatialConversionError(
            "feature comparison requires an id or configured identity property"
        )
    return str(value)


def _feature_map(
    features: Iterable[Mapping[str, Any]], identity_property: str | None
) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for feature in features:
        identity = _feature_identity(feature, identity_property)
        if identity in result:
            raise SpatialConversionError(f"duplicate feature identity in comparison: {identity}")
        properties = feature.get("properties")
        if not isinstance(properties, Mapping):
            raise SpatialConversionError(f"feature {identity} has no properties object")
        geometry = feature.get("geometry_object")
        if geometry is not None and not isinstance(geometry, BaseGeometry):
            raise SpatialConversionError(f"feature {identity} has an invalid geometry object")
        result[identity] = feature
    return result


def _feature_snapshot_hash(features: Mapping[str, Mapping[str, Any]]) -> str:
    return sha256_json(
        [
            {
                "id": identity,
                "properties": dict(feature["properties"]),
                "geometry_wkb": (
                    to_wkb(feature["geometry_object"], hex=True)
                    if feature.get("geometry_object") is not None
                    else None
                ),
            }
            for identity, feature in sorted(features.items())
        ]
    )


def compare_feature_snapshots(
    previous: Iterable[Mapping[str, Any]],
    current: Iterable[Mapping[str, Any]],
    *,
    identity_property: str | None = None,
    geometry_tolerance: float = 0.0,
) -> dict[str, Any]:
    """Classify feature changes with separate exact and tolerance evidence.

    The result does not infer whether a difference originated at the source or
    in a transformation. Callers must attach the returned, content-bound
    comparison to the relevant capture and transformation provenance.
    """

    if geometry_tolerance < 0:
        raise SpatialConversionError("geometry_tolerance must be non-negative")
    previous_by_id = _feature_map(previous, identity_property)
    current_by_id = _feature_map(current, identity_property)
    previous_ids = set(previous_by_id)
    current_ids = set(current_by_id)
    shared_ids = sorted(previous_ids & current_ids)

    previous_schema = sorted(
        {key for feature in previous_by_id.values() for key in feature["properties"]}
    )
    current_schema = sorted(
        {key for feature in current_by_id.values() for key in feature["properties"]}
    )
    attribute_changed: list[str] = []
    geometry_changed_exact: list[str] = []
    geometry_changed_within_tolerance: list[str] = []
    geometry_changed_beyond_tolerance: list[str] = []

    for identity in shared_ids:
        before = previous_by_id[identity]
        after = current_by_id[identity]
        if dict(before["properties"]) != dict(after["properties"]):
            attribute_changed.append(identity)
        before_geometry = before.get("geometry_object")
        after_geometry = after.get("geometry_object")
        exact_equal = (
            before_geometry is None
            and after_geometry is None
            or (
                before_geometry is not None
                and after_geometry is not None
                and to_wkb(before_geometry, hex=True) == to_wkb(after_geometry, hex=True)
            )
        )
        if exact_equal:
            continue
        geometry_changed_exact.append(identity)
        within_tolerance = (
            before_geometry is not None
            and after_geometry is not None
            and before_geometry.hausdorff_distance(after_geometry) <= geometry_tolerance
        )
        if within_tolerance:
            geometry_changed_within_tolerance.append(identity)
        else:
            geometry_changed_beyond_tolerance.append(identity)

    report: dict[str, Any] = {
        "record_type": "feature_snapshot_difference",
        "comparison_semantics": {
            "identity": identity_property or "feature.id",
            "geometry_exact": "canonical WKB byte equality",
            "geometry_tolerance": "Hausdorff distance",
            "geometry_tolerance_value": geometry_tolerance,
        },
        "evidence": {
            "previous_snapshot_sha256": _feature_snapshot_hash(previous_by_id),
            "current_snapshot_sha256": _feature_snapshot_hash(current_by_id),
        },
        "added": sorted(current_ids - previous_ids),
        "removed": sorted(previous_ids - current_ids),
        "attribute_changed": attribute_changed,
        "geometry_changed_exact": geometry_changed_exact,
        "geometry_changed_within_tolerance": geometry_changed_within_tolerance,
        "geometry_changed_beyond_tolerance": geometry_changed_beyond_tolerance,
        "schema_changed": {
            "changed": previous_schema != current_schema,
            "added_properties": sorted(set(current_schema) - set(previous_schema)),
            "removed_properties": sorted(set(previous_schema) - set(current_schema)),
        },
    }
    report["report_sha256"] = sha256_json(report)
    return report


def _ring_polygon(ring: Sequence[Sequence[float]]) -> Polygon | None:
    if len(ring) < 4:
        return None
    polygon = Polygon(ring)
    if polygon.is_empty or polygon.area == 0:
        return None
    return polygon


def _arcgis_rings_to_geometry(
    rings: Sequence[Sequence[Sequence[float]]], *, repair_invalid: bool = True
) -> BaseGeometry:
    """Build polygons by ring containment rather than trusting winding alone."""

    candidates: list[tuple[Polygon, Sequence[Sequence[float]]]] = []
    for ring in rings:
        polygon = _ring_polygon(ring)
        if polygon is not None:
            candidates.append((polygon, ring))
    if not candidates:
        return Polygon()

    parents: dict[int, int | None] = {}
    for index, (polygon, _) in enumerate(candidates):
        point = polygon.representative_point()
        containing = [
            (other.area, other_index)
            for other_index, (other, _) in enumerate(candidates)
            if other_index != index and other.area > polygon.area and other.contains(point)
        ]
        parents[index] = min(containing)[1] if containing else None

    def depth(index: int) -> int:
        value = 0
        seen: set[int] = set()
        parent = parents[index]
        while parent is not None:
            if parent in seen:
                raise SpatialConversionError("cyclic polygon ring containment")
            seen.add(parent)
            value += 1
            parent = parents[parent]
        return value

    polygons: list[Polygon] = []
    for index, (_, shell) in enumerate(candidates):
        if depth(index) % 2:
            continue
        holes = [
            list(candidates[child][1])
            for child, parent in parents.items()
            if parent == index and depth(child) % 2 == 1
        ]
        polygons.append(Polygon(shell, holes))
    if not polygons:
        return Polygon()
    geometry: BaseGeometry = polygons[0] if len(polygons) == 1 else MultiPolygon(polygons)
    return make_valid(geometry) if repair_invalid and not is_valid(geometry) else geometry


def arcgis_geometry(
    value: Mapping[str, Any] | None, *, repair_invalid: bool = True
) -> BaseGeometry | None:
    """Convert common ArcGIS JSON geometry forms into a Shapely geometry."""

    if value is None:
        return None
    if "curveRings" in value or "curvePaths" in value:
        raise SpatialConversionError(
            "ArcGIS true curves require densification with recorded tolerance"
        )
    if "x" in value and "y" in value:
        return Point(value["x"], value["y"])
    if "points" in value:
        return MultiPoint(value["points"])
    if "paths" in value:
        paths = value["paths"]
        lines = [LineString(path) for path in paths if len(path) >= 2]
        if not lines:
            return LineString()
        return lines[0] if len(lines) == 1 else MultiLineString(lines)
    if "rings" in value:
        return _arcgis_rings_to_geometry(value["rings"], repair_invalid=repair_invalid)
    if {"xmin", "ymin", "xmax", "ymax"} <= set(value):
        return Polygon(
            [
                (value["xmin"], value["ymin"]),
                (value["xmax"], value["ymin"]),
                (value["xmax"], value["ymax"]),
                (value["xmin"], value["ymax"]),
                (value["xmin"], value["ymin"]),
            ]
        )
    raise SpatialConversionError(f"unsupported ArcGIS geometry keys: {sorted(value)}")


def arcgis_features_to_geojson(
    payloads: Iterable[Mapping[str, Any]],
    *,
    object_id_field: str | None = None,
    repair_invalid: bool = True,
) -> tuple[list[dict[str, Any]], str | None]:
    """Convert paginated ArcGIS query payloads to GeoJSON-like feature records."""

    output: list[dict[str, Any]] = []
    crs: str | None = None
    for payload in payloads:
        spatial_reference = payload.get("spatialReference")
        if not spatial_reference:
            spatial_reference = payload.get("extent", {}).get("spatialReference")
        if isinstance(spatial_reference, Mapping):
            wkid = spatial_reference.get("latestWkid") or spatial_reference.get("wkid")
            if wkid:
                crs = f"EPSG:{wkid}"
        for source_feature in payload.get("features", []):
            attributes = dict(source_feature.get("attributes") or {})
            object_id = attributes.get(object_id_field) if object_id_field else None
            geometry = arcgis_geometry(
                source_feature.get("geometry"), repair_invalid=repair_invalid
            )
            output.append(
                {
                    "type": "Feature",
                    "id": object_id,
                    "properties": attributes,
                    "geometry_object": geometry,
                }
            )
    return output, crs


def geojson_features(payload: Mapping[str, Any]) -> tuple[list[dict[str, Any]], str | None]:
    """Read a GeoJSON FeatureCollection while preserving properties."""

    if payload.get("type") != "FeatureCollection" or not isinstance(payload.get("features"), list):
        raise SpatialConversionError("input must be a GeoJSON FeatureCollection")
    output: list[dict[str, Any]] = []
    for feature in payload["features"]:
        if not isinstance(feature, Mapping) or feature.get("type") != "Feature":
            raise SpatialConversionError("FeatureCollection contains a non-Feature member")
        geometry_value = feature.get("geometry")
        geometry = shape(geometry_value) if geometry_value is not None else None
        output.append(
            {
                "type": "Feature",
                "id": feature.get("id"),
                "properties": dict(feature.get("properties") or {}),
                "geometry_object": geometry,
            }
        )
    crs = None
    named_crs = payload.get("crs", {}).get("properties", {}).get("name")
    if isinstance(named_crs, str):
        crs = named_crs
    return output, crs


def _normalise_property_columns(features: list[dict[str, Any]]) -> dict[str, list[Any]]:
    keys = sorted({key for feature in features for key in feature["properties"]})
    result: dict[str, list[Any]] = {}
    for key in keys:
        output_key = f"source_{key}" if key.startswith("_riopa_") or key == "geometry" else key
        values = [feature["properties"].get(key) for feature in features]
        complex_values = any(isinstance(value, (dict, list, tuple)) for value in values)
        if complex_values:
            values = [
                json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
                if value is not None
                else None
                for value in values
            ]
        non_null = [value for value in values if value is not None]
        types = {type(value) for value in non_null}
        if str in types or len(types - {int, float, bool}) > 0:
            values = [str(value) if value is not None else None for value in values]
        elif float in types:
            values = [float(value) if value is not None else None for value in values]
        elif bool in types and int in types:
            values = [str(value) if value is not None else None for value in values]
        result[output_key] = values
    return result


def _stable_feature_id(
    source_id: str, layer_id: str, source_object_id: Any, feature: Mapping[str, Any]
) -> str:
    if source_object_id is None:
        identity = {
            "source_id": source_id,
            "layer_id": layer_id,
            "properties": feature["properties"],
            "geometry_wkb": (
                to_wkb(feature["geometry_object"], hex=True)
                if feature["geometry_object"] is not None
                else None
            ),
        }
    else:
        identity = {
            "source_id": source_id,
            "layer_id": layer_id,
            "source_object_id": str(source_object_id),
        }
    return f"urn:riopa:feature:{sha256_json(identity)}"


def _crs_metadata(crs: str | None) -> dict[str, Any] | None:
    if crs is None:
        return None
    return cast(dict[str, Any], CRS.from_user_input(crs).to_json_dict())


def materialize_features(
    features: list[dict[str, Any]],
    *,
    output_dir: str | Path,
    source_id: str,
    layer_id: str,
    capture_ids: Sequence[str],
    crs: str | None,
    object_id_field: str | None = None,
    base_name: str = "features",
    repair_invalid: bool = True,
) -> SpatialMaterialization:
    """Write canonical GeoParquet, DuckDB, and a quality report."""

    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    row_feature_pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    repaired = 0
    null_geometries = 0
    invalid_before = 0
    geometry_types: set[str] = set()
    bounds: list[tuple[float, float, float, float]] = []
    for feature in features:
        geometry: BaseGeometry | None = feature["geometry_object"]
        if geometry is None:
            null_geometries += 1
        elif not is_valid(geometry):
            invalid_before += 1
            if repair_invalid:
                geometry = make_valid(geometry)
                repaired += 1
        if geometry is not None and not geometry.is_empty:
            geometry_types.add(geometry.geom_type)
            bounds.append(geometry.bounds)
        source_object_id = (
            feature["properties"].get(object_id_field) if object_id_field else feature.get("id")
        )
        canonical_feature = {**feature, "geometry_object": geometry}
        row_feature_pairs.append(
            (
                {
                    "_riopa_feature_id": _stable_feature_id(
                        source_id, layer_id, source_object_id, canonical_feature
                    ),
                    "_riopa_source_id": source_id,
                    "_riopa_layer_id": layer_id,
                    "_riopa_source_object_id": (
                        str(source_object_id) if source_object_id is not None else None
                    ),
                    "_riopa_capture_ids": json.dumps(
                        list(feature.get("capture_ids", capture_ids)), separators=(",", ":")
                    ),
                    **(
                        {"_riopa_source_geometry_sha256": feature["source_geometry_sha256"]}
                        if "source_geometry_sha256" in feature
                        else {}
                    ),
                    "geometry": to_wkb(geometry) if geometry is not None else None,
                },
                canonical_feature,
            )
        )

    row_feature_pairs.sort(key=lambda item: item[0]["_riopa_feature_id"])
    rows = [item[0] for item in row_feature_pairs]
    sorted_features = [item[1] for item in row_feature_pairs]
    duplicate_ids = len(rows) - len({row["_riopa_feature_id"] for row in rows})
    if duplicate_ids:
        raise SpatialConversionError(
            f"{duplicate_ids} duplicate stable feature identifiers; provide a unique object ID"
        )
    base_columns = [
        "_riopa_feature_id",
        "_riopa_source_id",
        "_riopa_layer_id",
        "_riopa_source_object_id",
        "_riopa_capture_ids",
    ]
    if any("_riopa_source_geometry_sha256" in row for row in rows):
        base_columns.append("_riopa_source_geometry_sha256")
        for row in rows:
            row.setdefault("_riopa_source_geometry_sha256", None)
    base_columns.append("geometry")
    columns: dict[str, list[Any]] = {key: [row[key] for row in rows] for key in base_columns}
    columns.update(_normalise_property_columns(sorted_features))
    table = pa.table(columns)

    bbox = None
    if bounds:
        bbox = [
            min(item[0] for item in bounds),
            min(item[1] for item in bounds),
            max(item[2] for item in bounds),
            max(item[3] for item in bounds),
        ]
    geometry_column: dict[str, Any] = {
        "encoding": "WKB",
        "geometry_types": sorted(geometry_types),
    }
    crs_value = _crs_metadata(crs)
    if crs_value is not None:
        geometry_column["crs"] = crs_value
    if bbox is not None:
        geometry_column["bbox"] = bbox
    geo_metadata = {
        "version": "1.1.0",
        "primary_column": "geometry",
        "columns": {"geometry": geometry_column},
    }
    schema_metadata = dict(table.schema.metadata or {})
    schema_metadata[b"geo"] = json.dumps(
        geo_metadata, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    schema_metadata[b"riopa"] = json.dumps(
        {
            "source_id": source_id,
            "layer_id": layer_id,
            "capture_ids": list(capture_ids),
            "ordering": "_riopa_feature_id ascending",
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    table = table.replace_schema_metadata(schema_metadata)

    geoparquet_path = output / f"{base_name}.parquet"
    pq.write_table(
        table,
        geoparquet_path,
        compression="zstd",
        version="2.6",
        data_page_version="2.0",
        write_statistics=True,
        use_dictionary=True,
        row_group_size=65_536,
    )

    duckdb_path = output / f"{base_name}.duckdb"
    if duckdb_path.exists():
        duckdb_path.unlink()
    connection = duckdb.connect(str(duckdb_path))
    try:
        connection.execute(
            "CREATE TABLE features AS SELECT * FROM read_parquet(?)", [str(geoparquet_path)]
        )
        connection.execute("CREATE UNIQUE INDEX idx_feature_id ON features(_riopa_feature_id)")
        connection.execute(
            "CREATE TABLE riopa_metadata(key VARCHAR PRIMARY KEY, value JSON NOT NULL)"
        )
        metadata_rows = [
            ("source_id", json.dumps(source_id)),
            ("layer_id", json.dumps(layer_id)),
            ("capture_ids", json.dumps(list(capture_ids))),
            ("crs", json.dumps(crs)),
            ("geoparquet_sha256", json.dumps(sha256_file(geoparquet_path))),
        ]
        connection.executemany("INSERT INTO riopa_metadata VALUES (?, ?)", metadata_rows)
        connection.execute("CHECKPOINT")
    finally:
        connection.close()

    geoparquet_digest = sha256_file(geoparquet_path)
    duckdb_digest = sha256_file(duckdb_path)
    quality: dict[str, Any] = {
        "schema_version": "1.0.0",
        "record_type": "spatial_materialization_quality",
        "source_id": source_id,
        "layer_id": layer_id,
        "capture_ids": list(capture_ids),
        "feature_count": len(rows),
        "null_geometry_count": null_geometries,
        "invalid_geometry_count_before_repair": invalid_before,
        "repaired_geometry_count": repaired,
        "geometry_repair_enabled": repair_invalid,
        "duplicate_feature_id_count": duplicate_ids,
        "geometry_types": sorted(geometry_types),
        "bbox": bbox,
        "crs": crs,
        "geoparquet": {
            "path": geoparquet_path.name,
            "sha256": geoparquet_digest,
            "size_bytes": geoparquet_path.stat().st_size,
            "profile": "GeoParquet 1.1.0",
        },
        "duckdb": {
            "path": duckdb_path.name,
            "sha256": duckdb_digest,
            "size_bytes": duckdb_path.stat().st_size,
            "reproducibility_class": "deterministic-semantics",
        },
    }
    quality_report_path = output / f"{base_name}.quality.json"
    quality_report_path.write_text(
        json.dumps(quality, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return SpatialMaterialization(
        geoparquet_path=geoparquet_path,
        duckdb_path=duckdb_path,
        quality_report_path=quality_report_path,
        feature_count=len(rows),
        geoparquet_sha256=geoparquet_digest,
        duckdb_sha256=duckdb_digest,
    )


def materialize_geojson(
    input_path: str | Path,
    *,
    output_dir: str | Path,
    source_id: str,
    layer_id: str,
    capture_id: str,
    crs: str | None = None,
    object_id_field: str | None = None,
    base_name: str = "features",
) -> SpatialMaterialization:
    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    features, declared_crs = geojson_features(payload)
    return materialize_features(
        features,
        output_dir=output_dir,
        source_id=source_id,
        layer_id=layer_id,
        capture_ids=[capture_id],
        crs=crs or declared_crs,
        object_id_field=object_id_field,
        base_name=base_name,
    )


def _capture_payload(store_root: Path, capture_id: str) -> Mapping[str, Any]:
    safe_id = capture_id.removeprefix("urn:uuid:")
    metadata_path = resolve_local_reference(store_root, f"captures/{safe_id}.json")
    if not metadata_path.is_file():
        raise SpatialConversionError(f"capture metadata is missing: {capture_id}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if not isinstance(metadata, Mapping) or metadata.get("record_type") != "http_capture":
        raise SpatialConversionError(f"capture metadata is invalid: {capture_id}")
    if metadata.get("capture_id") != capture_id:
        raise SpatialConversionError(f"capture ID does not match metadata filename: {capture_id}")
    object_record = metadata.get("object")
    if not isinstance(object_record, Mapping) or not isinstance(
        object_record.get("storage_path"), str
    ):
        raise SpatialConversionError(f"capture has no object record: {capture_id}")
    object_path = resolve_local_reference(store_root, object_record["storage_path"])
    if not object_path.is_file():
        raise SpatialConversionError(f"capture object is missing: {capture_id}")
    if object_path.stat().st_size != object_record.get("size_bytes"):
        raise SpatialConversionError(f"capture object size mismatch: {capture_id}")
    if sha256_file(object_path) != object_record.get("sha256"):
        raise SpatialConversionError(f"capture object hash mismatch: {capture_id}")
    payload = json.loads(object_path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise SpatialConversionError(f"capture {capture_id} is not a JSON object")
    return payload


def _load_capture_set(path: str | Path, expected_type: str) -> dict[str, Any]:
    capture_set = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(capture_set, dict) or capture_set.get("record_type") != expected_type:
        raise SpatialConversionError(f"capture set must have record_type={expected_type}")
    expected_hash = sha256_json(capture_set, omit_keys={"manifest_sha256"})
    if capture_set.get("manifest_sha256") != expected_hash:
        raise SpatialConversionError("capture-set manifest hash mismatch")
    return capture_set


def materialize_arcgis_capture_set(
    capture_set_path: str | Path,
    *,
    store_root: str | Path,
    output_dir: str | Path,
    crs: str | None = None,
    base_name: str = "features",
    repair_invalid: bool = True,
) -> SpatialMaterialization:
    capture_set = _load_capture_set(capture_set_path, "arcgis_layer_capture_set")
    root = Path(store_root).resolve()
    metadata = _capture_payload(root, capture_set["metadata_capture_id"])
    object_id_field = capture_set.get("object_id_field") or metadata.get("objectIdField")
    if not object_id_field:
        object_id_field = next(
            (
                field.get("name")
                for field in metadata.get("fields", [])
                if isinstance(field, Mapping) and field.get("type") == "esriFieldTypeOID"
            ),
            None,
        )
    features: list[dict[str, Any]] = []
    payload_crs: str | None = None
    for capture_id in capture_set["page_capture_ids"]:
        page_features, page_crs = arcgis_features_to_geojson(
            [_capture_payload(root, capture_id)],
            object_id_field=object_id_field,
            repair_invalid=repair_invalid,
        )
        for feature in page_features:
            feature["capture_ids"] = [capture_id]
        features.extend(page_features)
        payload_crs = payload_crs or page_crs
    metadata_crs = None
    spatial_reference = metadata.get("extent", {}).get("spatialReference", {})
    wkid = spatial_reference.get("latestWkid") or spatial_reference.get("wkid")
    if wkid:
        metadata_crs = f"EPSG:{wkid}"
    capture_ids = [
        capture_set["metadata_capture_id"],
        *capture_set.get("count_capture_ids", []),
        *(
            [capture_set["object_ids_capture_id"]]
            if capture_set.get("object_ids_capture_id")
            else []
        ),
        *capture_set["page_capture_ids"],
    ]
    return materialize_features(
        features,
        output_dir=output_dir,
        source_id=capture_set["source_id"],
        layer_id=f"{capture_set['service_url']}/{capture_set['layer_id']}",
        capture_ids=capture_ids,
        crs=crs or payload_crs or metadata_crs,
        object_id_field=object_id_field,
        base_name=base_name,
        repair_invalid=repair_invalid,
    )


def materialize_wfs_capture_set(
    capture_set_path: str | Path,
    *,
    store_root: str | Path,
    output_dir: str | Path,
    crs: str | None = None,
    base_name: str = "features",
    canonical_layer_id: str | None = None,
) -> SpatialMaterialization:
    """Materialise a verified WFS GeoJSON capture set."""

    capture_set = _load_capture_set(capture_set_path, "wfs_feature_type_capture_set")
    root = Path(store_root).resolve()
    features: list[dict[str, Any]] = []
    payload_crs: str | None = None
    for capture_id in capture_set["page_capture_ids"]:
        payload = _capture_payload(root, capture_id)
        page_features, page_crs = geojson_features(payload)
        features.extend(page_features)
        payload_crs = payload_crs or page_crs
    capture_ids = [
        capture_set["capabilities_capture_id"],
        capture_set["schema_capture_id"],
        *capture_set["page_capture_ids"],
    ]
    if len(features) != capture_set["feature_count"]:
        raise SpatialConversionError(
            f"WFS feature count mismatch: materialised={len(features)} "
            f"capture-set={capture_set['feature_count']}"
        )
    return materialize_features(
        features,
        output_dir=output_dir,
        source_id=capture_set["source_id"],
        layer_id=(
            canonical_layer_id
            if canonical_layer_id is not None
            else f"{capture_set['service_url']}#{capture_set['type_name']}"
        ),
        capture_ids=capture_ids,
        crs=crs or capture_set.get("srs_name") or payload_crs,
        object_id_field=capture_set.get("id_property"),
        base_name=base_name,
    )
