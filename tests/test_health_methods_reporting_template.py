import json
from pathlib import Path


def test_health_reporting_template_is_complete_and_promotion_disabled() -> None:
    root = Path(__file__).resolve().parents[1]
    template = json.loads(
        (root / "docs/health-methods-reporting-template-20260825.json").read_text()
    )
    assert template["status"] == "bounded-candidate-not-stable-release"
    assert template["release_constraints"]["promotion_allowed"] is False
    assert len(template["required_sections"]) >= 8
    assert {"synthetic", "not-clinical", "not-causal"} <= set(template["required_labels"])
    assert template["release_constraints"]["requires_external_reproduction"] is True
