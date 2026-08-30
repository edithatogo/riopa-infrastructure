import json
import re
from pathlib import Path

from riopa_provenance.hashing import sha256_json


def test_derived_acceptance_binds_source_and_original_replay() -> None:
    root = Path(__file__).resolve().parents[1]
    evidence = json.loads((root / "docs/tasman-derived-acceptance-20260831.json").read_text())
    source = json.loads((root / "docs/tasman-publication-acceptance-20260830.json").read_text())[
        "publication_receipt"
    ]
    receipt = evidence["publication_receipt"]
    identity = receipt["identity"]
    assert evidence["track"] == "nz_spatial_archive_mvp_20260718"
    assert evidence["status"] == "hosted-derived-publication-and-replay-verified"
    assert receipt["status"] == "derivatives-published-and-verified"
    assert receipt["state"] == "verified"
    assert receipt["public_repository"] == source["public_dataset_repository"]
    assert identity["source_revision"] == source["public_revision"]
    assert identity["source_manifest_sha256"] == source["packet_manifest_sha256"]
    assert identity["geoparquet_sha256"] == source["reproduction"]["geoparquet_sha256"]
    assert identity["feature_count"] == source["reproduction"]["feature_count"]
    assert receipt["logical_sha256"] == sha256_json(identity)
    assert receipt["prefix"] == f"derivatives/tasman-zones/{receipt['logical_sha256']}"
    assert re.fullmatch(r"[0-9a-f]{40}", receipt["public_revision"])
    assert re.fullmatch(r"[0-9a-f]{64}", receipt["manifest_sha256"])
    assert receipt["licence"] == source["licence"] == "CC-BY-4.0"
    assert receipt["attribution"] == source["attribution"]
    assert set(receipt["files"]) == {"canonical.json", "features.parquet", "features.duckdb"}
    for item in receipt["files"].values():
        assert item["bytes"] > 0
        assert re.fullmatch(r"[0-9a-f]{64}", item["sha256"])
    assert evidence["hosted_execution"]["successful_attempts"] == [1, 2]
    assert evidence["hosted_execution"]["original_public_revision_reused"] is True
    assert re.fullmatch(r"[0-9a-f]{64}", evidence["hosted_execution"]["identical_receipts_sha256"])
    assert evidence["ci"]["coverage_gate_percent"] == 90
    assert evidence["ci"]["branch_aware_coverage_percent"] >= 90
    assert any("scheduled" in text for text in evidence["non_claims"])
    assert any("clean-room" in text for text in evidence["non_claims"])
