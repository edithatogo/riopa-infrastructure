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
