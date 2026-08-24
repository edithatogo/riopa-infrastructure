import json
from pathlib import Path

from riopa_provenance.health_longitudinal import event_study_contrasts


def test_synthetic_opening_and_closure_scenarios_execute() -> None:
    root = Path(__file__).resolve().parents[1]
    payload = json.loads(
        (root / "fixtures/health-longitudinal-scenarios-synthetic.json").read_text()
    )
    assert {scenario["event"] for scenario in payload["scenarios"]} == {"opening", "closure"}
    for scenario in payload["scenarios"]:
        result = event_study_contrasts(
            scenario["observations"],
            period_field="period",
            treated_field="treated",
            outcome_field="outcome",
            reference_period=scenario["reference_period"],
        )
        assert result["contrasts"][0]["baseline_adjusted_contrast"] == 0.0
        assert result["nonclaims"]
