"""Compare versioned spatial-quality evaluations without making release claims."""

from collections.abc import Mapping, Sequence
from math import isfinite
from typing import Any


class SpatialQualityTrendError(ValueError):
    """Raised when a quality trend cannot be compared safely."""


def classify_change_attribution(
    baseline: Mapping[str, Any], candidate: Mapping[str, Any]
) -> dict[str, Any]:
    """Classify declared revision changes without inferring undocumented causes."""

    axes = ("source_revision", "transformation_revision", "schema_revision", "boundary_revision")
    changed = [axis for axis in axes if baseline.get(axis) != candidate.get(axis)]
    missing = [axis for axis in axes if axis not in baseline or axis not in candidate]
    if len(changed) == 1:
        attribution = changed[0].removesuffix("_revision")
        status = "single-declared-cause"
    elif len(changed) > 1:
        attribution = None
        status = "multiple-possible-causes"
    else:
        attribution = None
        status = "no-declared-change" if not missing else "insufficient-declarations"
    return {
        "status": status,
        "candidate_cause": attribution,
        "changed_axes": changed,
        "missing_axes": missing,
        "promotion_allowed": False,
        "nonclaims": [
            "Declared revision differences do not prove causal provenance.",
            "A missing revision axis is not evidence that the corresponding layer did not change.",
        ],
    }


def build_spatial_quality_trend(
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
    *,
    tolerances: Mapping[str, float] | None = None,
    higher_is_better: Mapping[str, bool] | None = None,
) -> dict[str, Any]:
    """Return deterministic metric deltas and regression flags.

    Inputs are evaluator-shaped reports with a ``metrics`` list. Missing or
    malformed metrics fail closed. This is a diagnostic trend report only;
    it never authorises promotion.
    """
    base = _metric_map(baseline.get("metrics"))
    current = _metric_map(candidate.get("metrics"))
    if set(base) != set(current):
        missing = sorted(set(base) - set(current))
        added = sorted(set(current) - set(base))
        raise SpatialQualityTrendError(f"metric sets differ (missing={missing}, added={added})")
    limits = tolerances or {}
    directions = higher_is_better or {}
    changes: list[dict[str, Any]] = []
    regressions: list[str] = []
    for metric_id in sorted(base):
        before = base[metric_id]
        after = current[metric_id]
        delta = after - before
        tolerance = limits.get(metric_id, 0.0)
        if tolerance < 0 or not isfinite(tolerance):
            raise SpatialQualityTrendError(f"invalid tolerance for {metric_id}")
        better = directions.get(metric_id, False)
        regressed = delta < -tolerance if better else delta > tolerance
        changes.append(
            {
                "id": metric_id,
                "baseline": before,
                "candidate": after,
                "delta": delta,
                "tolerance": tolerance,
                "higher_is_better": better,
                "regression": regressed,
            }
        )
        if regressed:
            regressions.append(metric_id)
    return {
        "status": "regression" if regressions else "stable",
        "baseline_revision": baseline.get("revision"),
        "candidate_revision": candidate.get("revision"),
        "changes": changes,
        "regressions": regressions,
        "promotion_allowed": False,
        "nonclaims": [
            "A trend result is diagnostic, not national completeness or operational evidence.",
            "Promotion still requires external, elapsed-time and authority gates.",
        ],
    }


def _metric_map(metrics: Any) -> dict[str, float]:
    if not isinstance(metrics, Sequence) or isinstance(metrics, (str, bytes)):
        raise SpatialQualityTrendError("metrics must be a sequence")
    result: dict[str, float] = {}
    for item in metrics:
        if not isinstance(item, Mapping):
            raise SpatialQualityTrendError("each metric must be an object")
        metric_id = item.get("id")
        observed = item.get("observed")
        if not isinstance(metric_id, str) or not metric_id:
            raise SpatialQualityTrendError("metric id must be a non-empty string")
        if metric_id in result or not isinstance(observed, (int, float)):
            raise SpatialQualityTrendError(f"invalid or duplicate metric: {metric_id}")
        if not isfinite(float(observed)):
            raise SpatialQualityTrendError(f"metric {metric_id} must be finite")
        result[metric_id] = float(observed)
    return result
