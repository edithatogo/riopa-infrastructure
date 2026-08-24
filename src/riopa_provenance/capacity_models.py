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
