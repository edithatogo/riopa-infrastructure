"""Secret-free security incident exercise packet contracts."""

from __future__ import annotations

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
