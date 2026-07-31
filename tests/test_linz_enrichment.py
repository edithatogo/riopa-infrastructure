from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from riopa_provenance.capture import CaptureError, CaptureResult
from riopa_provenance.hashing import sha256_bytes, sha256_file, sha256_json
from riopa_provenance.linz_catalog import LinzCatalogError, normalise_catalog_item
from riopa_provenance.linz_enrichment import (
    LinzCatalogServiceArchiver,
    _detail_kind,
    _load_captured_json,
    _load_receipt,
    _receipt_index,
    _receipt_paths,
    build_service_queue,
    write_enriched_catalog_snapshot,
)


def test_service_queue_is_stable_and_explicit_about_owner_dispositions() -> None:
    items = [
        {
            "catalog_item_id": "urn:item:missing",
            "source_catalog_id": "missing",
            "item_type": "layer",
            "url": None,
        },
        {
            "catalog_item_id": "urn:item:table",
            "source_catalog_id": "table",
            "item_type": "table",
            "url": "https://data.linz.govt.nz/dataset/2/",
        },
        {
            "catalog_item_id": "urn:item:unknown",
            "source_catalog_id": "unknown",
            "item_type": "document",
            "url": "https://data.linz.govt.nz/dataset/3/",
        },
    ]
    jobs = build_service_queue(reversed(items))
    assert [job["catalog_item_id"] for job in jobs] == [
        "urn:item:missing",
        "urn:item:table",
        "urn:item:unknown",
    ]
    assert jobs[0]["disposition"] == "service-list-unavailable"
    assert jobs[0]["blocked_reason"]
    assert jobs[1]["disposition"] == "capture-service-list"
    assert jobs[1]["url"].endswith("/services/")
    assert jobs[2]["disposition"] == "not-a-service-owner"
    assert jobs[2]["url"] is None
    assert jobs == build_service_queue(items)


def _capture_result(tmp_path: Path, name: str, payload: bytes) -> CaptureResult:
    return CaptureResult(
        capture_id=f"capture-{name}",
        source_id="linz",
        endpoint_id=name,
        status_code=200,
        media_type="application/json",
        retrieved_at="2026-07-31T00:00:00Z",
        object_sha256=sha256_bytes(payload),
        size_bytes=len(payload),
        object_path=tmp_path / name,
        metadata_path=tmp_path / f"{name}.metadata.json",
        request_fingerprint=f"request-{name}",
    )


class FakeServiceClient:
    def __init__(self, result: CaptureResult, payload: Any) -> None:
        self.result = result
        self.payload = payload
        self.calls: list[tuple[str, str, dict[str, Any]]] = []

    def capture_json(self, method: str, url: str, **kwargs: Any) -> tuple[CaptureResult, Any]:
        self.calls.append((method, url, kwargs))
        return self.result, self.payload


def test_service_archiver_writes_deduplicated_resumable_receipt(tmp_path: Path) -> None:
    payload = [{"key": "wfs"}, {"key": "tiles"}, {"key": "wfs"}, {"other": 1}]
    encoded = json.dumps(payload).encode()
    client = FakeServiceClient(_capture_result(tmp_path, "services", encoded), payload)
    job = {
        "job_id": "urn:riopa:linz-service-job:abc",
        "catalog_item_id": "urn:riopa:linz-catalog:layer:1",
        "source_catalog_id": "1",
        "item_type": "layer",
        "url": "https://data.linz.govt.nz/layer/1/services/",
        "disposition": "capture-service-list",
    }
    archiver = LinzCatalogServiceArchiver(client)  # type: ignore[arg-type]
    paths = archiver.archive_jobs(
        [
            {**job, "disposition": "not-a-service-owner"},
            job,
        ],
        source_id="linz",
        endpoint_id="catalog",
        output_dir=tmp_path / "receipts",
        headers={"X-Test": "yes"},
        redact_values=("secret",),
    )
    assert len(paths) == 1
    receipt = _load_receipt(paths[0], "service")
    assert receipt["service_count"] == 4
    assert receipt["service_keys"] == ["tiles", "wfs"]
    assert receipt["receipt_sha256"] == sha256_json(receipt, omit_keys={"receipt_sha256"})
    assert len(client.calls) == 1
    assert (
        archiver.archive_jobs(
            [job],
            source_id="linz",
            endpoint_id="catalog",
            output_dir=tmp_path / "receipts",
        )
        == paths
    )
    assert len(client.calls) == 1

    with pytest.raises(ValueError, match="limit"):
        archiver.archive_jobs(
            [job],
            source_id="linz",
            endpoint_id="catalog",
            output_dir=tmp_path,
            limit=-1,
        )
    assert (
        archiver.archive_jobs(
            [job],
            source_id="linz",
            endpoint_id="catalog",
            output_dir=tmp_path / "limited",
            limit=0,
        )
        == []
    )


def test_service_archiver_rejects_bad_payload_and_wrong_resumed_job(
    tmp_path: Path,
) -> None:
    result = _capture_result(tmp_path, "bad", b"{}")
    client = FakeServiceClient(result, {"key": "not-an-array"})
    archiver = LinzCatalogServiceArchiver(client)  # type: ignore[arg-type]
    job = {
        "job_id": "urn:job:abc",
        "catalog_item_id": "urn:item:1",
        "source_catalog_id": "1",
        "item_type": "layer",
        "url": "https://data.linz.govt.nz/layer/1/services/",
        "disposition": "capture-service-list",
    }
    with pytest.raises(CaptureError, match="object array"):
        archiver.archive_jobs(
            [job],
            source_id="linz",
            endpoint_id="catalog",
            output_dir=tmp_path / "bad-payload",
        )

    receipts = tmp_path / "resumed"
    receipts.mkdir()
    path = receipts / "abc.json"
    wrong = {
        "job_id": "urn:job:different",
        "receipt_sha256": "",
    }
    wrong["receipt_sha256"] = sha256_json(wrong, omit_keys={"receipt_sha256"})
    path.write_text(json.dumps(wrong), encoding="utf-8")
    with pytest.raises(LinzCatalogError, match="another job"):
        archiver.archive_jobs(
            [job],
            source_id="linz",
            endpoint_id="catalog",
            output_dir=receipts,
        )


def _write_capture_and_receipt(
    root: Path,
    receipts: Path,
    *,
    item_id: str,
    payload: Any,
    label: str,
    record_type: str,
    source_id: str = "1",
) -> Path:
    encoded = json.dumps(payload, sort_keys=True).encode()
    digest = sha256_bytes(encoded)
    object_path = root / "objects" / "sha256" / digest[:2] / digest
    object_path.parent.mkdir(parents=True, exist_ok=True)
    object_path.write_bytes(encoded)
    receipt: dict[str, Any] = {
        "record_type": record_type,
        "catalog_item_id": item_id,
        "source_catalog_id": source_id,
        "capture_id": f"capture-{label}",
        "object_sha256": digest,
        f"{label}_sha256": sha256_json(payload),
        "receipt_sha256": "",
    }
    receipt["receipt_sha256"] = sha256_json(receipt, omit_keys={"receipt_sha256"})
    receipts.mkdir(parents=True, exist_ok=True)
    path = receipts / f"{label}.json"
    path.write_text(json.dumps(receipt), encoding="utf-8")
    return path


def _write_catalog_snapshot(tmp_path: Path, items: list[dict[str, Any]]) -> Path:
    items_path = tmp_path / "items.jsonl"
    items_path.write_text(
        "".join(json.dumps(item, sort_keys=True) + "\n" for item in items),
        encoding="utf-8",
    )
    manifest: dict[str, Any] = {
        "record_type": "linz_catalog_snapshot",
        "snapshot_id": "urn:snapshot:1",
        "items": {
            "path": items_path.name,
            "sha256": sha256_file(items_path),
            "size_bytes": items_path.stat().st_size,
        },
        "completeness": {"unfiltered_published_catalogue": True},
        "manifest_sha256": "",
    }
    manifest["manifest_sha256"] = sha256_json(manifest, omit_keys={"manifest_sha256"})
    path = tmp_path / "snapshot.manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


def test_write_enriched_snapshot_binds_detail_services_and_hashes(
    tmp_path: Path,
) -> None:
    summary = normalise_catalog_item(
        {
            "id": 1,
            "type": "layer",
            "title": "Summary title",
            "url": "https://data.linz.govt.nz/layer/1/",
        }
    )
    manifest_path = _write_catalog_snapshot(tmp_path, [summary])
    store = tmp_path / "store"
    details = tmp_path / "details"
    services = tmp_path / "services"
    _write_capture_and_receipt(
        store,
        details,
        item_id=summary["catalog_item_id"],
        payload={
            "id": 1,
            "type": "layer",
            "title": "Detailed title",
            "url": "https://data.linz.govt.nz/layer/1/",
            "data": {"kind": "vector"},
        },
        label="detail",
        record_type="linz_catalog_detail_capture",
    )
    _write_capture_and_receipt(
        store,
        services,
        item_id=summary["catalog_item_id"],
        payload=[{"key": "wfs"}],
        label="service",
        record_type="linz_catalog_service_capture",
    )
    result = write_enriched_catalog_snapshot(
        manifest_path,
        details,
        store,
        tmp_path / "output",
        service_receipts=services,
    )
    assert result.item_count == result.detail_count == result.service_count == 1
    record = json.loads(result.items_path.read_text(encoding="utf-8"))
    assert record["name"] == "Detailed title"
    assert record["kind"] == "vector"
    assert record["services"] == [{"key": "wfs"}]
    output_manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert output_manifest["detail_coverage"]["complete"] is True
    assert output_manifest["completeness"]["unfiltered_published_catalogue"] is True
    assert output_manifest["manifest_sha256"] == sha256_json(
        output_manifest, omit_keys={"manifest_sha256"}
    )


def test_write_enriched_snapshot_records_allowed_gaps(tmp_path: Path) -> None:
    layer = normalise_catalog_item(
        {
            "id": 1,
            "type": "layer",
            "url": "https://data.linz.govt.nz/layer/1/",
        }
    )
    document = normalise_catalog_item(
        {
            "id": 2,
            "type": "document",
            "url": "https://data.linz.govt.nz/document/2/",
        }
    )
    manifest_path = _write_catalog_snapshot(tmp_path, [document, layer])
    (tmp_path / "empty-details").mkdir()
    result = write_enriched_catalog_snapshot(
        manifest_path,
        tmp_path / "empty-details",
        tmp_path / "store",
        tmp_path / "output",
        require_complete_details=False,
        require_complete_services=False,
    )
    records = [
        json.loads(line) for line in result.items_path.read_text(encoding="utf-8").splitlines()
    ]
    assert [record["catalog_item_id"] for record in records] == [
        document["catalog_item_id"],
        layer["catalog_item_id"],
    ]
    assert records[0]["service_status"] == "not-applicable"
    assert records[1]["service_status"] == "missing"
    with pytest.raises(LinzCatalogError, match="detail coverage"):
        write_enriched_catalog_snapshot(
            manifest_path,
            tmp_path / "empty-details",
            tmp_path / "store",
            tmp_path / "strict-details",
            require_complete_services=False,
        )
    with pytest.raises(LinzCatalogError, match="service coverage"):
        write_enriched_catalog_snapshot(
            manifest_path,
            tmp_path / "empty-details",
            tmp_path / "store",
            tmp_path / "strict-services",
            require_complete_details=False,
        )


def test_receipt_and_capture_loaders_fail_closed(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{", encoding="utf-8")
    with pytest.raises(LinzCatalogError, match="cannot load"):
        _load_receipt(invalid, "detail")
    invalid.write_text("[]", encoding="utf-8")
    with pytest.raises(LinzCatalogError, match="root is not an object"):
        _load_receipt(invalid, "detail")
    invalid.write_text('{"receipt_sha256":"wrong"}', encoding="utf-8")
    with pytest.raises(LinzCatalogError, match="hash mismatch"):
        _load_receipt(invalid, "detail")

    good: dict[str, Any] = {
        "record_type": "wrong",
        "catalog_item_id": "urn:item:1",
        "receipt_sha256": "",
    }
    good["receipt_sha256"] = sha256_json(good, omit_keys={"receipt_sha256"})
    invalid.write_text(json.dumps(good), encoding="utf-8")
    with pytest.raises(LinzCatalogError, match="not a detail receipt"):
        _receipt_index(
            [invalid],
            record_type="linz_catalog_detail_capture",
            label="detail",
        )

    assert _receipt_paths(None) == []
    assert _receipt_paths(invalid) == [invalid]
    directory = tmp_path / "receipts"
    directory.mkdir()
    (directory / "b.json").write_text("{}", encoding="utf-8")
    (directory / "a.json").write_text("{}", encoding="utf-8")
    assert [path.name for path in _receipt_paths(directory)] == ["a.json", "b.json"]

    store = tmp_path / "store"
    with pytest.raises(LinzCatalogError, match="valid object digest"):
        _load_captured_json(
            {},
            store_root=store,
            expected_collection=False,
            label="detail",
        )
    with pytest.raises(LinzCatalogError, match="is missing"):
        _load_captured_json(
            {"object_sha256": "a" * 64},
            store_root=store,
            expected_collection=False,
            label="detail",
        )


@pytest.mark.parametrize(
    ("payload", "expected_collection", "semantic", "message"),
    [
        (b"\xff", False, None, "not JSON"),
        (b"[]", False, [], "not an object"),
        (b"{}", True, {}, "not an object array"),
        (b"[{}]", True, [{"different": True}], "semantic digest mismatch"),
    ],
)
def test_capture_loader_rejects_malformed_or_substituted_content(
    tmp_path: Path,
    payload: bytes,
    expected_collection: bool,
    semantic: Any,
    message: str,
) -> None:
    digest = sha256_bytes(payload)
    store = tmp_path / "store"
    object_path = store / "objects" / "sha256" / digest[:2] / digest
    object_path.parent.mkdir(parents=True)
    object_path.write_bytes(payload)
    digest_key = "service_sha256" if expected_collection else "detail_sha256"
    receipt = {
        "object_sha256": digest,
        digest_key: sha256_json(semantic),
    }
    with pytest.raises(LinzCatalogError, match=message):
        _load_captured_json(
            receipt,
            store_root=store,
            expected_collection=expected_collection,
            label="evidence",
        )


def test_receipt_index_rejects_missing_and_duplicate_identities(tmp_path: Path) -> None:
    paths: list[Path] = []
    for index, item_id in enumerate(("", "urn:item:1", "urn:item:1")):
        receipt: dict[str, Any] = {
            "record_type": "linz_catalog_detail_capture",
            "catalog_item_id": item_id,
            "receipt_sha256": "",
        }
        receipt["receipt_sha256"] = sha256_json(receipt, omit_keys={"receipt_sha256"})
        path = tmp_path / f"{index}.json"
        path.write_text(json.dumps(receipt), encoding="utf-8")
        paths.append(path)
    with pytest.raises(LinzCatalogError, match="no catalogue item identity"):
        _receipt_index(
            [paths[0]],
            record_type="linz_catalog_detail_capture",
            label="detail",
        )
    with pytest.raises(LinzCatalogError, match="duplicate detail receipt"):
        _receipt_index(
            paths[1:],
            record_type="linz_catalog_detail_capture",
            label="detail",
        )


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda manifest: manifest.update(record_type="other"), "not a LINZ"),
        (lambda manifest: manifest.update(manifest_sha256="bad"), "manifest hash"),
        (
            lambda manifest: manifest.update(
                items={"path": "items.jsonl", "sha256": "bad", "size_bytes": 1}
            ),
            "item hash",
        ),
    ],
)
def test_enriched_snapshot_rejects_invalid_source_manifest(
    tmp_path: Path,
    mutation: Any,
    message: str,
) -> None:
    summary = normalise_catalog_item({"id": 1, "type": "document"})
    source = _write_catalog_snapshot(tmp_path, [summary])
    manifest = json.loads(source.read_text(encoding="utf-8"))
    mutation(manifest)
    if message != "manifest hash":
        manifest["manifest_sha256"] = sha256_json(manifest, omit_keys={"manifest_sha256"})
    source.write_text(json.dumps(manifest), encoding="utf-8")
    receipts = tmp_path / "receipts"
    receipts.mkdir()
    with pytest.raises(LinzCatalogError, match=message):
        write_enriched_catalog_snapshot(
            source,
            receipts,
            tmp_path / "store",
            tmp_path / "output",
            require_complete_details=False,
            require_complete_services=False,
        )


def test_detail_kind_prefers_top_level_then_nested() -> None:
    assert _detail_kind({"kind": "raster", "data": {"kind": "vector"}}) == "raster"
    assert _detail_kind({"data": {"kind": "vector"}}) == "vector"
    assert _detail_kind({"data": []}) is None
