import json
from pathlib import Path

from riopa_provenance.roadmap import release_readiness

ROOT = Path(__file__).resolve().parents[1]
TRACK = ROOT / "conductor/tracks/nz_spatial_source_registry_20260718"
RECEIPT = ROOT / "docs/nz-source-registry-m2-promotion-20260829.json"


def test_nz_source_registry_m2_promotion_is_exact_tree_and_fail_closed() -> None:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    metadata = json.loads((TRACK / "metadata.json").read_text(encoding="utf-8"))

    assert receipt["decision"] == "promote-to-m2"
    assert receipt["compatibility"]["classification"] == "metadata-only-backward-compatible"
    assert receipt["authority"]["signature_claimed"] is False
    assert len(receipt["source_revision"]["tree_sha"]) == 40
    assert receipt["dependency_boundary"]["status"] == "satisfied"
    assert set(receipt["m2_repository_owned"].values()) == {"passed"}

    assert metadata["status"] == "validating"
    assert metadata["current_maturity"] == "M2"
    assert metadata["blocking_defect_maturity"] == receipt["remaining_blocking_gates"]
    assert receipt["evidence_id"] in metadata["evidence"]

    readiness = release_readiness(ROOT, "0.4.0")
    assert readiness.qualified_tracks == readiness.required_tracks == 3
    assert readiness.passed_gates == 0
    assert not any(
        "track nz_spatial_source_registry_20260718" in blocker for blocker in readiness.blockers
    )


def test_nz_source_registry_reports_m2_only() -> None:
    tracks = (ROOT / "conductor/tracks.md").read_text(encoding="utf-8")
    registry_line = next(
        line for line in tracks.splitlines() if "`nz_spatial_source_registry_20260718`" in line
    )
    assert "current `M2`" in registry_line
    assert "target `M6`" in registry_line
