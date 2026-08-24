"""Evaluate bounded spatial-quality reports without implying release qualification."""

from collections.abc import Mapping
from typing import Any


class SpatialQualityError(ValueError):
    """Raised when a spatial-quality report cannot be evaluated safely."""


def evaluate_spatial_quality(
    report: Mapping[str, Any],
    profile: Mapping[str, Any],
    *,
    transformation_revision: str | None = None,
    rights_disposition: str | None = None,
) -> dict[str, Any]:
    """Return a fail-closed evaluation of a synthetic or archived report.

    The evaluator is deliberately not a release gate: even a passing result has
    ``promotion_allowed=False`` until the applicable external and elapsed-time
    evidence exists.
    """
    metrics = profile.get("metrics")
    if not isinstance(metrics, list):
        raise SpatialQualityError("profile.metrics must be a list")

    values = {
        "geometry_validity": report.get("invalid_geometry_count_before_repair", 0),
        "geometry_repair": report.get("repaired_geometry_count", 0),
        "null_geometry": report.get("null_geometry_count", 0),
        "stable_identity": report.get("duplicate_feature_id_count", 0),
        "source_lineage": 1.0 if report.get("source_id") and report.get("capture_ids") else 0.0,
    }
    errors: list[str] = []
    warnings: list[str] = []
    evaluated: list[dict[str, Any]] = []
    for metric in metrics:
        if not isinstance(metric, Mapping):
            raise SpatialQualityError("each profile metric must be an object")
        metric_id = metric.get("id")
        if metric_id not in values:
            raise SpatialQualityError(f"unsupported profile metric: {metric_id}")
        observed = values[metric_id]
        threshold_spec = metric.get("threshold")
        if isinstance(threshold_spec, Mapping):
            threshold = threshold_spec.get("minimum", threshold_spec.get("warning"))
            comparator = "gte" if "minimum" in threshold_spec else "lte"
            release_block = bool(threshold_spec.get("release_block", False))
        else:
            threshold = threshold_spec
            comparator = metric.get("comparator", "eq")
            release_block = bool(metric.get("release_block", False))
        if threshold is None:
            raise SpatialQualityError(f"metric {metric_id} has no evaluable threshold")
        passed = (
            observed == threshold
            if comparator == "eq"
            else observed <= threshold
            if comparator == "lte"
            else observed >= threshold
            if comparator == "gte"
            else None
        )
        if passed is None:
            raise SpatialQualityError(f"unsupported comparator: {comparator}")
        item = {"id": metric_id, "observed": observed, "threshold": threshold, "passed": passed}
        evaluated.append(item)
        if not passed:
            if release_block:
                errors.append(f"{metric_id} failed")
            else:
                warnings.append(f"{metric_id} outside preferred bound")

    missing_evidence: list[str] = []
    if not transformation_revision:
        missing_evidence.append("transformation_revision")
    if not rights_disposition:
        missing_evidence.append("rights_disposition")
    if missing_evidence:
        errors.append("missing required evidence: " + ", ".join(missing_evidence))

    return {
        "status": "pass" if not errors else "fail",
        "promotion_allowed": False,
        "metrics": evaluated,
        "errors": errors,
        "warnings": warnings,
        "nonclaims": [
            "Does not establish source authority, national completeness, or operational readiness.",
            "Does not replace external operator or accountable release-authority evidence.",
        ],
    }
