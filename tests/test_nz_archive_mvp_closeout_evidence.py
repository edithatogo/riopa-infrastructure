import json
from pathlib import Path

PACKET = Path("docs/nz-archive-mvp-closeout-evidence-20260829.json")


def test_nz_archive_mvp_closeout_links_required_evidence_categories() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    assert packet["status"] == "repository-owned-closeout-slice"
    assert packet["promotion_allowed"] is False
    assert set(packet["evidence_categories"]) == {
        "implementation",
        "tests",
        "agent_panel",
        "migration",
        "release_candidate",
    }
    assert all(packet["evidence_categories"].values())


def test_nz_archive_mvp_closeout_preserves_scope_and_external_gates() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    text = " ".join(packet["non_claims"])
    assert "not a complete national spatial archive or production release" in text
    assert "cannot substitute" in text
    assert "authoritative claims remain disabled" in text
    assert packet["open_gates"]
