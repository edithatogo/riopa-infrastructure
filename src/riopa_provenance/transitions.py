"""Fail-closed planning-system transition and temporal perspective helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date
from typing import Any

from .hashing import sha256_json

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
DISCOVERY_MODES = {"contemporaneous", "retrospective"}
CONFIDENCE_LEVELS = {"unknown", "low", "medium", "high", "disputed"}


def classify_transition_evidence(record: Mapping[str, Any]) -> dict[str, Any]:
    """Keep discovery timing explicit without treating it as legal authority."""

    mode = record.get("discovery_mode")
    if mode not in DISCOVERY_MODES:
        raise ValueError("discovery_mode must be contemporaneous or retrospective")
    evidence = record.get("evidence")
    if (
        not isinstance(evidence, list)
        or not evidence
        or any(not isinstance(item, str) for item in evidence)
    ):
        raise ValueError("evidence must be a non-empty list of references")
    return {
        "discovery_mode": mode,
        "evidence": list(evidence),
        "authority_status": "not-established",
        "promotion_allowed": False,
        "nonclaims": [
            "Discovery timing does not establish legal effect, authority or completeness.",
            (
                "Retrospective evidence is retained separately and is not silently merged "
                "with contemporaneous evidence."
            ),
        ],
    }


def build_continuity_crosswalk(
    *,
    predecessor: str,
    successor: str,
    confidence: str,
    scope: str,
    evidence: Sequence[str],
    valid_time: Mapping[str, Any],
    recorded_time: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a bounded continuity assertion with explicit confidence and scope."""

    if not predecessor or not successor or predecessor == successor:
        raise ValueError("predecessor and successor must be distinct non-empty identifiers")
    if confidence not in CONFIDENCE_LEVELS:
        raise ValueError(f"confidence must be one of {sorted(CONFIDENCE_LEVELS)}")
    if not scope.strip():
        raise ValueError("scope must be non-empty")
    if not evidence or any(not isinstance(item, str) or not item for item in evidence):
        raise ValueError("evidence must be a non-empty sequence of references")
    transition = {
        "transition_id": "urn:riopa:transition:crosswalk",
        "relationship": "partial_continuity",
        "predecessors": [predecessor],
        "successors": [successor],
        "state": "transitional",
        "evidence": list(evidence),
        "scope": scope,
        "valid_time": dict(valid_time),
        "recorded_time": dict(recorded_time),
    }
    errors = validate_transition(transition)
    if errors:
        raise ValueError("invalid continuity window: " + "; ".join(errors))
    return {
        "crosswalk_id": f"urn:riopa:continuity:{predecessor}:{successor}",
        "predecessor": predecessor,
        "successor": successor,
        "relationship": "partial_continuity",
        "confidence": confidence,
        "scope": scope,
        "evidence": list(evidence),
        "valid_time": dict(valid_time),
        "recorded_time": dict(recorded_time),
        "promotion_allowed": False,
    }


def audit_transition_history(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Audit declared late evidence, corrections, supersessions and finite gaps."""

    invalid: list[dict[str, Any]] = []
    late_evidence: list[str] = []
    corrections: list[str] = []
    supersessions: list[str] = []
    windows: dict[str, list[tuple[date, date | None, str]]] = {}
    for record in records:
        transition_id = str(record.get("transition_id", ""))
        errors = validate_transition(record)
        if errors:
            invalid.append({"transition_id": transition_id, "errors": list(errors)})
            continue
        valid_start = date.fromisoformat(str(record["valid_time"]["from"]))
        recorded_start = date.fromisoformat(str(record["recorded_time"]["from"]))
        if recorded_start > valid_start:
            late_evidence.append(transition_id)
        event_type = record.get("event_type")
        if event_type == "correction":
            corrections.append(transition_id)
        if record.get("state") == "superseded" or event_type == "supersession":
            supersessions.append(transition_id)
        end_value = record["valid_time"].get("to")
        end = date.fromisoformat(str(end_value)) if end_value is not None else None
        group = str(record.get("history_group", "default"))
        windows.setdefault(group, []).append((valid_start, end, transition_id))
    gaps: list[dict[str, Any]] = []
    overlaps: list[dict[str, Any]] = []
    for group, entries in windows.items():
        ordered = sorted(entries)
        for previous, current in zip(ordered, ordered[1:], strict=False):
            if previous[1] is not None and current[0] <= previous[1]:
                overlaps.append(
                    {
                        "history_group": group,
                        "from": current[0].isoformat(),
                        "to": previous[1].isoformat(),
                        "first": previous[2],
                        "second": current[2],
                    }
                )
            elif previous[1] is not None and current[0].toordinal() > previous[1].toordinal() + 1:
                gaps.append(
                    {
                        "history_group": group,
                        "from": previous[1].isoformat(),
                        "to": current[0].isoformat(),
                        "before": previous[2],
                        "after": current[2],
                    }
                )
    return {
        "status": "invalid" if invalid else "audited",
        "invalid": invalid,
        "late_evidence": sorted(late_evidence),
        "corrections": sorted(corrections),
        "supersessions": sorted(supersessions),
        "historical_gaps": gaps,
        "overlapping_windows": overlaps,
        "promotion_allowed": False,
        "nonclaims": [
            (
                "The audit reports declared temporal observations; it does not establish legal "
                "effect or source completeness."
            ),
            "A finite gap is not evidence that no source existed during that interval.",
        ],
    }


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


def build_transition_release_packet(
    records: Sequence[Mapping[str, Any]], *, revision: str
) -> dict[str, Any]:
    """Build an immutable, unpublished candidate packet for transition records."""
    if not revision.strip():
        raise ValueError("revision must be non-empty")
    if not records:
        raise ValueError("records must be non-empty")
    normalized = [dict(record) for record in records]
    errors: dict[str, list[str]] = {}
    for record in normalized:
        record_errors = validate_transition(record)
        if record_errors:
            errors[str(record.get("transition_id", ""))] = list(record_errors)
    if errors:
        raise ValueError(f"invalid transition records: {errors}")
    normalized.sort(key=lambda record: str(record["transition_id"]))
    return {
        "record_type": "planning_transition_release_packet",
        "revision": revision,
        "status": "unpublished-candidate",
        "records": normalized,
        "records_sha256": sha256_json(normalized),
        "promotion_allowed": False,
        "nonclaims": [
            (
                "This packet is an immutable candidate and does not establish legal effect "
                "or authority."
            ),
            (
                "Real historical-source completeness, preservation acceptance and release "
                "approval remain open."
            ),
        ],
    }


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
