"""Fail-closed missingness and negative-control diagnostics."""

import math
from collections.abc import Mapping, Sequence
from typing import Any


class HealthDiagnosticError(ValueError):
    """Raised when diagnostic inputs are incomplete or invalid."""


def missingness_profile(
    observations: Sequence[Mapping[str, Any]], *, fields: Sequence[str]
) -> dict[str, Any]:
    """Count missing values without converting missingness into outcomes."""
    if not observations or not fields or any(not field for field in fields):
        raise HealthDiagnosticError("observations and non-empty fields are required")
    counts = {
        field: sum(1 for observation in observations if observation.get(field) is None)
        for field in fields
    }
    complete = sum(
        all(observation.get(field) is not None for field in fields) for observation in observations
    )
    return {
        "record_type": "bounded_missingness_profile",
        "observation_count": len(observations),
        "missing_by_field": counts,
        "complete_case_count": complete,
        "nonclaims": [
            "Missing values are pending information, not negative outcomes.",
            "Mechanism, imputation, selection, and sensitivity require a preregistered plan.",
        ],
    }


def negative_control_contrast(
    observations: Sequence[Mapping[str, Any]],
    *,
    exposure_field: str,
    control_outcome_field: str,
) -> dict[str, Any]:
    """Compute an exposure contrast for a declared negative-control outcome."""
    if not observations or not exposure_field or not control_outcome_field:
        raise HealthDiagnosticError("observations and field names are required")
    groups: dict[bool, list[float]] = {True: [], False: []}
    for observation in observations:
        exposure = observation.get(exposure_field)
        value = observation.get(control_outcome_field)
        if not isinstance(exposure, bool):
            raise HealthDiagnosticError("exposure must be boolean")
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
        ):
            raise HealthDiagnosticError("control outcome must be a finite number")
        groups[exposure].append(float(value))
    if not groups[True] or not groups[False]:
        raise HealthDiagnosticError("negative control requires both exposure groups")
    contrast = sum(groups[True]) / len(groups[True]) - sum(groups[False]) / len(groups[False])
    return {
        "record_type": "bounded_negative_control_contrast",
        "contrast": contrast,
        "treated_count": len(groups[True]),
        "untreated_count": len(groups[False]),
        "nonclaims": [
            "A non-zero contrast is a diagnostic signal, not proof of bias or causality.",
            "The control outcome must be justified independently and analysed with uncertainty.",
        ],
    }
