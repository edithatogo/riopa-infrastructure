from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pytest

from riopa_provenance.hashing import sha256_json
from riopa_provenance.linz import (
    LinzStateError,
    LinzStateStore,
    _validate_revision_interval,
    apply_linz_changeset,
    linz_service_url,
    reconcile_linz_full_export,
    semantic_table_digest,
)


def state(*, sequence: int, parent: str | None = None) -> dict[str, object]:
    return {
        "record_type": "linz_layer_state",
        "layer_kind": "layer",
        "layer_id": 42,
        "sequence": sequence,
        "parent_state_sha256": parent,
    }


def test_revision_intervals_require_utc_order_and_matching_precision() -> None:
    _validate_revision_interval("2026-01-01T00:00:00Z", "2026-01-01T00:00:01Z")
    _validate_revision_interval("2026-01-01T00:00:00.000Z", "2026-01-01T00:00:01.000Z")
    with pytest.raises(LinzStateError, match="full UTC RFC 3339"):
        _validate_revision_interval("2026-01-01T00:00:00+00:00", "2026-01-01T00:00:01Z")
    with pytest.raises(LinzStateError, match="identical timestamp precision"):
        _validate_revision_interval("2026-01-01T00:00:00Z", "2026-01-01T00:00:01.0Z")
    with pytest.raises(LinzStateError, match="later"):
        _validate_revision_interval("2026-01-01T00:00:01Z", "2026-01-01T00:00:01Z")


@pytest.mark.parametrize("api_key", ["", "bad/key", "bad?query", "bad#fragment", "bad\nkey"])
def test_service_url_rejects_unsafe_path_credentials(api_key: str) -> None:
    with pytest.raises(LinzStateError, match="unsafe for a path credential"):
        linz_service_url(api_key)
    assert linz_service_url("safe-key") == "https://data.linz.govt.nz/services;key=safe-key/wfs"


def test_state_store_enforces_immutable_sequence_and_parent_chain(tmp_path: Path) -> None:
    store = LinzStateStore(tmp_path, layer_kind="layer", layer_id=42)
    with pytest.raises(LinzStateError, match="no current pointer"):
        store.load_current()
    first = store.write_state(state(sequence=0))
    assert store.load_current() == first.state
    first_hash = str(first.state["state_sha256"])
    second = store.write_state(state(sequence=1, parent=first_hash))
    assert store.load_current() == second.state
    second_hash = str(second.state["state_sha256"])
    with pytest.raises(LinzStateError, match="increment by one"):
        store.write_state(state(sequence=3, parent=second_hash))
    with pytest.raises(LinzStateError, match="parent does not match"):
        store.write_state(state(sequence=2, parent=first_hash))

    pointer = json.loads(store.pointer_path.read_text(encoding="utf-8"))
    pointer["state_sha256"] = "0" * 64
    store.pointer_path.write_text(json.dumps(pointer), encoding="utf-8")
    with pytest.raises(LinzStateError, match="pointer hash"):
        store.load_current()


def test_state_store_rejects_wrong_identity_and_invalid_constructor(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="layer_kind"):
        LinzStateStore(tmp_path, layer_kind="feature", layer_id=1)
    with pytest.raises(ValueError, match="positive"):
        LinzStateStore(tmp_path, layer_kind="layer", layer_id=0)
    with pytest.raises(LinzStateError, match="identity"):
        LinzStateStore(tmp_path, layer_kind="table", layer_id=42).write_state(state(sequence=0))


def _database(path: Path, rows: list[tuple[int, str]]) -> Path:
    connection = duckdb.connect(str(path))
    try:
        connection.execute("CREATE TABLE features (id INTEGER, name VARCHAR)")
        connection.executemany("INSERT INTO features VALUES (?, ?)", rows)
    finally:
        connection.close()
    return path


def _changeset(path: Path, rows: list[tuple[int | None, str, str]]) -> Path:
    connection = duckdb.connect()
    try:
        connection.execute("CREATE TABLE changes (id INTEGER, name VARCHAR, __change__ VARCHAR)")
        connection.executemany("INSERT INTO changes VALUES (?, ?, ?)", rows)
        connection.execute("COPY changes TO ? (FORMAT PARQUET)", [str(path)])
    finally:
        connection.close()
    return path


def _apply(target: Path, changeset: Path, receipt: Path) -> dict[str, object]:
    return apply_linz_changeset(
        target_database=target,
        changeset_parquet=changeset,
        source_id="urn:source:linz",
        layer_id=42,
        primary_key="id",
        from_revision="2026-07-31T08:00:00Z",
        to_revision="2026-07-31T09:00:00Z",
        capture_set_id="urn:capture:set",
        capture_set_manifest_sha256="a" * 64,
        receipt_path=receipt,
        applied_at="2026-07-31T09:05:00Z",
    ).receipt


def test_changeset_application_is_atomic_idempotent_and_content_bound(tmp_path: Path) -> None:
    target = _database(tmp_path / "target.duckdb", [(1, "old"), (2, "delete")])
    changes = _changeset(
        tmp_path / "changes.parquet",
        [(1, "updated", "update"), (2, "ignored", "DELETE"), (3, "new", "INSERT")],
    )

    first = _apply(target, changes, tmp_path / "first.json")
    assert first["counts"] == {"INSERT": 1, "UPDATE": 1, "DELETE": 1}
    assert first["row_count_before"] == 2
    assert first["row_count_after"] == 2
    assert first["semantic_digest_before"] != first["semantic_digest_after"]
    connection = duckdb.connect(str(target), read_only=True)
    try:
        assert connection.execute("SELECT * FROM features ORDER BY id").fetchall() == [
            (1, "updated"),
            (3, "new"),
        ]
    finally:
        connection.close()

    second = _apply(target, changes, tmp_path / "recovered.json")
    assert second == first
    assert json.loads((tmp_path / "recovered.json").read_text(encoding="utf-8")) == first


@pytest.mark.parametrize(
    ("rows", "message"),
    [
        ([(None, "bad", "INSERT")], "null primary keys"),
        ([(3, "a", "INSERT"), (3, "b", "INSERT")], "duplicated primary-key groups"),
        ([(3, "bad", "UPSERT")], "invalid actions"),
        ([(1, "conflict", "INSERT")], "already exist"),
        ([(99, "missing", "UPDATE")], "do not exist"),
    ],
)
def test_changeset_validation_rolls_back_without_mutating_target(
    tmp_path: Path,
    rows: list[tuple[int | None, str, str]],
    message: str,
) -> None:
    target = _database(tmp_path / "target.duckdb", [(1, "one")])
    before = semantic_table_digest(target, primary_key="id")
    changes = _changeset(tmp_path / "changes.parquet", rows)
    with pytest.raises(LinzStateError, match=message):
        _apply(target, changes, tmp_path / "receipt.json")
    assert semantic_table_digest(target, primary_key="id") == before
    assert not (tmp_path / "receipt.json").exists()


def test_changeset_application_rejects_missing_files_and_columns(tmp_path: Path) -> None:
    target = _database(tmp_path / "target.duckdb", [(1, "one")])
    with pytest.raises(LinzStateError, match="does not exist"):
        _apply(tmp_path / "missing.duckdb", tmp_path / "missing.parquet", tmp_path / "r.json")
    with pytest.raises(LinzStateError, match="does not exist"):
        _apply(target, tmp_path / "missing.parquet", tmp_path / "r.json")

    connection = duckdb.connect()
    try:
        connection.execute("CREATE TABLE changes (id INTEGER, __change__ VARCHAR)")
        connection.execute("INSERT INTO changes VALUES (2, 'INSERT')")
        connection.execute(
            "COPY changes TO ? (FORMAT PARQUET)", [str(tmp_path / "incomplete.parquet")]
        )
    finally:
        connection.close()
    with pytest.raises(LinzStateError, match="missing columns: name"):
        _apply(target, tmp_path / "incomplete.parquet", tmp_path / "r.json")


def test_full_export_reconciliation_detects_changeset_drift(tmp_path: Path) -> None:
    target = _database(tmp_path / "target.duckdb", [(1, "one"), (2, "two")])
    matching = _database(tmp_path / "matching.duckdb", [(2, "two"), (1, "one")])
    divergent = _database(tmp_path / "divergent.duckdb", [(1, "one"), (2, "changed")])
    current = {
        "record_type": "linz_layer_state",
        "source_id": "urn:source:linz",
        "layer_kind": "layer",
        "layer_id": 42,
        "primary_key": "id",
        "current_revision": "2026-07-31T09:00:00Z",
        "pending_changesets": [],
        "state_sha256": "",
    }
    current["state_sha256"] = sha256_json(current, omit_keys={"state_sha256"})

    report = reconcile_linz_full_export(
        current,
        target_database=target,
        full_export_database=matching,
        full_export_revision="2026-07-31T09:00:00Z",
        captured_at="2026-07-31T09:05:00Z",
    )
    assert report["status"] == "matched"
    assert report["target"] == report["full_export"]
    assert (
        reconcile_linz_full_export(
            current,
            target_database=target,
            full_export_database=divergent,
            full_export_revision="2026-07-31T09:00:00Z",
            captured_at="2026-07-31T09:05:00Z",
        )["status"]
        == "diverged"
    )


def test_full_export_reconciliation_requires_a_stable_checkpoint(tmp_path: Path) -> None:
    database = _database(tmp_path / "data.duckdb", [(1, "one")])
    current = {
        "record_type": "linz_layer_state",
        "primary_key": "id",
        "current_revision": "2026-07-31T09:00:00Z",
        "pending_changesets": [{"status": "captured"}],
        "state_sha256": "",
    }
    current["state_sha256"] = sha256_json(current, omit_keys={"state_sha256"})
    with pytest.raises(LinzStateError, match="pending"):
        reconcile_linz_full_export(
            current,
            target_database=database,
            full_export_database=database,
            full_export_revision="2026-07-31T09:00:00Z",
            captured_at="2026-07-31T09:05:00Z",
        )
    invalid = {**current, "pending_changesets": []}
    with pytest.raises(LinzStateError, match="state hash"):
        reconcile_linz_full_export(
            invalid,
            target_database=database,
            full_export_database=database,
            full_export_revision="2026-07-31T09:00:00Z",
            captured_at="2026-07-31T09:05:00Z",
        )
