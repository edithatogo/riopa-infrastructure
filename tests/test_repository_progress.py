from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

import scripts.report_repository_progress as progress


def test_only_top_level_actual_tasks_are_counted() -> None:
    rows = progress.plan_tasks(
        "## Build\n- [x] done\n  - [ ] child\n```md\n- [x] example\n```\n"
        "- [~] current\n## Release\n- [ ] gate\n"
    )
    assert [r["state"] for r in rows] == ["x", "~", " "]
    assert rows[-1]["phase"] == "Release"


def test_empty_root_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="no Conductor tracks"):
        progress.track_progress(tmp_path)


def test_real_report_is_repeatable_and_non_mutating() -> None:
    root = Path(__file__).resolve().parents[1]
    state = root / ".riopa-local/codex/state.json"
    before = state.read_bytes() if state.exists() else None
    first = progress.report(root)
    assert first == progress.report(root)
    assert (state.read_bytes() if state.exists() else None) == before
    assert len(first["tracks"]) == 29
    assert first["task_totals"]["completed"] < first["task_totals"]["total"]
    mvp = next(t for t in first["tracks"] if t["track_id"] == "nz_spatial_archive_mvp_20260718")
    assert mvp["status"] == "active" and mvp["maturity"] == "M1"
    stable = first["release_readiness"]["releases"][-1]
    assert stable["version"] == "1.0.0" and stable["ready"] is False
    assert "hosted systems" in first["non_claims"][0]
    assert first["recorded_cycle_ledger"]["three_cycle_gate_qualified"] is False
    assert first["recorded_cycle_ledger"]["scheduled_automatic_source_runs"] == []
    assert "## Release qualification" in progress.markdown(first)


def test_cli_failure_does_not_claim_success(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr("sys.argv", ["progress", "--root", str(tmp_path), "--format", "json"])
    assert progress.main() == 1
    assert json.loads(capsys.readouterr().out)["status"] == "invalid"


@pytest.mark.parametrize("tamper", ["hash", "escape", "duplicate", "missing", "unbound"])
def test_archive_evidence_validation_rejects_tampering(tamper: str) -> None:
    root = Path(__file__).resolve().parents[1]
    archive = json.loads((root / "docs/archive-current-status-20260831.json").read_bytes())
    if tamper == "hash":
        archive["evidence_refs"][0]["sha256"] = "0" * 64
    elif tamper == "escape":
        archive["evidence_refs"][0]["path"] = "../outside.json"
    elif tamper == "duplicate":
        archive["evidence_refs"].append(copy.deepcopy(archive["evidence_refs"][0]))
    elif tamper == "missing":
        archive["evidence_refs"][0]["path"] = "docs/nonexistent-progress-evidence.json"
    else:
        archive["dispositions"]["source_publication"]["evidence"] = "docs/unbound.json"
    with pytest.raises(ValueError):
        progress.validate_archive_evidence(root, archive)


def test_track_identity_and_symlink_fail_closed(tmp_path: Path) -> None:
    track = tmp_path / "conductor/tracks/sample"
    track.mkdir(parents=True)
    metadata = {"track_id": "wrong", "status": "active", "current_maturity": "M1"}
    (track / "metadata.json").write_text(json.dumps(metadata))
    (track / "plan.md").write_text("- [ ] pending\n")
    with pytest.raises(ValueError, match="identity"):
        progress.track_progress(tmp_path)
    (track / "plan.md").unlink()
    target = tmp_path / "plan-source.md"
    target.write_text("- [x] done\n")
    (track / "plan.md").symlink_to(target)
    with pytest.raises(ValueError, match="symlink"):
        progress.track_progress(tmp_path)
