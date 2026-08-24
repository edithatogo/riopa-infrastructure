import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError


def test_synthetic_health_analysis_design_is_explicit_and_non_clinical() -> None:
    root = Path(__file__).resolve().parents[1]
    schema = json.loads((root / "schemas/health-analysis-design.schema.json").read_text())
    fixture = json.loads((root / "fixtures/health-analysis-design-synthetic.json").read_text())
    Draft202012Validator(schema).validate(fixture)
    assert fixture["domain"] == "synthetic-non-clinical"
    assert fixture["estimand"] and fixture["limitations"]
    assert fixture["governance"]["clinical_claims_allowed"] is False
    assert fixture["missing_data"]["allowed"] is False


def test_health_analysis_design_rejects_clinical_domain() -> None:
    root = Path(__file__).resolve().parents[1]
    schema = json.loads((root / "schemas/health-analysis-design.schema.json").read_text())
    fixture = json.loads((root / "fixtures/health-analysis-design-synthetic.json").read_text())
    fixture["domain"] = "clinical"
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(fixture)


def test_health_analysis_design_requires_explicit_denominator_and_governance() -> None:
    root = Path(__file__).resolve().parents[1]
    schema = json.loads((root / "schemas/health-analysis-design.schema.json").read_text())
    fixture = json.loads((root / "fixtures/health-analysis-design-synthetic.json").read_text())
    fixture.pop("denominator")
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(fixture)
