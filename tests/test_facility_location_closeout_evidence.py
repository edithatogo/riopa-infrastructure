import json
from pathlib import Path

PACKET = Path("docs/facility-location-closeout-evidence-20260825.json")


def test_facility_location_closeout_links_required_evidence_categories() -> None:
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


def test_facility_location_closeout_preserves_scale_and_authority_gates() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    text = " ".join(packet["non_claims"])
    assert "not a release" in text
    assert "cannot substitute" in text
    assert "authoritative claims remain disabled" in text
