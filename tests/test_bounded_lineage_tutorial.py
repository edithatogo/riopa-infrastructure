from pathlib import Path

from scripts.run_bounded_lineage_tutorial import run_tutorial


def test_bounded_lineage_tutorial_has_positive_and_fail_closed_paths(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    report = run_tutorial(root, tmp_path)
    assert report["status"] == "bounded-rehearsal"
    assert report["query_answer_count"] > 0
    assert report["troubleshooting"]["status"] == "failed-closed"
    assert report["troubleshooting"]["error"].startswith("manifest validation failed:")
    assert "missing-manifest.json" in report["troubleshooting"]["error"]
