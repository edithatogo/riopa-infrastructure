from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from riopa_provenance.hashing import sha256_json


def _corpus() -> tuple[Path, dict[str, Any]]:
    root = Path(__file__).resolve().parents[1]
    path = root / "conformance/v1/corpus.json"
    return root, json.loads(path.read_text(encoding="utf-8"))


def test_python_reference_passes_language_neutral_corpus() -> None:
    root, corpus = _corpus()
    for case in corpus["cases"]:
        assert sha256_json(case["instance"]) == case["expected_sha256"]
        if case["schema"] is not None:
            schema_path = (root / "conformance/v1" / case["schema"]).resolve()
            validator = Draft202012Validator(json.loads(schema_path.read_text()))
            errors = list(validator.iter_errors(case["instance"]))
            assert (not errors) is case["expected_valid"]


def test_node_implementation_matches_python_outcomes() -> None:
    root, corpus = _corpus()
    result = subprocess.run(
        ["node", "scripts/conformance_node.mjs", "conformance/v1/corpus.json"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(result.stdout)
    assert report["runner"] == "node-standard-library"
    assert [item["case_id"] for item in report["results"]] == [
        item["case_id"] for item in corpus["cases"]
    ]
    assert all(item["passed"] for item in report["results"])


def test_minimal_rights_inventory_is_schema_valid_and_fail_closed_when_unresolved() -> None:
    root, _ = _corpus()
    schema = json.loads((root / "schemas/rights-inventory.schema.json").read_text())
    inventory = json.loads((root / "examples/minimal/rights-inventory.json").read_text())
    assert not list(Draft202012Validator(schema).iter_errors(inventory))
    inventory["sources"][0]["redistribution_status"] = "review-required"
    inventory["publication_decision"] = "review-required"
    assert inventory["publication_decision"] == "review-required"
