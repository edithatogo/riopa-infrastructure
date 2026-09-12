"""Lossless experimental views over immutable archived HTTP capture records."""

from __future__ import annotations

import copy
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from riopa_provenance.hashing import canonical_json_bytes, sha256_json


class CaptureMigrationError(ValueError):
    """The input, view or destination cannot be safely migrated."""


def _check_source(source: dict[str, Any]) -> None:
    if not isinstance(source, dict) or set(source) != {"capture_id", "record", "record_sha256"}:
        raise CaptureMigrationError("source requires capture_id, record and record_sha256")
    record = source["record"]
    if not isinstance(record, dict) or record.get("schema_version") != "1.0.0":
        raise CaptureMigrationError("only archived capture schema 1.0.0 is supported")
    if (
        record.get("record_type") != "archived_http_capture"
        or not isinstance(record.get("source_id"), str)
        or not record["source_id"].strip()
    ):
        raise CaptureMigrationError("source must identify an archived HTTP capture")
    digest = sha256_json(record)
    if (
        source["record_sha256"] != digest
        or source["capture_id"] != f"urn:riopa:capture:sha256:{digest}"
    ):
        raise CaptureMigrationError("source digest or capture identity mismatch")


def _check_facets(facets: dict[str, Any]) -> None:
    if not isinstance(facets, dict) or set(facets) - {"quality", "source_rights"}:
        raise CaptureMigrationError("unsupported evidence facet")
    for references in facets.values():
        if not isinstance(references, list) or not references:
            raise CaptureMigrationError("evidence facets require nonempty reference lists")
        for ref in references:
            if not isinstance(ref, dict) or set(ref) != {"uri", "sha256"}:
                raise CaptureMigrationError("evidence reference requires uri and sha256")
            if not isinstance(ref["uri"], str) or not ref["uri"].strip():
                raise CaptureMigrationError("evidence URI must be nonempty")
            digest = ref["sha256"]
            if (
                not isinstance(digest, str)
                or len(digest) != 64
                or any(char not in "0123456789abcdef" for char in digest)
            ):
                raise CaptureMigrationError("evidence digest must be lowercase SHA-256")


def migrate_capture(
    source: dict[str, Any], *, facets: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Create a derived 1.1 view; never rewrite a native record or confer rights."""
    _check_source(source)
    evidence = {} if facets is None else facets
    _check_facets(evidence)
    view = {
        "schema_version": "1.1.0",
        "record_type": "archived_capture_view",
        "source": copy.deepcopy(source),
        "facets": copy.deepcopy(evidence),
    }
    return {**view, "view_sha256": sha256_json(view)}


def recover_capture(view: dict[str, Any]) -> dict[str, Any]:
    """Verify a view and return the original native record with its identity."""
    if set(view) != {"schema_version", "record_type", "source", "facets", "view_sha256"}:
        raise CaptureMigrationError("invalid view fields")
    if view["schema_version"] != "1.1.0" or view["record_type"] != "archived_capture_view":
        raise CaptureMigrationError("unsupported view version or type")
    if not isinstance(view["source"], dict) or not isinstance(view["facets"], dict):
        raise CaptureMigrationError("source and facets must be objects")
    _check_source(view["source"])
    _check_facets(view["facets"])
    if view["view_sha256"] != sha256_json(view, omit_keys={"view_sha256"}):
        raise CaptureMigrationError("view digest mismatch")
    return copy.deepcopy(view["source"])


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CaptureMigrationError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def migrate_capture_jsonl(source_path: Path, destination: Path) -> int:
    """Validate a complete batch, then create an immutable destination atomically.

    Existing equal bytes are an idempotent retry; conflicting bytes are never
    replaced. Recovery leaves the source file intact, including its formatting.
    """
    if source_path.resolve() == destination.resolve():
        raise CaptureMigrationError("source and destination must differ")
    rows = []
    for line in source_path.read_text(encoding="utf-8").splitlines():
        source = json.loads(line, object_pairs_hook=_unique_object)
        if not isinstance(source, dict):
            raise CaptureMigrationError("capture row must be an object")
        rows.append(canonical_json_bytes(migrate_capture(source)) + b"\n")
    if not rows:
        raise CaptureMigrationError("source batch is empty")
    payload = b"".join(rows)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, destination)
        except FileExistsError:
            if destination.read_bytes() != payload:
                raise CaptureMigrationError("destination conflicts with migrated bytes") from None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return len(rows)
