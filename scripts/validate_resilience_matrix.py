#!/usr/bin/env python3
"""Validate the bounded WP-010 resilience matrix without running it."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "examples/wp010-performance-benchmark/resilience-matrix.json"

REQUIRED_CASES = {
    "baseline",
    "stressed",
    "degraded",
    "concurrency",
    "retry-storm",
    "cancellation",
    "malformed-input",
}


def validate(matrix: dict[str, Any]) -> None:
    if matrix.get("classification") != "repository-rehearsal-plan-not-operational-evidence":
        raise ValueError("resilience matrix must remain a rehearsal plan")
    if set(matrix.get("required_cases", [])) != REQUIRED_CASES:
        raise ValueError("resilience matrix case coverage is incomplete")
    safety = matrix.get("safety", {})
    if any(
        safety.get(key) is not False
        for key in (
            "live_endpoint_contacted",
            "production_failure_injection",
            "network_timetable_facility_claims",
            "national_scale_measurement",
        )
    ):
        raise ValueError("resilience matrix safety boundary must be fail-closed")
    completion = matrix.get("completion", {})
    if completion.get("status") != "not-run":
        raise ValueError("unexecuted resilience matrix must remain not-run")


def main() -> int:
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    validate(matrix)
    print(matrix["matrix_id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
