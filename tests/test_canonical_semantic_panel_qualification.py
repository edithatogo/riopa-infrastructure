import json
from pathlib import Path

PACKET = Path("docs/canonical-semantic-panel-qualification-20260825.json")


def test_canonical_semantic_panel_packet_is_bounded_and_fail_closed() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    assert packet["status"] == "bounded-agent-panel-not-qualified"
    assert packet["promotion_allowed"] is False
    assert len(packet["lenses"]) == 4
    assert any("SHACL" in gate for gate in packet["open_gates"])
    assert any("publication identifier" in gate for gate in packet["open_gates"])


def test_canonical_panel_does_not_create_external_semantic_evidence() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    text = " ".join(packet["non_claims"])
    assert "not SHACL conformance" in text
    assert "cannot create" in text
