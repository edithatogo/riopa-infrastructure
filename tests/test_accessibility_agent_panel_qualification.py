import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_accessibility_agent_panel_is_bounded_and_promotion_disabled() -> None:
    packet = json.loads(
        (ROOT / "docs/accessibility-agent-panel-qualification-20260825.json").read_text()
    )
    assert packet["schema"] == "riopa.accessibility-agent-panel-qualification.v1"
    assert packet["status"] == "bounded-agent-panel-qualified-open-gates"
    assert len(packet["panel"]) == 4
    assert packet["decisions"]["reference_contracts"] is True
    assert packet["decisions"]["real_network_qualification"] is False
    assert packet["decisions"]["promotion_allowed"] is False
    assert any("external user" in gate for gate in packet["open_gates"])
