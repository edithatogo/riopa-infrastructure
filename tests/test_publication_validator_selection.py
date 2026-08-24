import json
from pathlib import Path


def test_validator_selection_contract_is_agent_panel_and_fail_closed() -> None:
    root = Path(__file__).resolve().parents[1]
    record = json.loads(
        (root / "docs/publication-validator-selection-contract-20260825.json").read_text()
    )
    assert record["status"] == "bounded-repository-contract"
    assert "single-developer" in record["operating_model"]
    assert len(record["required_lenses"]) == 4
    assert {environment["id"] for environment in record["execution_environments"]} == {
        "local-reproducible",
        "hosted-ci",
        "archive-restore",
    }
    assert len(record["independence_criteria"]) >= 5
    assert any("factual external operator" in claim for claim in record["independence_criteria"])


def test_publication_plan_records_validator_selection_without_authority_claim() -> None:
    root = Path(__file__).resolve().parents[1]
    plan = (root / "conductor/tracks/publication_validation_20260718/plan.md").read_text()
    assert "[x] 1.3 Select agent-panel validators" in plan
    assert "factual participant and authority gates remain open" in plan
