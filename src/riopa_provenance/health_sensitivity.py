"""Bounded sensitivity summaries for non-clinical spatial method references."""

import math
from collections.abc import Mapping, Sequence
from typing import Any


class HealthSensitivityError(ValueError):
    """Raised when a sensitivity input is not complete or finite."""


def spatial_confounding_sensitivity(
    observations: Sequence[Mapping[str, Any]],
    *,
    exposure_field: str,
    outcome_field: str,
    confounder_field: str,
) -> dict[str, Any]:
    """Compare crude and confounder-stratified descriptive mean contrasts.

    The result is a sensitivity diagnostic only; it is not a causal estimate.
    """
    if not observations or not all((exposure_field, outcome_field, confounder_field)):
        raise HealthSensitivityError("observations and field names are required")
    groups: dict[str, dict[bool, list[float]]] = {}
    all_values: dict[bool, list[float]] = {True: [], False: []}
    for row in observations:
        exposure = row.get(exposure_field)
        outcome = row.get(outcome_field)
        confounder = row.get(confounder_field)
        if not isinstance(exposure, bool) or not isinstance(confounder, str) or not confounder:
            raise HealthSensitivityError("exposure must be boolean and confounder non-empty")
        if (
            not isinstance(outcome, (int, float))
            or isinstance(outcome, bool)
            or not math.isfinite(outcome)
        ):
            raise HealthSensitivityError("outcome must be a finite number")
        groups.setdefault(confounder, {True: [], False: []})[exposure].append(float(outcome))
        all_values[exposure].append(float(outcome))

    def contrast(values: Mapping[bool, Sequence[float]]) -> float | None:
        if not values[True] or not values[False]:
            return None
        return sum(values[True]) / len(values[True]) - sum(values[False]) / len(values[False])

    crude = contrast(all_values)
    strata = {group: contrast(values) for group, values in sorted(groups.items())}
    usable = [value for value in strata.values() if value is not None]
    return {
        "record_type": "bounded_spatial_confounding_sensitivity",
        "crude_contrast": crude,
        "stratified_contrasts": strata,
        "stratified_range": (max(usable) - min(usable)) if usable else None,
        "nonclaims": [
            "Contrasts are descriptive diagnostics and do not establish causality.",
            (
                "Residual confounding, selection, measurement error and spatial dependence "
                "remain open."
            ),
        ],
    }


def maup_sensitivity(values_by_scale: Mapping[str, float]) -> dict[str, Any]:
    """Report the observed range across explicitly named spatial aggregations."""
    if len(values_by_scale) < 2:
        raise HealthSensitivityError("at least two spatial scales are required")
    if any(not scale or not math.isfinite(value) for scale, value in values_by_scale.items()):
        raise HealthSensitivityError("scales must be named and values finite")
    values = list(values_by_scale.values())
    return {
        "record_type": "bounded_maup_sensitivity",
        "values_by_scale": dict(sorted(values_by_scale.items())),
        "range": max(values) - min(values),
        "nonclaims": [
            "Scale variation is descriptive and does not identify a preferred geography.",
            "Boundary, source, denominator and temporal comparability remain required.",
        ],
    }


def measurement_error_sensitivity(
    values: Sequence[float], *, absolute_error: float
) -> dict[str, Any]:
    """Bound a mean under a symmetric absolute measurement-error assumption."""
    if not values or not math.isfinite(absolute_error) or absolute_error < 0:
        raise HealthSensitivityError("values are required and absolute_error must be non-negative")
    if any(not math.isfinite(value) for value in values):
        raise HealthSensitivityError("values must be finite")
    mean = sum(values) / len(values)
    return {
        "record_type": "bounded_measurement_error_sensitivity",
        "observed_mean": mean,
        "lower_mean": mean - absolute_error,
        "upper_mean": mean + absolute_error,
        "absolute_error": absolute_error,
        "nonclaims": [
            "Bounds reflect only the supplied symmetric-error assumption.",
            "They do not replace validation, calibration or uncertainty estimation.",
        ],
    }
