from pathlib import Path

from scripts.validate_real_data_release_candidate import validate_candidate


def test_real_data_candidate_artifact_digests_are_verified() -> None:
    root = Path(__file__).resolve().parents[1]
    report = validate_candidate(root)
    assert report["status"] == "digest-validated-promotion-disabled"
    assert report["promotion_allowed"] is False
    assert len(report["artifacts"]) == 3
    assert all(len(item["sha256"]) == 64 for item in report["artifacts"])
    assert any("preservation" in gate for gate in report["open_gates"])
