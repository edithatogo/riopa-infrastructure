import json
import re
from pathlib import Path


def test_hosted_acceptance_binds_preparation_and_preserves_scope() -> None:
    root = Path(__file__).resolve().parents[1]
    evidence = json.loads((root / "docs/tasman-publication-acceptance-20260830.json").read_text())
    preparation = json.loads((root / "docs/tasman-hosted-preparation-20260830.json").read_text())
    receipt = evidence["publication_receipt"]
    assert evidence["status"] == "hosted-publication-and-rebuild-verified"
    assert evidence["track"] == preparation["track"]
    assert receipt["private_revision"] == preparation["private_revision"]
    assert receipt["private_manifest_sha256"] == preparation["private_manifest_sha256"]
    assert receipt["packet_manifest_sha256"] == preparation["candidate"]["manifest_sha256"]
    assert receipt["capture_set_id"] == preparation["candidate"]["capture_set_id"]
    for field in ("file_count", "file_bytes", "licence", "attribution"):
        assert receipt[field] == preparation["candidate"][field]
    assert receipt["reproduction"]["feature_count"] == preparation["candidate"]["feature_count"]
    assert receipt["reproduction"]["builds"] == 2
    assert receipt["anonymous_full_packet_verified"] is True
    assert receipt["state"] == "verified"
    assert re.fullmatch(r"[0-9a-f]{40}", receipt["public_revision"])
    assert receipt["prefix"] == f"snapshots/tasman-zones/{receipt['packet_manifest_sha256']}"
    for field in ("canonical_sha256", "geoparquet_sha256", "duckdb_semantic_sha256"):
        assert re.fullmatch(r"[0-9a-f]{64}", receipt["reproduction"][field])
    assert evidence["ci"]["branch_aware_coverage_percent"] >= 90
    assert evidence["ci"]["coverage_gate_percent"] == 90
    assert evidence["hosted_execution"]["successful_attempts"] == [1, 2]
    assert evidence["hosted_execution"]["original_public_revision_reused"] is True
    assert re.fullmatch(r"[0-9a-f]{64}", evidence["hosted_execution"]["identical_receipts_sha256"])
    assert any("scheduled" in text for text in evidence["non_claims"])
    assert any("clean-room" in text for text in evidence["non_claims"])
    assert any("Only the licensed source packet" in text for text in evidence["non_claims"])
