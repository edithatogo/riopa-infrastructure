"""LINZ baseline-plus-changeset archival and transactional application.

The coordinator models a changeset update as two distinct durable operations:

1. capture and verify the immutable WFS changeset without moving the local
   revision checkpoint; and
2. apply that captured changeset transactionally, emit a content-bound receipt,
   then advance the checkpoint only after the receipt and target database are
   verified.

This makes a crash between capture, application, and checkpoint advancement
recoverable without silently skipping a LINZ revision interval.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import duckdb

from .capture import _atomic_write
from .hashing import canonical_json_bytes, sha256_file, sha256_json
from .validation import resolve_local_reference
from .wfs import WFSFeatureTypeArchive, WFSFeatureTypeArchiver

_RFC3339_UTC = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})T(?P<time>\d{2}:\d{2}:\d{2})"
    r"(?P<fraction>\.\d+)?Z$"
)
_ACTIONS = ("INSERT", "UPDATE", "DELETE")


class LinzStateError(RuntimeError):
    """Raised when a LINZ capture or checkpoint transition is unsafe."""


@dataclass(frozen=True)
class LinzStateWrite:
    state: dict[str, Any]
    state_path: Path
    pointer_path: Path


@dataclass(frozen=True)
class LinzCaptureTransition:
    archive: WFSFeatureTypeArchive
    state_write: LinzStateWrite


@dataclass(frozen=True)
class LinzApplication:
    receipt: dict[str, Any]
    receipt_path: Path


def _parse_revision(value: str) -> datetime:
    match = _RFC3339_UTC.fullmatch(value)
    if not match:
        raise LinzStateError("LINZ revisions must be full UTC RFC 3339 timestamps ending in Z")
    try:
        return datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError as exc:
        raise LinzStateError(f"invalid LINZ revision timestamp: {value}") from exc


def _revision_precision(value: str) -> int:
    match = _RFC3339_UTC.fullmatch(value)
    if not match:
        _parse_revision(value)
        raise AssertionError("unreachable")
    fraction = match.group("fraction")
    return len(fraction) - 1 if fraction else 0


def _validate_revision_interval(from_revision: str, to_revision: str) -> None:
    start = _parse_revision(from_revision)
    end = _parse_revision(to_revision)
    if _revision_precision(from_revision) != _revision_precision(to_revision):
        raise LinzStateError("FROM and TO revisions must use identical timestamp precision")
    if end <= start:
        raise LinzStateError("TO revision must be later than FROM revision")


def _load_hashed_json(path: Path, *, hash_field: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LinzStateError(f"cannot read JSON evidence {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise LinzStateError(f"JSON evidence must be an object: {path}")
    expected = sha256_json(value, omit_keys={hash_field})
    if value.get(hash_field) != expected:
        raise LinzStateError(f"{hash_field} mismatch: {path}")
    return value


def _capture_set_reference(archive: WFSFeatureTypeArchive, *, capture_root: Path) -> dict[str, Any]:
    manifest = _load_hashed_json(archive.manifest_path, hash_field="manifest_sha256")
    try:
        manifest_path = archive.manifest_path.resolve().relative_to(capture_root.resolve())
    except ValueError as exc:
        raise LinzStateError("capture-set manifest is outside the capture store") from exc
    return {
        "capture_set_id": archive.capture_set_id,
        "manifest_path": manifest_path.as_posix(),
        "manifest_sha256": manifest["manifest_sha256"],
        "feature_count": archive.feature_count,
    }


def linz_service_url(api_key: str) -> str:
    """Return the LDS WFS endpoint while rejecting unsafe path material."""

    if not api_key or any(character in api_key for character in "/?#;\r\n"):
        raise LinzStateError("LINZ API key contains characters unsafe for a path credential")
    return f"https://data.linz.govt.nz/services;key={api_key}/wfs"


class LinzStateStore:
    """Immutable state versions plus one atomically replaced current pointer."""

    def __init__(self, root: str | Path, *, layer_kind: str, layer_id: int) -> None:
        if layer_kind not in {"layer", "table"}:
            raise ValueError("layer_kind must be 'layer' or 'table'")
        if layer_id < 1:
            raise ValueError("layer_id must be positive")
        self.root = Path(root).resolve()
        self.layer_kind = layer_kind
        self.layer_id = layer_id
        self.layer_root = self.root / "layers" / f"{layer_kind}-{layer_id}"
        self.states_root = self.layer_root / "states"
        self.pointer_path = self.layer_root / "current.json"

    def load_current(self, *, required: bool = True) -> dict[str, Any] | None:
        if not self.pointer_path.is_file():
            if required:
                raise LinzStateError(f"LINZ state has no current pointer: {self.pointer_path}")
            return None
        try:
            pointer = json.loads(self.pointer_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise LinzStateError(f"cannot read LINZ state pointer: {exc}") from exc
        if not isinstance(pointer, dict):
            raise LinzStateError("LINZ state pointer must be an object")
        relative_path = pointer.get("state_path")
        expected_hash = pointer.get("state_sha256")
        if not isinstance(relative_path, str) or not isinstance(expected_hash, str):
            raise LinzStateError("LINZ state pointer is incomplete")
        state_path = resolve_local_reference(self.layer_root, relative_path)
        state = _load_hashed_json(state_path, hash_field="state_sha256")
        if state["state_sha256"] != expected_hash:
            raise LinzStateError("LINZ state pointer hash does not match state object")
        self._validate_identity(state)
        return state

    def write_state(self, state: Mapping[str, Any]) -> LinzStateWrite:
        candidate = dict(state)
        candidate["state_sha256"] = ""
        candidate["state_sha256"] = sha256_json(candidate, omit_keys={"state_sha256"})
        self._validate_identity(candidate)

        current = self.load_current(required=False)
        if current is None:
            if candidate.get("sequence") != 0 or candidate.get("parent_state_sha256") is not None:
                raise LinzStateError("initial LINZ state must have sequence 0 and no parent")
        else:
            if candidate.get("sequence") != current["sequence"] + 1:
                raise LinzStateError("LINZ state sequence must increment by one")
            if candidate.get("parent_state_sha256") != current["state_sha256"]:
                raise LinzStateError("LINZ state parent does not match current state")

        self.states_root.mkdir(parents=True, exist_ok=True)
        filename = f"{candidate['sequence']:08d}-{candidate['state_sha256']}.json"
        state_path = self.states_root / filename
        payload = json.dumps(candidate, indent=2, ensure_ascii=False).encode("utf-8") + b"\n"
        if state_path.exists():
            if state_path.read_bytes() != payload:
                raise LinzStateError(
                    f"immutable state path already contains different bytes: {state_path}"
                )
        else:
            _atomic_write(state_path, payload)
        pointer = {
            "schema_version": "1.0.0",
            "record_type": "linz_layer_state_pointer",
            "state_sha256": candidate["state_sha256"],
            "state_path": state_path.relative_to(self.layer_root).as_posix(),
        }
        _atomic_write(
            self.pointer_path,
            json.dumps(pointer, indent=2, ensure_ascii=False).encode("utf-8") + b"\n",
        )
        return LinzStateWrite(candidate, state_path, self.pointer_path)

    def _validate_identity(self, state: Mapping[str, Any]) -> None:
        if state.get("record_type") != "linz_layer_state":
            raise LinzStateError("state record_type must be linz_layer_state")
        if state.get("layer_kind") != self.layer_kind or state.get("layer_id") != self.layer_id:
            raise LinzStateError("state identity does not match the state store")


class LinzChangesetCoordinator:
    """Coordinate full baselines and gap-free LINZ WFS changeset captures."""

    def __init__(self, archiver: WFSFeatureTypeArchiver) -> None:
        self.archiver = archiver

    def capture_baseline(
        self,
        *,
        state_store: LinzStateStore,
        api_key: str,
        source_id: str,
        endpoint_id: str,
        primary_key: str,
        revision: str,
        page_size: int = 1000,
        srs_name: str = "EPSG:2193",
    ) -> LinzCaptureTransition:
        _parse_revision(revision)
        if state_store.load_current(required=False) is not None:
            raise LinzStateError("a baseline already exists for this LINZ layer state")
        type_name = f"{state_store.layer_kind}-{state_store.layer_id}"
        service_url = linz_service_url(api_key)
        archive = self.archiver.archive_feature_type(
            source_id=source_id,
            endpoint_id=f"{endpoint_id}:baseline",
            service_url=service_url,
            type_name=type_name,
            page_size=page_size,
            sort_by=f"{primary_key} A",
            id_property=primary_key,
            srs_name=srs_name,
            redact_values=(api_key,),
        )
        reference = _capture_set_reference(
            archive, capture_root=self.archiver.capture_client.store.root
        )
        state = {
            "schema_version": "1.0.0",
            "record_type": "linz_layer_state",
            "source_id": source_id,
            "endpoint_id": endpoint_id,
            "layer_kind": state_store.layer_kind,
            "layer_id": state_store.layer_id,
            "primary_key": primary_key,
            "type_name": type_name,
            "changeset_type_name": f"{type_name}-changeset",
            "service_url": archive.service_url,
            "sequence": 0,
            "parent_state_sha256": None,
            "created_at": archive.capabilities_capture.retrieved_at,
            "baseline": {
                **reference,
                "revision": revision,
                "captured_at": archive.capabilities_capture.retrieved_at,
            },
            "current_revision": revision,
            "pending_changesets": [],
            "applied_changesets": [],
            "state_sha256": "",
        }
        return LinzCaptureTransition(archive, state_store.write_state(state))

    def capture_changeset(
        self,
        *,
        state_store: LinzStateStore,
        api_key: str,
        to_revision: str,
        page_size: int = 1000,
        srs_name: str = "EPSG:2193",
        cql_filter: str | None = None,
    ) -> LinzCaptureTransition:
        if cql_filter is not None:
            raise LinzStateError(
                "filtered LINZ changesets are not supported until a matching "
                "baseline subset definition can be content-bound and enforced"
            )
        state = state_store.load_current()
        assert state is not None
        if state["pending_changesets"]:
            raise LinzStateError(
                "apply or explicitly resolve the pending changeset before capturing another"
            )
        from_revision = state["current_revision"]
        _validate_revision_interval(from_revision, to_revision)
        service_url = linz_service_url(api_key)
        archive = self.archiver.archive_feature_type(
            source_id=state["source_id"],
            endpoint_id=f"{state['endpoint_id']}:changeset:{state['sequence'] + 1:08d}",
            service_url=service_url,
            type_name=state["changeset_type_name"],
            page_size=page_size,
            sort_by=f"{state['primary_key']} A",
            id_property=state["primary_key"],
            srs_name=srs_name,
            cql_filter=cql_filter,
            request_params={"viewparams": f"from:{from_revision};to:{to_revision}"},
            redact_values=(api_key,),
        )
        reference = _capture_set_reference(
            archive, capture_root=self.archiver.capture_client.store.root
        )
        pending = {
            **reference,
            "from_revision": from_revision,
            "to_revision": to_revision,
            "captured_at": archive.capabilities_capture.retrieved_at,
            "status": "captured",
        }
        next_state = {
            **state,
            "sequence": state["sequence"] + 1,
            "parent_state_sha256": state["state_sha256"],
            "created_at": archive.capabilities_capture.retrieved_at,
            "pending_changesets": [pending],
            "state_sha256": "",
        }
        # Deliberately do not update current_revision here.  The checkpoint
        # advances only after a verified application receipt exists.
        return LinzCaptureTransition(archive, state_store.write_state(next_state))

    @staticmethod
    def advance_checkpoint(
        *,
        state_store: LinzStateStore,
        receipt_path: str | Path,
        target_database: str | Path,
    ) -> LinzStateWrite:
        state = state_store.load_current()
        assert state is not None
        pending = state["pending_changesets"]
        if len(pending) != 1:
            raise LinzStateError("exactly one captured changeset is required to advance")
        receipt_file = Path(receipt_path).resolve()
        receipt = _load_hashed_json(receipt_file, hash_field="receipt_sha256")
        change = pending[0]
        expected_pairs = {
            "source_id": state["source_id"],
            "layer_id": state["layer_id"],
            "primary_key": state["primary_key"],
            "from_revision": change["from_revision"],
            "to_revision": change["to_revision"],
            "capture_set_id": change["capture_set_id"],
            "capture_set_manifest_sha256": change["manifest_sha256"],
        }
        for key, expected in expected_pairs.items():
            if receipt.get(key) != expected:
                raise LinzStateError(f"application receipt {key} does not match pending changeset")
        database = Path(target_database).resolve()
        journal_receipt = _journal_receipt(database, str(receipt["application_id"]))
        if journal_receipt != receipt:
            raise LinzStateError(
                "external application receipt does not match the transaction journal"
            )
        _verify_receipt_matches_database(receipt, database, primary_key=str(state["primary_key"]))

        applications_root = state_store.layer_root / "applications"
        applications_root.mkdir(parents=True, exist_ok=True)
        archived_receipt = applications_root / f"{receipt['receipt_sha256']}.json"
        receipt_bytes = receipt_file.read_bytes()
        if archived_receipt.exists():
            if archived_receipt.read_bytes() != receipt_bytes:
                raise LinzStateError("immutable application receipt path contains different bytes")
        else:
            _atomic_write(archived_receipt, receipt_bytes)

        applied = {
            **change,
            "status": "applied",
            "applied_at": receipt["applied_at"],
            "application_receipt_path": archived_receipt.relative_to(
                state_store.layer_root
            ).as_posix(),
            "application_receipt_sha256": receipt["receipt_sha256"],
        }
        next_state = {
            **state,
            "sequence": state["sequence"] + 1,
            "parent_state_sha256": state["state_sha256"],
            "created_at": receipt["applied_at"],
            "current_revision": change["to_revision"],
            "pending_changesets": [],
            "applied_changesets": [*state["applied_changesets"], applied],
            "state_sha256": "",
        }
        return state_store.write_state(next_state)


def _quote_identifier(value: str) -> str:
    if not value or "\x00" in value:
        raise LinzStateError("SQL identifier is empty or contains NUL")
    return '"' + value.replace('"', '""') + '"'


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if value != value or value in {float("inf"), float("-inf")}:
            raise LinzStateError("non-finite values cannot be semantically hashed")
        return value
    if isinstance(value, (bytes, bytearray, memoryview)):
        return {"$binary_hex": bytes(value).hex()}
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in sorted(value.items())}
    if isinstance(value, Iterable):
        return [_json_safe(item) for item in value]
    return str(value)


def _table_columns(connection: duckdb.DuckDBPyConnection, table_name: str) -> list[str]:
    rows = connection.execute(f"PRAGMA table_info({_quote_identifier(table_name)})").fetchall()
    if not rows:
        raise LinzStateError(f"target table does not exist: {table_name}")
    return [str(row[1]) for row in rows]


def _semantic_digest_connection(
    connection: duckdb.DuckDBPyConnection, *, table_name: str, primary_key: str
) -> tuple[str, int]:
    columns = sorted(_table_columns(connection, table_name))
    if primary_key not in columns:
        raise LinzStateError(f"primary key column is missing from target table: {primary_key}")
    quoted_columns = ", ".join(_quote_identifier(item) for item in columns)
    query = (
        f"SELECT {quoted_columns} FROM {_quote_identifier(table_name)} "  # nosec B608
        f"ORDER BY {_quote_identifier(primary_key)}"
    )
    hasher = hashlib.sha256()
    hasher.update(canonical_json_bytes({"columns": columns, "primary_key": primary_key}))
    count = 0
    reader = connection.execute(query).to_arrow_reader(65_536)
    for batch in reader:
        data = batch.to_pydict()
        for offset in range(batch.num_rows):
            row = {column: _json_safe(data[column][offset]) for column in columns}
            encoded = canonical_json_bytes(row)
            hasher.update(len(encoded).to_bytes(8, byteorder="big"))
            hasher.update(encoded)
            count += 1
    return hasher.hexdigest(), count


def semantic_table_digest(
    database_path: str | Path, *, table_name: str = "features", primary_key: str
) -> tuple[str, int]:
    """Hash table semantics in primary-key order, independent of DuckDB file bytes."""

    database = Path(database_path).resolve()
    if not database.is_file():
        raise LinzStateError(f"target DuckDB database does not exist: {database}")
    connection = duckdb.connect(str(database), read_only=True)
    try:
        return _semantic_digest_connection(
            connection, table_name=table_name, primary_key=primary_key
        )
    finally:
        connection.close()


def _scalar_int(
    connection: duckdb.DuckDBPyConnection,
    query: str,
    parameters: list[Any] | None = None,
) -> int:
    row = connection.execute(query, parameters or []).fetchone()
    if row is None:
        raise LinzStateError("scalar SQL query returned no row")
    return int(row[0])


def _application_identity(
    *,
    database: Path,
    table_name: str,
    source_id: str,
    layer_id: int,
    primary_key: str,
    from_revision: str,
    to_revision: str,
    capture_set_id: str,
    capture_set_manifest_sha256: str,
    changeset_parquet_sha256: str,
) -> str:
    identity = {
        "database_path": str(database),
        "table_name": table_name,
        "source_id": source_id,
        "layer_id": layer_id,
        "primary_key": primary_key,
        "from_revision": from_revision,
        "to_revision": to_revision,
        "capture_set_id": capture_set_id,
        "capture_set_manifest_sha256": capture_set_manifest_sha256,
        "changeset_parquet_sha256": changeset_parquet_sha256,
    }
    return f"urn:riopa:linz-application:{sha256_json(identity)}"


def _ensure_application_journal(connection: duckdb.DuckDBPyConnection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS _riopa_linz_applications (
            application_id VARCHAR PRIMARY KEY,
            receipt_json VARCHAR NOT NULL,
            receipt_sha256 VARCHAR NOT NULL
        )
        """
    )


def _load_journal_receipt(
    connection: duckdb.DuckDBPyConnection, application_id: str
) -> dict[str, Any] | None:
    row = connection.execute(
        "SELECT receipt_json, receipt_sha256 FROM _riopa_linz_applications "
        "WHERE application_id = ?",
        [application_id],
    ).fetchone()
    if row is None:
        return None
    try:
        receipt = json.loads(str(row[0]))
    except json.JSONDecodeError as exc:
        raise LinzStateError("LINZ application journal contains invalid JSON") from exc
    if not isinstance(receipt, dict):
        raise LinzStateError("LINZ application journal receipt must be an object")
    expected = sha256_json(receipt, omit_keys={"receipt_sha256"})
    if receipt.get("receipt_sha256") != expected or str(row[1]) != expected:
        raise LinzStateError("LINZ application journal receipt integrity check failed")
    if receipt.get("application_id") != application_id:
        raise LinzStateError("LINZ application journal identity mismatch")
    return receipt


def _write_application_receipt(receipt: Mapping[str, Any], receipt_path: str | Path) -> Path:
    output = Path(receipt_path).resolve()
    _atomic_write(
        output,
        json.dumps(receipt, indent=2, ensure_ascii=False).encode("utf-8") + b"\n",
    )
    return output


def _verify_receipt_matches_database(
    receipt: Mapping[str, Any], database: Path, *, primary_key: str
) -> None:
    if str(database) != receipt.get("database_path"):
        raise LinzStateError("application receipt refers to a different target database")
    current_digest, current_count = semantic_table_digest(
        database, table_name=str(receipt["table_name"]), primary_key=primary_key
    )
    if current_digest != receipt.get("semantic_digest_after"):
        raise LinzStateError("target database no longer matches application receipt")
    if current_count != receipt.get("row_count_after"):
        raise LinzStateError("target database row count no longer matches application receipt")


def _journal_receipt(database: Path, application_id: str) -> dict[str, Any]:
    connection = duckdb.connect(str(database), read_only=True)
    try:
        tables = {str(row[0]) for row in connection.execute("SHOW TABLES").fetchall()}
        if "_riopa_linz_applications" not in tables:
            raise LinzStateError("target database has no LINZ application journal")
        receipt = _load_journal_receipt(connection, application_id)
        if receipt is None:
            raise LinzStateError("target database journal has no matching LINZ application")
        return receipt
    finally:
        connection.close()


def apply_linz_changeset(
    *,
    target_database: str | Path,
    changeset_parquet: str | Path,
    source_id: str,
    layer_id: int,
    primary_key: str,
    from_revision: str,
    to_revision: str,
    capture_set_id: str,
    capture_set_manifest_sha256: str,
    receipt_path: str | Path,
    table_name: str = "features",
    applied_at: str | None = None,
) -> LinzApplication:
    """Apply one complete LINZ changeset atomically and recoverably.

    The data mutation and a complete, content-bound receipt are committed to a
    journal table in the same DuckDB transaction.  If the process stops after
    the database commit but before the external receipt is written, rerunning
    this function reconstructs the receipt without replaying the changeset.
    """

    _validate_revision_interval(from_revision, to_revision)
    database = Path(target_database).resolve()
    changeset = Path(changeset_parquet).resolve()
    if not database.is_file():
        raise LinzStateError(f"target DuckDB database does not exist: {database}")
    if not changeset.is_file():
        raise LinzStateError(f"changeset GeoParquet does not exist: {changeset}")
    timestamp = applied_at or datetime.now(UTC).isoformat().replace("+00:00", "Z")
    _parse_revision(timestamp)
    changeset_sha256 = sha256_file(changeset)
    application_id = _application_identity(
        database=database,
        table_name=table_name,
        source_id=source_id,
        layer_id=layer_id,
        primary_key=primary_key,
        from_revision=from_revision,
        to_revision=to_revision,
        capture_set_id=capture_set_id,
        capture_set_manifest_sha256=capture_set_manifest_sha256,
        changeset_parquet_sha256=changeset_sha256,
    )

    connection = duckdb.connect(str(database))
    receipt: dict[str, Any]
    transaction_open = False
    try:
        connection.execute("BEGIN TRANSACTION")
        transaction_open = True
        _ensure_application_journal(connection)
        existing = _load_journal_receipt(connection, application_id)
        if existing is not None:
            connection.execute("COMMIT")
            transaction_open = False
            receipt = existing
        else:
            before_digest, before_count = _semantic_digest_connection(
                connection, table_name=table_name, primary_key=primary_key
            )
            target_columns = _table_columns(connection, table_name)
            quoted_target = _quote_identifier(table_name)
            connection.execute(
                "CREATE TEMP TABLE _riopa_linz_changes AS SELECT * FROM read_parquet(?)",
                [str(changeset)],
            )
            changeset_columns = _table_columns(connection, "_riopa_linz_changes")
            required = {primary_key, "__change__", *target_columns}
            missing = sorted(required - set(changeset_columns))
            if missing:
                raise LinzStateError(
                    "changeset schema is incompatible with target; missing columns: "
                    + ", ".join(missing)
                )
            pk = _quote_identifier(primary_key)
            action = _quote_identifier("__change__")
            null_keys_query = f"SELECT count(*) FROM _riopa_linz_changes WHERE {pk} IS NULL"  # nosec B608
            null_keys = _scalar_int(connection, null_keys_query)
            if null_keys:
                raise LinzStateError(f"changeset contains {null_keys} null primary keys")
            duplicate_keys_query = (
                f"SELECT count(*) FROM (SELECT {pk} FROM _riopa_linz_changes "  # nosec B608
                f"GROUP BY {pk} HAVING count(*) > 1)"
            )
            duplicate_keys = _scalar_int(connection, duplicate_keys_query)
            if duplicate_keys:
                raise LinzStateError(
                    f"changeset contains {duplicate_keys} duplicated primary-key groups"
                )
            invalid_actions_query = (
                f"SELECT DISTINCT {action} FROM _riopa_linz_changes "  # nosec B608
                f"WHERE {action} IS NULL OR upper({action}) NOT IN ('INSERT','UPDATE','DELETE')"
            )
            invalid_actions = connection.execute(invalid_actions_query).fetchall()
            if invalid_actions:
                raise LinzStateError(f"changeset contains invalid actions: {invalid_actions}")
            normalise_actions_query = f"UPDATE _riopa_linz_changes SET {action}=upper({action})"  # nosec B608
            connection.execute(normalise_actions_query)
            count_query = f"SELECT count(*) FROM _riopa_linz_changes WHERE {action}=?"  # nosec B608
            counts = {item: _scalar_int(connection, count_query, [item]) for item in _ACTIONS}
            insert_conflicts_query = (
                f"SELECT count(*) FROM _riopa_linz_changes c JOIN {quoted_target} t "  # nosec B608
                f"ON c.{pk}=t.{pk} WHERE c.{action}='INSERT'"
            )
            insert_conflicts = _scalar_int(connection, insert_conflicts_query)
            if insert_conflicts:
                raise LinzStateError(
                    f"{insert_conflicts} INSERT actions already exist in the target"
                )
            missing_existing_query = (
                f"SELECT count(*) FROM _riopa_linz_changes c LEFT JOIN {quoted_target} t "  # nosec B608
                f"ON c.{pk}=t.{pk} WHERE c.{action} IN ('UPDATE','DELETE') AND t.{pk} IS NULL"
            )
            missing_existing = _scalar_int(connection, missing_existing_query)
            if missing_existing:
                raise LinzStateError(
                    f"{missing_existing} UPDATE/DELETE actions do not exist in the target"
                )
            delete_query = (
                f"DELETE FROM {quoted_target} USING _riopa_linz_changes c "  # nosec B608
                f"WHERE {quoted_target}.{pk}=c.{pk} AND c.{action} IN ('UPDATE','DELETE')"
            )
            connection.execute(delete_query)
            rendered_columns = ", ".join(_quote_identifier(item) for item in target_columns)
            insert_query = (
                f"INSERT INTO {quoted_target} ({rendered_columns}) "  # nosec B608
                f"SELECT {rendered_columns} FROM _riopa_linz_changes "
                f"WHERE {action} IN ('INSERT','UPDATE')"
            )
            connection.execute(insert_query)
            expected_count = before_count + counts["INSERT"] - counts["DELETE"]
            after_count_query = f"SELECT count(*) FROM {quoted_target}"  # nosec B608
            after_count = _scalar_int(connection, after_count_query)
            if after_count != expected_count:
                raise LinzStateError(
                    f"row-count invariant failed: expected {expected_count}, got {after_count}"
                )
            after_digest, verified_after_count = _semantic_digest_connection(
                connection, table_name=table_name, primary_key=primary_key
            )
            receipt = {
                "schema_version": "1.0.0",
                "record_type": "linz_changeset_application",
                "application_id": application_id,
                "source_id": source_id,
                "layer_id": layer_id,
                "primary_key": primary_key,
                "from_revision": from_revision,
                "to_revision": to_revision,
                "capture_set_id": capture_set_id,
                "capture_set_manifest_sha256": capture_set_manifest_sha256,
                "changeset_parquet_sha256": changeset_sha256,
                "database_path": str(database),
                "table_name": table_name,
                "applied_at": timestamp,
                "counts": counts,
                "row_count_before": before_count,
                "row_count_after": verified_after_count,
                "semantic_digest_before": before_digest,
                "semantic_digest_after": after_digest,
                "receipt_sha256": "",
            }
            receipt["receipt_sha256"] = sha256_json(receipt, omit_keys={"receipt_sha256"})
            connection.execute(
                "INSERT INTO _riopa_linz_applications "
                "(application_id, receipt_json, receipt_sha256) VALUES (?, ?, ?)",
                [
                    application_id,
                    json.dumps(receipt, sort_keys=True, separators=(",", ":")),
                    receipt["receipt_sha256"],
                ],
            )
            connection.execute("COMMIT")
            transaction_open = False
            connection.execute("CHECKPOINT")
    except Exception:
        if transaction_open:
            connection.execute("ROLLBACK")
        raise
    finally:
        connection.close()

    _verify_receipt_matches_database(receipt, database, primary_key=primary_key)
    output = _write_application_receipt(receipt, receipt_path)
    return LinzApplication(receipt, output)
