import json
from pathlib import Path

from scripts.generate_release_decision_readiness import generate


def test_readiness_reconciles_missing_matrix_rows(tmp_path: Path) -> None:
    root = Path(__file__).parents[1]
    output = tmp_path / "readiness.json"
    generate(
        root / "docs/panel-qualification-report-templates-20260801.json",
        root / "docs/open-issue-track-evidence-matrix-20260801.json",
        output,
    )
    payload = json.loads(output.read_text())
    assert payload["release_ready"] is False
    assert payload["release_authority"] == "pending"
    assert len(payload["tracks"]) == 28
    assert any("no row" in blocker for t in payload["tracks"] for blocker in t["blockers"])
    assert all(t["disposition"] is None for t in payload["tracks"])


def test_committed_readiness_projection_is_regenerable() -> None:
    """The checked-in projection must not drift from its source manifests."""
    root = Path(__file__).parents[1]
    expected = root / "docs/release-decision-readiness-20260801.json"
    generated = expected.with_suffix(".tmp.json")
    try:
        generate(
            root / "docs/panel-qualification-report-templates-20260801.json",
            root / "docs/open-issue-track-evidence-matrix-20260801.json",
            generated,
        )
        assert generated.read_text(encoding="utf-8") == expected.read_text(encoding="utf-8")
    finally:
        generated.unlink(missing_ok=True)
