import json
from pathlib import Path

PACKET = Path("docs/emergency-health-closeout-evidence-20260825.json")


def test_emergency_health_closeout_links_required_evidence_categories() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    assert packet["status"] == "repository-owned-closeout-slice"
    assert packet["promotion_allowed"] is False
    assert set(packet["evidence_categories"]) == {
        "implementation",
        "tests",
        "review",
        "migration",
        "release_candidate",
    }
    assert all(packet["evidence_categories"].values())


def test_emergency_health_closeout_preserves_safety_and_authority_gates() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    text = " ".join(packet["non_claims"])
    assert "not clinical" in text
    assert "cannot substitute" in text
    assert "authoritative claims" in text
