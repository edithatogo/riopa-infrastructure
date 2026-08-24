import pytest

from riopa_provenance.health_sensitivity import (
    HealthSensitivityError,
    maup_sensitivity,
    measurement_error_sensitivity,
    spatial_confounding_sensitivity,
)


def test_spatial_confounding_sensitivity_is_descriptive() -> None:
    result = spatial_confounding_sensitivity(
        [
            {"exposed": True, "outcome": 4, "zone": "urban"},
            {"exposed": False, "outcome": 2, "zone": "urban"},
            {"exposed": True, "outcome": 3, "zone": "rural"},
            {"exposed": False, "outcome": 1, "zone": "rural"},
        ],
        exposure_field="exposed",
        outcome_field="outcome",
        confounder_field="zone",
    )
    assert result["crude_contrast"] == 2.0
    assert result["stratified_range"] == 0.0
    assert result["nonclaims"]


def test_maup_requires_multiple_named_scales() -> None:
    result = maup_sensitivity({"meshblock": 0.4, "district": 0.6})
    assert result["range"] == 0.19999999999999996
    with pytest.raises(HealthSensitivityError, match="two spatial scales"):
        maup_sensitivity({"meshblock": 0.4})


def test_measurement_error_returns_symmetric_mean_bounds() -> None:
    result = measurement_error_sensitivity([1.0, 3.0], absolute_error=0.25)
    assert result["observed_mean"] == 2.0
    assert result["lower_mean"] == 1.75
    assert result["upper_mean"] == 2.25
