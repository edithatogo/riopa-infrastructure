from __future__ import annotations

import pytest

from riopa_provenance.wfs import WFSFeatureTypeArchiver


@pytest.mark.parametrize("max_pages", [0, -1])
def test_wfs_archiver_requires_positive_page_budget(max_pages: int) -> None:
    with pytest.raises(ValueError, match="max_pages must be positive"):
        WFSFeatureTypeArchiver(None, max_pages=max_pages)  # type: ignore[arg-type]


def test_wfs_request_contract_rejects_invalid_page_size_and_version() -> None:
    archiver = WFSFeatureTypeArchiver(None)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="page_size must be between"):
        archiver.archive_feature_type(
            source_id="source",
            endpoint_id="endpoint",
            service_url="https://data.example/wfs",
            type_name="layer",
            page_size=0,
        )
    with pytest.raises(ValueError, match="WFS 2.0.0 only"):
        archiver.archive_feature_type(
            source_id="source",
            endpoint_id="endpoint",
            service_url="https://data.example/wfs",
            type_name="layer",
            version="1.1.0",
        )
