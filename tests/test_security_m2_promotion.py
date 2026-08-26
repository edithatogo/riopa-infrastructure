import json
from pathlib import Path

from riopa_provenance.roadmap import release_readiness

ROOT = Path(__file__).resolve().parents[1]
TRACK = ROOT / "conductor/tracks/security_supply_chain_20260719"
RECEIPT = ROOT / "docs/security-m2-promotion-20260826.json"


def test_security_m2_promotion_is_exact_tree_and_fail_closed() -> None:
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
        "track_id": "foundation_architecture_20260718",
        "required_maturity": "M2",
        "observed_maturity": "M2",
        "status": "satisfied",
    }
    assert set(receipt["m2_repository_owned"].values()) == {"passed"}
    assert receipt["validation"]["tests"]["count"] == 1153
    assert receipt["validation"]["tests"]["coverage_percent"] >= 90

    assert metadata["status"] == "validating"
    assert metadata["current_maturity"] == "M2"
    assert "foundation-dependency-not-complete" not in metadata["blocking_defects"]
    assert metadata["blocking_defect_maturity"] == receipt["remaining_blocking_gates"]
    assert receipt["evidence_id"] in metadata["evidence"]

    readiness = release_readiness(ROOT, "0.3.0")
    assert readiness.qualified_tracks >= 3
    assert not any(
        track_id in item
        for item in readiness.blockers
        for track_id in (
            "foundation_architecture_20260718",
            "governance_maori_data_sovereignty_20260718",
            "security_supply_chain_20260719",
        )
    )


def test_programme_registry_reports_security_validating_m2_only() -> None:
    tracks = (ROOT / "conductor/tracks.md").read_text(encoding="utf-8")
    security_line = next(
        line for line in tracks.splitlines() if "`security_supply_chain_20260719`" in line
    )
    assert "current `M2`" in security_line
    assert "target `M6`" in security_line
    assert "**Active:** 23" in tracks
    assert "**Validating:** 5" in tracks
