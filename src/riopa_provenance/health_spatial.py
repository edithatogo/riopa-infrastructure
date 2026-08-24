"""Dependency-free, bounded spatial-health reference summaries.

These helpers operate on supplied records only. They do not infer clinical risk,
causality, equity, or population-level truth from a synthetic or preview sample.
"""

import math
from collections.abc import Mapping, Sequence
from typing import Any


class HealthSpatialError(ValueError):
    """Raised when a bounded spatial-method input is incomplete or invalid."""


def descriptive_mapping(
    numerator_by_area: Mapping[str, float],
    denominator_by_area: Mapping[str, float],
) -> dict[str, Any]:
    """Return deterministic area rates with explicit denominator checks."""
    if set(numerator_by_area) != set(denominator_by_area):
        raise HealthSpatialError("numerator and denominator areas must match")
    rows: list[dict[str, Any]] = []
    for area in sorted(numerator_by_area):
        numerator = numerator_by_area[area]
        denominator = denominator_by_area[area]
        if not isinstance(area, str) or not area:
            raise HealthSpatialError("area identifiers must be non-empty strings")
        if not math.isfinite(numerator) or not math.isfinite(denominator):
            raise HealthSpatialError(f"non-finite value for area {area}")
        if denominator <= 0 or numerator < 0:
            raise HealthSpatialError(f"invalid numerator or denominator for area {area}")
        rows.append(
            {
                "area": area,
                "numerator": numerator,
                "denominator": denominator,
                "rate": numerator / denominator,
            }
        )
    return {
        "record_type": "bounded_descriptive_mapping",
        "rows": rows,
        "nonclaims": [
            "Rates describe supplied records only and are not clinical or causal estimates.",
            "No missing area is treated as a zero or negative finding.",
        ],
    }


def moran_i(values: Mapping[str, float], adjacency: Mapping[str, Sequence[str]]) -> dict[str, Any]:
    """Compute an unstandardized binary-weight Moran statistic for a closed graph."""
    areas = set(values)
    if not areas or set(adjacency) != areas:
        raise HealthSpatialError("values and adjacency must contain the same non-empty areas")
    edges = {
        (area, neighbour) for area, neighbours in adjacency.items() for neighbour in neighbours
    }
    if any(neighbour not in areas or area == neighbour for area, neighbour in edges):
        raise HealthSpatialError("adjacency contains an unknown or self neighbour")
    if any((neighbour, area) not in edges for area, neighbour in edges):
        raise HealthSpatialError("adjacency must be symmetric")
    if any(not math.isfinite(value) for value in values.values()):
        raise HealthSpatialError("values must be finite")
    mean = sum(values.values()) / len(values)
    deviations = {area: value - mean for area, value in values.items()}
    denominator = sum(deviation * deviation for deviation in deviations.values())
    weight_total = len(edges)
    if not denominator or not weight_total:
        raise HealthSpatialError("Moran statistic requires variation and at least one edge")
    numerator = sum(deviations[area] * deviations[neighbour] for area, neighbour in edges)
    return {
        "record_type": "bounded_spatial_autocorrelation",
        "statistic": len(areas) / weight_total * numerator / denominator,
        "area_count": len(areas),
        "edge_count": weight_total,
        "nonclaims": [
            (
                "The statistic is descriptive and does not establish spatial causation or "
                "significance."
            ),
            (
                "Inference requires a preregistered model, uncertainty method, and "
                "source-qualified data."
            ),
        ],
    }


def multilevel_ecological_summary(
    observations: Sequence[Mapping[str, Any]], *, group_field: str, value_field: str
) -> dict[str, Any]:
    """Summarize finite observations by group without fitting a causal model."""
    if not observations or not group_field or not value_field:
        raise HealthSpatialError("observations and field names are required")
    groups: dict[str, list[float]] = {}
    for observation in observations:
        group = observation.get(group_field)
        value = observation.get(value_field)
        if not isinstance(group, str) or not group:
            raise HealthSpatialError("group values must be non-empty strings")
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
        ):
            raise HealthSpatialError("outcome values must be finite numbers")
        groups.setdefault(group, []).append(float(value))
    rows = [
        {"group": group, "count": len(values), "mean": sum(values) / len(values)}
        for group, values in sorted(groups.items())
    ]
    return {
        "record_type": "bounded_ecological_group_summary",
        "groups": rows,
        "nonclaims": [
            "Grouped summaries do not support individual-level or causal interpretation.",
            (
                "Small-cell, missing-data, confounding, and measurement-error controls "
                "remain required."
            ),
        ],
    }
