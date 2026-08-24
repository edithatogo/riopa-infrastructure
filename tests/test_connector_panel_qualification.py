import json
from pathlib import Path

PACKET = Path("docs/connector-panel-qualification-20260825.json")


def test_connector_panel_packet_is_bounded_and_fail_closed() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    assert packet["status"] == "bounded-agent-panel-not-qualified"
    assert packet["promotion_allowed"] is False
    assert len(packet["lenses"]) == 4
    assert any("source capture" in gate for gate in packet["open_gates"])
    assert any("preservation" in gate for gate in packet["open_gates"])


def test_connector_panel_does_not_create_source_authority() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    text = " ".join(packet["non_claims"])
    assert "not live-source capture" in text
    assert "cannot create source authority" in text
