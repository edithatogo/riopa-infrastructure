"""Bounded synthetic capacity, scaling and cost model helpers."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any


class CapacityModelError(ValueError):
    """Raised when a capacity model is incomplete or non-physical."""


_NUMERIC_FIELDS = (
    "base_units",
    "base_seconds",
    "unit_seconds",
    "base_cost",
    "unit_cost",
    "max_units",
)


def validate_capacity_model(model: Mapping[str, Any] | None) -> tuple[str, ...]:
    """Validate a bounded linear model without claiming empirical calibration."""

    if not isinstance(model, Mapping):
        return ("capacity model must be an object",)
    errors: list[str] = []
    for field in _NUMERIC_FIELDS:
        value = model.get(field)
        if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            errors.append(f"{field} must be finite and non-negative")
    if isinstance(model.get("base_units"), (int, float)) and model["base_units"] <= 0:
        errors.append("base_units must be positive")
    return tuple(dict.fromkeys(errors))


def project_capacity(model: Mapping[str, Any], units: int) -> dict[str, float]:
    """Project time and cost for a bounded synthetic workload size."""

    errors = validate_capacity_model(model)
    if errors:
        raise CapacityModelError("; ".join(errors))
    if not isinstance(units, int) or units < 0:
        raise CapacityModelError("units must be a non-negative integer")
    maximum = float(model["max_units"])
    if units > maximum:
        raise CapacityModelError("units exceed the declared model envelope")
    base_units = float(model["base_units"])
    scale = units / base_units
    return {
        "units": float(units),
        "projected_seconds": float(model["base_seconds"]) + float(model["unit_seconds"]) * scale,
        "projected_cost": float(model["base_cost"]) + float(model["unit_cost"]) * scale,
    }


def classify_bottlenecks(observation: Mapping[str, Any] | None) -> dict[str, Any]:
    """Classify bounded observations into remediation hints without weakening gates.

    Ratios are compared with explicit thresholds.  The result is diagnostic
    only: it never changes a benchmark verdict, projects national capacity, or
    treats missing measurements as evidence of absence.
    """

    if not isinstance(observation, Mapping):
        raise CapacityModelError("bottleneck observation must be an object")
    required = ("latency_ratio", "throughput_ratio", "memory_ratio", "error_rate")
    values: dict[str, float] = {}
    for field in required:
        value = observation.get(field)
        if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise CapacityModelError(f"{field} must be finite and non-negative")
        values[field] = float(value)
    limits = {
        "latency": float(observation.get("latency_limit", 1.10)),
        "throughput": float(observation.get("throughput_limit", 0.90)),
        "memory": float(observation.get("memory_limit", 1.10)),
        "errors": float(observation.get("error_limit", 0.01)),
    }
    if any(not math.isfinite(value) or value < 0 for value in limits.values()):
        raise CapacityModelError("bottleneck limits must be finite and non-negative")
    bottlenecks: list[str] = []
    actions: list[str] = []
    if values["latency_ratio"] > limits["latency"]:
        bottlenecks.append("latency")
        actions.append("profile-query-and-ingestion")
    if values["throughput_ratio"] < limits["throughput"]:
        bottlenecks.append("throughput")
        actions.append("inspect-concurrency-and-backpressure")
    if values["memory_ratio"] > limits["memory"]:
        bottlenecks.append("memory")
        actions.append("inspect-batch-size-and-materialisation")
    if values["error_rate"] > limits["errors"]:
        bottlenecks.append("errors")
        actions.append("preserve-failure-and-stop-promotion")
    return {
        "bottlenecks": bottlenecks,
        "actions": actions,
        "non_assertive": True,
        "source": "bounded-observation",
    }


def evaluate_capacity_resilience(
    *,
    demand_units: int,
    primary_capacity: int,
    backup_capacity: int,
    primary_available: bool = True,
    backup_available: bool = True,
    reserve_target: int = 0,
) -> dict[str, int | bool | str]:
    """Evaluate a bounded synthetic primary/backup capacity scenario.

    This deterministic reference calculation is for service-capacity and
    resilience examples only. It is not a hospital, clinical, dispatch,
    national-scale, or operational-readiness model.
    """

    integer_values = {
        "demand_units": demand_units,
        "primary_capacity": primary_capacity,
        "backup_capacity": backup_capacity,
        "reserve_target": reserve_target,
    }
    for name, value in integer_values.items():
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise CapacityModelError(f"{name} must be a non-negative integer")
    if not isinstance(primary_available, bool) or not isinstance(backup_available, bool):
        raise CapacityModelError("availability flags must be booleans")

    available_primary = primary_capacity if primary_available else 0
    available_backup = backup_capacity if backup_available else 0
    available_capacity = available_primary + available_backup
    served_units = min(demand_units, available_capacity)
    unmet_units = demand_units - served_units
    reserve_after_service = available_capacity - served_units
    reserve_gap = max(0, reserve_target - reserve_after_service)
    return {
        "demand_units": demand_units,
        "available_primary": available_primary,
        "available_backup": available_backup,
        "available_capacity": available_capacity,
        "served_units": served_units,
        "unmet_units": unmet_units,
        "reserve_after_service": reserve_after_service,
        "reserve_gap": reserve_gap,
        "fail_closed": unmet_units > 0 or reserve_gap > 0,
        "non_assertive": True,
        "source": "bounded-synthetic-capacity",
    }
