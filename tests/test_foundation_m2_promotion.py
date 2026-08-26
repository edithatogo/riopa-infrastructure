import json
from pathlib import Path

from riopa_provenance.roadmap import release_readiness

ROOT = Path(__file__).resolve().parents[1]
TRACK = ROOT / "conductor/tracks/foundation_architecture_20260718"
RECEIPT = ROOT / "docs/foundation-m2-promotion-20260826.json"


def test_foundation_m2_promotion_is_exact_tree_and_fail_closed() -> None:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    metadata = json.loads((TRACK / "metadata.json").read_text(encoding="utf-8"))

    assert receipt["decision"] == "promote-to-m2"
    assert receipt["compatibility"]["classification"] == "backward-compatible-additive"
    assert receipt["authority"]["kind"] == "repository-owner-instruction"
    assert receipt["authority"]["signature_claimed"] is False
    assert len(receipt["source_revision"]["tree_sha"]) == 40
    assert set(receipt["m2_repository_owned"].values()) == {"passed", "recorded"}
    assert receipt["validation"]["tests"]["count"] == 1149
    assert receipt["validation"]["tests"]["coverage_percent"] >= 90
    assert receipt["validation"]["hosted_required_checks"] == {
        "status": "passed",
        "count": 5,
        "actions_run": "https://github.com/edithatogo/riopa-infrastructure/actions/runs/32949281831",
        "codeql_run": "https://github.com/edithatogo/riopa-infrastructure/actions/runs/32949281893",
    }

    assert metadata["status"] == "validating"
    assert metadata["current_maturity"] == "M2"
    assert "m2-executable-proof-and-negative-tests" not in metadata["blocking_defects"]
    assert metadata["blocking_defects"] == receipt["remaining_blocking_gates"]
    assert metadata["blocking_defect_maturity"] == {
        gate: f"M{index}" for index, gate in enumerate(metadata["blocking_defects"], start=3)
    }
    assert receipt["evidence_id"] in metadata["evidence"]

    readiness = release_readiness(ROOT, "0.3.0")
    assert readiness.qualified_tracks >= 1
    assert not any("foundation_architecture_20260718" in item for item in readiness.blockers)


def test_programme_registry_reports_foundation_m2_only() -> None:
    tracks = (ROOT / "conductor/tracks.md").read_text(encoding="utf-8")
    foundation_line = next(
        line for line in tracks.splitlines() if "`foundation_architecture_20260718`" in line
    )
    assert "current `M2`" in foundation_line
    assert "target `M6`" in foundation_line
