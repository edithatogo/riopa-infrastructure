from pathlib import Path

from scripts.run_release_candidate_tutorials import TUTORIALS, run_release_candidate_tutorials


def test_release_candidate_tutorial_rehearsal_is_bounded(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    report = run_release_candidate_tutorials(root, tmp_path)
    assert report["status"] == "repository-candidate-rehearsal"
    assert report["candidate_revision"]
    assert report["promotion_eligible"] is False
    assert [item["tutorial"] for item in report["tutorials"]] == list(TUTORIALS)
    assert all(item["status"] == "pass" for item in report["tutorials"])
    assert all(item["troubleshooting_status"] == "failed-closed" for item in report["tutorials"])
