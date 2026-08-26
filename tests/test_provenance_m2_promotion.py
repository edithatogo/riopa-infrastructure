import json
from pathlib import Path

from riopa_provenance.roadmap import release_readiness

ROOT = Path(__file__).resolve().parents[1]
TRACK = ROOT / "conductor/tracks/provenance_profile_v1_20260718"
RECEIPT = ROOT / "docs/provenance-m2-promotion-20260827.json"


def test_provenance_m2_promotion_is_exact_tree_and_fail_closed() -> None:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    metadata = json.loads((TRACK / "metadata.json").read_text(encoding="utf-8"))

    assert receipt["decision"] == "promote-to-m2"
    assert receipt["compatibility"]["classification"] == "metadata-only-backward-compatible"
    assert receipt["authority"] == {
        "kind": "repository-owner-instruction",
        "instruction": "Proceed with the next recommended repository-owned step.",
        "signature_claimed": False,
    }
    assert len(receipt["source_revision"]["tree_sha"]) == 40
    assert receipt["dependency_boundary"] == {
        "required_maturity": "M2",
        "tracks": {
            "foundation_architecture_20260718": "M2",
            "security_supply_chain_20260719": "M2",
        },
        "status": "satisfied",
    }
    assert set(receipt["m2_repository_owned"].values()) == {"passed"}
    assert receipt["validation"]["tests"]["count"] == 1157
    assert receipt["validation"]["tests"]["coverage_percent"] >= 90

    assert metadata["status"] == "validating"
    assert metadata["current_maturity"] == "M2"
    assert metadata["blocking_defect_maturity"] == receipt["remaining_blocking_gates"]
    assert receipt["evidence_id"] in metadata["evidence"]

    readiness = release_readiness(ROOT, "0.3.0")
    assert readiness.qualified_tracks == readiness.required_tracks == 5
    assert not any(
        "track provenance_profile_v1_20260718" in blocker for blocker in readiness.blockers
    )
    assert readiness.passed_gates == readiness.required_gates == 4
    assert readiness.blockers == ()


def test_programme_registry_reports_provenance_m2_only() -> None:
    tracks = (ROOT / "conductor/tracks.md").read_text(encoding="utf-8")
    provenance_line = next(
        line for line in tracks.splitlines() if "`provenance_profile_v1_20260718`" in line
    )
    assert "current `M2`" in provenance_line
    assert "target `M6`" in provenance_line
