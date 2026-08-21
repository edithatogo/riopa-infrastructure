import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_operations_runbook_catalog_is_complete_and_paths_exist() -> None:
    catalog = json.loads((ROOT / "docs/operations-runbook-catalog-20260822.json").read_text())
    required = {
        "source-health",
        "schema-drift",
        "rights-review",
        "corruption-recovery",
        "capacity-and-cost",
    }
    assert {item["id"] for item in catalog["runbooks"]} == required
    for item in catalog["runbooks"]:
        path = ROOT / item["path"]
        assert path.is_file()
        text = path.read_text()
        assert "Stop conditions" in text
        assert "Trigger" in text


def test_operations_runbooks_are_not_execution_receipts() -> None:
    catalog = json.loads((ROOT / "docs/operations-runbook-catalog-20260822.json").read_text())
    assert any("not evidence" in claim for claim in catalog["non_claims"])
