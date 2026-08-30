#!/usr/bin/env python3
"""Validate a bounded WP-010 report without promoting its projection."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


def _number(value: Any, name: str, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    if positive and value <= 0:
        raise ValueError(f"{name} must be positive")
    return float(value)


def validate_report(report: Any) -> tuple[str, ...]:
    """Return deterministic errors for a benchmark report."""
    if not isinstance(report, dict):
        return ("report must be an object",)
    errors: list[str] = []
    if report.get("benchmark_id") != "urn:riopa:benchmark:wp010:performance-contract:1.0.0":
        errors.append("benchmark_id is not the WP-010 contract")
    regional = report.get("regional")
    scenarios = report.get("scenarios")
    if not isinstance(regional, dict) or not isinstance(scenarios, list) or not scenarios:
        return tuple(errors + ["regional and scenarios are required"])
    scenario_ids: set[str] = set()
    for index, scenario in enumerate(scenarios):
        prefix = f"scenarios[{index}]"
        if not isinstance(scenario, dict):
            errors.append(f"{prefix} must be an object")
            continue
        case_id = scenario.get("case_id")
        if not isinstance(case_id, str) or not case_id.strip() or case_id in scenario_ids:
            errors.append(f"{prefix}.case_id must be unique and non-empty")
        else:
            scenario_ids.add(case_id)
        if scenario.get("classification") != "measured-regional-synthetic":
            errors.append(f"{prefix}.classification must remain regional synthetic")
        try:
            records = _number(scenario.get("records"), f"{prefix}.records", positive=True)
            elapsed = _number(scenario.get("elapsed_ns"), f"{prefix}.elapsed_ns", positive=True)
            repetitions = _number(scenario.get("repetitions"), f"{prefix}.repetitions")
            if records != int(records) or repetitions != int(repetitions) or repetitions < 3:
                errors.append(f"{prefix} requires integer records and at least three repetitions")
            expected = records * 1_000_000_000 / elapsed
            observed = scenario.get("records_per_second")
            if abs(_number(observed, f"{prefix}.records_per_second") - expected) > max(
                1e-9, expected * 1e-9
            ):
                errors.append(f"{prefix}.records_per_second is inconsistent with elapsed_ns")
        except TypeError, ValueError:
            errors.append(f"{prefix} has invalid measurement fields")
        resources = scenario.get("resources")
        cost = scenario.get("cost")
        if not isinstance(resources, dict) or resources.get("status") == "measured":
            errors.append(f"{prefix}.resources must retain non-measured status")
        if not isinstance(cost, dict) or cost.get("status") == "measured":
            errors.append(f"{prefix}.cost must retain non-measured status")
    if regional.get("case_id") != "baseline":
        errors.append("regional must identify the baseline scenario")
    elif regional not in scenarios:
        errors.append("regional must be one of the measured scenarios")
    projection = report.get("national")
    if not isinstance(projection, dict):
        errors.append("national projection is required")
    else:
        if projection.get("classification") != "projection-not-measurement":
            errors.append("national must remain projection-not-measurement")
        if projection.get("method") != (
            "linear record-count extrapolation from regional measured median"
        ):
            errors.append("national projection method is not the declared bounded method")
    ingestion = report.get("ingestion")
    if not isinstance(ingestion, dict) or ingestion.get("live_endpoint_contacted") is not False:
        errors.append("ingestion must declare live_endpoint_contacted false")
    accessibility = report.get("accessibility")
    if not isinstance(accessibility, dict) or accessibility.get("claim_supported") is not False:
        errors.append("accessibility claims must remain unsupported")
    return tuple(dict.fromkeys(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    errors = validate_report(json.loads(args.report.read_text(encoding="utf-8")))
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print(f"PASS {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
