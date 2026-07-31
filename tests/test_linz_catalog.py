from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from riopa_provenance.capture import CaptureError, CaptureResult
from riopa_provenance.linz_catalog import (
    LinzCatalogArchiver,
    LinzCatalogDetailArchiver,
    LinzCatalogError,
    build_detail_queue,
    catalog_items_path,
    diff_catalog_items,
    load_catalog_items,
    normalise_catalog_item,
    parse_link_header,
    parse_resource_range,
    validate_detail_url,
    write_catalog_diff,
)


class _CatalogClient:
    def __init__(self, tmp_path: Path, pages: list[tuple[Any, dict[str, str]]]) -> None:
        self.tmp_path = tmp_path
        self.pages = iter(pages)
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def capture_json(self, method: str, url: str, **kwargs: Any) -> tuple[CaptureResult, Any]:
        payload, headers = next(self.pages)
        index = len(self.calls) + 1
        metadata = self.tmp_path / f"metadata-{index}.json"
        metadata.write_text(json.dumps({"response": {"headers": headers}}), encoding="utf-8")
        digest = str(headers.get("_digest", index)).zfill(64)
        result = CaptureResult(
            capture_id=f"urn:uuid:{index}",
            source_id=str(kwargs["source_id"]),
            endpoint_id=str(kwargs["endpoint_id"]),
            status_code=200,
            media_type="application/json",
            retrieved_at="2026-07-31T00:00:00Z",
            object_sha256=digest,
            size_bytes=len(json.dumps(payload)),
            object_path=self.tmp_path / f"object-{index}",
            metadata_path=metadata,
            request_fingerprint="f" * 64,
        )
        self.calls.append((url, kwargs))
        return result, payload


def test_pagination_headers_accept_supported_forms() -> None:
    assert parse_link_header(None) == {}
    assert parse_link_header(
        '<https://data.linz.govt.nz/services/api/v1.x/?page=2>; rel="page-next", </last>; rel=last'
    ) == {
        "page-next": "https://data.linz.govt.nz/services/api/v1.x/?page=2",
        "last": "/last",
    }
    assert parse_resource_range(" 0-25/101 ") == (0, 25, 101)
    assert parse_resource_range("25-50/*") == (25, 50, None)
    assert parse_resource_range(None) is None


@pytest.mark.parametrize("value", ["0-1", "first-last/10", "0-1/all", "-1-2/4"])
def test_resource_range_rejects_ambiguous_values(value: str) -> None:
    with pytest.raises(LinzCatalogError, match="invalid X-Resource-Range"):
        parse_resource_range(value)


def test_catalogue_normalisation_is_stable_and_requires_identity() -> None:
    raw = {
        "id": 42,
        "type": "layers",
        "title": "Road centrelines",
        "url": "https://data.linz.govt.nz/layer/42/",
        "tags": ["transport"],
    }
    first = normalise_catalog_item(raw)
    second = normalise_catalog_item(dict(reversed(list(raw.items()))))
    assert first == second
    assert first["catalog_item_id"] == "urn:riopa:linz-catalog:layer:42"
    assert first["name"] == "Road centrelines"
    assert first["raw"] == raw
    with pytest.raises(LinzCatalogError, match="has no id"):
        normalise_catalog_item({"name": "unidentified"})


def test_manifest_item_resolution_is_bounded_to_snapshot_root(tmp_path: Path) -> None:
    items = tmp_path / "items.jsonl"
    items.write_text('{"catalog_item_id":"urn:item:1"}\n', encoding="utf-8")
    manifest = tmp_path / "snapshot.manifest.json"
    manifest.write_text(json.dumps({"items": {"path": "items.jsonl"}}), encoding="utf-8")
    assert catalog_items_path(manifest) == items
    assert load_catalog_items(manifest) == [{"catalog_item_id": "urn:item:1"}]

    manifest.write_text(json.dumps({"items": {"path": "../escape.jsonl"}}), encoding="utf-8")
    with pytest.raises(LinzCatalogError, match="escapes snapshot root"):
        catalog_items_path(manifest)


def test_jsonl_loader_rejects_non_object_records(tmp_path: Path) -> None:
    path = tmp_path / "items.jsonl"
    path.write_text('{"catalog_item_id":"urn:item:1"}\n[]\n', encoding="utf-8")
    with pytest.raises(LinzCatalogError, match="line 2 is not an object"):
        load_catalog_items(path)


def test_catalogue_archiver_follows_pagination_and_writes_verifiable_snapshot(
    tmp_path: Path,
) -> None:
    client = _CatalogClient(
        tmp_path,
        [
            (
                [{"id": 2, "type": "tables", "name": "B"}],
                {
                    "x-resource-range": "0-1/2",
                    "link": '</catalog?page=2>; rel="page-next"',
                },
            ),
            (
                [{"id": 1, "url": "https://data.linz.govt.nz/layers/1/"}],
                {"x-resource-range": "1-2/2"},
            ),
        ],
    )
    snapshot = LinzCatalogArchiver(client).archive(  # type: ignore[arg-type]
        source_id="linz",
        endpoint_id="catalog",
        catalog_url="https://data.linz.govt.nz/catalog",
        output_dir=tmp_path / "snapshot",
    )
    assert snapshot.item_count == 2
    assert snapshot.page_count == 2
    assert [item["source_catalog_id"] for item in load_catalog_items(snapshot.manifest_path)] == [
        "1",
        "2",
    ]
    manifest = json.loads(snapshot.manifest_path.read_text(encoding="utf-8"))
    assert manifest["completeness"]["catalogue_enumerated"] is True
    assert manifest["completeness"]["unfiltered_published_catalogue"] is True
    assert client.calls[0][1]["params"] == {"sort": "name"}
    assert client.calls[1][1]["params"] is None


@pytest.mark.parametrize(
    ("pages", "max_pages", "message"),
    [
        ([({"not": "an array"}, {})], 2, "not a JSON array"),
        ([([{"id": 1}, "bad"], {})], 2, "non-object entry"),
        ([([{"id": 1}], {"x-resource-range": "0-2/1"})], 2, "disagrees"),
        (
            [
                ([{"id": 1}], {"x-resource-range": "0-1/2", "link": "</p2>; rel=next"}),
                ([{"id": 2}], {"x-resource-range": "1-2/3"}),
            ],
            3,
            "total changed",
        ),
        ([([{"id": 1}], {"link": "<https://example.test/p2>; rel=next"})], 2, "changes host"),
        ([([{"id": 1}], {"link": "</catalog>; rel=next"})], 2, "pagination loop"),
        ([([{"id": 1}], {"link": "</p2>; rel=next"})], 1, "exceeded max_pages"),
        ([([{"id": 1}, {"id": 1}], {})], 2, "duplicate catalogue item"),
        ([([{"id": 1}], {"x-resource-range": "0-1/2"})], 2, "incomplete"),
    ],
)
def test_catalogue_archiver_fails_closed_on_incomplete_or_unsafe_pages(
    tmp_path: Path,
    pages: list[tuple[Any, dict[str, str]]],
    max_pages: int,
    message: str,
) -> None:
    client = _CatalogClient(tmp_path, pages)
    with pytest.raises(LinzCatalogError, match=message):
        LinzCatalogArchiver(client, max_pages=max_pages).archive(  # type: ignore[arg-type]
            source_id="linz",
            endpoint_id="catalog",
            catalog_url="https://data.linz.govt.nz/catalog",
            output_dir=tmp_path / "snapshot",
        )


def test_catalogue_diff_file_binds_inputs_and_results(tmp_path: Path) -> None:
    previous = tmp_path / "previous.jsonl"
    current = tmp_path / "current.jsonl"
    previous.write_text('{"catalog_item_id":"a","raw_sha256":"old"}\n', encoding="utf-8")
    current.write_text(
        '{"catalog_item_id":"a","raw_sha256":"new"}\n{"catalog_item_id":"b","raw_sha256":"same"}\n',
        encoding="utf-8",
    )
    output = write_catalog_diff(previous, current, tmp_path / "reports" / "diff.json")
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["changed"] == ["a"]
    assert report["added"] == ["b"]
    assert report["report_sha256"]


def test_detail_archiver_resumes_valid_receipts_and_rejects_bad_payloads(
    tmp_path: Path,
) -> None:
    jobs = build_detail_queue(
        [
            {
                "catalog_item_id": "urn:item:1",
                "source_catalog_id": "1",
                "item_type": "layer",
                "url": "https://data.linz.govt.nz/layer/1/",
            }
        ]
    )
    client = _CatalogClient(tmp_path, [({"id": 1, "name": "Layer"}, {})])
    archiver = LinzCatalogDetailArchiver(client)  # type: ignore[arg-type]
    first = archiver.archive_jobs(
        jobs, source_id="linz", endpoint_id="catalog", output_dir=tmp_path / "details"
    )
    assert len(first) == 1
    assert (
        archiver.archive_jobs(
            jobs, source_id="linz", endpoint_id="catalog", output_dir=tmp_path / "details"
        )
        == first
    )
    assert len(client.calls) == 1

    receipt = json.loads(first[0].read_text(encoding="utf-8"))
    receipt["receipt_sha256"] = "0" * 64
    first[0].write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(LinzCatalogError, match="receipt is corrupt"):
        archiver.archive_jobs(
            jobs, source_id="linz", endpoint_id="catalog", output_dir=tmp_path / "details"
        )

    bad_client = _CatalogClient(tmp_path, [([], {})])
    with pytest.raises(CaptureError, match="detail is not an object"):
        LinzCatalogDetailArchiver(bad_client).archive_jobs(  # type: ignore[arg-type]
            jobs,
            source_id="linz",
            endpoint_id="catalog",
            output_dir=tmp_path / "bad-details",
        )


def test_detail_archiver_limit_and_non_capture_jobs_do_not_request(tmp_path: Path) -> None:
    client = _CatalogClient(tmp_path, [])
    archiver = LinzCatalogDetailArchiver(client)  # type: ignore[arg-type]
    assert (
        archiver.archive_jobs(
            [{"disposition": "metadata-summary-only"}],
            source_id="linz",
            endpoint_id="catalog",
            output_dir=tmp_path,
            limit=0,
        )
        == []
    )
    with pytest.raises(ValueError, match="limit must be non-negative"):
        archiver.archive_jobs(
            [], source_id="linz", endpoint_id="catalog", output_dir=tmp_path, limit=-1
        )


def test_catalogue_diff_classifies_every_identity_deterministically() -> None:
    previous = [
        {"catalog_item_id": "urn:item:removed", "raw_sha256": "a"},
        {"catalog_item_id": "urn:item:changed", "raw_sha256": "old"},
        {"catalog_item_id": "urn:item:same", "raw_sha256": "same"},
    ]
    current = [
        {"catalog_item_id": "urn:item:same", "raw_sha256": "same"},
        {"catalog_item_id": "urn:item:added", "raw_sha256": "b"},
        {"catalog_item_id": "urn:item:changed", "raw_sha256": "new"},
    ]
    result = diff_catalog_items(reversed(previous), reversed(current))
    assert result.as_dict() == {
        "added": ["urn:item:added"],
        "removed": ["urn:item:removed"],
        "changed": ["urn:item:changed"],
        "unchanged": ["urn:item:same"],
        "counts": {"added": 1, "removed": 1, "changed": 1, "unchanged": 1},
    }


def test_detail_queue_is_stable_sharded_and_explicit_about_missing_urls() -> None:
    items = [
        {
            "catalog_item_id": "urn:item:2",
            "source_catalog_id": "2",
            "item_type": "table",
            "url": None,
        },
        {
            "catalog_item_id": "urn:item:1",
            "source_catalog_id": "1",
            "item_type": "layer",
            "url": "https://data.linz.govt.nz/layer/1/",
        },
    ]
    jobs = build_detail_queue(items, shard_count=3)
    assert [job["catalog_item_id"] for job in jobs] == ["urn:item:1", "urn:item:2"]
    assert all(0 <= job["shard"] < 3 for job in jobs)
    assert jobs[0]["disposition"] == "capture-item-detail"
    assert jobs[0]["blocked_reason"] is None
    assert jobs[1]["disposition"] == "metadata-summary-only"
    assert jobs[1]["blocked_reason"]
    assert jobs == build_detail_queue(reversed(items), shard_count=3)
    with pytest.raises(ValueError, match="shard_count must be positive"):
        build_detail_queue(items, shard_count=0)


@pytest.mark.parametrize(
    ("url", "message"),
    [
        ("http://data.linz.govt.nz/layer/1/", "must use HTTPS"),
        ("https://user:pass@data.linz.govt.nz/layer/1/", "credentials"),
        ("https://example.test/layer/1/", "changes host"),
    ],
)
def test_detail_url_fails_closed(url: str, message: str) -> None:
    with pytest.raises(LinzCatalogError, match=message):
        validate_detail_url(url, expected_host="data.linz.govt.nz")
    validate_detail_url(
        "https://DATA.LINZ.GOVT.NZ/layer/1/",
        expected_host="data.linz.govt.nz",
    )
