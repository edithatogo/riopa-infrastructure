from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from riopa_provenance.arcgis import (
    ArcGISFeatureLayerArchiver,
    _effective_out_fields,
    _feature_object_ids,
)
from riopa_provenance.capture import CaptureError, CaptureResult


def _capture(tmp_path: Path, endpoint_id: str, digest: str = "a" * 64) -> CaptureResult:
    return CaptureResult(
        capture_id=f"urn:uuid:{endpoint_id}",
        source_id="source",
        endpoint_id=endpoint_id,
        status_code=200,
        media_type="application/json",
        retrieved_at="2026-07-31T00:00:00Z",
        object_sha256=digest,
        size_bytes=2,
        object_path=tmp_path / "object",
        metadata_path=tmp_path / "metadata",
        request_fingerprint="f" * 64,
    )


class _ArcGISClient:
    def __init__(
        self,
        tmp_path: Path,
        metadata: Any,
        *,
        counts: tuple[Any, Any] = (0, 0),
        ids: Any = None,
        pages: list[Any] | None = None,
    ) -> None:
        self.store = SimpleNamespace(root=tmp_path)
        self.metadata = metadata
        self.counts = iter(counts)
        self.ids = ids
        self.pages = iter(pages or [])
        self.requests: list[dict[str, Any]] = []

    def capture_json(self, method: str, url: str, **kwargs: Any) -> tuple[CaptureResult, Any]:
        del method, url
        self.requests.append(kwargs)
        endpoint = kwargs["endpoint_id"]
        params = kwargs["params"]
        capture = _capture(self.store.root, endpoint)
        if endpoint.endswith(":layer-metadata"):
            return capture, self.metadata
        if params.get("returnCountOnly") == "true":
            return capture, next(self.counts)
        if params.get("returnIdsOnly") == "true":
            return capture, self.ids
        return capture, next(self.pages)


def test_arcgis_out_fields_always_include_object_id() -> None:
    assert _effective_out_fields("name", None) == "name"
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


def test_arcgis_offset_archive_writes_redacted_manifest(tmp_path: Path) -> None:
    client = _ArcGISClient(
        tmp_path,
        {
            "objectIdField": "OBJECTID",
            "maxRecordCount": 2,
            "advancedQueryCapabilities": {"supportsPagination": True},
        },
        counts=({"count": 3}, {"count": 3}),
        pages=[
            {
                "features": [
                    {"attributes": {"OBJECTID": 1}},
                    {"attributes": {"OBJECTID": 2}},
                ],
                "exceededTransferLimit": True,
            },
            {"features": [{"attributes": {"OBJECTID": 3}}]},
        ],
    )
    result = ArcGISFeatureLayerArchiver(client).archive_layer(
        source_id="source",
        endpoint_id="layer",
        service_url="https://secret.example/token/FeatureServer/",
        layer_id=4,
        out_fields="name",
        request_params={"token": "secret"},
        redact_values=("secret",),
    )

    assert result.feature_count == 3
    manifest = json.loads(result.manifest_path.read_text())
    assert manifest["service_url"] == "https://REDACTED.example/token/FeatureServer"
    assert manifest["pagination_strategy"] == "offset"
    assert manifest["query"]["out_fields"] == "name,OBJECTID"
    page_requests = [item for item in client.requests if ":query-page-" in item["endpoint_id"]]
    assert [item["params"]["resultOffset"] for item in page_requests] == [0, 2]
    assert all(item["params"]["orderByFields"] == "OBJECTID ASC" for item in page_requests)


def test_arcgis_object_id_archive_sorts_and_chunks(tmp_path: Path) -> None:
    client = _ArcGISClient(
        tmp_path,
        {
            "objectIdFieldName": "fid",
            "maxRecordCount": 2,
            "advancedQueryCapabilities": {"supportsPagination": False},
        },
        counts=({"count": 3}, {"count": 3}),
        ids={"objectIds": [3, 1, 2]},
        pages=[
            {"features": [{"attributes": {"fid": 1}}, {"attributes": {"fid": 2}}]},
            {"features": [{"attributes": {"fid": 3}}]},
        ],
    )
    result = ArcGISFeatureLayerArchiver(client).archive_layer(
        source_id="source",
        endpoint_id="layer",
        service_url="https://data.example/FeatureServer",
        layer_id=0,
    )
    manifest = json.loads(result.manifest_path.read_text())
    assert result.feature_count == 3
    assert result.object_ids_capture is not None
    assert manifest["pagination_strategy"] == "object_ids"
    chunk_requests = [item for item in client.requests if ":object-id-page-" in item["endpoint_id"]]
    assert [item["params"]["objectIds"] for item in chunk_requests] == ["1,2", "3"]


@pytest.mark.parametrize(
    ("metadata", "counts", "pages", "message"),
    [
        ([], ({"count": 0}, {"count": 0}), [], "metadata response"),
        ({"error": "denied"}, ({"count": 0}, {"count": 0}), [], "metadata error"),
        ({}, ({"count": True}, {"count": 0}), [], "non-negative integer"),
        ({}, ({"error": "bad"}, {"count": 0}), [], "count query failed"),
        ({}, ({"count": 0}, {"count": 0}), [[]], "JSON object"),
        ({}, ({"count": 0}, {"count": 0}), [{"error": "bad"}], "query error"),
        ({}, ({"count": 0}, {"count": 0}), [{}], "features array"),
        (
            {"objectIdField": "id", "maxRecordCount": 2},
            ({"count": 2}, {"count": 2}),
            [
                {
                    "features": [
                        {"attributes": {"id": 1}},
                        {"attributes": {"id": 1}},
                    ]
                }
            ],
            "duplicate object IDs",
        ),
        (
            {"maxRecordCount": 1},
            ({"count": 1}, {"count": 1}),
            [{"features": [], "exceededTransferLimit": True}],
            "empty page",
        ),
    ],
)
def test_arcgis_offset_capture_rejects_malformed_or_inconsistent_responses(
    tmp_path: Path,
    metadata: Any,
    counts: tuple[Any, Any],
    pages: list[Any],
    message: str,
) -> None:
    client = _ArcGISClient(tmp_path, metadata, counts=counts, pages=pages)
    with pytest.raises(CaptureError, match=message):
        ArcGISFeatureLayerArchiver(client).archive_layer(
            source_id="source",
            endpoint_id="layer",
            service_url="https://data.example/FeatureServer",
            layer_id=0,
        )


@pytest.mark.parametrize(
    ("metadata", "counts", "ids", "pages", "message"),
    [
        (
            {"advancedQueryCapabilities": {"supportsPagination": False}},
            ({"count": 0}, {"count": 0}),
            {"objectIds": []},
            [],
            "no object ID field",
        ),
        (
            {
                "objectIdField": "id",
                "advancedQueryCapabilities": {"supportsPagination": False},
            },
            ({"count": 1}, {"count": 1}),
            {"error": "bad"},
            [],
            "object-ID query failed",
        ),
        (
            {
                "objectIdField": "id",
                "advancedQueryCapabilities": {"supportsPagination": False},
            },
            ({"count": 1}, {"count": 1}),
            {},
            [],
            "no objectIds array",
        ),
        (
            {
                "objectIdField": "id",
                "advancedQueryCapabilities": {"supportsPagination": False},
            },
            ({"count": 1}, {"count": 1}),
            {"objectIds": [True]},
            [],
            "non-integer ID",
        ),
        (
            {
                "objectIdField": "id",
                "advancedQueryCapabilities": {"supportsPagination": False},
            },
            ({"count": 2}, {"count": 2}),
            {"objectIds": [1, 1]},
            [],
            "duplicate IDs",
        ),
        (
            {
                "objectIdField": "id",
                "advancedQueryCapabilities": {"supportsPagination": False},
            },
            ({"count": 2}, {"count": 2}),
            {"objectIds": [1]},
            [],
            "does not match count",
        ),
        (
            {
                "objectIdField": "id",
                "advancedQueryCapabilities": {"supportsPagination": False},
            },
            ({"count": 1}, {"count": 1}),
            {"objectIds": [1]},
            [{"features": [{"attributes": {"id": 1}}], "exceededTransferLimit": True}],
            "still exceeded",
        ),
        (
            {
                "objectIdField": "id",
                "advancedQueryCapabilities": {"supportsPagination": False},
            },
            ({"count": 1}, {"count": 1}),
            {"objectIds": [1]},
            [{"features": [{"attributes": {"id": 2}}]}],
            "exact requested ID sequence",
        ),
    ],
)
def test_arcgis_object_id_capture_fails_closed(
    tmp_path: Path,
    metadata: Any,
    counts: tuple[Any, Any],
    ids: Any,
    pages: list[Any],
    message: str,
) -> None:
    client = _ArcGISClient(tmp_path, metadata, counts=counts, ids=ids, pages=pages)
    with pytest.raises(CaptureError, match=message):
        ArcGISFeatureLayerArchiver(client).archive_layer(
            source_id="source",
            endpoint_id="layer",
            service_url="https://data.example/FeatureServer",
            layer_id=0,
        )


def test_arcgis_reconciles_source_counts_and_completeness(tmp_path: Path) -> None:
    changed = _ArcGISClient(
        tmp_path / "changed",
        {},
        counts=({"count": 0}, {"count": 1}),
        pages=[{"features": []}],
    )
    with pytest.raises(CaptureError, match="source count changed"):
        ArcGISFeatureLayerArchiver(changed).archive_layer(
            source_id="source",
            endpoint_id="layer",
            service_url="https://data.example/FeatureServer",
            layer_id=0,
        )

    incomplete = _ArcGISClient(
        tmp_path / "incomplete",
        {},
        counts=({"count": 1}, {"count": 1}),
        pages=[{"features": []}],
    )
    with pytest.raises(CaptureError, match="capture is incomplete"):
        ArcGISFeatureLayerArchiver(incomplete).archive_layer(
            source_id="source",
            endpoint_id="layer",
            service_url="https://data.example/FeatureServer",
            layer_id=0,
        )


def test_arcgis_enforces_page_budget(tmp_path: Path) -> None:
    client = _ArcGISClient(
        tmp_path,
        {"maxRecordCount": 1},
        counts=({"count": 2}, {"count": 2}),
        pages=[{"features": [{"attributes": {}}], "exceededTransferLimit": True}],
    )
    with pytest.raises(CaptureError, match="exceeded max_pages=1"):
        ArcGISFeatureLayerArchiver(client, max_pages=1).archive_layer(
            source_id="source",
            endpoint_id="layer",
            service_url="https://data.example/FeatureServer",
            layer_id=0,
        )
