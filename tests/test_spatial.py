from __future__ import annotations

import pytest
from shapely.geometry import Point

from riopa_provenance.spatial import (
    SpatialConversionError,
    arcgis_features_to_geojson,
    arcgis_geometry,
    compare_feature_snapshots,
    geojson_features,
)


def test_arcgis_geometry_supports_common_forms() -> None:
    assert arcgis_geometry({"x": 1, "y": 2}).geom_type == "Point"
    assert arcgis_geometry({"paths": [[[0, 0], [1, 1]]]}).geom_type == "LineString"
    assert arcgis_geometry({"xmin": 0, "ymin": 0, "xmax": 1, "ymax": 1}).area == 1


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
