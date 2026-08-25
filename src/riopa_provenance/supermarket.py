"""Fail-closed supermarket density reference calculations.

The calculation operates only on caller-supplied area counts and denominators.
It is a descriptive reference helper, not a supermarket catalogue, population
estimate, health analysis, or evidence of source completeness.
"""

from __future__ import annotations

from collections.abc import Mapping
from math import isfinite
from typing import Any


class SupermarketReferenceError(ValueError):
    """Raised when a supplied reference value is not usable."""


def build_density_reference(
    supermarket_counts: Mapping[str, int],
    population: Mapping[str, float],
    *,
    per_population: float = 1_000.0,
) -> dict[str, Any]:
    """Build deterministic area-level supermarket density reference rows.

    The union of area identifiers is retained. A missing facility count or
    denominator produces a ``missing`` row with no density; it is never treated
    as zero. This keeps source coverage and denominator coverage observable.
    """

    if not isfinite(per_population) or per_population <= 0:
        raise SupermarketReferenceError("per_population must be finite and positive")
    for area, count in supermarket_counts.items():
        if not isinstance(area, str) or not area:
            raise SupermarketReferenceError("area identifiers must be non-empty strings")
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise SupermarketReferenceError("supermarket counts must be non-negative integers")
    for area, value in population.items():
        if not isinstance(area, str) or not area:
            raise SupermarketReferenceError("area identifiers must be non-empty strings")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise SupermarketReferenceError("population values must be finite numbers")
        if not isfinite(float(value)) or value <= 0:
            raise SupermarketReferenceError("population values must be finite and positive")

    rows: list[dict[str, Any]] = []
    for area in sorted(set(supermarket_counts) | set(population)):
        has_facilities = area in supermarket_counts
        has_population = area in population
        if not has_facilities or not has_population:
            rows.append(
                {
                    "area": area,
                    "status": "missing",
                    "facility_count": supermarket_counts.get(area),
                    "population": population.get(area),
                    "density_per_population": None,
                }
            )
            continue
        rows.append(
            {
                "area": area,
                "status": "observed",
                "facility_count": supermarket_counts[area],
                "population": float(population[area]),
                "density_per_population": supermarket_counts[area]
                / float(population[area])
                * per_population,
            }
        )
    observed = sum(row["status"] == "observed" for row in rows)
    return {
        "record_type": "supermarket-density-reference",
        "per_population": per_population,
        "rows": rows,
        "area_count": len(rows),
        "observed_area_count": observed,
        "missing_area_count": len(rows) - observed,
        "claim_classification": "reference-only",
        "promotion_allowed": False,
        "nonclaims": [
            "Rows describe caller-supplied counts and denominators only.",
            (
                "Missing facility or denominator coverage is not evidence of absence or zero "
                "population."
            ),
            (
                "This does not reproduce a motivating study or establish health, causal, "
                "national-scale or operational claims."
            ),
        ],
    }
