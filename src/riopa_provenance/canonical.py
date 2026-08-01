"""Conservative helpers for canonical identity and crosswalk records.

These helpers intentionally do not assert semantic equivalence.  They provide
stable, content-addressed identifiers while retaining the source assertion and
the method/reviewer metadata required for later adjudication.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import date
from typing import Any

from .hashing import sha256_json

_URN_PART = re.compile(r"[^A-Za-z0-9._~-]+")


def _part(value: str) -> str:
    value = _URN_PART.sub("-", str(value).strip()).strip("-")
    if not value:
        raise ValueError("identifier parts must not be empty")
    return value


def canonical_entity_id(namespace: str, source_id: str) -> str:
    """Build a stable identity URN independent of mutable labels or geometry."""

    return f"urn:riopa:entity:{_part(namespace)}:{_part(source_id)}"


def canonical_version_id(entity_id: str, *, valid_from: str, valid_to: str | None,
                         representation: Mapping[str, Any]) -> str:
    """Build a deterministic version identifier from temporal and content state."""

    if not entity_id.startswith("urn:riopa:entity:"):
        raise ValueError("entity_id must be a canonical RIOPA entity URN")
    state = {"valid_from": valid_from, "valid_to": valid_to, "representation": representation}
    return f"{entity_id}:version:{sha256_json(state)[:24]}"


def build_crosswalk(*, source_id: str, source_label: str, canonical_id: str,
                    method: str, confidence: str, reviewer: str,
                    valid_from: str, valid_to: str | None = None,
                    evidence: list[str] | None = None) -> dict[str, Any]:
    """Create a versioned mapping claim without discarding the original value."""

    allowed = {"unknown", "low", "medium", "high", "disputed", "inapplicable"}
    if confidence not in allowed:
        raise ValueError(f"confidence must be one of {sorted(allowed)}")
    mapping_key = {"source_id": source_id, "canonical_id": canonical_id, "valid_from": valid_from}
    return {
        "mapping_id": f"urn:riopa:mapping:{sha256_json(mapping_key)[:24]}",
        "source_assertion": {"source_id": source_id, "label": source_label},
        "canonical_id": canonical_id,
        "method": method,
        "confidence": confidence,
        "reviewer": reviewer,
        "valid_time": {"from": valid_from, "to": valid_to},
        "evidence": evidence or [],
    }


def validate_crosswalk_semantics(record: Mapping[str, Any]) -> tuple[str, ...]:
    """Apply fail-closed semantic checks not expressible in JSON Schema alone."""
    errors: list[str] = []
    valid_time = record.get("valid_time")
    if not isinstance(valid_time, Mapping):
        return ("valid_time must be an object",)
    try:
        start = date.fromisoformat(str(valid_time.get("from")))
        end_value = valid_time.get("to")
        end = date.fromisoformat(str(end_value)) if end_value is not None else None
        if end is not None and end < start:
            errors.append("valid_time.to must not precede valid_time.from")
    except ValueError:
        errors.append("valid_time values must be ISO dates")
    uncertain = {"disputed", "unknown", "inapplicable"}
    if record.get("confidence") in uncertain and not record.get("evidence"):
        errors.append("uncertain mappings require at least one evidence reference")
    return tuple(errors)


def validate_crosswalk_contract(record: Mapping[str, Any]) -> tuple[str, ...]:
    """Fail-closed structural and semantic validation for crosswalk claims."""
    required = {
        "mapping_id", "source_assertion", "canonical_id", "method",
        "confidence", "reviewer", "valid_time", "evidence",
    }
    errors = [f"missing required field: {key}" for key in sorted(required - record.keys())]
    if not isinstance(record.get("mapping_id"), str) or not str(
        record.get("mapping_id", "")
    ).startswith("urn:riopa:mapping:"):
        errors.append("mapping_id must be a canonical mapping URN")
    assertion = record.get("source_assertion")
    if (
        not isinstance(assertion, Mapping)
        or not assertion.get("source_id")
        or not assertion.get("label")
    ):
        errors.append("source_assertion requires source_id and label")
    if not isinstance(record.get("evidence"), list):
        errors.append("evidence must be an array")
    errors.extend(validate_crosswalk_semantics(record))
    return tuple(dict.fromkeys(errors))


def validate_conformance_manifest(
    manifest: Mapping[str, Any], *, root: str | None = None
) -> tuple[str, ...]:
    """Validate conformance references and prevent premature status promotion."""
    from pathlib import Path
    import hashlib

    errors: list[str] = []
    if manifest.get("status") != "bounded-pending":
        errors.append("conformance manifest must remain bounded-pending")
    publication = manifest.get("publication", {})
    if (
        publication.get("status") != "unpublished"
        or publication.get("persistent_identifier") is not None
    ):
        errors.append("unpublished manifest must not contain a persistent identifier")
    checks = manifest.get("checks", {})
    for name in ("shacl", "cross_language_round_trip"):
        if checks.get(name, {}).get("status") != "not-run":
            errors.append(f"{name} cannot be promoted without external evidence")
    base = Path(root or ".")
    artifacts = manifest.get("artifacts", [])
    if not isinstance(artifacts, list) or any(
        not isinstance(item, str) or not item or item.startswith("/") or ".." in Path(item).parts
        for item in artifacts
    ):
        errors.append("artifacts must contain safe repository-relative paths")
        artifacts = artifacts if isinstance(artifacts, list) else []
    digests = manifest.get("artifact_sha256", {})
    if not isinstance(digests, Mapping):
        errors.append("artifact_sha256 must be an object")
        digests = {}
    if set(digests) != set(artifacts):
        errors.append("artifact_sha256 keys must exactly match artifacts")
    for artifact in artifacts:
        path = base / artifact
        if not path.is_file():
            errors.append(f"missing conformance artifact: {artifact}")
            continue
        expected = digests.get(artifact)
        if not isinstance(expected, str) or len(expected) != 64:
            errors.append(f"invalid SHA-256 digest for conformance artifact: {artifact}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            errors.append(
                f"conformance artifact digest mismatch for {artifact}: "
                f"expected {expected}, found {actual}"
            )
    return tuple(errors)


def validate_migration_fixture(migration: Mapping[str, Any]) -> tuple[str, ...]:
    """Validate the bounded, declarative shape of a schema migration fixture.

    This deliberately does not claim that the transformation has been run against
    real data; it only prevents malformed or ambiguous migration metadata from
    entering the conformance inventory.
    """
    import re

    errors: list[str] = []
    for key in ("migration_id", "from_version", "to_version", "compatibility", "notes"):
        if not isinstance(migration.get(key), str) or not migration[key].strip():
            errors.append(f"migration {key} must be a non-empty string")
    if not isinstance(migration.get("automated"), bool):
        errors.append("migration automated must be boolean")
    version_pattern = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
    versions = (migration.get("from_version"), migration.get("to_version"))
    if all(isinstance(version, str) for version in versions):
        for field, version in zip(("from_version", "to_version"), versions):
            if not version_pattern.fullmatch(version):
                errors.append(f"migration {field} must use semantic version form X.Y.Z")
    compatibility = migration.get("compatibility")
    if compatibility not in {"backward-compatible", "breaking", "experimental"}:
        errors.append(
            "migration compatibility must be one of backward-compatible, breaking, experimental"
        )
    changes = migration.get("changes")
    if not isinstance(changes, list) or not changes:
        errors.append("migration changes must be a non-empty array")
    else:
        for index, change in enumerate(changes):
            if not isinstance(change, Mapping):
                errors.append(f"migration change {index} must be an object")
                continue
            for key in ("path", "kind", "rule"):
                if not isinstance(change.get(key), str) or not change[key].strip():
                    errors.append(f"migration change {index} {key} must be a non-empty string")
            path = change.get("path")
            if isinstance(path, str) and (
                not path.startswith("/") or ".." in path.split("/")
            ):
                errors.append(f"migration change {index} path must be a safe JSON Pointer")
    if isinstance(migration.get("from_version"), str) and isinstance(migration.get("to_version"), str):
        if migration["from_version"] == migration["to_version"]:
            errors.append("migration from_version and to_version must differ")
    return tuple(errors)
