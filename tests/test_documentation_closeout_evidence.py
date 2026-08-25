import json
from pathlib import Path

PACKET = Path("docs/documentation-closeout-evidence-20260825.json")


def test_documentation_closeout_packet_links_required_evidence_categories() -> None:
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


def test_documentation_closeout_preserves_external_and_release_gates() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    text = " ".join(packet["non_claims"])
    assert "not RC or stable release evidence" in text
    assert "cannot substitute" in text
    assert "authoritative claims" in text
