"""Fail-closed orchestration records for spatial archive operations.

The helpers in this module are pure: callers provide already-observed source
metadata and the functions produce deterministic decisions and reports.  They
do not contact endpoints, deploy connectors, or claim national coverage.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from .hashing import sha256_json
from .health import detect_capability_drift


class ArchiveOperationsError(ValueError):
    """Raised when an operations observation cannot produce safe evidence."""


_REQUIRED_FIELDS = (
    "authority_id",
    "source_id",
    "endpoint_id",
    "layer_type",
    "legal_status",
    "rights_status",
    "quality_status",
    "time_depth",
    "operational_disposition",
    "owner_role",
    "availability_status",
    "capture_kind",
)
_DIMENSIONS = (
    "authority_id",
    "layer_type",
    "time_depth",
    "legal_status",
    "rights_status",
    "quality_status",
    "operational_disposition",
    "availability_status",
)
_RIGHTS_ALLOWED = {"permitted", "restricted", "unknown", "prohibited"}
_AVAILABILITY_ALLOWED = {"healthy", "degraded", "missing", "not-observed"}
_CAPTURE_KINDS = {"current", "reconstructed-backfill"}


def _non_empty_string(row: Mapping[str, Any], field: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ArchiveOperationsError(f"source observation requires non-empty {field}")
    return value.strip()


def _digest(row: Mapping[str, Any], field: str, *, required: bool) -> str | None:
    value = row.get(field)
    if value is None and not required:
        return None
    if not isinstance(value, str) or len(value) != 64:
        raise ArchiveOperationsError(f"{field} must be a 64-character digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ArchiveOperationsError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _validate_observation(row: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(row, Mapping):
        raise ArchiveOperationsError("source observations must be objects")
    normalized = dict(row)
    for field in _REQUIRED_FIELDS:
        normalized[field] = _non_empty_string(row, field)
    if normalized["rights_status"] not in _RIGHTS_ALLOWED:
        raise ArchiveOperationsError("rights_status is unsupported")
    if normalized["availability_status"] not in _AVAILABILITY_ALLOWED:
        raise ArchiveOperationsError("availability_status is unsupported")
    if normalized["capture_kind"] not in _CAPTURE_KINDS:
        raise ArchiveOperationsError("capture_kind is unsupported")
    if normalized["capture_kind"] == "reconstructed-backfill":
        reconstructed_at = row.get("reconstructed_at")
        if not isinstance(reconstructed_at, str) or not reconstructed_at.strip():
            raise ArchiveOperationsError("reconstructed backfill requires reconstructed_at")
    for field in ("schema", "capabilities"):
        if not isinstance(row.get(field), Mapping):
            raise ArchiveOperationsError(f"source observation requires {field} object")
        normalized[field] = dict(row[field])
    normalized["payload_sha256"] = _digest(row, "payload_sha256", required=False)
    return normalized


def build_delta_decision(
    previous: Mapping[str, Any] | None,
    current: Mapping[str, Any],
    *,
    observed_at: str,
) -> dict[str, Any]:
    """Bind delta, schema/capability drift, rights, and quarantine into one decision."""

    if not isinstance(observed_at, str) or not observed_at.strip():
        raise ArchiveOperationsError("observed_at must be non-empty")
    now = _validate_observation(current)
    before = _validate_observation(previous) if previous is not None else None
    identity = (now["source_id"], now["endpoint_id"])
    if before is not None and identity != (before["source_id"], before["endpoint_id"]):
        raise ArchiveOperationsError(
            "previous and current observations identify different endpoints"
        )

    schema_drift = detect_capability_drift(
        before["schema"] if before is not None else now["schema"], now["schema"]
    )
    capability_drift = detect_capability_drift(
        before["capabilities"] if before is not None else now["capabilities"],
        now["capabilities"],
    )
    previous_payload = before["payload_sha256"] if before is not None else None
    payload_changed = previous_payload != now["payload_sha256"]
    quarantine_reasons: list[str] = []
    if now["availability_status"] != "healthy":
        quarantine_reasons.append(f"availability:{now['availability_status']}")
    if now["rights_status"] != "permitted":
        quarantine_reasons.append(f"rights:{now['rights_status']}")
    if now["payload_sha256"] is None:
        quarantine_reasons.append("payload:missing-digest")
    if schema_drift.drifted:
        quarantine_reasons.append("schema:unresolved-drift")
    if capability_drift.drifted:
        quarantine_reasons.append("capability:unresolved-drift")

    if quarantine_reasons:
        action = "quarantine"
    elif before is None or payload_changed:
        action = "store-delta"
    else:
        action = "no-change"
    body: dict[str, Any] = {
        "schema_version": "1.0.0",
        "record_type": "archive_delta_decision",
        "identity_key": f"{identity[0]}:{identity[1]}",
        "observed_at": observed_at.strip(),
        "authority_id": now["authority_id"],
        "source_id": now["source_id"],
        "endpoint_id": now["endpoint_id"],
        "capture_kind": now["capture_kind"],
        "reconstructed_at": now.get("reconstructed_at"),
        "previous_payload_sha256": previous_payload,
        "current_payload_sha256": now["payload_sha256"],
        "payload_changed": payload_changed,
        "schema_drift": schema_drift.to_record(),
        "capability_drift": capability_drift.to_record(),
        "action": action,
        "quarantine_reasons": quarantine_reasons,
        "promotion_allowed": False,
        "source_observation": now,
        "nonclaims": [
            "The decision evaluates supplied observations and does not contact an endpoint.",
            "A clear decision does not establish national completeness or release authority.",
        ],
    }
    body["decision_sha256"] = sha256_json(body)
    return body


def assemble_partial_release(
    decisions: Sequence[Mapping[str, Any]], *, release_id: str, assembled_at: str
) -> dict[str, Any]:
    """Assemble an explicit partial release from digest-bound source decisions."""

    if not release_id.strip() or not assembled_at.strip():
        raise ArchiveOperationsError("release_id and assembled_at must be non-empty")
    if not decisions:
        raise ArchiveOperationsError("release assembly requires at least one decision")
    included: list[dict[str, str]] = []
    excluded: list[dict[str, Any]] = []
    seen: set[str] = set()
    for decision in decisions:
        if decision.get("record_type") != "archive_delta_decision":
            raise ArchiveOperationsError("release assembly requires archive delta decisions")
        if decision.get("promotion_allowed") is not False:
            raise ArchiveOperationsError("release decisions must prohibit promotion")
        identity = decision.get("identity_key")
        if not isinstance(identity, str) or not identity.strip() or identity in seen:
            raise ArchiveOperationsError("release decisions require unique identities")
        seen.add(identity)
        supplied_digest = decision.get("decision_sha256")
        unsigned = {key: value for key, value in decision.items() if key != "decision_sha256"}
        if supplied_digest != sha256_json(unsigned):
            raise ArchiveOperationsError(f"decision digest mismatch for {identity}")
        action = decision.get("action")
        payload = decision.get("current_payload_sha256")
        if action not in {"store-delta", "no-change", "quarantine"}:
            raise ArchiveOperationsError(f"unsupported decision action for {identity}")
        reasons = decision.get("quarantine_reasons")
        if not isinstance(reasons, list) or any(
            not isinstance(reason, str) or not reason for reason in reasons
        ):
            raise ArchiveOperationsError(f"invalid quarantine reasons for {identity}")
        if action == "quarantine" and not reasons:
            raise ArchiveOperationsError(f"quarantine decision lacks reasons for {identity}")
        if action != "quarantine" and reasons:
            raise ArchiveOperationsError(f"clear decision has quarantine reasons for {identity}")
        if action in {"store-delta", "no-change"}:
            if not isinstance(payload, str):
                raise ArchiveOperationsError(f"clear decision lacks payload digest for {identity}")
            _digest({"payload": payload}, "payload", required=True)
            included.append({"identity_key": identity, "payload_sha256": payload})
        else:
            excluded.append(
                {
                    "identity_key": identity,
                    "action": action,
                    "reasons": list(reasons),
                }
            )
    included.sort(key=lambda item: item["identity_key"])
    excluded.sort(key=lambda item: item["identity_key"])
    body: dict[str, Any] = {
        "schema_version": "1.0.0",
        "record_type": "archive_partial_release",
        "release_id": release_id.strip(),
        "assembled_at": assembled_at.strip(),
        "included": included,
        "excluded": excluded,
        "partial": bool(excluded),
        "promotion_allowed": False,
        "nonclaims": [
            "Assembly is digest-only and does not publish or preserve payload bytes.",
            "Included observations do not establish national completeness or release approval.",
        ],
    }
    body["release_sha256"] = sha256_json(body)
    return body


def build_coverage_report(
    observations: Sequence[Mapping[str, Any]], *, report_id: str, generated_at: str
) -> dict[str, Any]:
    """Report coverage across required dimensions without a national percentage."""

    if not report_id.strip() or not generated_at.strip():
        raise ArchiveOperationsError("report_id and generated_at must be non-empty")
    if not observations:
        raise ArchiveOperationsError("coverage report requires at least one observation")
    normalized = [_validate_observation(row) for row in observations]
    identities = [f"{row['source_id']}:{row['endpoint_id']}" for row in normalized]
    if len(set(identities)) != len(identities):
        raise ArchiveOperationsError("coverage observations require unique identities")
    dimensions = {
        dimension: dict(sorted(Counter(str(row[dimension]) for row in normalized).items()))
        for dimension in _DIMENSIONS
    }
    body: dict[str, Any] = {
        "schema_version": "1.0.0",
        "record_type": "archive_coverage_report",
        "report_id": report_id.strip(),
        "generated_at": generated_at.strip(),
        "source_count": len(normalized),
        "dimensions": dimensions,
        "sources": sorted(
            [
                {
                    "identity_key": identity,
                    **{dimension: row[dimension] for dimension in _DIMENSIONS},
                    "owner_role": row["owner_role"],
                }
                for identity, row in zip(identities, normalized, strict=True)
            ],
            key=lambda row: str(row["identity_key"]),
        ),
        "national_coverage_percentage": None,
        "promotion_allowed": False,
        "nonclaims": [
            "Counts describe supplied observations, not all current New Zealand authorities.",
            "No single percentage is reported because coverage is multidimensional.",
        ],
    }
    body["report_sha256"] = sha256_json(body)
    return body
