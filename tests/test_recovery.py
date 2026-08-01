from pathlib import Path

import pytest

from riopa_provenance.recovery import restore, rollback, snapshot, write_evidence


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
