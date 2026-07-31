from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import duckdb
import pytest

from riopa_provenance.hashing import sha256_json
from riopa_provenance.linz import (
    LinzChangesetCoordinator,
    LinzStateError,
    LinzStateStore,
    _capture_set_reference,
    _json_safe,
    _load_hashed_json,
    _quote_identifier,
    _scalar_int,
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


def test_state_store_rejects_malformed_pointer_state_and_immutable_collision(
    tmp_path: Path,
) -> None:
    store = LinzStateStore(tmp_path, layer_kind="layer", layer_id=42)
    assert store.load_current(required=False) is None
    store.pointer_path.parent.mkdir(parents=True)
    store.pointer_path.write_text("[", encoding="utf-8")
    with pytest.raises(LinzStateError, match="cannot read LINZ state pointer"):
        store.load_current()
    store.pointer_path.write_text("[]", encoding="utf-8")
    with pytest.raises(LinzStateError, match="must be an object"):
        store.load_current()
    store.pointer_path.write_text("{}", encoding="utf-8")
    with pytest.raises(LinzStateError, match="incomplete"):
        store.load_current()

    store.pointer_path.unlink()
    first = store.write_state(state(sequence=0))
    first.state_path.write_text("different", encoding="utf-8")
    store.pointer_path.unlink()
    with pytest.raises(LinzStateError, match="immutable state path"):
        store.write_state(state(sequence=0))


def test_hashed_json_reference_and_revision_validation_fail_closed(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence.json"
    evidence.write_text("[]", encoding="utf-8")
    with pytest.raises(LinzStateError, match="must be an object"):
        _load_hashed_json(evidence, hash_field="sha256")
    evidence.write_text("{}", encoding="utf-8")
    with pytest.raises(LinzStateError, match="sha256 mismatch"):
        _load_hashed_json(evidence, hash_field="sha256")
    directory = tmp_path / "directory"
    directory.mkdir()
    with pytest.raises(LinzStateError, match="cannot read JSON evidence"):
        _load_hashed_json(directory, hash_field="sha256")
    with pytest.raises(LinzStateError, match="invalid LINZ revision timestamp"):
        _validate_revision_interval("2026-02-30T00:00:00Z", "2026-03-01T00:00:00Z")


def test_sql_and_semantic_value_helpers_cover_supported_types() -> None:
    assert _quote_identifier('a"b') == '"a""b"'
    with pytest.raises(LinzStateError, match="empty or contains NUL"):
        _quote_identifier("")
    with pytest.raises(LinzStateError, match="empty or contains NUL"):
        _quote_identifier("bad\x00name")
    assert _json_safe(None) is None
    assert _json_safe(b"\x00\xff") == {"$binary_hex": "00ff"}
    assert _json_safe(datetime(2026, 7, 31, 1, 2, 3)) == "2026-07-31T01:02:03"
    assert _json_safe(date(2026, 7, 31)) == "2026-07-31"
    assert _json_safe(Decimal("1.20")) == "1.20"
    assert _json_safe({"b": {2, 1}, "a": (3,)}) == {"a": [3], "b": [1, 2]}
    assert _json_safe(object()).startswith("<object object at")
    for value in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(LinzStateError, match="non-finite"):
            _json_safe(value)


class _FakeArchiver:
    def __init__(self, root: Path) -> None:
        self.capture_client = SimpleNamespace(store=SimpleNamespace(root=root))
        self.root = root
        self.calls: list[dict[str, Any]] = []

    def archive_feature_type(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        index = len(self.calls)
        path = self.root / f"capture-{index}.json"
        manifest = {"manifest_sha256": ""}
        manifest["manifest_sha256"] = sha256_json(manifest, omit_keys={"manifest_sha256"})
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest), encoding="utf-8")
        return SimpleNamespace(
            manifest_path=path,
            capture_set_id=f"urn:capture:{index}",
            feature_count=index,
            service_url=kwargs["service_url"].replace("secret", "REDACTED"),
            capabilities_capture=SimpleNamespace(retrieved_at=f"2026-07-31T0{index}:00:00Z"),
        )


def test_changeset_coordinator_captures_gap_free_baseline_and_pending_state(
    tmp_path: Path,
) -> None:
    archiver = _FakeArchiver(tmp_path / "captures")
    coordinator = LinzChangesetCoordinator(archiver)  # type: ignore[arg-type]
    store = LinzStateStore(tmp_path / "state", layer_kind="layer", layer_id=42)
    baseline = coordinator.capture_baseline(
        state_store=store,
        api_key="secret",
        source_id="urn:source:linz",
        endpoint_id="linz",
        primary_key="id",
        revision="2026-07-31T01:00:00Z",
    )
    assert baseline.state_write.state["current_revision"] == "2026-07-31T01:00:00Z"
    assert "secret" not in json.dumps(baseline.state_write.state)
    assert archiver.calls[0]["redact_values"] == ("secret",)
    with pytest.raises(LinzStateError, match="baseline already exists"):
        coordinator.capture_baseline(
            state_store=store,
            api_key="secret",
            source_id="urn:source:linz",
            endpoint_id="linz",
            primary_key="id",
            revision="2026-07-31T01:00:00Z",
        )
    with pytest.raises(LinzStateError, match="filtered LINZ changesets"):
        coordinator.capture_changeset(
            state_store=store,
            api_key="secret",
            to_revision="2026-07-31T02:00:00Z",
            cql_filter="id=1",
        )
    captured = coordinator.capture_changeset(
        state_store=store,
        api_key="secret",
        to_revision="2026-07-31T02:00:00Z",
    )
    pending = captured.state_write.state
    assert pending["current_revision"] == "2026-07-31T01:00:00Z"
    assert pending["pending_changesets"][0]["to_revision"] == "2026-07-31T02:00:00Z"
    assert archiver.calls[1]["request_params"] == {
        "viewparams": "from:2026-07-31T01:00:00Z;to:2026-07-31T02:00:00Z"
    }
    with pytest.raises(LinzStateError, match="pending changeset"):
        coordinator.capture_changeset(
            state_store=store,
            api_key="secret",
            to_revision="2026-07-31T03:00:00Z",
        )


def test_capture_set_reference_rejects_manifest_outside_store(tmp_path: Path) -> None:
    manifest = tmp_path / "outside.json"
    payload = {"manifest_sha256": ""}
    payload["manifest_sha256"] = sha256_json(payload, omit_keys={"manifest_sha256"})
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    archive = SimpleNamespace(manifest_path=manifest, capture_set_id="urn:capture", feature_count=0)
    with pytest.raises(LinzStateError, match="outside the capture store"):
        _capture_set_reference(archive, capture_root=tmp_path / "other")


def test_coordinator_advances_only_from_journal_bound_application(tmp_path: Path) -> None:
    archiver = _FakeArchiver(tmp_path / "captures")
    coordinator = LinzChangesetCoordinator(archiver)  # type: ignore[arg-type]
    store = LinzStateStore(tmp_path / "state", layer_kind="layer", layer_id=42)
    coordinator.capture_baseline(
        state_store=store,
        api_key="secret",
        source_id="urn:source:linz",
        endpoint_id="linz",
        primary_key="id",
        revision="2026-07-31T01:00:00Z",
    )
    captured = coordinator.capture_changeset(
        state_store=store,
        api_key="secret",
        to_revision="2026-07-31T02:00:00Z",
    )
    pending = captured.state_write.state["pending_changesets"][0]
    target = _database(tmp_path / "target.duckdb", [(1, "one")])
    changeset = _changeset(tmp_path / "changes.parquet", [(2, "two", "INSERT")])
    application = apply_linz_changeset(
        target_database=target,
        changeset_parquet=changeset,
        source_id="urn:source:linz",
        layer_id=42,
        primary_key="id",
        from_revision="2026-07-31T01:00:00Z",
        to_revision="2026-07-31T02:00:00Z",
        capture_set_id=str(pending["capture_set_id"]),
        capture_set_manifest_sha256=str(pending["manifest_sha256"]),
        receipt_path=tmp_path / "receipt.json",
        applied_at="2026-07-31T02:05:00Z",
    )
    advanced = coordinator.advance_checkpoint(
        state_store=store,
        receipt_path=application.receipt_path,
        target_database=target,
    )
    assert advanced.state["current_revision"] == "2026-07-31T02:00:00Z"
    assert advanced.state["pending_changesets"] == []
    assert advanced.state["applied_changesets"][0]["status"] == "applied"
    archived = store.layer_root / str(
        advanced.state["applied_changesets"][0]["application_receipt_path"]
    )
    assert archived.read_bytes() == application.receipt_path.read_bytes()

    with pytest.raises(LinzStateError, match="exactly one captured changeset"):
        coordinator.advance_checkpoint(
            state_store=store,
            receipt_path=application.receipt_path,
            target_database=target,
        )


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


def test_semantic_digest_rejects_missing_table_and_primary_key(tmp_path: Path) -> None:
    target = _database(tmp_path / "target.duckdb", [(1, "one")])
    with pytest.raises(LinzStateError, match="target table does not exist"):
        semantic_table_digest(target, table_name="absent", primary_key="id")
    with pytest.raises(LinzStateError, match="primary key column is missing"):
        semantic_table_digest(target, primary_key="absent")

    connection = duckdb.connect()
    try:
        with pytest.raises(LinzStateError, match="scalar SQL query returned no row"):
            _scalar_int(connection, "SELECT 1 WHERE false")
    finally:
        connection.close()


@pytest.mark.parametrize(
    ("column", "replacement", "message"),
    [
        ("receipt_json", "{", "invalid JSON"),
        ("receipt_json", "[]", "must be an object"),
        ("receipt_sha256", "0" * 64, "integrity check failed"),
    ],
)
def test_idempotent_recovery_rejects_corrupt_application_journal(
    tmp_path: Path, column: str, replacement: str, message: str
) -> None:
    target = _database(tmp_path / "target.duckdb", [(1, "one")])
    changes = _changeset(tmp_path / "changes.parquet", [(2, "two", "INSERT")])
    _apply(target, changes, tmp_path / "receipt.json")
    connection = duckdb.connect(str(target))
    try:
        connection.execute(
            f"UPDATE _riopa_linz_applications SET {column} = ?",  # nosec B608
            [replacement],
        )
    finally:
        connection.close()
    with pytest.raises(LinzStateError, match=message):
        _apply(target, changes, tmp_path / "recovered.json")


def test_idempotent_recovery_rejects_wrong_journal_identity(tmp_path: Path) -> None:
    target = _database(tmp_path / "target.duckdb", [(1, "one")])
    changes = _changeset(tmp_path / "changes.parquet", [(2, "two", "INSERT")])
    receipt = _apply(target, changes, tmp_path / "receipt.json")
    tampered = {**receipt, "application_id": "urn:wrong", "receipt_sha256": ""}
    tampered["receipt_sha256"] = sha256_json(tampered, omit_keys={"receipt_sha256"})
    connection = duckdb.connect(str(target))
    try:
        connection.execute(
            "UPDATE _riopa_linz_applications SET receipt_json = ?, receipt_sha256 = ?",
            [json.dumps(tampered), tampered["receipt_sha256"]],
        )
    finally:
        connection.close()
    with pytest.raises(LinzStateError, match="identity mismatch"):
        _apply(target, changes, tmp_path / "recovered.json")


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


def test_full_export_reconciliation_rejects_identity_checkpoint_and_primary_key(
    tmp_path: Path,
) -> None:
    database = _database(tmp_path / "data.duckdb", [(1, "one")])

    def hashed(**updates: object) -> dict[str, object]:
        value: dict[str, object] = {
            "record_type": "linz_layer_state",
            "primary_key": "id",
            "current_revision": "2026-07-31T09:00:00Z",
            "pending_changesets": [],
            "state_sha256": "",
            **updates,
        }
        value["state_sha256"] = sha256_json(value, omit_keys={"state_sha256"})
        return value

    with pytest.raises(LinzStateError, match="requires a LINZ layer state"):
        reconcile_linz_full_export(
            hashed(record_type="other"),
            target_database=database,
            full_export_database=database,
            full_export_revision="2026-07-31T09:00:00Z",
            captured_at="2026-07-31T09:05:00Z",
        )
    with pytest.raises(LinzStateError, match="does not match"):
        reconcile_linz_full_export(
            hashed(),
            target_database=database,
            full_export_database=database,
            full_export_revision="2026-07-31T10:00:00Z",
            captured_at="2026-07-31T10:05:00Z",
        )
    with pytest.raises(LinzStateError, match="has no primary key"):
        reconcile_linz_full_export(
            hashed(primary_key=""),
            target_database=database,
            full_export_database=database,
            full_export_revision="2026-07-31T09:00:00Z",
            captured_at="2026-07-31T09:05:00Z",
        )
