import json
from pathlib import Path

PACKET = Path("docs/provenance-profile-panel-qualification-20260825.json")


def test_provenance_panel_packet_is_bounded_and_fail_closed() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    assert packet["status"] == "bounded-agent-panel-not-qualified"
    assert packet["promotion_allowed"] is False
    assert len(packet["lenses"]) == 4
    assert any("semantic-loss" in gate for gate in packet["open_gates"])
    assert any("signed v1 attestation" in gate for gate in packet["open_gates"])


def test_provenance_panel_does_not_substitute_for_release_evidence() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    text = " ".join(packet["non_claims"])
    assert "not standards certification" in text
    assert "cannot create" in text
