import pytest

from riopa_provenance.spatial_quality_trend import (
    SpatialQualityTrendError,
    build_spatial_quality_trend,
    classify_change_attribution,
)


def _report(revision: str, validity: float, repairs: float) -> dict:
    return {
        "revision": revision,
        "metrics": [
            {"id": "geometry_validity", "observed": validity},
            {"id": "geometry_repair", "observed": repairs},
        ],
    }


def test_trend_marks_directional_regression_and_never_promotes() -> None:
    result = build_spatial_quality_trend(
        _report("baseline", 0.99, 2),
        _report("candidate", 0.97, 3),
        tolerances={"geometry_validity": 0.005, "geometry_repair": 0},
        higher_is_better={"geometry_validity": True},
    )
    assert result["status"] == "regression"
    assert result["regressions"] == ["geometry_repair", "geometry_validity"]
    assert result["promotion_allowed"] is False


def test_trend_accepts_changes_within_tolerance() -> None:
    result = build_spatial_quality_trend(
        _report("baseline", 0.99, 2),
        _report("candidate", 0.987, 2.1),
        tolerances={"geometry_validity": 0.005, "geometry_repair": 0.2},
        higher_is_better={"geometry_validity": True},
    )
    assert result["status"] == "stable"
    assert result["regressions"] == []


def test_trend_fails_closed_on_metric_mismatch() -> None:
    with pytest.raises(SpatialQualityTrendError, match="metric sets differ"):
        build_spatial_quality_trend(_report("a", 1, 0), {"metrics": []})


def test_change_attribution_is_declared_and_ambiguous_by_default() -> None:
    baseline = {
        "source_revision": "source-a",
        "transformation_revision": "transform-a",
        "schema_revision": "schema-a",
        "boundary_revision": "boundary-a",
    }
    candidate = {**baseline, "transformation_revision": "transform-b"}
    result = classify_change_attribution(baseline, candidate)
    assert result["status"] == "single-declared-cause"
    assert result["candidate_cause"] == "transformation"
    ambiguous = classify_change_attribution(baseline, {**candidate, "source_revision": "source-b"})
    assert ambiguous["status"] == "multiple-possible-causes"
    assert ambiguous["candidate_cause"] is None
    assert ambiguous["promotion_allowed"] is False
