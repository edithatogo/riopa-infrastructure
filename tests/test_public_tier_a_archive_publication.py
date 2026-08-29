import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_public_tier_a_archive_receipt_is_revision_and_rights_bound() -> None:
    receipt = json.loads(
        (ROOT / "docs/public-tier-a-archive-publication-20260829.json").read_text()
    )

    repository = receipt["repository"]
    assert repository["visibility"] == "public"
    assert len(repository["revision"]) == 40
    assert receipt["review"]["status"] == "merged"
    assert len(receipt["packets"]) == 3
    assert sum(packet["feature_count"] for packet in receipt["packets"]) == 230
    assert {packet["licence"] for packet in receipt["packets"]} == {
        "CC-BY-3.0-NZ",
        "CC-BY-4.0",
    }
    assert all(len(packet["manifest_sha256"]) == 64 for packet in receipt["packets"])


def test_public_tier_a_archive_receipt_preserves_bounded_non_claims() -> None:
    receipt = json.loads(
        (ROOT / "docs/public-tier-a-archive-publication-20260829.json").read_text()
    )
    non_claims = " ".join(receipt["non_claims"])

    assert "national completeness" in non_claims
    assert "mixed-source" in non_claims
    assert "bounded regional reference" in non_claims
    assert all(value == "passed" for value in receipt["validation"].values())
