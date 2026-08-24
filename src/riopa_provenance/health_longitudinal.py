"""Bounded event-study reference contrasts for synthetic/public-preview data."""

import math
from collections import defaultdict
from collections.abc import Mapping, Sequence
from typing import Any


class HealthLongitudinalError(ValueError):
    """Raised when longitudinal reference inputs are incomplete or invalid."""


def event_study_contrasts(
    observations: Sequence[Mapping[str, Any]],
    *,
    period_field: str,
    treated_field: str,
    outcome_field: str,
    reference_period: int,
) -> dict[str, Any]:
    """Return baseline-adjusted treated/control mean contrasts by period.

    This is a reference calculation, not a causal estimator. It intentionally
    requires both groups at every period and a declared reference period.
    """
    if not observations or not all((period_field, treated_field, outcome_field)):
        raise HealthLongitudinalError("observations and field names are required")
    cells: dict[int, dict[bool, list[float]]] = defaultdict(lambda: {True: [], False: []})
    for observation in observations:
        period = observation.get(period_field)
        treated = observation.get(treated_field)
        outcome = observation.get(outcome_field)
        if not isinstance(period, int) or isinstance(period, bool) or not isinstance(treated, bool):
            raise HealthLongitudinalError("period must be an integer and treated must be boolean")
        if (
            not isinstance(outcome, (int, float))
            or isinstance(outcome, bool)
            or not math.isfinite(outcome)
        ):
            raise HealthLongitudinalError("outcome must be a finite number")
        cells[period][treated].append(float(outcome))
    if reference_period not in cells:
        raise HealthLongitudinalError("reference period is missing")

    raw: dict[int, float] = {}
    for period, groups in sorted(cells.items()):
        if not groups[True] or not groups[False]:
            raise HealthLongitudinalError(f"period {period} must contain both groups")
        raw[period] = sum(groups[True]) / len(groups[True]) - sum(groups[False]) / len(
            groups[False]
        )
    baseline = raw[reference_period]
    rows = [
        {
            "period": period,
            "raw_contrast": contrast,
            "baseline_adjusted_contrast": contrast - baseline,
            "is_reference": period == reference_period,
        }
        for period, contrast in raw.items()
    ]
    return {
        "record_type": "bounded_event_study_reference",
        "reference_period": reference_period,
        "contrasts": rows,
        "nonclaims": [
            "Contrasts are descriptive reference calculations and do not establish causality.",
            (
                "Parallel trends, anticipation, interference, missingness and temporal validity "
                "require separate evidence."
            ),
        ],
    }
