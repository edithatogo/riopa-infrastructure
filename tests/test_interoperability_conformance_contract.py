import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def test_interoperability_contract_is_schema_valid() -> None:
    schema = json.loads(
        (ROOT / "schemas/interoperability-conformance-contract.schema.json").read_text()
    )
    record = json.loads(
        (ROOT / "docs/interoperability-conformance-contract-20260822.json").read_text()
    )
    assert list(Draft202012Validator(schema).iter_errors(record)) == []
    assert record["corpus"]["case_classes"] == ["positive", "negative", "migration"]


def test_corpus_has_normative_case_classes() -> None:
    corpus = json.loads((ROOT / "conformance/v1/corpus.json").read_text())
    assert {case["case_class"] for case in corpus["cases"]} == {"positive", "negative", "migration"}


def test_interoperability_contract_rejects_single_runner() -> None:
    schema = json.loads(
        (ROOT / "schemas/interoperability-conformance-contract.schema.json").read_text()
    )
    record = json.loads(
        (ROOT / "docs/interoperability-conformance-contract-20260822.json").read_text()
    )
    record["corpus"]["runners"] = ["Python reference validator"]
    errors = list(Draft202012Validator(schema).iter_errors(record))
    assert any(list(error.path) == ["corpus", "runners"] for error in errors)
