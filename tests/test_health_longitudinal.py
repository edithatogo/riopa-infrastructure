import pytest

from riopa_provenance.health_longitudinal import HealthLongitudinalError, event_study_contrasts


def test_event_study_contrasts_are_baseline_adjusted() -> None:
    result = event_study_contrasts(
        [
            {"period": 0, "treated": True, "outcome": 3},
            {"period": 0, "treated": False, "outcome": 2},
            {"period": 1, "treated": True, "outcome": 6},
            {"period": 1, "treated": False, "outcome": 3},
        ],
        period_field="period",
        treated_field="treated",
        outcome_field="outcome",
        reference_period=0,
    )
    assert result["contrasts"] == [
        {"period": 0, "raw_contrast": 1.0, "baseline_adjusted_contrast": 0.0, "is_reference": True},
        {
            "period": 1,
            "raw_contrast": 3.0,
            "baseline_adjusted_contrast": 2.0,
            "is_reference": False,
        },
    ]
    assert result["nonclaims"]


def test_event_study_requires_both_groups_and_reference() -> None:
    with pytest.raises(HealthLongitudinalError, match="both groups"):
        event_study_contrasts(
            [{"period": 0, "treated": True, "outcome": 1}],
            period_field="period",
            treated_field="treated",
            outcome_field="outcome",
            reference_period=0,
        )
