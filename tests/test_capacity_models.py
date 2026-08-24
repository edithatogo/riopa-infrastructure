import pytest

from riopa_provenance.capacity_models import (
    CapacityModelError,
    classify_bottlenecks,
    evaluate_capacity_resilience,
    project_capacity,
    validate_capacity_model,
)

MODEL = {
    "base_units": 100,
    "base_seconds": 10,
    "unit_seconds": 2,
    "base_cost": 1.0,
    "unit_cost": 0.05,
    "max_units": 1000,
}


def test_capacity_projection_is_bounded_and_deterministic() -> None:
    assert validate_capacity_model(MODEL) == ()
    assert project_capacity(MODEL, 200) == {
        "units": 200.0,
        "projected_seconds": 14.0,
        "projected_cost": 1.1,
    }


def test_capacity_model_rejects_invalid_values_and_silent_extrapolation() -> None:
    invalid = dict(MODEL, base_units=0)
    assert any("base_units must be positive" in error for error in validate_capacity_model(invalid))
    with pytest.raises(CapacityModelError, match="exceed"):
        project_capacity(MODEL, 1001)


def test_bottleneck_classification_is_diagnostic_and_fail_closed() -> None:
    result = classify_bottlenecks(
        {
            "latency_ratio": 1.2,
            "throughput_ratio": 0.8,
            "memory_ratio": 1.0,
            "error_rate": 0.0,
        }
    )
    assert result["bottlenecks"] == ["latency", "throughput"]
    assert result["non_assertive"] is True
    with pytest.raises(CapacityModelError, match="finite"):
        classify_bottlenecks({"latency_ratio": "unknown"})


def test_capacity_resilience_tracks_backup_and_reserve_gap() -> None:
    assert evaluate_capacity_resilience(
        demand_units=100,
        primary_capacity=80,
        backup_capacity=40,
        backup_available=True,
        reserve_target=10,
    ) == {
        "demand_units": 100,
        "available_primary": 80,
        "available_backup": 40,
        "available_capacity": 120,
        "served_units": 100,
        "unmet_units": 0,
        "reserve_after_service": 20,
        "reserve_gap": 0,
        "fail_closed": False,
        "non_assertive": True,
        "source": "bounded-synthetic-capacity",
    }
    degraded = evaluate_capacity_resilience(
        demand_units=100,
        primary_capacity=80,
        backup_capacity=40,
        backup_available=False,
        reserve_target=10,
    )
    assert degraded["unmet_units"] == 20
    assert degraded["fail_closed"] is True


def test_capacity_resilience_rejects_non_boolean_availability() -> None:
    with pytest.raises(CapacityModelError, match="booleans"):
        evaluate_capacity_resilience(
            demand_units=1,
            primary_capacity=1,
            backup_capacity=1,
            primary_available=1,  # type: ignore[arg-type]
        )
