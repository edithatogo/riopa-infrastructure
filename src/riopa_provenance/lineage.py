"""Queryable provenance and rebuild-impact index.

The SQLite projection is derived from a validated RIOPA snapshot.  It is not a
replacement for the signed/event provenance records; it is a disposable query
index that can always be rebuilt from them.
"""

from __future__ import annotations

import json
import sqlite3
from collections import OrderedDict
from collections.abc import Iterable, Mapping
from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

from .hashing import sha256_file
from .validation import (
    load_json,
    manifest_reference_specs,
    resolve_local_reference,
    validate_manifest_closure,
)


class LineageError(ValueError):
    """Raised when a lineage index cannot be built or queried safely."""


@dataclass(frozen=True)
class LineageNode:
    node_id: str
    node_type: str
    label: str | None
    record_path: str | None


@dataclass(frozen=True)
class LineageEdge:
    source_id: str
    target_id: str
    relation: str
    record_path: str | None


class QueryCache:
    """Bounded in-process cache keyed by a logical projection fingerprint."""

    def __init__(self, max_entries: int = 128) -> None:
        if max_entries < 1:
            raise LineageError("max_entries must be positive")
        self.max_entries = max_entries
        self._items: OrderedDict[tuple[str, str, str, int], dict[str, Any]] = OrderedDict()

    def get(self, key: tuple[str, str, str, int]) -> dict[str, Any] | None:
        value = self._items.get(key)
        if value is None:
            return None
        self._items.move_to_end(key)
        return deepcopy(value)

    def put(self, key: tuple[str, str, str, int], value: dict[str, Any]) -> None:
        self._items[key] = deepcopy(value)
        self._items.move_to_end(key)
        while len(self._items) > self.max_entries:
            self._items.popitem(last=False)

    @property
    def size(self) -> int:
        return len(self._items)


@dataclass(frozen=True)
class LineageQuery:
    """Transport-neutral request shared by local lineage clients.

    This is a serialisable request contract only.  It carries no endpoint,
    credentials or remote-authority semantics; a client remains responsible
    for executing it against a validated local projection.
    """

    node_id: str
    question: str
    max_depth: int = 20

    def __post_init__(self) -> None:
        if not self.node_id.strip():
            raise LineageError("node_id must not be empty")
        if self.question not in {"where", "why", "how"}:
            raise LineageError("question must be one of: where, why, how")
        if self.max_depth < 1 or self.max_depth > 100:
            raise LineageError("max_depth must be between 1 and 100")

    def to_payload(self) -> dict[str, object]:
        """Return a stable JSON-compatible request payload."""

        return {
            "contract_version": "1.0.0",
            "node_id": self.node_id,
            "question": self.question,
            "max_depth": self.max_depth,
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> LineageQuery:
        """Parse a request and reject unknown or malformed contract fields."""

        if payload.get("contract_version") != "1.0.0":
            raise LineageError("unsupported lineage query contract version")
        expected = {"contract_version", "node_id", "question", "max_depth"}
        if set(payload) != expected:
            raise LineageError("lineage query fields must match the 1.0.0 contract")
        node_id = payload["node_id"]
        question = payload["question"]
        max_depth = payload["max_depth"]
        if not isinstance(node_id, str) or not isinstance(question, str):
            raise LineageError("node_id and question must be strings")
        if not isinstance(max_depth, int) or isinstance(max_depth, bool):
            raise LineageError("max_depth must be an integer")
        return cls(node_id=node_id, question=question, max_depth=max_depth)


_ID_KEYS = (
    "event_id",
    "run_id",
    "materialization_id",
    "report_id",
    "inventory_id",
    "methods_facts_id",
    "link_id",
    "registry_id",
    "publication_id",
    "artifact_id",
    "source_id",
    "mapping_id",
    "version_id",
)

_LABEL_KEYS = ("title", "name", "logical_id", "description")

_SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS manifests (
    manifest_id TEXT PRIMARY KEY,
    manifest_path TEXT NOT NULL,
    manifest_sha256 TEXT NOT NULL,
    snapshot_id TEXT NOT NULL,
    dataset_id TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS nodes (
    node_id TEXT PRIMARY KEY,
    node_type TEXT NOT NULL,
    label TEXT,
    record_path TEXT,
    metadata_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS edges (
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    relation TEXT NOT NULL,
    record_path TEXT,
    manifest_id TEXT NOT NULL,
    PRIMARY KEY (source_id, target_id, relation, manifest_id),
    FOREIGN KEY (manifest_id) REFERENCES manifests(manifest_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id);
CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id);
CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(node_type);
"""


def _identifier(record: Mapping[str, Any]) -> str | None:
    for key in _ID_KEYS:
        value = record.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _label(record: Mapping[str, Any]) -> str | None:
    for key in _LABEL_KEYS:
        value = record.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _role_node_type(role: str, record: Mapping[str, Any]) -> str:
    if role == "domain_record":
        record_type = record.get("record_type")
        return str(record_type) if record_type else "domain_record"
    return role


def _normalise_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class LineageIndex:
    """A reproducible SQLite projection of validated RIOPA provenance."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).resolve()
        self._query_cache = QueryCache()

    def _connect(self, *, read_only: bool = False) -> sqlite3.Connection:
        if read_only:
            uri = f"file:{self.path.as_posix()}?mode=ro"
            connection = sqlite3.connect(uri, uri=True)
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def export_duckdb(self, target: str | Path) -> dict[str, Any]:
        """Export the current SQLite projection to a deterministic DuckDB index.

        The DuckDB file is a disposable query projection: authoritative
        manifests and their digests remain the source of truth. Existing
        lineage tables in the target are replaced, while unrelated tables are
        left untouched.
        """

        target_path = Path(target).resolve()
        if target_path == self.path:
            raise LineageError("DuckDB target must differ from the SQLite projection")
        try:
            import duckdb
        except ModuleNotFoundError as exc:
            raise LineageError("DuckDB export requires the optional duckdb dependency") from exc
        source = self._connect(read_only=True)
        try:
            manifests = [
                tuple(row) for row in source.execute("SELECT * FROM manifests ORDER BY manifest_id")
            ]
            nodes = [tuple(row) for row in source.execute("SELECT * FROM nodes ORDER BY node_id")]
            edges = [
                tuple(row)
                for row in source.execute(
                    "SELECT * FROM edges ORDER BY manifest_id, source_id, target_id, relation"
                )
            ]
        finally:
            source.close()

        target_path.parent.mkdir(parents=True, exist_ok=True)
        connection = duckdb.connect(str(target_path))
        try:
            connection.execute("DROP TABLE IF EXISTS edges")
            connection.execute("DROP TABLE IF EXISTS nodes")
            connection.execute("DROP TABLE IF EXISTS manifests")
            connection.execute(
                """
                CREATE TABLE manifests (
                    manifest_id VARCHAR PRIMARY KEY,
                    manifest_path VARCHAR NOT NULL,
                    manifest_sha256 VARCHAR NOT NULL,
                    snapshot_id VARCHAR NOT NULL,
                    dataset_id VARCHAR NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE nodes (
                    node_id VARCHAR PRIMARY KEY,
                    node_type VARCHAR NOT NULL,
                    label VARCHAR,
                    record_path VARCHAR,
                    metadata_json VARCHAR NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE edges (
                    source_id VARCHAR NOT NULL,
                    target_id VARCHAR NOT NULL,
                    relation VARCHAR NOT NULL,
                    record_path VARCHAR,
                    manifest_id VARCHAR NOT NULL
                )
                """
            )
            if manifests:
                connection.executemany("INSERT INTO manifests VALUES (?, ?, ?, ?, ?)", manifests)
            if nodes:
                connection.executemany("INSERT INTO nodes VALUES (?, ?, ?, ?, ?)", nodes)
            if edges:
                connection.executemany("INSERT INTO edges VALUES (?, ?, ?, ?, ?)", edges)
            connection.execute("CREATE INDEX idx_edges_source ON edges(source_id)")
            connection.execute("CREATE INDEX idx_edges_target ON edges(target_id)")
            connection.execute("CREATE INDEX idx_nodes_type ON nodes(node_type)")
        finally:
            connection.close()
        return {
            "target": str(target_path),
            "manifests": len(manifests),
            "nodes": len(nodes),
            "edges": len(edges),
            "sha256": sha256_file(target_path),
            "source_projection_sha256": sha256_file(self.path),
            "projection_fingerprint": self.projection_fingerprint(),
        }

    @staticmethod
    def _put_node(
        connection: sqlite3.Connection,
        node_id: str,
        node_type: str,
        *,
        label: str | None = None,
        record_path: str | None = None,
        metadata: Any | None = None,
    ) -> None:
        existing = connection.execute(
            "SELECT node_type, label, record_path, metadata_json FROM nodes WHERE node_id = ?",
            (node_id,),
        ).fetchone()
        payload = _normalise_json(metadata if metadata is not None else {})
        if existing is not None:
            # A concrete record is allowed to enrich an earlier external stub,
            # but conflicting concrete identities are rejected.
            if (
                existing["node_type"] != "external"
                and node_type != "external"
                and existing["node_type"] != node_type
            ):
                raise LineageError(
                    f"node {node_id} has conflicting types {existing['node_type']} and {node_type}"
                )
            node_type = node_type if node_type != "external" else existing["node_type"]
            label = label or existing["label"]
            record_path = record_path or existing["record_path"]
            payload = payload if metadata is not None else existing["metadata_json"]
        connection.execute(
            """
            INSERT INTO nodes(node_id, node_type, label, record_path, metadata_json)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(node_id) DO UPDATE SET
                node_type = excluded.node_type,
                label = excluded.label,
                record_path = excluded.record_path,
                metadata_json = excluded.metadata_json
            """,
            (node_id, node_type, label, record_path, payload),
        )

    @classmethod
    def _put_edge(
        cls,
        connection: sqlite3.Connection,
        source_id: str,
        target_id: str,
        relation: str,
        *,
        record_path: str | None,
        manifest_id: str,
    ) -> None:
        cls._put_node(connection, source_id, "external")
        cls._put_node(connection, target_id, "external")
        connection.execute(
            """
            INSERT OR IGNORE INTO edges(
                source_id, target_id, relation, record_path, manifest_id
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (source_id, target_id, relation, record_path, manifest_id),
        )

    def import_manifest(
        self,
        manifest_path: str | Path,
        *,
        schema_dir: str | Path | None = None,
    ) -> str:
        """Validate and transactionally import one snapshot manifest."""

        manifest_file = Path(manifest_path).resolve()
        validation = validate_manifest_closure(manifest_file, schema_dir=schema_dir)
        if not validation.valid:
            detail = "\n".join(f"- {item}" for item in validation.errors)
            raise LineageError(f"manifest validation failed:\n{detail}")

        manifest = load_json(manifest_file)
        if not isinstance(manifest, Mapping):
            raise LineageError("manifest root must be an object")
        manifest_id = str(manifest["snapshot_id"])
        base = manifest_file.parent
        records: list[tuple[str, str, Mapping[str, Any]]] = []
        for spec in manifest_reference_specs(manifest):
            path = resolve_local_reference(base, spec.reference)
            record = load_json(path)
            if not isinstance(record, Mapping):
                raise LineageError(f"record {spec.reference} is not an object")
            records.append((spec.reference, spec.role, record))

        connection = self._connect()
        try:
            connection.executescript(_SCHEMA)
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("DELETE FROM edges WHERE manifest_id = ?", (manifest_id,))
            connection.execute("DELETE FROM manifests WHERE manifest_id = ?", (manifest_id,))
            connection.execute(
                """
                INSERT INTO manifests(
                    manifest_id, manifest_path, manifest_sha256, snapshot_id, dataset_id
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    manifest_id,
                    str(manifest_file),
                    sha256_file(manifest_file),
                    str(manifest["snapshot_id"]),
                    str(manifest["dataset_id"]),
                ),
            )

            dataset_id = str(manifest["dataset_id"])
            snapshot_id = str(manifest["snapshot_id"])
            self._put_node(
                connection,
                dataset_id,
                "dataset",
                label=str(manifest.get("title") or dataset_id),
                record_path=manifest_file.name,
                metadata={"dataset_id": dataset_id},
            )
            self._put_node(
                connection,
                snapshot_id,
                "snapshot",
                label=str(manifest.get("title") or snapshot_id),
                record_path=manifest_file.name,
                metadata=dict(manifest),
            )
            self._put_edge(
                connection,
                dataset_id,
                snapshot_id,
                "has_snapshot",
                record_path=manifest_file.name,
                manifest_id=manifest_id,
            )

            for reference, role, record in records:
                node_id = _identifier(record)
                if node_id is None:
                    # Some extension records may not expose an identity yet;
                    # retain them by a deterministic local identity.
                    node_id = (
                        f"urn:riopa:record:{sha256_file(resolve_local_reference(base, reference))}"
                    )
                node_type = _role_node_type(role, record)
                self._put_node(
                    connection,
                    node_id,
                    node_type,
                    label=_label(record),
                    record_path=reference,
                    metadata=dict(record),
                )
                self._put_edge(
                    connection,
                    node_id,
                    snapshot_id,
                    "included_in_snapshot",
                    record_path=reference,
                    manifest_id=manifest_id,
                )

            for source_entry in manifest.get("sources", []):
                if not isinstance(source_entry, Mapping):
                    continue
                source_id = source_entry.get("source_id")
                if not isinstance(source_id, str):
                    continue
                for capture_id in source_entry.get("capture_ids", []):
                    if isinstance(capture_id, str):
                        self._put_node(connection, capture_id, "capture")
                        self._put_edge(
                            connection,
                            source_id,
                            capture_id,
                            "captured_as",
                            record_path=manifest_file.name,
                            manifest_id=manifest_id,
                        )

            for reference, role, record in records:
                node_id = _identifier(record)
                if node_id is None:
                    continue
                if role == "artifact":
                    source_id = record.get("source_id")
                    if isinstance(source_id, str):
                        self._put_edge(
                            connection,
                            source_id,
                            node_id,
                            "source_of_artifact",
                            record_path=reference,
                            manifest_id=manifest_id,
                        )
                elif role == "transformation":
                    for input_id in record.get("inputs", []):
                        if isinstance(input_id, str):
                            self._put_edge(
                                connection,
                                input_id,
                                node_id,
                                "used_by_run",
                                record_path=reference,
                                manifest_id=manifest_id,
                            )
                    for output_id in record.get("outputs", []):
                        if isinstance(output_id, str):
                            self._put_edge(
                                connection,
                                node_id,
                                output_id,
                                "generated_by_run",
                                record_path=reference,
                                manifest_id=manifest_id,
                            )
                elif role == "provenance_event":
                    for input_id in record.get("inputs", []):
                        if isinstance(input_id, str):
                            self._put_edge(
                                connection,
                                input_id,
                                node_id,
                                "used_by_event",
                                record_path=reference,
                                manifest_id=manifest_id,
                            )
                    for output_id in record.get("outputs", []):
                        if isinstance(output_id, str):
                            self._put_edge(
                                connection,
                                node_id,
                                output_id,
                                "generated_by_event",
                                record_path=reference,
                                manifest_id=manifest_id,
                            )
                    for parent_id in record.get("causal_parent_event_ids", []):
                        if isinstance(parent_id, str):
                            self._put_edge(
                                connection,
                                parent_id,
                                node_id,
                                "causal_predecessor",
                                record_path=reference,
                                manifest_id=manifest_id,
                            )
                elif role == "materialization":
                    generated_by = record.get("generated_by")
                    artifact_id = record.get("artifact_id")
                    if isinstance(generated_by, str):
                        self._put_edge(
                            connection,
                            generated_by,
                            node_id,
                            "generated_materialization",
                            record_path=reference,
                            manifest_id=manifest_id,
                        )
                    if isinstance(artifact_id, str):
                        self._put_edge(
                            connection,
                            node_id,
                            artifact_id,
                            "describes_artifact",
                            record_path=reference,
                            manifest_id=manifest_id,
                        )

            for relationship in manifest.get("relationships", []):
                if not isinstance(relationship, Mapping):
                    continue
                identifier = relationship.get("identifier")
                relation = relationship.get("relation")
                if isinstance(identifier, str) and isinstance(relation, str):
                    self._put_edge(
                        connection,
                        snapshot_id,
                        identifier,
                        relation,
                        record_path=manifest_file.name,
                        manifest_id=manifest_id,
                    )

            connection.execute(
                """
                DELETE FROM nodes
                WHERE NOT EXISTS (
                    SELECT 1 FROM edges
                    WHERE edges.source_id = nodes.node_id
                       OR edges.target_id = nodes.node_id
                )
                """
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        return manifest_id

    def _walk(self, node_id: str, *, downstream: bool, max_depth: int) -> list[dict[str, Any]]:
        if max_depth < 1 or max_depth > 100:
            raise LineageError("max_depth must be between 1 and 100")
        connection = self._connect(read_only=True)
        try:
            exists = connection.execute(
                "SELECT 1 FROM nodes WHERE node_id = ?", (node_id,)
            ).fetchone()
            if exists is None:
                raise LineageError(f"unknown lineage node: {node_id}")
            downstream_query = """
            WITH RECURSIVE walk(node_id, depth, path) AS (
                SELECT ?, 0, json_array(?)
                UNION ALL
                SELECT e.target_id, walk.depth + 1,
                       json_insert(walk.path, '$[#]', e.target_id)
                FROM walk
                JOIN edges e ON e.source_id = walk.node_id
                WHERE walk.depth < ?
                  AND NOT EXISTS (
                    SELECT 1 FROM json_each(walk.path)
                    WHERE json_each.value = e.target_id
                  )
            )
            SELECT walk.node_id, MIN(walk.depth) AS depth,
                   nodes.node_type, nodes.label, nodes.record_path
            FROM walk JOIN nodes USING(node_id)
            WHERE walk.depth > 0
            GROUP BY walk.node_id, nodes.node_type, nodes.label, nodes.record_path
            ORDER BY depth, walk.node_id
            """
            upstream_query = """
            WITH RECURSIVE walk(node_id, depth, path) AS (
                SELECT ?, 0, json_array(?)
                UNION ALL
                SELECT e.source_id, walk.depth + 1,
                       json_insert(walk.path, '$[#]', e.source_id)
                FROM walk
                JOIN edges e ON e.target_id = walk.node_id
                WHERE walk.depth < ?
                  AND NOT EXISTS (
                    SELECT 1 FROM json_each(walk.path)
                    WHERE json_each.value = e.source_id
                  )
            )
            SELECT walk.node_id, MIN(walk.depth) AS depth,
                   nodes.node_type, nodes.label, nodes.record_path
            FROM walk JOIN nodes USING(node_id)
            WHERE walk.depth > 0
            GROUP BY walk.node_id, nodes.node_type, nodes.label, nodes.record_path
            ORDER BY depth, walk.node_id
            """
            query = downstream_query if downstream else upstream_query
            return [dict(row) for row in connection.execute(query, (node_id, node_id, max_depth))]
        finally:
            connection.close()

    def upstream(self, node_id: str, *, max_depth: int = 20) -> list[dict[str, Any]]:
        return self._walk(node_id, downstream=False, max_depth=max_depth)

    def downstream(self, node_id: str, *, max_depth: int = 20) -> list[dict[str, Any]]:
        return self._walk(node_id, downstream=True, max_depth=max_depth)

    def direct_edges(self, node_id: str) -> list[LineageEdge]:
        connection = self._connect(read_only=True)
        try:
            exists = connection.execute(
                "SELECT 1 FROM nodes WHERE node_id = ?", (node_id,)
            ).fetchone()
            if exists is None:
                raise LineageError(f"unknown lineage node: {node_id}")
            rows = connection.execute(
                """
                SELECT source_id, target_id, relation, record_path
                FROM edges WHERE source_id = ? OR target_id = ?
                ORDER BY CASE relation
                        WHEN 'source_of_artifact' THEN 0
                        WHEN 'included_in_snapshot' THEN 1
                        ELSE 2
                    END,
                    relation, source_id, target_id
                """,
                (node_id, node_id),
            )
            return [LineageEdge(**dict(row)) for row in rows]
        finally:
            connection.close()

    def nodes(self, *, node_type: str | None = None) -> list[LineageNode]:
        connection = self._connect(read_only=True)
        try:
            if node_type is None:
                rows = connection.execute(
                    "SELECT node_id, node_type, label, record_path FROM nodes ORDER BY node_id"
                )
            else:
                rows = connection.execute(
                    """
                    SELECT node_id, node_type, label, record_path
                    FROM nodes WHERE node_type = ? ORDER BY node_id
                    """,
                    (node_type,),
                )
            return [LineageNode(**dict(row)) for row in rows]
        finally:
            connection.close()

    def page_nodes(
        self, *, node_type: str | None = None, limit: int = 100, offset: int = 0
    ) -> dict[str, Any]:
        """Return a bounded, deterministic node page with projection diagnostics."""

        if limit < 1 or limit > 1000:
            raise LineageError("limit must be between 1 and 1000")
        if offset < 0:
            raise LineageError("offset must be non-negative")
        all_nodes = self.nodes(node_type=node_type)
        page = all_nodes[offset : offset + limit]
        next_offset = offset + limit if offset + limit < len(all_nodes) else None
        return {
            "nodes": [node.__dict__ for node in page],
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(all_nodes),
                "next_offset": next_offset,
            },
            "diagnostics": self.projection_metadata(),
            "access_control": "local-filesystem-permissions; no remote authorization asserted",
        }

    def projection_metadata(self) -> dict[str, Any]:
        """Describe the evidence set and granularity represented by this projection."""

        connection = self._connect(read_only=True)
        try:
            manifests = [
                dict(row)
                for row in connection.execute(
                    """
                    SELECT manifest_id, manifest_sha256, snapshot_id, dataset_id
                    FROM manifests ORDER BY manifest_id
                    """
                )
            ]
            node_types = [
                str(row["node_type"])
                for row in connection.execute(
                    "SELECT DISTINCT node_type FROM nodes ORDER BY node_type"
                )
            ]
        finally:
            connection.close()
        granularities = ["dataset"]
        if any(item in {"partition", "feature", "row"} for item in node_types):
            granularities.extend(
                item for item in ("partition", "feature", "row") if item in node_types
            )
        return {
            "authoritative_evidence": manifests,
            "projection_sha256": sha256_file(self.path),
            "freshness": "current-for-listed-authoritative-evidence",
            "lineage_granularities": granularities,
            "granularity_limitation": (
                None
                if any(item in {"feature", "row"} for item in node_types)
                else "feature and row lineage were not captured by the authoritative evidence"
            ),
        }

    def projection_fingerprint(self) -> str:
        """Return a deterministic digest of the logical projection rows.

        SQLite file layout, temporary paths and page allocation are excluded;
        the digest therefore supports rebuild and migration equivalence checks.
        """
        connection = self._connect(read_only=True)
        try:
            payload = {
                "manifests": [
                    list(row)
                    for row in connection.execute("SELECT * FROM manifests ORDER BY manifest_id")
                ],
                "nodes": [
                    list(row) for row in connection.execute("SELECT * FROM nodes ORDER BY node_id")
                ],
                "edges": [
                    list(row)
                    for row in connection.execute(
                        "SELECT * FROM edges ORDER BY manifest_id, source_id, target_id, relation"
                    )
                ],
            }
        finally:
            connection.close()
        return sha256(_normalise_json(payload).encode("utf-8")).hexdigest()

    def export_prov_jsonld(self, target: str | Path) -> dict[str, Any]:
        """Export a deterministic PROV-JSON-LD interoperability projection.

        Native RIOPA records and validated manifests remain authoritative. The
        JSON-LD file is a disposable, standards-shaped projection whose digest
        is bound to the logical SQLite projection fingerprint.
        """
        target_path = Path(target).resolve()
        if target_path == self.path:
            raise LineageError("JSON-LD target must differ from the SQLite projection")
        connection = self._connect(read_only=True)
        try:
            nodes = [
                dict(row)
                for row in connection.execute(
                    "SELECT node_id, node_type, label, record_path FROM nodes ORDER BY node_id"
                )
            ]
            edges = [
                dict(row)
                for row in connection.execute(
                    "SELECT source_id, target_id, relation, record_path, manifest_id "
                    "FROM edges ORDER BY manifest_id, source_id, target_id, relation"
                )
            ]
        finally:
            connection.close()
        graph: list[dict[str, Any]] = []
        for node in nodes:
            item: dict[str, Any] = {
                "@id": node["node_id"],
                "@type": (
                    "prov:Activity"
                    if node["node_type"] in {"run", "transformation", "provenance_event"}
                    else "prov:Entity"
                ),
                "riopa:nodeType": node["node_type"],
            }
            if node["label"] is not None:
                item["rdfs:label"] = node["label"]
            if node["record_path"] is not None:
                item["riopa:recordPath"] = node["record_path"]
            graph.append(item)
        for edge in edges:
            edge_key = _normalise_json(
                [edge["manifest_id"], edge["source_id"], edge["target_id"], edge["relation"]]
            )
            graph.append(
                {
                    "@id": f"urn:riopa:lineage-edge:{sha256(edge_key.encode()).hexdigest()}",
                    "@type": "riopa:LineageRelation",
                    "riopa:source": {"@id": edge["source_id"]},
                    "riopa:target": {"@id": edge["target_id"]},
                    "riopa:relation": edge["relation"],
                    "riopa:manifest": {"@id": edge["manifest_id"]},
                    **(
                        {"riopa:recordPath": edge["record_path"]}
                        if edge["record_path"] is not None
                        else {}
                    ),
                }
            )
        payload = {
            "@context": {
                "prov": "http://www.w3.org/ns/prov#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "riopa": "https://w3id.org/riopa/ontology/",
            },
            "riopa:projectionFingerprint": self.projection_fingerprint(),
            "riopa:authoritativeEvidence": self.projection_metadata()["authoritative_evidence"],
            "riopa:promotionAllowed": False,
            "riopa:nonClaims": [
                "This is an interoperability projection, not authoritative provenance.",
                "The projection does not establish external reproduction, authority "
                "or release approval.",
            ],
            "@graph": graph,
        }
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        )
        return {
            "target": str(target_path),
            "nodes": len(nodes),
            "edges": len(edges),
            "projection_fingerprint": self.projection_fingerprint(),
            "sha256": sha256_file(target_path),
        }

    def query(self, node_id: str, *, question: str, max_depth: int = 20) -> dict[str, Any]:
        """Answer a normative where/why/how query with an explicit evidence envelope."""

        if question == "where":
            answer = self.downstream(node_id, max_depth=max_depth)
        elif question == "why":
            answer = self.upstream(node_id, max_depth=max_depth)
        elif question == "how":
            answer = [
                {
                    "source_id": edge.source_id,
                    "target_id": edge.target_id,
                    "relation": edge.relation,
                    "record_path": edge.record_path,
                }
                for edge in self.direct_edges(node_id)
            ]
        else:
            raise LineageError("question must be one of: where, why, how")
        return {
            "question": question,
            "node_id": node_id,
            "answer": answer,
            "projection": self.projection_metadata(),
        }

    def query_cached(self, node_id: str, *, question: str, max_depth: int = 20) -> dict[str, Any]:
        """Answer a query with bounded cache reuse tied to the logical projection."""

        fingerprint = self.projection_fingerprint()
        key = (fingerprint, node_id, question, max_depth)
        cached = self._query_cache.get(key)
        if cached is not None:
            cached["cache"] = {"hit": True, "projection_fingerprint": fingerprint}
            return cached
        result = self.query(node_id, question=question, max_depth=max_depth)
        self._query_cache.put(key, result)
        result["cache"] = {"hit": False, "projection_fingerprint": fingerprint}
        return result

    def reconcile_projection(self) -> dict[str, Any]:
        """Remove nodes no longer referenced by any authoritative manifest edge."""

        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            stale = [
                str(row["node_id"])
                for row in connection.execute(
                    """
                    SELECT node_id FROM nodes
                    WHERE NOT EXISTS (
                        SELECT 1 FROM edges
                        WHERE edges.source_id = nodes.node_id
                           OR edges.target_id = nodes.node_id
                    )
                    ORDER BY node_id
                    """
                )
            ]
            connection.executemany(
                "DELETE FROM nodes WHERE node_id = ?", ((item,) for item in stale)
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        return {
            "removed_stale_node_ids": stale,
            "removed_count": len(stale),
            "policy": "remove nodes unreferenced by every authoritative manifest edge",
        }

    def rebuild_impact(self, node_ids: Iterable[str], *, max_depth: int = 50) -> dict[str, Any]:
        roots = sorted(set(node_ids))
        impacted: dict[str, dict[str, Any]] = {}
        for root in roots:
            for item in self.downstream(root, max_depth=max_depth):
                current = impacted.get(item["node_id"])
                if current is None or item["depth"] < current["depth"]:
                    impacted[item["node_id"]] = item
        return {
            "roots": roots,
            "impacted": sorted(
                impacted.values(), key=lambda item: (item["depth"], item["node_id"])
            ),
            "projection": self.projection_metadata(),
        }
