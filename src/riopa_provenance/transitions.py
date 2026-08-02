"""Fail-closed planning-system transition and temporal perspective helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date
from typing import Any

TRANSITION_STATES = {
    "proposed",
    "notified",
    "operative",
    "partly_operative",
    "appealed",
    "superseded",
    "transitional",
}
TRANSITION_RELATIONSHIPS = {"rename", "merge", "split", "replacement", "partial_continuity"}
PERSPECTIVES = {"valid_time", "recorded_time", "as_known_at"}


def validate_transition(record: Mapping[str, Any]) -> tuple[str, ...]:
    """Return contract errors; unknown dates, states and identities fail closed."""
    errors: list[str] = []
    required = {"transition_id", "relationship", "predecessors", "successors", "state", "evidence"}
    errors.extend(f"missing required field: {key}" for key in sorted(required - record.keys()))
    if not isinstance(record.get("transition_id"), str) or not str(
        record.get("transition_id", "")
    ).startswith("urn:riopa:transition:"):
        errors.append("transition_id must be a transition URN")
    if record.get("relationship") not in TRANSITION_RELATIONSHIPS:
        errors.append("relationship must be a supported transition relationship")
    for field in ("predecessors", "successors", "evidence"):
        value = record.get(field)
        if (
            not isinstance(value, list)
            or not value
            or any(not isinstance(item, str) or not item for item in value)
        ):
            errors.append(f"{field} must be a non-empty array of strings")
    if record.get("state") not in TRANSITION_STATES:
        errors.append("state must be a supported planning state")
    for field in ("valid_time", "recorded_time"):
        value = record.get(field)
        if not isinstance(value, Mapping) or "from" not in value:
            errors.append(f"{field} must include an ISO date from value")
            continue
        try:
            start = date.fromisoformat(str(value["from"]))
            end = value.get("to")
            if end is not None and date.fromisoformat(str(end)) < start:
                errors.append(f"{field}.to must not precede {field}.from")
        except ValueError:
            errors.append(f"{field} values must be ISO dates")
    if record.get("relationship") == "partial_continuity" and not record.get("scope"):
        errors.append("partial_continuity requires an explicit scope")
    return tuple(dict.fromkeys(errors))


def select_temporal_records(
    records: Sequence[Mapping[str, Any]], *, perspective: str, at: str
) -> list[Mapping[str, Any]]:
    """Select records visible at a date under one explicit temporal perspective."""
    if perspective not in PERSPECTIVES:
        raise ValueError(f"perspective must be one of {sorted(PERSPECTIVES)}")
    point = date.fromisoformat(at)
    selected: list[Mapping[str, Any]] = []
    for record in records:
        if validate_transition(record):
            continue
        field = "valid_time" if perspective == "valid_time" else "recorded_time"
        if perspective == "as_known_at":
            field = "recorded_time"
        window = record[field]
        start = date.fromisoformat(str(window["from"]))
        end = window.get("to")
        if start <= point and (end is None or point <= date.fromisoformat(str(end))):
            selected.append(record)
    return selected
