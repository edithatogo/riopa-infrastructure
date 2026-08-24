import json
from pathlib import Path


def test_claim_classification_contract_is_complete_and_fail_closed() -> None:
    root = Path(__file__).resolve().parents[1]
    record = json.loads(
        (root / "docs/publication-claim-classification-contract-20260825.json").read_text()
    )
    assert record["status"] == "bounded-repository-contract"
    assert {item["id"] for item in record["claim_classes"]} == {
        "reference-only",
        "exploratory",
        "confirmatory",
        "prohibited",
    }
    assert {
        "claim_id",
        "statement",
        "classification",
        "evidence_refs",
        "scope",
        "limitations",
        "non_claims",
    } <= set(record["claim_record_requirements"])
    assert len(record["fail_closed_rules"]) >= 4
    assert set(record["disabled_claims"]) >= {
        "network",
        "timetable",
        "facility",
        "national",
        "clinical",
        "dispatch",
        "authoritative",
    }


def test_publication_plan_records_claim_classification_without_promotion() -> None:
    plan = (
        Path(__file__).resolve().parents[1]
        / "conductor/tracks/publication_validation_20260718/plan.md"
    ).read_text()
    assert "[x] 1.2 Define claim-to-evidence" in plan
    assert "publication, participant and authority gates remain open" in plan
