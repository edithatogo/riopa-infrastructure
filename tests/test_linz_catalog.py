from __future__ import annotations

import json
from pathlib import Path

import pytest

from riopa_provenance.linz_catalog import (
    LinzCatalogError,
    build_detail_queue,
    catalog_items_path,
    diff_catalog_items,
    load_catalog_items,
    normalise_catalog_item,
    parse_link_header,
    parse_resource_range,
    validate_detail_url,
)


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
