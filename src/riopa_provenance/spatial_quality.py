"""Evaluate bounded spatial-quality reports without implying release qualification."""

from collections.abc import Mapping
from datetime import date
from typing import Any


class SpatialQualityError(ValueError):
    """Raised when a spatial-quality report cannot be evaluated safely."""


def evaluate_quality_waiver(waiver: Mapping[str, Any] | None, *, as_of: str) -> dict[str, Any]:
    """Evaluate a bounded quality waiver without permitting release bypass."""

    required = ("waiver_id", "metric_id", "rationale", "owner", "expires_on")
    errors: list[str] = []
    if not isinstance(waiver, Mapping):
        errors.append("waiver must be an object")
        waiver = {}
    for field in required:
        if not isinstance(waiver.get(field), str) or not str(waiver[field]).strip():
            errors.append(f"waiver requires {field}")
    try:
        review_date = date.fromisoformat(as_of)
        expiry = date.fromisoformat(str(waiver.get("expires_on", "")))
    except ValueError:
        errors.append("as_of and expires_on must be ISO dates")
        review_date = date.min
        expiry = date.min
    if expiry < review_date:
        errors.append("waiver is expired")
    if waiver.get("release_blocking") is True:
        errors.append("release-blocking metrics cannot be waived")
    status = "active" if not errors else "invalid-or-expired"
    return {
        "waiver_id": waiver.get("waiver_id"),
        "metric_id": waiver.get("metric_id"),
        "status": status,
        "errors": list(dict.fromkeys(errors)),
        "promotion_allowed": False,
        "source": "bounded-quality-waiver",
        "nonclaims": [
            "A waiver records bounded rationale and expiry; it does not establish quality, "
            "authority or release approval.",
            "Release-blocking metrics and expired waivers remain fail-closed.",
        ],
    }


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


def build_quality_benchmark_report(
    observations: list[Mapping[str, Any]],
    profile: Mapping[str, Any],
    *,
    profile_id: str,
    revision: str,
) -> dict[str, Any]:
    """Summarize bounded quality observations without creating a release gate."""

    if not observations:
        raise SpatialQualityError("observations must not be empty")
    if not profile_id.strip() or not revision.strip():
        raise SpatialQualityError("profile_id and revision must be non-empty")
    results: list[dict[str, Any]] = []
    for observation in observations:
        if not isinstance(observation, Mapping):
            raise SpatialQualityError("observations must contain objects")
        observation_id = observation.get("observation_id")
        report = observation.get("report")
        if not isinstance(observation_id, str) or not observation_id.strip():
            raise SpatialQualityError("observations require observation_id")
        if not isinstance(report, Mapping):
            raise SpatialQualityError("observations require report objects")
        result = evaluate_spatial_quality(
            report,
            profile,
            transformation_revision=observation.get("transformation_revision"),
            rights_disposition=observation.get("rights_disposition"),
        )
        results.append(
            {
                "observation_id": observation_id,
                "status": result["status"],
                "errors": result["errors"],
                "warnings": result["warnings"],
            }
        )
    results.sort(key=lambda item: item["observation_id"])
    passed = sum(item["status"] == "pass" for item in results)
    return {
        "record_type": "bounded_spatial_quality_benchmark",
        "profile_id": profile_id,
        "revision": revision,
        "observation_count": len(results),
        "passed_count": passed,
        "failed_count": len(results) - passed,
        "observations": results,
        "scale_class": "bounded-reference-or-archived-sample",
        "promotion_allowed": False,
        "nonclaims": [
            "This report summarizes supplied quality observations and does not establish "
            "real-council or national qualification.",
            "It does not establish source authority, operational readiness or release approval.",
        ],
    }
