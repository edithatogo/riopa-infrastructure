import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def test_repository_template_contract_is_schema_valid_and_additive() -> None:
    schema = json.loads((ROOT / "schemas/repository-template-contract.schema.json").read_text())
    record = json.loads((ROOT / "docs/repository-template-contract-20260822.json").read_text())
    assert list(Draft202012Validator(schema).iter_errors(record)) == []
    assert "raw source bytes" in record["generated_boundaries"]["never_overwrite"]
    assert any("not evidence" in value for value in record["non_claims"])


def test_repository_template_contract_requires_brownfield_preservation() -> None:
    schema = json.loads((ROOT / "schemas/repository-template-contract.schema.json").read_text())
    record = json.loads((ROOT / "docs/repository-template-contract-20260822.json").read_text())
    record["mode_contract"]["brownfield"] = []
    errors = list(Draft202012Validator(schema).iter_errors(record))
    assert any(list(error.path) == ["mode_contract", "brownfield"] for error in errors)
