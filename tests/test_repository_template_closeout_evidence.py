import json
from pathlib import Path

PACKET = Path("docs/repository-template-closeout-evidence-20260825.json")


def test_repository_template_closeout_links_required_evidence_categories() -> None:
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


def test_repository_template_closeout_preserves_adoption_and_authority_gates() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    text = " ".join(packet["non_claims"])
    assert "not adoption or release evidence" in text
    assert "cannot substitute" in text
    assert "stable-v1" in text
