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


def test_exercise_report_rejects_invalid_shape_and_values() -> None:
    assert validate_exercise_report(None) == ("exercise report must be an object",)
    errors = validate_exercise_report(
        {
            "operation": "deploy",
            "status": "unknown",
            "recovery_point_sha256": "bad",
            "restored_object_sha256": "bad",
            "raw_log_sha256": "bad",
            "timings": {"rpo_seconds": -1, "rto_seconds": "slow"},
            "scope": [],
        }
    )
    assert any("exercise_id is required" in error for error in errors)
    assert any("operation is unsupported" in error for error in errors)
    assert any("status is unsupported" in error for error in errors)
    assert any("lowercase SHA-256" in error for error in errors)
    assert any("timings.rpo_seconds" in error for error in errors)
    assert any("scope must" in error for error in errors)


def test_exercise_report_requires_hosted_id_and_failed_reason() -> None:
    base = {
        "exercise_id": "dr-1",
        "operation": "restore",
        "source_revision": "a" * 40,
        "started_at": "2026-08-24T00:00:00Z",
        "ended_at": "2026-08-24T00:00:01Z",
        "recovery_point_sha256": "a" * 64,
        "restored_object_sha256": "b" * 64,
        "raw_log_sha256": "c" * 64,
        "timings": {"rpo_seconds": 0, "rto_seconds": 1},
        "scope": ["bounded-regional"],
    }
    assert any(
        "failure_reason" in error
        for error in validate_exercise_report({**base, "status": "failed"})
    )
    assert any(
        "hosted_run_id" in error
        for error in validate_exercise_report({**base, "status": "executed-hosted"})
    )


def test_snapshot_restore_and_rollback_reject_invalid_or_existing_targets(
    tmp_path: Path,
) -> None:
    source = _fixture(tmp_path / "source")
    with pytest.raises(ValueError, match="source must be a directory"):
        snapshot(tmp_path / "missing", tmp_path / "snapshot")
    snap = snapshot(source, tmp_path / "snapshot")
    with pytest.raises(FileExistsError):
        snapshot(source, tmp_path / "snapshot")
    with pytest.raises(ValueError, match="snapshot must be a directory"):
        restore(tmp_path / "missing", tmp_path / "restored", snap.digest)
    with pytest.raises(FileExistsError):
        restore(tmp_path / "snapshot", tmp_path / "snapshot", snap.digest)
    current = _fixture(tmp_path / "current", "v2")
    prior = _fixture(tmp_path / "prior", "v1")
    with pytest.raises(ValueError, match="current and prior"):
        rollback(tmp_path / "missing", prior, tmp_path / "rolled-back")
    rollback(current, prior, tmp_path / "rolled-back")
    with pytest.raises(FileExistsError):
        rollback(current, prior, tmp_path / "rolled-back")
