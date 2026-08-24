import pytest

from riopa_provenance.health_diagnostics import (
    HealthDiagnosticError,
    missingness_profile,
    negative_control_contrast,
)


def test_missingness_profile_is_not_negative_evidence() -> None:
    result = missingness_profile(
        [{"outcome": 1, "group": "a"}, {"outcome": None, "group": "b"}],
        fields=["outcome", "group"],
    )
    assert result["missing_by_field"] == {"outcome": 1, "group": 0}
    assert result["complete_case_count"] == 1
    assert result["nonclaims"]


def test_negative_control_contrast_requires_both_groups() -> None:
    result = negative_control_contrast(
        [{"exposed": True, "control": 3}, {"exposed": False, "control": 1}],
        exposure_field="exposed",
        control_outcome_field="control",
    )
    assert result["contrast"] == 2.0
    with pytest.raises(HealthDiagnosticError, match="both exposure groups"):
        negative_control_contrast(
            [{"exposed": True, "control": 3}],
            exposure_field="exposed",
            control_outcome_field="control",
        )
