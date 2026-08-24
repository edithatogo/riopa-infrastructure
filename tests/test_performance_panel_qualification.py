import json
from pathlib import Path

PACKET = Path("docs/performance-panel-qualification-20260825.json")


def test_performance_panel_packet_is_bounded_and_fail_closed() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    assert packet["status"] == "bounded-agent-panel-not-qualified"
    assert packet["promotion_allowed"] is False
    assert len(packet["lenses"]) == 4
    assert any("national-scale" in gate for gate in packet["open_gates"])
    assert any("second execution environment" in gate for gate in packet["open_gates"])


def test_performance_panel_does_not_substitute_for_external_evidence() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    text = " ".join(packet["non_claims"])
    assert "not a national-scale measurement" in text
    assert "cannot close hosted" in text
