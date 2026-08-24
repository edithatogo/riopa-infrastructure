"""Secret-free security incident exercise packet contracts."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any


class SecurityExerciseError(ValueError):
    """Raised when an incident exercise packet is unsafe or incomplete."""


SCENARIO_CONTROLS: dict[str, tuple[str, ...]] = {
    "credential-compromise": ("revoke", "rotate", "audit", "rollback"),
    "malicious-input": ("quarantine", "validate", "preserve-failure", "notify"),
    "rollback": ("verify-fixity", "restore-predecessor", "record-receipt", "revoke"),
}


def build_exercise_packet(scenario: str, *, source_revision: str) -> dict[str, Any]:
    """Build a planned, secret-free exercise packet."""

    if scenario not in SCENARIO_CONTROLS:
        raise SecurityExerciseError("unsupported security exercise scenario")
    if not source_revision.strip():
        raise SecurityExerciseError("source revision is required")
    return {
        "exercise_id": f"urn:riopa:security-exercise:{scenario}:{source_revision}",
        "scenario": scenario,
        "source_revision": source_revision,
        "status": "planned",
        "credential_material": "absent",
        "required_controls": list(SCENARIO_CONTROLS[scenario]),
        "observations": [],
        "non_claims": [
            "This is a planned exercise packet, not an executed compromise or rollback receipt.",
            "No credential, token, payload or secret is stored in this packet.",
        ],
    }


def validate_exercise_packet(packet: Mapping[str, Any] | None) -> tuple[str, ...]:
    """Validate scenario controls and reject secret-shaped content."""

    if not isinstance(packet, Mapping):
        return ("exercise packet must be an object",)
    errors: list[str] = []
    for field in ("exercise_id", "scenario", "source_revision", "status"):
        if not isinstance(packet.get(field), str) or not str(packet[field]).strip():
            errors.append(f"{field} is required")
    scenario = packet.get("scenario")
    if scenario not in SCENARIO_CONTROLS:
        errors.append("scenario is unsupported")
    elif packet.get("required_controls") != list(SCENARIO_CONTROLS[scenario]):
        errors.append("required_controls do not match scenario")
    if packet.get("status") not in {"planned", "executed", "failed"}:
        errors.append("status is unsupported")
    if packet.get("credential_material") != "absent":
        errors.append("credential_material must be absent")
    observations = packet.get("observations")
    if not isinstance(observations, Sequence) or isinstance(observations, (str, bytes)):
        errors.append("observations must be an array")
    forbidden = {"token", "secret", "password", "api_key", "access_token", "private_key"}
    stack: list[object] = [packet]
    while stack:
        current = stack.pop()
        if isinstance(current, Mapping):
            for key, value in current.items():
                if str(key).lower() in forbidden:
                    errors.append(f"credential-shaped field is prohibited: {key}")
                stack.append(value)
        elif isinstance(current, Sequence) and not isinstance(current, (str, bytes)):
            stack.extend(current)
    return tuple(dict.fromkeys(errors))


def validate_exercise_execution(report: Mapping[str, Any] | None) -> tuple[str, ...]:
    """Validate a secret-free execution report without qualifying the exercise.

    The report is deliberately separate from the planned packet: an execution
    record must bind to one scenario and source revision, identify the execution
    environment, and preserve an outcome for every required control.  A hosted
    identifier proves only where the run was recorded; it does not establish a
    production security qualification.
    """

    if not isinstance(report, Mapping):
        return ("execution report must be an object",)
    errors: list[str] = []
    for field in ("exercise_id", "scenario", "source_revision", "status", "environment"):
        if not isinstance(report.get(field), str) or not str(report[field]).strip():
            errors.append(f"{field} is required")
    scenario = report.get("scenario")
    if scenario not in SCENARIO_CONTROLS:
        errors.append("scenario is unsupported")
    if report.get("status") not in {"executed", "failed"}:
        errors.append("status must be executed or failed")
    if report.get("environment") not in {"local", "hosted"}:
        errors.append("environment must be local or hosted")
    if report.get("environment") == "hosted" and not str(report.get("hosted_run_id", "")).strip():
        errors.append("hosted execution requires hosted_run_id")
    controls = report.get("controls")
    if not isinstance(controls, Mapping):
        errors.append("controls must be an object")
    elif scenario in SCENARIO_CONTROLS:
        expected = set(SCENARIO_CONTROLS[scenario])
        if set(controls) != expected:
            errors.append("controls must exactly match scenario controls")
        for control, outcome in controls.items():
            if outcome not in {"passed", "failed", "not-run"}:
                errors.append(f"control outcome is unsupported: {control}")
        if report.get("status") == "failed" and not isinstance(report.get("failure_reason"), str):
            errors.append("failed executions require failure_reason")
    if not isinstance(report.get("raw_log_sha256"), str) or not re.fullmatch(
        r"[0-9a-f]{64}", str(report.get("raw_log_sha256"))
    ):
        errors.append("raw_log_sha256 must be a lowercase SHA-256 digest")
    if report.get("non_assertive") is not True:
        errors.append("non_assertive must be true")
    return tuple(dict.fromkeys(errors))
