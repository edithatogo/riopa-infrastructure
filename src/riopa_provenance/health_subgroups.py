"""Bounded subgroup and small-cell controls for public-preview methods."""

import math
from collections.abc import Mapping, Sequence
from typing import Any


class HealthSubgroupError(ValueError):
    """Raised when subgroup or disclosure-control inputs are invalid."""


def subgroup_summary(
    observations: Sequence[Mapping[str, Any]],
    *,
    group_field: str,
    value_field: str,
    minimum_cell_size: int,
) -> dict[str, Any]:
    """Return means while suppressing cells below an explicit minimum size."""
    if not observations or not group_field or not value_field or minimum_cell_size < 1:
        raise HealthSubgroupError(
            "observations, fields, and a positive minimum cell size are required"
        )
    groups: dict[str, list[float]] = {}
    for observation in observations:
        group = observation.get(group_field)
        value = observation.get(value_field)
        if not isinstance(group, str) or not group:
            raise HealthSubgroupError("group values must be non-empty strings")
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
        ):
            raise HealthSubgroupError("outcomes must be finite numbers")
        groups.setdefault(group, []).append(float(value))
    rows = []
    for group, values in sorted(groups.items()):
        count = len(values)
        rows.append(
            {
                "group": group,
                "count": count,
                "suppressed": count < minimum_cell_size,
                "mean": None if count < minimum_cell_size else sum(values) / count,
            }
        )
    return {
        "record_type": "bounded_subgroup_summary",
        "minimum_cell_size": minimum_cell_size,
        "rows": rows,
        "nonclaims": [
            "Suppression protects small cells but does not establish representativeness or equity.",
            "No suppressed cell is interpreted as zero, absence, or a negative finding.",
        ],
    }


def equity_gap(values_by_group: Mapping[str, float]) -> dict[str, Any]:
    """Report a descriptive max-min gap across already-qualified group values."""
    if len(values_by_group) < 2:
        raise HealthSubgroupError("at least two groups are required")
    if any(not group or not math.isfinite(value) for group, value in values_by_group.items()):
        raise HealthSubgroupError("groups must be named and values finite")
    ordered = sorted(values_by_group.items(), key=lambda item: (item[1], item[0]))
    return {
        "record_type": "bounded_subgroup_gap",
        "lowest_group": ordered[0][0],
        "highest_group": ordered[-1][0],
        "gap": ordered[-1][1] - ordered[0][1],
        "nonclaims": [
            "A descriptive gap is not an inequity attribution or policy recommendation.",
            "Comparability, uncertainty, confounding, and context must be assessed separately.",
        ],
    }
