from __future__ import annotations

import pytest

from riopa_provenance.arcgis import (
    ArcGISFeatureLayerArchiver,
    _effective_out_fields,
    _feature_object_ids,
)
from riopa_provenance.capture import CaptureError


def test_arcgis_out_fields_always_include_object_id() -> None:
    assert _effective_out_fields("*", "OBJECTID") == "*"
    assert _effective_out_fields("name,shape", "OBJECTID") == "name,shape,OBJECTID"
    assert _effective_out_fields("name,objectid", "OBJECTID") == "name,objectid"


def test_arcgis_feature_ids_require_integer_attributes() -> None:
    assert _feature_object_ids(
        [{"attributes": {"OBJECTID": 1}}, {"attributes": {"OBJECTID": 2}}],
        "OBJECTID",
    ) == [1, 2]
    with pytest.raises(CaptureError, match="attributes object"):
        _feature_object_ids([{"geometry": {}}], "OBJECTID")
    with pytest.raises(CaptureError, match="invalid integer"):
        _feature_object_ids([{"attributes": {"OBJECTID": "1"}}], "OBJECTID")
    with pytest.raises(CaptureError, match="invalid integer"):
        _feature_object_ids([{"attributes": {"OBJECTID": True}}], "OBJECTID")


@pytest.mark.parametrize("max_pages", [0, -1])
def test_arcgis_archiver_requires_positive_page_budget(max_pages: int) -> None:
    with pytest.raises(ValueError, match="max_pages must be positive"):
        ArcGISFeatureLayerArchiver(None, max_pages=max_pages)  # type: ignore[arg-type]
