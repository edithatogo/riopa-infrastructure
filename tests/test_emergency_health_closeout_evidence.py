import hashlib
import json
from pathlib import Path

PACKET = Path("docs/emergency-health-closeout-evidence-20260825.json")
REMEDIATION = Path("docs/emergency-health-review-remediation-20260825.json")


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


def test_review_remediation_is_digest_bound_and_keeps_external_gates_open() -> None:
    packet = json.loads(REMEDIATION.read_text(encoding="utf-8"))
    assert packet["status"] == "repository-review-remediated-external-gates-open"
    assert packet["archive_eligible"] is False
    assert packet["promotion_allowed"] is False
    assert len(packet["review_lenses"]) == 4
    for relative_path, expected_digest in packet["artifact_sha256"].items():
        assert hashlib.sha256(Path(relative_path).read_bytes()).hexdigest() == expected_digest
    gates = " ".join(packet["remaining_blocking_gates"])
    for boundary in (
        "dependencies",
        "clinical",
        "external reproduction",
        "preservation",
        "elapsed",
        "release-authority",
    ):
        assert boundary in gates
