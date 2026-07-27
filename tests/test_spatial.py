from __future__ import annotations

import pytest

from riopa_provenance.spatial import (
    SpatialConversionError,
    arcgis_features_to_geojson,
    arcgis_geometry,
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
