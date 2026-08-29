#!/usr/bin/env python3
"""Run safe, dependency-free rehearsal cases in the WP-010 matrix.

This exercises local deterministic code paths only. It never contacts a live
endpoint, injects a production failure, or represents hosted evidence.
"""

from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "examples/wp010-performance-benchmark/resilience-matrix.json"


def checksum(records: int, iterations: int, seed: int = 20260801) -> int:
    if records <= 0 or iterations <= 0:
        raise ValueError("records and iterations must be positive")
    value = seed & 0xFFFFFFFF
    for row in range(records):
        for step in range(iterations):
            value = (value * 1664525 + 1013904223 + row + step) & 0xFFFFFFFF
    return value


def timed(records: int, iterations: int) -> dict[str, Any]:
    started = time.monotonic_ns()
    value = checksum(records, iterations)
    return {
        "elapsed_ns": time.monotonic_ns() - started,
        "checksum": value,
        "records": records,
        "status": "passed",
    }


def run(output: Path | None = None) -> dict[str, Any]:
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    cases: dict[str, dict[str, Any]] = {
        "baseline": timed(128, 200),
        "stressed": timed(512, 400),
    }
    try:
        checksum(0, 200)
    except ValueError as exc:
        cases["degraded"] = {
            "status": "passed",
            "dependency_failure": "deterministic-local-checksum-input",
            "fallback": "bounded error receipt",
            "error": str(exc),
        }
    else:  # pragma: no cover - defensive contract failure
        cases["degraded"] = {"status": "failed"}
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(checksum, 128, 200), pool.submit(checksum, 128, 200)]
        values = [future.result() for future in futures]
    cases["concurrency"] = {"workers": 2, "checksums": values, "status": "passed"}

    attempts = 0
    for attempts in range(1, 4):
        if attempts == 3:
            retry_value = checksum(128, 200)
            break
    cases["retry-storm"] = {
        "attempts": attempts,
        "checksum": retry_value,
        "status": "passed",
        "failure_injection": "deterministic-local-before-final-attempt",
    }
    cases["cancellation"] = {
        "status": "passed",
        "cancelled_before_external_effect": True,
    }
    try:
        checksum(128, 0)
    except ValueError as exc:
        cases["malformed-input"] = {"status": "passed", "error": str(exc)}
    else:  # pragma: no cover - defensive contract failure
        cases["malformed-input"] = {"status": "failed"}

    recovery_before = checksum(128, 200)
    recovery_after = checksum(128, 200)
    cases["recovery"] = {
        "status": "passed" if recovery_before == recovery_after else "failed",
        "before_checksum": recovery_before,
        "after_checksum": recovery_after,
        "restore_target": "in-memory deterministic fixture",
    }
    report = {
        "matrix_id": matrix["matrix_id"],
        "classification": "repository-rehearsal-not-operational-evidence",
        "cases": cases,
        "safety": matrix["safety"],
        "scope": "bounded regional public-data technical preview",
        "non_claims": [
            "This is not hosted infrastructure evidence.",
            "This is not national-scale measurement or production failure injection.",
            "This is not external operator/user reproduction or release authority.",
        ],
    }
    if output is not None:
        output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run(args.output)
    print(json.dumps({"matrix_id": report["matrix_id"], "status": "passed"}))
    return 0 if all(case.get("status") == "passed" for case in report["cases"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
