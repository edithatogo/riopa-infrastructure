import json
from pathlib import Path

from riopa_provenance.roadmap import release_readiness

ROOT = Path(__file__).resolve().parents[1]
TRACK = ROOT / "conductor/tracks/methods_research_objects_20260718"
RECEIPT = ROOT / "docs/methods-research-objects-m2-promotion-20260827.json"


def test_methods_research_objects_m2_promotion_is_exact_tree_and_fail_closed() -> None:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    metadata = json.loads((TRACK / "metadata.json").read_text(encoding="utf-8"))

    assert receipt["decision"] == "promote-to-m2"
    assert receipt["compatibility"]["classification"] == "metadata-only-backward-compatible"
    assert receipt["authority"]["signature_claimed"] is False
    assert len(receipt["source_revision"]["tree_sha"]) == 40
    assert receipt["dependency_boundary"] == {
        "required_maturity": "M2",
        "tracks": {
            "provenance_profile_v1_20260718": "M2",
            "security_supply_chain_20260719": "M2",
        },
        "status": "satisfied",
    }
    assert set(receipt["m2_repository_owned"].values()) == {"passed"}

    assert metadata["status"] == "validating"
    assert metadata["current_maturity"] == "M2"
    expected_gates = dict(receipt["remaining_blocking_gates"])
    expected_gates["repeated-supported-environment-use-and-preservation-operation"] = (
        expected_gates.pop("repeated-external-use-and-preservation-operation")
    )
    expected_gates["isolated-role-separated-clean-room-agent-reproduction"] = expected_gates.pop(
        "independent-external-reproduction"
    )
    assert metadata["blocking_defect_maturity"] == expected_gates
    assert receipt["evidence_id"] in metadata["evidence"]

    readiness = release_readiness(ROOT, "0.4.0")
    assert readiness.qualified_tracks >= 1
    assert readiness.required_tracks == 3
    assert not any(
        "track methods_research_objects_20260718" in blocker for blocker in readiness.blockers
    )
    assert readiness.passed_gates == 0


def test_programme_registry_reports_methods_research_objects_m2_only() -> None:
    tracks = (ROOT / "conductor/tracks.md").read_text(encoding="utf-8")
    methods_line = next(
        line for line in tracks.splitlines() if "`methods_research_objects_20260718`" in line
    )
    assert "current `M2`" in methods_line
    assert "target `M6`" in methods_line
