import json
from pathlib import Path

PACKET = Path("docs/canonical-closeout-evidence-20260825.json")


def test_canonical_closeout_packet_links_all_repository_evidence_categories() -> None:
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


def test_canonical_closeout_preserves_release_gates() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    text = " ".join(packet["non_claims"])
    assert "unsigned unpublished candidate" in text
    assert "cannot substitute" in text
    assert "authoritative" in text
