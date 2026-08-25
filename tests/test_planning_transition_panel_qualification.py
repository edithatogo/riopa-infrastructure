import json
from pathlib import Path

PACKET = Path("docs/planning-transition-panel-qualification-20260825.json")


def test_planning_transition_panel_packet_is_bounded_and_fail_closed() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    assert packet["status"] == "bounded-agent-panel-not-qualified"
    assert packet["promotion_allowed"] is False
    assert len(packet["lenses"]) == 4
    assert any("public-source" in gate for gate in packet["open_gates"])
    assert any("preservation" in gate for gate in packet["open_gates"])


def test_planning_transition_panel_does_not_create_authority_or_real_data() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    text = " ".join(packet["non_claims"])
    assert "not legal review" in text
    assert "cannot create public-source evidence" in text
    assert "authoritative claims remain disabled" in text
