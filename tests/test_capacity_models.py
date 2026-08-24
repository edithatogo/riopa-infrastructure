import pytest

from riopa_provenance.capacity_models import (
    CapacityModelError,
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
