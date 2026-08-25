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


_COMPARISON_FIELDS = (
    "estimand",
    "geography",
    "population_denominator",
    "facility_definition",
    "exclusions",
    "missing_data_policy",
)


def compare_declared_study_reference(
    reference_report: Mapping[str, Any],
    study_descriptor: Mapping[str, Any],
) -> dict[str, Any]:
    """Compare a reference report with a declared study descriptor.

    This is a structural comparison only.  It deliberately does not fetch a
    source, infer a motivating study's methods, or label a reference report as
    a reproduction.  Missing and differing fields remain visible so a future
    source-bounded comparison can be audited without silently filling gaps.
    """

    if not isinstance(reference_report, Mapping):
        raise SupermarketReferenceError("reference_report must be a mapping")
    if reference_report.get("record_type") != "supermarket-density-reference":
        raise SupermarketReferenceError(
            "reference_report must be a supermarket-density-reference record"
        )
    if not isinstance(study_descriptor, Mapping):
        raise SupermarketReferenceError("study_descriptor must be a mapping")
    if study_descriptor.get("record_type") != "declared-motivating-study":
        raise SupermarketReferenceError(
            "study_descriptor must be a declared-motivating-study record"
        )

    reference_fields = reference_report.get("comparison_fields", {})
    descriptor_fields = study_descriptor.get("comparison_fields", {})
    if not isinstance(reference_fields, Mapping) or not isinstance(descriptor_fields, Mapping):
        raise SupermarketReferenceError("comparison_fields must be mappings")

    matches: list[str] = []
    mismatches: list[str] = []
    missing_reference_fields: list[str] = []
    missing_descriptor_fields: list[str] = []
    for field in _COMPARISON_FIELDS:
        in_reference = field in reference_fields
        in_descriptor = field in descriptor_fields
        if not in_reference:
            missing_reference_fields.append(field)
        if not in_descriptor:
            missing_descriptor_fields.append(field)
        if in_reference and in_descriptor:
            if reference_fields[field] == descriptor_fields[field]:
                matches.append(field)
            else:
                mismatches.append(field)

    if missing_reference_fields or missing_descriptor_fields or mismatches:
        comparison_status = "descriptor-mismatch-or-incomplete"
    else:
        comparison_status = "descriptor-aligned-not-reproduced"
    return {
        "record_type": "supermarket-study-comparison",
        "comparison_status": comparison_status,
        "reference_record_type": reference_report["record_type"],
        "study_descriptor_id": study_descriptor.get("study_id"),
        "matches": matches,
        "mismatches": mismatches,
        "missing_reference_fields": missing_reference_fields,
        "missing_descriptor_fields": missing_descriptor_fields,
        "claim_classification": "reference-only",
        "promotion_allowed": False,
        "nonclaims": [
            "This compares declared fields only; it does not reproduce a motivating study.",
            (
                "No source payload, health outcome, causal, commercial, national or "
                "operational claim is enabled."
            ),
            "Missing fields and disagreement are not evidence of source absence or study error.",
        ],
    }


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
