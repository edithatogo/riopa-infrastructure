#!/usr/bin/env python3
"""Validate noise-aware, host-neutral benchmark envelope observations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def validate(report: dict[str, Any], *, max_p95_to_p50: float = 3.0) -> tuple[str, ...]:
    errors: list[str] = []
    scenarios = report.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        return ("report scenarios must be a non-empty array",)
    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            errors.append(f"scenario {index} must be an object")
            continue
        case_id = scenario.get("case_id", index)
        repetitions = scenario.get("repetitions")
        if not isinstance(repetitions, int) or repetitions < 3:
            errors.append(f"scenario {case_id} needs at least three repetitions")
        latency = scenario.get("latency")
        if not isinstance(latency, dict):
            errors.append(f"scenario {case_id} latency must be an object")
            continue
        p50 = latency.get("p50_ms")
        p95 = latency.get("p95_ms")
        if not isinstance(p50, (int, float)) or not isinstance(p95, (int, float)):
            errors.append(f"scenario {case_id} latency must include numeric p50_ms and p95_ms")
        elif p50 <= 0 or p95 < p50:
            errors.append(f"scenario {case_id} latency ordering is invalid")
        elif p95 / p50 > max_p95_to_p50:
            errors.append(f"scenario {case_id} exceeds noise ratio {max_p95_to_p50:g}")
    return tuple(errors)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("--max-p95-to-p50", type=float, default=3.0)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    errors = validate(report, max_p95_to_p50=args.max_p95_to_p50)
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print("PASS noise-aware performance envelope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
