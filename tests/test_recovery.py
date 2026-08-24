from pathlib import Path

import pytest

from riopa_provenance.recovery import (
    restore,
    rollback,
    snapshot,
    validate_exercise_report,
    write_evidence,
)


def _fixture(root: Path, value: str = "v1") -> Path:
    root.mkdir()
    (root / "state.json").write_text('{"state": "' + value + '"}\n', encoding="utf-8")
    return root


def test_snapshot_restore_round_trip(tmp_path: Path) -> None:
    source = _fixture(tmp_path / "source")
    snap = snapshot(source, tmp_path / "snapshot")
    restored = restore(tmp_path / "snapshot", tmp_path / "restored", snap.digest)
    assert restored.digest == snap.digest
    assert (tmp_path / "restored/state.json").read_text() == (source / "state.json").read_text()


def test_restore_rejects_tampered_snapshot(tmp_path: Path) -> None:
    source = _fixture(tmp_path / "source")
    snap = snapshot(source, tmp_path / "snapshot")
    (tmp_path / "snapshot/state.json").write_text("tampered\n", encoding="utf-8")
    with pytest.raises(ValueError, match="digest mismatch"):
        restore(tmp_path / "snapshot", tmp_path / "restored", snap.digest)


def test_rollback_materialises_prior_state_and_writes_json(tmp_path: Path) -> None:
    current = _fixture(tmp_path / "current", "v2")
    prior = _fixture(tmp_path / "prior", "v1")
    evidence = rollback(current, prior, tmp_path / "rolled-back")
    assert evidence.operation == "rollback"
    assert '"v1"' in (tmp_path / "rolled-back/state.json").read_text()
    out = tmp_path / "evidence.json"
    write_evidence(evidence, out)
    assert '"status": "executed-local"' in out.read_text()


def test_exercise_report_requires_hashes_timings_and_explicit_scope() -> None:
    report = {
        "exercise_id": "dr-1",
        "operation": "restore",
        "status": "executed-local",
        "source_revision": "a" * 40,
        "started_at": "2026-08-24T00:00:00Z",
        "ended_at": "2026-08-24T00:00:01Z",
        "recovery_point_sha256": "a" * 64,
        "restored_object_sha256": "b" * 64,
        "raw_log_sha256": "c" * 64,
        "timings": {"rpo_seconds": 0, "rto_seconds": 1},
        "scope": ["bounded-regional", "public-datasets-only"],
    }
    assert validate_exercise_report(report) == ()


def test_exercise_report_preserves_failed_run_boundary() -> None:
    report = {
        "exercise_id": "dr-failed",
        "operation": "rollback",
        "status": "failed",
        "source_revision": "a" * 40,
        "started_at": "2026-08-24T00:00:00Z",
        "ended_at": "2026-08-24T00:00:01Z",
        "recovery_point_sha256": "a" * 64,
        "restored_object_sha256": "b" * 64,
        "raw_log_sha256": "c" * 64,
        "timings": {"rpo_seconds": 1, "rto_seconds": 2},
        "scope": ["bounded-regional"],
    }
    assert any("failure_reason" in error for error in validate_exercise_report(report))
