"""Bounded sensitivity summaries for boundary and denominator revisions."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from math import isfinite
from typing import Any


class SpatialSensitivityError(ValueError):
    """Raised when a sensitivity comparison cannot be evaluated safely."""


def compare_revision_sensitivity(observations: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarise an estimate across declared boundary/denominator revisions.

    Every observation remains visible; the function never chooses a preferred
    revision and never interprets a range as uncertainty beyond the supplied
    estimates.  It is a bounded diagnostic for synthetic or archived inputs.
    """

    if not observations:
        raise SpatialSensitivityError("observations must be non-empty")
    normalised: list[dict[str, Any]] = []
    for item in observations:
        if not isinstance(item, Mapping):
            raise SpatialSensitivityError("each observation must be an object")
        required = ("analysis_id", "boundary_revision", "denominator_revision", "estimate")
        if any(
            not isinstance(item.get(field), str) or not str(item[field]).strip()
            for field in required[:3]
        ):
            raise SpatialSensitivityError(
                "analysis and revision identifiers must be non-empty strings"
            )
        estimate = item.get("estimate")
        if not isinstance(estimate, (int, float)) or not isfinite(float(estimate)):
            raise SpatialSensitivityError("estimate must be finite and numeric")
        normalised.append(
            {
                "analysis_id": item["analysis_id"],
                "boundary_revision": item["boundary_revision"],
                "denominator_revision": item["denominator_revision"],
                "estimate": float(estimate),
            }
        )
    estimates = [item["estimate"] for item in normalised]
    minimum = min(estimates)
    maximum = max(estimates)
    centre = abs((minimum + maximum) / 2)
    return {
        "status": "bounded-sensitive" if minimum != maximum else "bounded-stable",
        "observations": sorted(
            normalised,
            key=lambda item: (
                item["boundary_revision"],
                item["denominator_revision"],
                item["analysis_id"],
            ),
        ),
        "minimum": minimum,
        "maximum": maximum,
        "range": maximum - minimum,
        "relative_range": (maximum - minimum) / centre if centre else 0.0,
        "promotion_allowed": False,
        "nonclaims": [
            "The range is conditional on the supplied revisions and estimates.",
            "This does not establish a preferred boundary, denominator or causal effect.",
            (
                "Real boundary authority, denominator provenance and external qualification "
                "remain open."
            ),
        ],
    }
