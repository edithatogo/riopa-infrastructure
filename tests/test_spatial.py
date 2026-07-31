from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pyarrow.parquet as pq
import pytest
from shapely.geometry import Point, Polygon

from riopa_provenance.spatial import (
    SpatialConversionError,
    arcgis_features_to_geojson,
    arcgis_geometry,
    compare_feature_snapshots,
    geojson_features,
    materialize_features,
    materialize_geojson,
)


def test_arcgis_geometry_supports_common_forms() -> None:
    assert arcgis_geometry({"x": 1, "y": 2}).geom_type == "Point"
    assert arcgis_geometry({"points": [[1, 2], [3, 4]]}).geom_type == "MultiPoint"
    assert arcgis_geometry({"paths": [[[0, 0], [1, 1]]]}).geom_type == "LineString"
    multiline = arcgis_geometry({"paths": [[[0, 0]], [[0, 0], [1, 1]], [[2, 2], [3, 3]]]})
    assert multiline.geom_type == "MultiLineString"
    assert arcgis_geometry({"paths": [[[0, 0]]]}).is_empty
    assert (
        arcgis_geometry(
            {
                "rings": [
                    [[0, 0], [4, 0], [4, 4], [0, 4], [0, 0]],
                    [[1, 1], [1, 2], [2, 2], [2, 1], [1, 1]],
                    [[8, 8], [9, 8], [9, 9], [8, 9], [8, 8]],
                ]
            }
        ).area
        == 16
    )
    assert arcgis_geometry({"rings": [[[0, 0], [1, 1], [0, 0]]]}).is_empty
    assert arcgis_geometry({"xmin": 0, "ymin": 0, "xmax": 1, "ymax": 1}).area == 1
    assert arcgis_geometry(None) is None
    with pytest.raises(SpatialConversionError, match="unsupported"):
        arcgis_geometry({"z": 1})


def test_arcgis_geometry_rejects_true_curves_without_tolerance() -> None:
    with pytest.raises(SpatialConversionError, match="true curves"):
        arcgis_geometry({"curvePaths": []})


def test_feature_conversion_preserves_ids_and_latest_wkid() -> None:
    features, crs = arcgis_features_to_geojson(
        [
            {
                "spatialReference": {"wkid": 2193},
                "features": [
                    {"attributes": {"OBJECTID": 7, "name": "A"}, "geometry": {"x": 1, "y": 2}}
                ],
            }
        ],
        object_id_field="OBJECTID",
    )
    assert crs == "EPSG:2193"
    assert features[0]["id"] == 7
    assert features[0]["properties"]["name"] == "A"


def test_geojson_features_rejects_non_feature_collection() -> None:
    with pytest.raises(SpatialConversionError, match="FeatureCollection"):
        geojson_features({"type": "Feature", "geometry": None})
    with pytest.raises(SpatialConversionError, match="non-Feature"):
        geojson_features({"type": "FeatureCollection", "features": [{"type": "nope"}]})


def test_geojson_features_reads_named_crs_and_null_geometry() -> None:
    features, crs = geojson_features(
        {
            "type": "FeatureCollection",
            "crs": {"properties": {"name": "EPSG:2193"}},
            "features": [
                {"type": "Feature", "id": "a", "properties": None, "geometry": None},
                {
                    "type": "Feature",
                    "properties": {"name": "point"},
                    "geometry": {"type": "Point", "coordinates": [1, 2]},
                },
            ],
        }
    )
    assert crs == "EPSG:2193"
    assert features[0]["properties"] == {}
    assert features[0]["geometry_object"] is None
    assert features[1]["geometry_object"].equals(Point(1, 2))


def _feature(identity: str, x: float, *, name: str, extra: str | None = None) -> dict[str, object]:
    properties = {"name": name}
    if extra is not None:
        properties["extra"] = extra
    return {
        "type": "Feature",
        "id": identity,
        "properties": properties,
        "geometry_object": Point(x, 0),
    }


def test_feature_difference_separates_change_classes_and_tolerance() -> None:
    report = compare_feature_snapshots(
        [
            _feature("removed", 0, name="old"),
            _feature("attribute", 1, name="before"),
            _feature("near", 2, name="same"),
            _feature("far", 3, name="same"),
        ],
        [
            _feature("added", 0, name="new", extra="schema"),
            _feature("attribute", 1, name="after", extra="schema"),
            _feature("near", 2.01, name="same", extra="schema"),
            _feature("far", 4, name="same", extra="schema"),
        ],
        geometry_tolerance=0.1,
    )

    assert report["added"] == ["added"]
    assert report["removed"] == ["removed"]
    assert report["attribute_changed"] == ["attribute", "far", "near"]
    assert report["geometry_changed_exact"] == ["far", "near"]
    assert report["geometry_changed_within_tolerance"] == ["near"]
    assert report["geometry_changed_beyond_tolerance"] == ["far"]
    assert report["schema_changed"] == {
        "changed": True,
        "added_properties": ["extra"],
        "removed_properties": [],
    }
    assert len(report["report_sha256"]) == 64


def test_feature_difference_rejects_invalid_identity_and_tolerance() -> None:
    with pytest.raises(SpatialConversionError, match="non-negative"):
        compare_feature_snapshots([], [], geometry_tolerance=-1)
    duplicate = [_feature("same", 0, name="a"), _feature("same", 1, name="b")]
    with pytest.raises(SpatialConversionError, match="duplicate feature identity"):
        compare_feature_snapshots(duplicate, [])
    with pytest.raises(SpatialConversionError, match="requires an id"):
        compare_feature_snapshots([{"properties": {}, "geometry_object": None}], [])
    with pytest.raises(SpatialConversionError, match="no properties"):
        compare_feature_snapshots([{"id": "x", "properties": None, "geometry_object": None}], [])
    with pytest.raises(SpatialConversionError, match="invalid geometry"):
        compare_feature_snapshots(
            [{"id": "x", "properties": {}, "geometry_object": "not geometry"}], []
        )


def test_feature_difference_identity_property_and_null_geometry() -> None:
    report = compare_feature_snapshots(
        [{"properties": {"key": 1}, "geometry_object": None}],
        [{"properties": {"key": 1}, "geometry_object": Point(0, 0)}],
        identity_property="key",
    )
    assert report["comparison_semantics"]["identity"] == "key"
    assert report["geometry_changed_beyond_tolerance"] == ["1"]


def test_materialize_features_writes_queryable_products_and_quality(tmp_path: Path) -> None:
    invalid = Polygon([(0, 0), (2, 2), (0, 2), (2, 0), (0, 0)])
    features = [
        {
            "id": "2",
            "properties": {
                "OBJECTID": 2,
                "geometry": "reserved",
                "_riopa_note": "reserved",
                "nested": {"b": 2, "a": 1},
                "mixed": True,
            },
            "geometry_object": invalid,
        },
        {
            "id": "1",
            "properties": {"OBJECTID": 1, "mixed": 1, "score": 1.5},
            "geometry_object": None,
        },
    ]
    result = materialize_features(
        features,
        output_dir=tmp_path,
        source_id="source",
        layer_id="layer",
        capture_ids=["capture"],
        crs="EPSG:2193",
        object_id_field="OBJECTID",
        base_name="sample",
    )
    assert result.feature_count == 2
    table = pq.read_table(result.geoparquet_path)
    assert table.column_names == [
        "_riopa_feature_id",
        "_riopa_source_id",
        "_riopa_layer_id",
        "_riopa_source_object_id",
        "_riopa_capture_ids",
        "geometry",
        "OBJECTID",
        "source__riopa_note",
        "source_geometry",
        "mixed",
        "nested",
        "score",
    ]
    assert json.loads(table.schema.metadata[b"geo"])["version"] == "1.1.0"
    with duckdb.connect(str(result.duckdb_path), read_only=True) as connection:
        assert connection.execute("SELECT count(*) FROM features").fetchone() == (2,)
    quality = json.loads(result.quality_report_path.read_text(encoding="utf-8"))
    assert quality["null_geometry_count"] == 1
    assert quality["invalid_geometry_count_before_repair"] == 1
    assert quality["repaired_geometry_count"] == 1
    assert quality["bbox"] is not None


def test_materialize_features_rejects_duplicate_stable_ids(tmp_path: Path) -> None:
    feature = {
        "id": None,
        "properties": {"OBJECTID": 1},
        "geometry_object": Point(0, 0),
    }
    with pytest.raises(SpatialConversionError, match="duplicate stable"):
        materialize_features(
            [feature, feature],
            output_dir=tmp_path,
            source_id="source",
            layer_id="layer",
            capture_ids=[],
            crs=None,
            object_id_field="OBJECTID",
        )


def test_materialize_geojson_uses_declared_and_override_crs(tmp_path: Path) -> None:
    source = tmp_path / "source.json"
    source.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "crs": {"properties": {"name": "EPSG:4326"}},
                "features": [
                    {
                        "type": "Feature",
                        "id": "one",
                        "properties": {},
                        "geometry": {"type": "Point", "coordinates": [174, -41]},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    result = materialize_geojson(
        source,
        output_dir=tmp_path / "out",
        source_id="source",
        layer_id="layer",
        capture_id="capture",
        crs="EPSG:2193",
    )
    quality = json.loads(result.quality_report_path.read_text(encoding="utf-8"))
    assert quality["crs"] == "EPSG:2193"
