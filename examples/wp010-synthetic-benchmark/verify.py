#!/usr/bin/env python3
"""Independent standard-library verifier for the WP-010 synthetic benchmark."""

from __future__ import annotations

import heapq
import json
import statistics
from pathlib import Path
from typing import Any


def _queue(payload: dict[str, Any]) -> dict[str, Any]:
    arrivals = payload["arrival_times"]
    services = payload["service_times"]
    capacity = payload["capacity"]
    warm_up = payload["warm_up_customers"]
    resources = [(0.0, resource) for resource in range(capacity)]
    heapq.heapify(resources)
    waits: list[float] = []
    busy = 0.0
    last_end = 0.0
    for customer, (arrival, duration) in enumerate(zip(arrivals, services, strict=True)):
        available, resource = heapq.heappop(resources)
        start = max(arrival, available)
        end = start + duration
        heapq.heappush(resources, (end, resource))
        if customer >= warm_up:
            waits.append(start - arrival)
            busy += duration
            last_end = max(last_end, end)
    window = max(0.0, last_end - arrivals[warm_up])
    return {
        "waits": waits,
        "mean_wait": statistics.fmean(waits),
        "maximum_wait": max(waits),
        "utilisation": busy / (capacity * window) if window else 0.0,
        "observed_customers": len(waits),
    }


def _did(payload: dict[str, Any]) -> dict[str, Any]:
    names = ("treated_pre", "treated_post", "comparison_pre", "comparison_post")
    means = {name: statistics.fmean(payload[name]) for name in names}
    estimate = (means["treated_post"] - means["treated_pre"]) - (
        means["comparison_post"] - means["comparison_pre"]
    )
    return {"estimate": estimate, "group_means": means}


def main() -> int:
    path = Path(__file__).with_name("benchmark.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    if payload.get("operational_status") != "synthetic-non-operational":
        errors.append("operational boundary is missing")
    if set(payload.get("suitability", {}).values()) != {False}:
        errors.append("all suitability fields must be false")
    if _queue(payload["queue"]) != payload["queue"]["expected"]:
        errors.append("queue result differs from committed expectation")
    if (
        _did(payload["difference_in_differences"])
        != payload["difference_in_differences"]["expected"]
    ):
        errors.append("difference-in-differences result differs from committed expectation")
    if errors:
        print("FAIL " + "; ".join(errors))
        return 1
    print(f"PASS {payload['benchmark_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
