import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError


def test_preregistration_labels_exploratory_and_reference_analyses() -> None:
    root = Path(__file__).resolve().parents[1]
    schema = json.loads((root / "schemas/analysis-preregistration.schema.json").read_text())
    packet = json.loads((root / "fixtures/analysis-preregistration-synthetic.json").read_text())
    Draft202012Validator(schema).validate(packet)
    assert {item["classification"] for item in packet["analyses"]} == {"reference", "exploratory"}
    assert all(item["decision_rule"] for item in packet["analyses"])


def test_preregistration_rejects_unclassified_analysis() -> None:
    root = Path(__file__).resolve().parents[1]
    schema = json.loads((root / "schemas/analysis-preregistration.schema.json").read_text())
    packet = json.loads((root / "fixtures/analysis-preregistration-synthetic.json").read_text())
    packet["analyses"][0]["classification"] = "unclassified"
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(packet)
