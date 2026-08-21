import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def test_operations_control_contract_is_schema_valid_and_fail_closed() -> None:
    schema = json.loads((ROOT / "schemas/operations-control.schema.json").read_text())
    record = json.loads((ROOT / "docs/operations-control-contract-20260822.json").read_text())
    errors = sorted(
        Draft202012Validator(schema).iter_errors(record), key=lambda error: list(error.path)
    )
    assert errors == []
    assert record["qualification_status"] == "candidate-not-measured"
    assert any("does not satisfy" in value for value in record["non_claims"])


def test_operations_control_contract_rejects_measured_status() -> None:
    schema = json.loads((ROOT / "schemas/operations-control.schema.json").read_text())
    record = json.loads((ROOT / "docs/operations-control-contract-20260822.json").read_text())
    record["qualification_status"] = "qualified"
    errors = list(Draft202012Validator(schema).iter_errors(record))
    assert any(list(error.path) == ["qualification_status"] for error in errors)


def test_operations_control_contract_rejects_unknown_transition_state() -> None:
    schema = json.loads((ROOT / "schemas/operations-control.schema.json").read_text())
    record = json.loads((ROOT / "docs/operations-control-contract-20260822.json").read_text())
    record["job_lifecycle"]["transitions"][0]["to"] = "unknown"
    errors = list(Draft202012Validator(schema).iter_errors(record))
    assert any(list(error.path) == ["job_lifecycle", "transitions", 0, "to"] for error in errors)
