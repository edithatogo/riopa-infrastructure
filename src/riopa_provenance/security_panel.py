"""Digest-bound security agent-panel rerun packet validation."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any


class SecurityPanelPacketError(ValueError):
    """Raised when a panel packet cannot be safely qualified."""


_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_ROLES = ("adversarial-analyst", "evidence-auditor", "reproducer")


def build_panel_rerun_packet(*, source_revision: str) -> dict[str, Any]:
    """Create an explicitly pending packet for the three required lenses."""

    if not source_revision.strip():
        raise SecurityPanelPacketError("source revision is required")
    return {
        "schema": "riopa.security-panel-rerun.v1",
        "batch_id": f"security-rerun-{source_revision}",
        "source_revision": source_revision,
        "status": "pending",
        "required_roles": list(_ROLES),
        "reports": [],
        "synthesis": None,
        "final_disposition": "pending",
        "non_assertive": True,
        "non_claims": [
            "A packet validator does not conduct or qualify a panel.",
            "Agent-panel findings cannot substitute for external participant, elapsed-time "
            "or accountable-authority evidence.",
        ],
    }


def validate_panel_rerun_packet(packet: Mapping[str, Any] | None) -> tuple[str, ...]:
    """Validate role coverage, revision binding and report digests."""

    if not isinstance(packet, Mapping):
        return ("panel packet must be an object",)
    errors: list[str] = []
    for field in ("batch_id", "source_revision", "status", "final_disposition"):
        if not isinstance(packet.get(field), str) or not str(packet[field]).strip():
            errors.append(f"{field} is required")
    if packet.get("status") not in {"pending", "complete"}:
        errors.append("status is unsupported")
    if packet.get("final_disposition") not in {"pending", "qualified", "not-qualified"}:
        errors.append("final_disposition is unsupported")
    if packet.get("non_assertive") is not True:
        errors.append("non_assertive must be true")
    reports = packet.get("reports")
    if not isinstance(reports, list):
        errors.append("reports must be an array")
        reports = []
    roles: list[str] = []
    source_revision = packet.get("source_revision")
    for report in reports:
        if not isinstance(report, Mapping):
            errors.append("each report must be an object")
            continue
        role = report.get("role")
        if role not in _ROLES:
            errors.append("report role is unsupported")
        elif role in roles:
            errors.append("report roles must be unique")
        else:
            roles.append(role)
        if report.get("source_revision") != source_revision:
            errors.append("report source revisions must match packet")
        if not isinstance(report.get("report_id"), str) or not report["report_id"].strip():
            errors.append("report_id is required")
        if not isinstance(report.get("sha256"), str) or not _DIGEST.fullmatch(report["sha256"]):
            errors.append("report sha256 must be a lowercase digest")
        if not isinstance(report.get("findings"), list):
            errors.append("report findings must be an array")
    if packet.get("status") == "complete" and set(roles) != set(_ROLES):
        errors.append("complete packet requires all three panel roles")
    synthesis = packet.get("synthesis")
    if packet.get("status") == "complete":
        if not isinstance(synthesis, Mapping):
            errors.append("complete packet requires synthesis")
        elif not isinstance(synthesis.get("sha256"), str) or not _DIGEST.fullmatch(
            synthesis["sha256"]
        ):
            errors.append("synthesis sha256 must be a lowercase digest")
    return tuple(dict.fromkeys(errors))
