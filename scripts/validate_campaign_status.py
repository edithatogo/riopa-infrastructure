#!/usr/bin/env python3
"""Validate the checked-in hosted campaign status snapshot fail-closed."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

_REVISION = re.compile(r"^[0-9a-f]{40}$")


def validate_status(document: Any) -> tuple[str, ...]:
    """Return deterministic validation errors for a campaign status snapshot."""

    if not isinstance(document, dict):
        return ("status snapshot must be an object",)
    errors: list[str] = []
    source_revision = document.get("source_revision")
    if not isinstance(source_revision, str) or _REVISION.fullmatch(source_revision) is None:
        errors.append("source_revision must be a 40-character lowercase hexadecimal revision")
    observations = document.get("observations")
    if not isinstance(observations, list) or not observations:
        errors.append("observations must be a non-empty array")
        observations = []
    run_ids: set[str] = set()
    rc_observations: list[dict[str, Any]] = []
    latest_revision: str | None = None
    for index, observation in enumerate(observations):
        prefix = f"observations[{index}]"
        if not isinstance(observation, dict):
            errors.append(f"{prefix} must be an object")
            continue
        run_id = observation.get("run_id")
        if not isinstance(run_id, str) or not run_id.strip():
            errors.append(f"{prefix}.run_id is required")
        elif run_id in run_ids:
            errors.append(f"{prefix}.run_id is duplicated")
        else:
            run_ids.add(run_id)
        lane = observation.get("lane")
        if not isinstance(lane, str) or not lane.strip():
            errors.append(f"{prefix}.lane is required")
        status = observation.get("status")
        if status not in {"passed", "failed"}:
            errors.append(f"{prefix}.status must be passed or failed")
        revision = observation.get("revision")
        if not isinstance(revision, str) or not revision.strip():
            errors.append(f"{prefix}.revision is required")
        else:
            latest_revision = revision
            if _REVISION.fullmatch(revision) is None:
                errors.append(
                    f"{prefix}.revision must be a 40-character lowercase hexadecimal revision"
                )
        if lane == "rc-soak-observation":
            candidate = observation.get("candidate_revision")
            if candidate != revision:
                errors.append(f"{prefix} RC candidate must equal revision")
            for field in ("campaign_id", "qualification_epoch", "operational_cycle_id"):
                if not isinstance(observation.get(field), str) or not observation[field].strip():
                    errors.append(f"{prefix}.{field} is required for RC observations")
            rc_observations.append(observation)
    if isinstance(source_revision, str) and latest_revision and source_revision != latest_revision:
        errors.append("source_revision must match the latest receipt-bearing observation")
    supplemental = document.get("supplemental_observations", [])
    if not isinstance(supplemental, list):
        errors.append("supplemental_observations must be an array when present")
    else:
        for index, observation in enumerate(supplemental):
            prefix = f"supplemental_observations[{index}]"
            if not isinstance(observation, dict):
                errors.append(f"{prefix} must be an object")
                continue
            for field in ("revision", "candidate_revision"):
                value = observation.get(field)
                if value is not None and (
                    not isinstance(value, str) or _REVISION.fullmatch(value) is None
                ):
                    errors.append(
                        f"{prefix}.{field} must be a 40-character lowercase hexadecimal revision"
                    )
    rc_gate = document.get("rc_gate")
    if not isinstance(rc_gate, dict):
        errors.append("rc_gate must be an object")
    elif rc_observations:
        expected = rc_observations[-1].get("candidate_revision")
        if rc_gate.get("candidate_revision") != expected:
            errors.append("rc_gate candidate_revision must match the latest RC observation")
    if not isinstance(document.get("elapsed_gate"), dict):
        errors.append("elapsed_gate must be an object")
    return tuple(dict.fromkeys(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("status", type=Path)
    args = parser.parse_args()
    errors = validate_status(json.loads(args.status.read_text(encoding="utf-8")))
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print(f"PASS {args.status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
