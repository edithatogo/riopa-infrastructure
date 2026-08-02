from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from riopa_provenance.hashing import sha256_file, sha256_json

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence/stats-nz-meshblock-2026-projection"


def test_meshblock_projection_records_are_content_addressed_and_complete() -> None:
    manifest = json.loads((EVIDENCE / "records-manifest.json").read_text())
    assert manifest["manifest_sha256"] == sha256_json(manifest, omit_keys={"manifest_sha256"})
    for path_field, digest_field in (
        ("source_record", "source_record_sha256"),
        ("capture_records", "capture_records_sha256"),
        ("projection_record", "projection_record_sha256"),
        ("materialization_receipt", "materialization_receipt_sha256"),
    ):
        path = EVIDENCE / manifest[path_field]
        assert path.is_file()
        assert sha256_file(path) == manifest[digest_field]

    source = json.loads((EVIDENCE / manifest["source_record"]).read_text())
    assert source["record_id"].endswith(source["record_sha256"])
    assert source["record_sha256"] == sha256_json(source["record"])
    schema = json.loads((ROOT / "schemas/source-record.schema.json").read_text())
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(source["record"])

    captures = [
        json.loads(line)
        for line in (EVIDENCE / manifest["capture_records"]).read_text().splitlines()
    ]
    assert len(captures) == 236
    assert all(value["capture_id"].endswith(value["record_sha256"]) for value in captures)
    assert all(value["record_sha256"] == sha256_json(value["record"]) for value in captures)
    for value in captures:
        digest = value["record_sha256"]
        addressed = EVIDENCE / f"capture-records/sha256/{digest[:2]}/{digest}.json"
        assert json.loads(addressed.read_text()) == value

    projection = json.loads((EVIDENCE / manifest["projection_record"]).read_text())
    assert projection["projection_id"] == manifest["projection_id"]
    assert projection["record_sha256"] == sha256_json(projection["record"])
    record = projection["record"]
    assert record["feature_count"] == 57575
    assert len(record["capture_record_ids"]) == 236
    assert record["archive_only"] is True
    assert record["live_endpoint_contacted"] is False
    assert "never repair implicitly" in record["geometry_policy"]

    receipt = json.loads((EVIDENCE / manifest["materialization_receipt"]).read_text())
    assert receipt["projection_id"] == projection["projection_id"]
    assert receipt["receipt_sha256"] == sha256_json(receipt, omit_keys={"receipt_sha256"})
