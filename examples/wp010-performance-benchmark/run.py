#!/usr/bin/env python3
"""Run the reproducible WP-010 performance contract.

The regional result measures a deterministic synthetic workload. The national
value is deliberately labelled a projection and is never presented as a run.
Only the standard library is required.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent


def checksum(records: int, iterations: int, seed: int) -> int:
    value = seed & 0xFFFFFFFF
    for row in range(records):
        for step in range(iterations):
            value = (value * 1664525 + 1013904223 + row + step) & 0xFFFFFFFF
    return value


def measure(
    records: int, iterations: int, seed: int, repeats: int = 3, degraded: bool = False
) -> dict[str, Any]:
    if repeats < 3:
        raise ValueError("repeats must be at least 3")
    checksum(records, iterations, seed)  # deterministic discarded warm-up
    samples: list[int] = []
    results: list[int] = []
    for _ in range(repeats):
        started = time.monotonic_ns()
        results.append(checksum(records, iterations, seed))
        if degraded:
            # Deterministically model a degraded path without claiming an outage.
            checksum(1, iterations // 2, seed ^ 0xDEAD)
        samples.append(time.monotonic_ns() - started)
    elapsed = int(statistics.median(samples))
    return {
        "records": records,
        "iterations": iterations,
        "elapsed_ns": elapsed,
        "records_per_second": records * 1_000_000_000 / elapsed if elapsed else 0.0,
        "checksum": results[0],
        "repetitions": repeats,
        "classification": "measured-regional-synthetic",
        "latency": {"p50_ms": elapsed / 1_000_000, "p95_ms": max(samples) / 1_000_000},
        "throughput": {"records_per_second": records * 1_000_000_000 / elapsed if elapsed else 0.0},
        "resources": {
            "cpu_seconds": None,
            "memory_mb": None,
            "storage_mb": None,
            "status": "not-instrumented",
        },
        "cost": {"currency": None, "amount": None, "status": "not-priced"},
    }


def run(output: Path | None = None) -> dict[str, Any]:
    workload = json.loads((HERE / "workload.json").read_text(encoding="utf-8"))
    scenarios = []
    for scenario in workload["scenarios"]:
        result = measure(
            scenario["records"],
            scenario["iterations"],
            workload["seed"],
            degraded=scenario.get("degraded", False),
        )
        result["case_id"] = scenario["scenario_id"]
        scenarios.append(result)
    regional = next(item for item in scenarios if item["case_id"] == "baseline")
    factor = workload["national_projection_records"] / workload["records"]
    projection = {
        "records": workload["national_projection_records"],
        "records_per_second": regional["records_per_second"],
        "estimated_elapsed_ns": int(regional["elapsed_ns"] * factor),
        "scaling_factor": factor,
        "classification": "projection-not-measurement",
        "method": "linear record-count extrapolation from regional measured median",
    }
    report = {
        "benchmark_id": "urn:riopa:benchmark:wp010:performance-contract:1.0.0",
        "workload": workload,
        "regional": regional,
        "scenarios": scenarios,
        "national": projection,
        "environment": {"python": __import__("sys").version.split()[0]},
    }
    if output:
        output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run(args.output)
    print(
        json.dumps(
            {
                "benchmark_id": report["benchmark_id"],
                "classification": report["national"]["classification"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
