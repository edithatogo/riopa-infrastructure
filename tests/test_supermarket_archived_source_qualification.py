import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_archived_supermarket_source_is_revision_and_digest_bound() -> None:
    record = json.loads(
        (ROOT / "docs/supermarket-archived-source-qualification-20260829.json").read_text()
    )
    source = record["source"]
    validation = record["archive_validation"]
    assert len(source["archive_revision"]) == 40
    assert len(source["payload_sha256"]) == 64
    assert validation["status"] == "captured-and-content-addressed"
    assert validation["feature_count"] == 3245
    assert validation["premise_type_matching_supermarket_case_insensitive"] == 241
    assert validation["matching_status_counts"]["Active"] == 108
    assert record["qualification"]["promotion_allowed"] is False


def test_archived_supermarket_source_preserves_scope_non_claims() -> None:
    record = json.loads(
        (ROOT / "docs/supermarket-archived-source-qualification-20260829.json").read_text()
    )
    non_claims = " ".join(record["non_claims"])
    assert "national completeness" in non_claims
    assert "live endpoint" in non_claims
    assert "currently operating supermarket" in non_claims
