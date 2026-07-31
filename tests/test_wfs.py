from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from riopa_provenance.capture import CaptureError, CaptureResult
from riopa_provenance.wfs import WFSFeatureTypeArchiver


def _capture(tmp_path: Path, endpoint: str, digest: str) -> CaptureResult:
    return CaptureResult(
        capture_id=f"urn:uuid:{endpoint}",
        source_id="source",
        endpoint_id=endpoint,
        status_code=200,
        media_type="application/json",
        retrieved_at="2026-07-31T00:00:00Z",
        object_sha256=digest,
        size_bytes=2,
        object_path=tmp_path / "object",
        metadata_path=tmp_path / "metadata",
        request_fingerprint="f" * 64,
    )


class _WFSClient:
    def __init__(self, tmp_path: Path, pages: list[Any]) -> None:
        self.store = SimpleNamespace(root=tmp_path)
        self.pages = iter(pages)
        self.requests: list[dict[str, Any]] = []

    def capture(self, method: str, url: str, **kwargs: Any) -> CaptureResult:
        del method, url
        self.requests.append(kwargs)
        return _capture(self.store.root, kwargs["endpoint_id"], kwargs["endpoint_id"] * 4)

    def capture_json(self, method: str, url: str, **kwargs: Any) -> tuple[CaptureResult, Any]:
        del method, url
        self.requests.append(kwargs)
        endpoint = kwargs["endpoint_id"]
        payload = next(self.pages)
        digest = payload.pop("_digest", endpoint * 4) if isinstance(payload, dict) else endpoint * 4
        return _capture(self.store.root, endpoint, digest), payload


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


def test_wfs_archive_pages_with_property_ids_and_manifest(tmp_path: Path) -> None:
    client = _WFSClient(
        tmp_path,
        [
            {
                "type": "FeatureCollection",
                "numberMatched": "3",
                "features": [
                    {"properties": {"fid": 1}},
                    {"properties": {"fid": 2}},
                ],
            },
            {
                "type": "FeatureCollection",
                "numberMatched": 3,
                "features": [{"properties": {"fid": 3}}],
            },
        ],
    )
    result = WFSFeatureTypeArchiver(client).archive_feature_type(
        source_id="source",
        endpoint_id="wfs",
        service_url="https://secret.example/wfs",
        type_name="plan:zones",
        page_size=2,
        sort_by="fid ASC",
        id_property="fid",
        srs_name="EPSG:2193",
        cql_filter="status='current'",
        request_params={"token": "secret"},
        redact_values=("secret",),
    )

    assert result.feature_count == 3
    manifest = json.loads(result.manifest_path.read_text())
    assert manifest["service_url"] == "https://REDACTED.example/wfs"
    assert manifest["declared_feature_count"] == 3
    page_requests = [
        item for item in client.requests if ":get-feature-page-" in item["endpoint_id"]
    ]
    assert [item["params"]["startIndex"] for item in page_requests] == [0, 2]
    assert page_requests[0]["params"]["sortBy"] == "fid ASC"
    assert page_requests[0]["params"]["srsName"] == "EPSG:2193"
    assert page_requests[0]["params"]["CQL_FILTER"] == "status='current'"


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ([], "FeatureCollection"),
        ({"type": "Feature"}, "FeatureCollection"),
        ({"type": "FeatureCollection"}, "features array"),
        (
            {"type": "FeatureCollection", "features": [None]},
            "non-object value",
        ),
    ],
)
def test_wfs_rejects_malformed_geojson(tmp_path: Path, payload: Any, message: str) -> None:
    client = _WFSClient(tmp_path, [payload])
    with pytest.raises(CaptureError, match=message):
        WFSFeatureTypeArchiver(client).archive_feature_type(
            source_id="source",
            endpoint_id="wfs",
            service_url="https://data.example/wfs",
            type_name="layer",
        )


def test_wfs_requires_stable_multi_page_identity_and_sort(tmp_path: Path) -> None:
    no_sort = _WFSClient(
        tmp_path / "no-sort",
        [{"type": "FeatureCollection", "features": [{"id": 1}]}],
    )
    with pytest.raises(CaptureError, match="requires sort_by"):
        WFSFeatureTypeArchiver(no_sort).archive_feature_type(
            source_id="source",
            endpoint_id="wfs",
            service_url="https://data.example/wfs",
            type_name="layer",
            page_size=1,
        )

    no_id = _WFSClient(
        tmp_path / "no-id",
        [{"type": "FeatureCollection", "features": [{"properties": {}}]}],
    )
    with pytest.raises(CaptureError, match="feature IDs or id_property"):
        WFSFeatureTypeArchiver(no_id).archive_feature_type(
            source_id="source",
            endpoint_id="wfs",
            service_url="https://data.example/wfs",
            type_name="layer",
            page_size=1,
            sort_by="fid",
        )


def test_wfs_rejects_duplicate_ids_and_repeated_pages(tmp_path: Path) -> None:
    duplicate = _WFSClient(
        tmp_path / "duplicate",
        [
            {"type": "FeatureCollection", "features": [{"id": "same"}]},
            {"type": "FeatureCollection", "features": [{"id": "same"}]},
        ],
    )
    with pytest.raises(CaptureError, match="duplicate WFS feature identity"):
        WFSFeatureTypeArchiver(duplicate).archive_feature_type(
            source_id="source",
            endpoint_id="wfs",
            service_url="https://data.example/wfs",
            type_name="layer",
            page_size=1,
            sort_by="id",
        )

    repeated = _WFSClient(
        tmp_path / "repeated",
        [
            {
                "type": "FeatureCollection",
                "features": [{"properties": {}}],
                "_digest": "same",
            },
            {
                "type": "FeatureCollection",
                "features": [{"properties": {}}],
                "_digest": "same",
            },
        ],
    )
    with pytest.raises(CaptureError, match="repeated non-empty page"):
        WFSFeatureTypeArchiver(repeated).archive_feature_type(
            source_id="source",
            endpoint_id="wfs",
            service_url="https://data.example/wfs",
            type_name="layer",
            page_size=1,
            sort_by="fid",
            id_property="fid",
        )


@pytest.mark.parametrize(
    ("pages", "message"),
    [
        (
            [
                {
                    "type": "FeatureCollection",
                    "numberMatched": 0,
                    "features": [{"id": 1}],
                }
            ],
            "but numberMatched=0",
        ),
        (
            [
                {
                    "type": "FeatureCollection",
                    "numberMatched": 2,
                    "features": [{"id": 1}],
                },
                {
                    "type": "FeatureCollection",
                    "numberMatched": 2,
                    "features": [],
                },
            ],
            "captured 1 WFS features",
        ),
    ],
)
def test_wfs_reconciles_declared_total(tmp_path: Path, pages: list[Any], message: str) -> None:
    client = _WFSClient(tmp_path, pages)
    with pytest.raises(CaptureError, match=message):
        WFSFeatureTypeArchiver(client).archive_feature_type(
            source_id="source",
            endpoint_id="wfs",
            service_url="https://data.example/wfs",
            type_name="layer",
            page_size=1,
            sort_by="id",
        )


def test_wfs_enforces_page_budget(tmp_path: Path) -> None:
    client = _WFSClient(
        tmp_path,
        [{"type": "FeatureCollection", "features": [{"id": 1}]}],
    )
    with pytest.raises(CaptureError, match="exceeded max_pages=1"):
        WFSFeatureTypeArchiver(client, max_pages=1).archive_feature_type(
            source_id="source",
            endpoint_id="wfs",
            service_url="https://data.example/wfs",
            type_name="layer",
            page_size=1,
            sort_by="id",
        )
