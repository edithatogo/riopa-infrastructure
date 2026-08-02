from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

import pyarrow.parquet as pq
import pytest
from jsonschema import Draft202012Validator, FormatChecker

from riopa_provenance.archived_spatial import (
    ArchivedPacketDescriptor,
    ArchivedPacketError,
    build_archived_arcgis_projection,
    download_archived_packet,
    immutable_hugging_face_url,
)
from riopa_provenance.hashing import sha256_json

ROOT = Path(__file__).resolve().parents[1]


def _json_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def _fixture() -> tuple[ArchivedPacketDescriptor, dict[str, bytes]]:
    item = {
        "id": "item",
        "title": "Meshblock 2026",
        "access": "public",
        "modified": 1,
        "licenseInfo": "CC BY 4.0",
        "accessInformation": "Stats NZ – Tatauranga Aotearoa",
    }
    layer = {
        "serviceItemId": "item",
        "objectIdField": "OBJECTID",
        "extent": {"spatialReference": {"wkid": 2193}},
    }
    inventory = {"objectIdFieldName": "OBJECTID", "objectIds": [1, 2]}
    page = {
        "spatialReference": {"wkid": 2193},
        "features": [
            {
                "attributes": {"OBJECTID": 1, "MB2026_V1_00": "001"},
                "geometry": {
                    "rings": [[[0, 0], [3, 3], [0, 4], [4, 0], [0, 0]]]
                },
            },
            {
                "attributes": {"OBJECTID": 2, "MB2026_V1_00": "002"},
                "geometry": None,
            },
        ],
    }
    raw = {
        "raw/item.json.gz": _json_bytes(item),
        "raw/layer.json.gz": _json_bytes(layer),
        "raw/object-ids.json.gz": _json_bytes(inventory),
        "raw/object-ids-post.json.gz": _json_bytes(inventory),
        "raw/features/page-00001.json.gz": _json_bytes(page),
    }
    files = []
    compressed: dict[str, bytes] = {}
    receipts = []
    for index, (path, body) in enumerate(raw.items()):
        zipped = gzip.compress(body, mtime=0)
        compressed[path] = zipped
        files.append(
            {
                "path": path,
                "media_type": "application/json",
                "content_encoding": "gzip",
                "bytes": len(zipped),
                "sha256": hashlib.sha256(zipped).hexdigest(),
                "uncompressed_bytes": len(body),
                "uncompressed_sha256": hashlib.sha256(body).hexdigest(),
            }
        )
        receipts.append(
            {
                "artifact": path,
                "url": f"https://services2.arcgis.com/archive/{index}",
                "method": "GET",
                "status": 200,
                "retrieved_at": "2026-08-02T00:00:00Z",
                "headers": {"content-type": "application/json"},
            }
        )
    payload_set_sha256 = sha256_json(
        [{"path": item["path"], "sha256": item["sha256"]} for item in files]
    )
    manifest = {
        "schema": "open-social-data.arcgis-archive.v1",
        "capture_id": "20260802T000000Z",
        "started_at": "2026-08-02T00:00:00Z",
        "completed_at": "2026-08-02T00:01:00Z",
        "source": {
            "authority": "Stats NZ Tatauranga Aotearoa",
            "dataset": "Meshblock 2026",
            "edition": "boundaries as at 1 January 2026",
            "arcgis_item_id": "item",
            "arcgis_item_modified": 1,
            "service_url": "https://services2.arcgis.com/live/FeatureServer/0",
            "service_item_id": "item",
            "license": "CC BY 4.0",
            "license_url": "https://creativecommons.org/licenses/by/4.0/",
        },
        "scope": {
            "mode": "full",
            "available_features": 2,
            "captured_features": 2,
            "null_geometries": 1,
            "oid_field": "OBJECTID",
            "pages": 1,
        },
        "integrity": {
            "payload_set_sha256": payload_set_sha256,
            "object_ids_sha256": hashlib.sha256(_json_bytes([1, 2])).hexdigest(),
            "source_stable_during_capture": True,
            "files": files,
        },
        "retrieval_receipts": receipts,
        "execution": {"repository": "owner/archive", "revision": "b" * 40},
        "non_claims": ["not population data"],
    }
    manifest_bytes = json.dumps(manifest, indent=2, sort_keys=True).encode() + b"\n"
    checksums = "\n".join(
        [*(f"{item['sha256']}  {item['path']}" for item in files),
         f"{hashlib.sha256(manifest_bytes).hexdigest()}  manifest.json"]
    ).encode() + b"\n"
    receipt = {
        "schema": "open-social-data.hugging-face-receipt.v1",
        "dataset": "owner/archive",
        "packet_revision": "c" * 40,
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "credentials_recorded": False,
    }
    receipt_bytes = json.dumps(receipt, sort_keys=True).encode()
    descriptor = ArchivedPacketDescriptor(
        source_id="urn:riopa:source:stats-nz:meshblock-2026",
        dataset_repository="owner/archive",
        packet_revision="c" * 40,
        receipt_revision="d" * 40,
        manifest_path="snapshots/stats-nz-meshblock-2026/capture/manifest.json",
        manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
        checksums_sha256=hashlib.sha256(checksums).hexdigest(),
        receipt_path="receipts/github/run.json",
        receipt_sha256=hashlib.sha256(receipt_bytes).hexdigest(),
        expected_features=2,
        expected_pages=1,
        expected_null_geometries=1,
    )
    base = descriptor.manifest_path.rsplit("/", 1)[0]
    payloads = {
        immutable_hugging_face_url(descriptor, descriptor.manifest_path): manifest_bytes,
        immutable_hugging_face_url(descriptor, f"{base}/checksums.sha256"): checksums,
        immutable_hugging_face_url(
            descriptor, descriptor.receipt_path, revision=descriptor.receipt_revision
        ): receipt_bytes,
    }
    payloads.update(
        {
            immutable_hugging_face_url(descriptor, f"{base}/{path}"): body
            for path, body in compressed.items()
        }
    )
    return descriptor, payloads


def test_descriptor_rejects_mutable_or_unsafe_archive_identity() -> None:
    descriptor, _ = _fixture()
    descriptor.validate()
    with pytest.raises(ArchivedPacketError, match="40-character"):
        ArchivedPacketDescriptor(**{**descriptor.__dict__, "packet_revision": "main"}).validate()
    with pytest.raises(ArchivedPacketError, match="unsafe"):
        ArchivedPacketDescriptor(
            **{**descriptor.__dict__, "manifest_path": "../manifest.json"}
        ).validate()


def test_download_uses_only_immutable_hugging_face_objects(tmp_path: Path) -> None:
    descriptor, payloads = _fixture()
    requested: list[str] = []

    def fetch(url: str) -> bytes:
        requested.append(url)
        return payloads[url]

    packet = download_archived_packet(descriptor, tmp_path / "packet", fetch=fetch)
    assert packet.manifest["scope"]["captured_features"] == 2
    assert requested
    assert all("huggingface.co/datasets/owner/archive/resolve/" in url for url in requested)
    assert all("services2.arcgis.com" not in url for url in requested)
    assert (tmp_path / "packet" / "receipt.json").is_file()


def test_download_fails_closed_on_archived_digest_drift(tmp_path: Path) -> None:
    descriptor, payloads = _fixture()
    page_url = next(url for url in payloads if url.endswith("page-00001.json.gz"))
    payloads[page_url] += b"tampered"
    with pytest.raises(ArchivedPacketError, match="digest mismatch"):
        download_archived_packet(
            descriptor, tmp_path / "packet", fetch=lambda url: payloads[url]
        )


def test_builds_content_addressed_records_and_repair_free_projection(tmp_path: Path) -> None:
    descriptor, payloads = _fixture()
    packet_root = tmp_path / "packet"
    download_archived_packet(descriptor, packet_root, fetch=lambda url: payloads[url])
    result = build_archived_arcgis_projection(
        descriptor,
        packet_root=packet_root,
        records_dir=tmp_path / "records",
        output_dir=tmp_path / "bulk",
        base_name="meshblocks",
    )

    assert result.feature_count == 2
    assert result.capture_record_count == 5
    assert result.projection_record["archive_only"] is True
    assert result.projection_record["live_endpoint_contacted"] is False
    assert result.projection_record["manifest_sha256"] == descriptor.manifest_sha256

    source_envelope = json.loads(result.source_record_path.read_text())
    assert source_envelope["record_id"].endswith(source_envelope["record_sha256"])
    assert source_envelope["record_sha256"] == sha256_json(source_envelope["record"])
    source_schema = json.loads((ROOT / "schemas/source-record.schema.json").read_text())
    Draft202012Validator(source_schema, format_checker=FormatChecker()).validate(
        source_envelope["record"]
    )

    captures = [json.loads(line) for line in result.capture_records_path.read_text().splitlines()]
    assert all(item["capture_id"].endswith(item["record_sha256"]) for item in captures)
    assert all(item["record_sha256"] == sha256_json(item["record"]) for item in captures)

    table = pq.read_table(result.materialization.geoparquet_path)
    assert table.num_rows == 2
    assert "_riopa_source_geometry_sha256" in table.column_names
    page_capture = next(
        item["capture_id"]
        for item in captures
        if item["record"]["artifact"]["path"].endswith("page-00001.json.gz")
    )
    assert {tuple(json.loads(value.as_py())) for value in table["_riopa_capture_ids"]} == {
        (page_capture,)
    }
    quality = json.loads(result.materialization.quality_report_path.read_text())
    assert quality["null_geometry_count"] == 1
    assert quality["invalid_geometry_count_before_repair"] == 1
    assert quality["repaired_geometry_count"] == 0
    assert quality["geometry_repair_enabled"] is False


def test_projection_rejects_incomplete_inventory(tmp_path: Path) -> None:
    descriptor, payloads = _fixture()
    packet_root = tmp_path / "packet"
    download_archived_packet(descriptor, packet_root, fetch=lambda url: payloads[url])
    page = packet_root / "raw/features/page-00001.json.gz"
    value = json.loads(gzip.decompress(page.read_bytes()))
    value["features"].pop()
    page.write_bytes(gzip.compress(_json_bytes(value), mtime=0))
    with pytest.raises(ArchivedPacketError, match="digest mismatch"):
        build_archived_arcgis_projection(
            descriptor,
            packet_root=packet_root,
            records_dir=tmp_path / "records",
            output_dir=tmp_path / "bulk",
        )
