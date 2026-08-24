"""Deterministic, non-authoritative reconciliation of facility assertions."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from math import asin, cos, radians, sin, sqrt
from typing import Literal

from .hashing import sha256_json

Authority = Literal["official-reference", "community-reference", "other-reference"]
Disposition = Literal["candidate-match", "source-only", "reviewed-match", "reviewed-distinct"]
HistoryEventType = Literal["opening", "closure", "relocation", "rebrand", "source-disagreement"]
ReleaseClassification = Literal["public", "restricted", "sensitive", "controlled"]


@dataclass(frozen=True)
class FacilityAssertion:
    """One source's assertion; source coordinates remain source-specific evidence."""

    assertion_id: str
    source_id: str
    facility_type: str
    name: str
    latitude: float
    longitude: float
    authority: Authority
    licence: str
    observed_at: str | None = None
    positional_uncertainty_m: float | None = None
    release_classification: ReleaseClassification = "public"

    def __post_init__(self) -> None:
        required = (self.assertion_id, self.source_id, self.facility_type, self.name, self.licence)
        if any(not value.strip() for value in required):
            raise ValueError("assertion identity, type, name and licence must be non-empty")
        if not -90 <= self.latitude <= 90 or not -180 <= self.longitude <= 180:
            raise ValueError("coordinates must be valid WGS84 longitude/latitude")
        if self.positional_uncertainty_m is not None and self.positional_uncertainty_m < 0:
            raise ValueError("positional uncertainty must be non-negative")
        if self.release_classification not in {"public", "restricted", "sensitive", "controlled"}:
            raise ValueError("release classification is unsupported")


@dataclass(frozen=True)
class Reconciliation:
    left_assertion_id: str
    right_assertion_id: str | None
    disposition: Disposition
    distance_m: float | None
    name_similarity: float | None
    method: str = "riopa-name-distance-v1"
    reviewer: str | None = None
    rationale: str | None = None


@dataclass(frozen=True)
class FacilityHistoryEvent:
    """An append-only, source-linked change observation for a facility assertion."""

    event_id: str
    facility_id: str
    event_type: HistoryEventType
    valid_from: str
    recorded_at: str
    source_assertion_ids: tuple[str, ...]
    details: str
    valid_to: str | None = None

    def __post_init__(self) -> None:
        if any(not value.strip() for value in (self.event_id, self.facility_id, self.details)):
            raise ValueError("history identity, facility identity and details must be non-empty")
        if self.event_type not in {
            "opening",
            "closure",
            "relocation",
            "rebrand",
            "source-disagreement",
        }:
            raise ValueError("history event type is unsupported")
        if not self.source_assertion_ids or any(
            not value.strip() for value in self.source_assertion_ids
        ):
            raise ValueError("history events require source assertion identities")
        try:
            start = date.fromisoformat(self.valid_from)
            recorded = date.fromisoformat(self.recorded_at)
            end = date.fromisoformat(self.valid_to) if self.valid_to is not None else None
        except ValueError as exc:
            raise ValueError("history dates must be ISO dates") from exc
        if end is not None and end < start:
            raise ValueError("history valid_to must not precede valid_from")
        if recorded < start:
            raise ValueError("history recorded_at must not precede valid_from")


def history_snapshot(events: tuple[FacilityHistoryEvent, ...]) -> dict[str, object]:
    """Return a deterministic non-authoritative history projection without overwrites."""

    identifiers = [event.event_id for event in events]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("history event IDs must be unique")
    rows = [
        {
            "event_id": event.event_id,
            "facility_id": event.facility_id,
            "event_type": event.event_type,
            "valid_from": event.valid_from,
            "valid_to": event.valid_to,
            "recorded_at": event.recorded_at,
            "source_assertion_ids": list(event.source_assertion_ids),
            "details": event.details,
        }
        for event in sorted(events, key=lambda item: (item.valid_from, item.event_id))
    ]
    return {"record_type": "facility_history", "authoritative": False, "events": rows}


def public_release_snapshot(assertions: tuple[FacilityAssertion, ...]) -> dict[str, object]:
    """Project only public assertions and retain excluded IDs as an audit ledger."""

    public = tuple(item for item in assertions if item.release_classification == "public")
    excluded = sorted(
        item.assertion_id for item in assertions if item.release_classification != "public"
    )
    snapshot = assertions_snapshot(public)
    snapshot["excluded_assertion_ids"] = excluded
    snapshot["release_filter"] = "public-only"
    return snapshot


def assertions_snapshot(assertions: tuple[FacilityAssertion, ...]) -> dict[str, object]:
    """Return a deterministic, non-authoritative registry snapshot.

    The snapshot is deliberately a set of source assertions rather than a
    canonical facility list. Duplicate assertion IDs are rejected so that a
    capture cannot silently overwrite evidence during materialisation.
    """
    identifiers = [item.assertion_id for item in assertions]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("assertion IDs must be unique")
    rows = [
        {
            "assertion_id": item.assertion_id,
            "source_id": item.source_id,
            "facility_type": item.facility_type,
            "name": item.name,
            "latitude": item.latitude,
            "longitude": item.longitude,
            "authority": item.authority,
            "licence": item.licence,
            "observed_at": item.observed_at,
            "positional_uncertainty_m": item.positional_uncertainty_m,
            "release_classification": item.release_classification,
        }
        for item in sorted(assertions, key=lambda value: value.assertion_id)
    ]
    return {"record_type": "facility_assertions", "authoritative": False, "assertions": rows}


def assertions_snapshot_json(assertions: tuple[FacilityAssertion, ...]) -> str:
    """Encode :func:`assertions_snapshot` with stable JSON formatting."""
    return (
        json.dumps(assertions_snapshot(assertions), ensure_ascii=False, sort_keys=True, indent=2)
        + "\n"
    )


def build_snapshot_record(
    assertions: tuple[FacilityAssertion, ...], *, revision: str, supersedes: str | None = None
) -> dict[str, object]:
    """Build a content-addressed, unpublished registry snapshot successor."""

    if not revision.strip():
        raise ValueError("snapshot revision must be non-empty")
    payload = public_release_snapshot(assertions)
    payload_digest = sha256_json(payload)
    return {
        "record_type": "facility_registry_snapshot",
        "revision": revision,
        "payload": payload,
        "payload_sha256": payload_digest,
        "status": "unpublished",
        "supersedes": supersedes,
        "correction_policy": "append-successor-preserve-predecessor",
        "non_claims": [
            "This snapshot is a public-only source assertion projection, not an "
            "authoritative registry.",
            "Corrections create a successor record and never mutate a published predecessor.",
        ],
    }


def validate_snapshot_record(record: Mapping[str, object] | None) -> tuple[str, ...]:
    """Validate snapshot integrity and successor-only correction semantics."""

    if not isinstance(record, Mapping):
        return ("snapshot record must be an object",)
    errors: list[str] = []
    if record.get("record_type") != "facility_registry_snapshot":
        errors.append("record_type is unsupported")
    if not isinstance(record.get("revision"), str) or not str(record["revision"]).strip():
        errors.append("revision is required")
    payload = record.get("payload")
    if not isinstance(payload, Mapping):
        errors.append("payload must be an object")
    else:
        if (
            payload.get("authoritative") is not False
            or payload.get("release_filter") != "public-only"
        ):
            errors.append("payload must remain public-only and non-authoritative")
        digest = record.get("payload_sha256")
        if not isinstance(digest, str) or digest != sha256_json(payload):
            errors.append("payload_sha256 does not match payload")
    if record.get("status") not in {"unpublished", "candidate"}:
        errors.append("status must remain unpublished or candidate")
    if record.get("correction_policy") != "append-successor-preserve-predecessor":
        errors.append("correction policy must preserve predecessors")
    return tuple(dict.fromkeys(errors))


def normalize_name(value: str) -> tuple[str, ...]:
    """Return stable name tokens, treating punctuation and common legal noise alike."""

    tokens = re.findall(r"[a-z0-9]+", value.casefold())
    noise = {"limited", "ltd", "the"}
    return tuple(token for token in tokens if token not in noise)


def name_similarity(left: str, right: str) -> float:
    left_tokens, right_tokens = set(normalize_name(left)), set(normalize_name(right))
    union = left_tokens | right_tokens
    return len(left_tokens & right_tokens) / len(union) if union else 0.0


def distance_m(left: FacilityAssertion, right: FacilityAssertion) -> float:
    """Calculate great-circle distance using a fixed mean Earth radius."""

    lat1, lat2 = radians(left.latitude), radians(right.latitude)
    delta_lat = lat2 - lat1
    delta_lon = radians(right.longitude - left.longitude)
    term = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
    return 6_371_008.8 * 2 * asin(sqrt(term))


def reconcile(
    left: tuple[FacilityAssertion, ...],
    right: tuple[FacilityAssertion, ...],
    *,
    maximum_distance_m: float = 250.0,
    minimum_name_similarity: float = 0.5,
) -> tuple[Reconciliation, ...]:
    """Generate one-to-one candidates without creating an authoritative registry record."""

    if maximum_distance_m < 0 or not 0 <= minimum_name_similarity <= 1:
        raise ValueError("thresholds must be non-negative and similarity must be at most one")
    candidates: list[tuple[float, float, str, str, FacilityAssertion, FacilityAssertion]] = []
    for left_item in left:
        for right_item in right:
            if left_item.facility_type != right_item.facility_type:
                continue
            distance = distance_m(left_item, right_item)
            similarity = name_similarity(left_item.name, right_item.name)
            if distance <= maximum_distance_m and similarity >= minimum_name_similarity:
                candidates.append(
                    (
                        distance,
                        -similarity,
                        left_item.assertion_id,
                        right_item.assertion_id,
                        left_item,
                        right_item,
                    )
                )
    used_left: set[str] = set()
    used_right: set[str] = set()
    results: list[Reconciliation] = []
    for distance, negative_similarity, _, _, left_item, right_item in sorted(candidates):
        if left_item.assertion_id in used_left or right_item.assertion_id in used_right:
            continue
        used_left.add(left_item.assertion_id)
        used_right.add(right_item.assertion_id)
        results.append(
            Reconciliation(
                left_item.assertion_id,
                right_item.assertion_id,
                "candidate-match",
                round(distance, 3),
                -negative_similarity,
            )
        )
    results.extend(
        Reconciliation(item.assertion_id, None, "source-only", None, None)
        for item in left
        if item.assertion_id not in used_left
    )
    results.extend(
        Reconciliation(item.assertion_id, None, "source-only", None, None)
        for item in right
        if item.assertion_id not in used_right
    )
    return tuple(
        sorted(results, key=lambda item: (item.left_assertion_id, item.right_assertion_id or ""))
    )


def apply_review(
    candidate: Reconciliation, *, reviewer: str, same_facility: bool, rationale: str
) -> Reconciliation:
    """Record an accountable human or agent review without changing source assertions."""

    if candidate.disposition != "candidate-match":
        raise ValueError("only candidate matches can be reviewed")
    if not reviewer.strip() or not rationale.strip():
        raise ValueError("reviewer and rationale are required")
    return Reconciliation(
        candidate.left_assertion_id,
        candidate.right_assertion_id,
        "reviewed-match" if same_facility else "reviewed-distinct",
        candidate.distance_m,
        candidate.name_similarity,
        candidate.method,
        reviewer,
        rationale,
    )


def disagreement_coverage_report(
    assertions: tuple[FacilityAssertion, ...],
    reconciliations: tuple[Reconciliation, ...],
) -> dict[str, object]:
    """Build a deterministic, non-authoritative report over supplied assertions."""
    assertion_ids = {item.assertion_id for item in assertions}
    referenced = {
        identifier
        for row in reconciliations
        for identifier in (row.left_assertion_id, row.right_assertion_id)
        if identifier is not None
    }
    unknown = sorted(referenced - assertion_ids)
    if unknown:
        raise ValueError(f"reconciliation references unknown assertions: {unknown}")
    by_source: dict[str, int] = {}
    by_type: dict[str, int] = {}
    for item in assertions:
        by_source[item.source_id] = by_source.get(item.source_id, 0) + 1
        by_type[item.facility_type] = by_type.get(item.facility_type, 0) + 1
    disposition_counts: dict[str, int] = {}
    for row in reconciliations:
        disposition_counts[row.disposition] = disposition_counts.get(row.disposition, 0) + 1
    return {
        "record_type": "facility_disagreement_coverage",
        "authoritative": False,
        "assertion_count": len(assertions),
        "source_counts": dict(sorted(by_source.items())),
        "facility_type_counts": dict(sorted(by_type.items())),
        "reconciliation_counts": dict(sorted(disposition_counts.items())),
        "unmatched_assertion_ids": sorted(
            row.left_assertion_id for row in reconciliations if row.disposition == "source-only"
        ),
        "candidate_match_count": disposition_counts.get("candidate-match", 0),
        "reviewed_match_count": disposition_counts.get("reviewed-match", 0),
        "reviewed_distinct_count": disposition_counts.get("reviewed-distinct", 0),
        "scope": "supplied archived assertions only",
    }
