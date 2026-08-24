import json
from pathlib import Path

PACKET = Path("docs/operations-panel-qualification-20260825.json")


def test_operations_panel_packet_is_bounded_and_fail_closed() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    assert packet["status"] == "bounded-agent-panel-not-qualified"
    assert packet["promotion_allowed"] is False
    assert len(packet["lenses"]) == 4
    assert any("disaster-recovery" in gate for gate in packet["open_gates"])
    assert any("90-day" in gate for gate in packet["open_gates"])


def test_operations_panel_does_not_create_elapsed_or_provider_evidence() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    text = " ".join(packet["non_claims"])
    assert "not a production disaster-recovery result" in text
    assert "cannot substitute" in text
