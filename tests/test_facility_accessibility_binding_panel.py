import json
from pathlib import Path


def test_facility_accessibility_binding_panel_keeps_promotion_disabled() -> None:
    root = Path(__file__).parents[1]
    packet = json.loads(
        (root / "docs/facility-accessibility-binding-panel-review-20260825.json").read_text()
    )
    assert packet["status"] == "bounded-agent-panel-qualified-open-gates"
    assert len(packet["panel"]) == 4
    assert packet["decisions"]["binding_contract_qualified"] is True
    assert packet["decisions"]["promotion_allowed"] is False
    assert packet["open_gates"]
