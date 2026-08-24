"""Bounded boundary crosswalk and population interpolation contracts."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from math import isclose, isfinite
from typing import Any


class CrosswalkError(ValueError):
    """Raised when a boundary crosswalk cannot be used safely."""


def validate_boundary_crosswalk(
    crosswalk: Sequence[Mapping[str, Any]], *, tolerance: float = 1e-9
) -> tuple[str, ...]:
    """Validate source/target identities, revisions and conservative weights."""

    if tolerance < 0 or not isfinite(tolerance):
        return ("tolerance must be finite and non-negative",)
    errors: list[str] = []
    totals: dict[str, float] = defaultdict(float)
    if not crosswalk:
        return ("crosswalk must not be empty",)
    for index, row in enumerate(crosswalk):
        if not isinstance(row, Mapping):
            errors.append(f"row {index} must be an object")
            continue
        for field in ("source_id", "target_id", "source_revision", "target_revision"):
            if not isinstance(row.get(field), str) or not str(row[field]).strip():
                errors.append(f"row {index} {field} must be a non-empty string")
        weight = row.get("weight")
        if not isinstance(weight, (int, float)) or not isfinite(float(weight)):
            errors.append(f"row {index} weight must be finite")
        elif weight < 0 or weight > 1:
            errors.append(f"row {index} weight must be between 0 and 1")
        elif isinstance(row.get("source_id"), str):
            totals[row["source_id"]] += float(weight)
    for source_id, total in sorted(totals.items()):
        if not isclose(total, 1.0, abs_tol=tolerance):
            errors.append(f"source {source_id} weights must sum to 1 (found {total:g})")
    return tuple(errors)


def interpolate_population(
    source_population: Mapping[str, float],
    crosswalk: Sequence[Mapping[str, Any]],
    *,
    tolerance: float = 1e-9,
) -> dict[str, Any]:
    """Interpolate source population to targets using a validated crosswalk."""

    errors = validate_boundary_crosswalk(crosswalk, tolerance=tolerance)
    if errors:
        raise CrosswalkError("invalid boundary crosswalk: " + "; ".join(errors))
    missing = sorted(set(source_population) - {str(row["source_id"]) for row in crosswalk})
    if missing:
        raise CrosswalkError("source population has no crosswalk rows: " + ", ".join(missing))
    if any(
        not isinstance(value, (int, float)) or not isfinite(float(value)) or value < 0
        for value in source_population.values()
    ):
        raise CrosswalkError("source population values must be finite and non-negative")
    totals: dict[str, float] = defaultdict(float)
    for row in crosswalk:
        source_id = str(row["source_id"])
        target_id = str(row["target_id"])
        totals[target_id] += float(source_population[source_id]) * float(row["weight"])
    revisions = sorted({f"{row['source_revision']}->{row['target_revision']}" for row in crosswalk})
    return {
        "values": dict(sorted(totals.items())),
        "source_count": len(source_population),
        "target_count": len(totals),
        "revision_pairs": revisions,
        "promotion_allowed": False,
        "nonclaims": [
            "Interpolation is a weighted projection, not a geometry or legal-boundary assertion.",
            (
                "Results do not establish national completeness, MAUP robustness or "
                "denominator authority."
            ),
        ],
    }
