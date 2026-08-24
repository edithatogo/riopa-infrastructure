import json
from pathlib import Path

PACKET = Path("docs/documentation-inventory-and-safety-review-20260825.json")


def test_documentation_inventory_is_bounded_and_fail_closed() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    assert packet["status"] == "bounded-agent-panel-not-qualified"
    assert packet["promotion_allowed"] is False
    assert len(packet["audiences"]) == 5
    assert any("disabled" in finding for finding in packet["safety_findings"])
    assert any("external operator" in gate for gate in packet["open_gates"])


def test_documentation_review_does_not_create_participant_evidence() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    text = " ".join(packet["non_claims"])
    assert "not factual external-user evidence" in text
    assert "cannot substitute" in text
