import json
from pathlib import Path


def test_documentation_support_contract_is_bounded() -> None:
    root = Path(__file__).resolve().parents[1]
    record = json.loads((root / "docs/documentation-support-readiness-20260825.json").read_text())
    assert record["status"] == "preview-support-contract"
    assert record["repository_model"] == "single-developer"
    assert {item["priority"] for item in record["triage"]} == {"P0", "P1", "P2"}
    assert record["ownership"]["agent_panels"].startswith("advisory")
    assert record["promotion_allowed"] is False
    assert any("external" in gate for gate in record["open_gates"])
