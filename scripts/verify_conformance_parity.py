#!/usr/bin/env python3
"""Compare Python and Node outcomes for the bounded conformance corpus."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from riopa_provenance.canonical import validate_conformance_corpus
from riopa_provenance.hashing import sha256_json


def build_receipt(root: Path) -> dict[str, Any]:
    corpus_path = root / "conformance/v1/corpus.json"
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    corpus_errors = validate_conformance_corpus(corpus, root=str(root / "conformance/v1"))
    if corpus_errors:
        raise ValueError("invalid conformance corpus: " + "; ".join(corpus_errors))
    node = subprocess.run(
        ["node", "scripts/conformance_node.mjs", "conformance/v1/corpus.json"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    node_report = json.loads(node.stdout)
    python_results: list[dict[str, Any]] = []
    for case in corpus["cases"]:
        schema_valid = None
        if case["schema"] is not None:
            schema = json.loads(
                (root / "conformance/v1" / case["schema"]).read_text(encoding="utf-8")
            )
            schema_valid = not list(Draft202012Validator(schema).iter_errors(case["instance"]))
        python_results.append(
            {
                "case_id": case["case_id"],
                "sha256": sha256_json(case["instance"]),
                "schema_valid": schema_valid,
                "passed": sha256_json(case["instance"]) == case["expected_sha256"]
                and (case["expected_valid"] is None or schema_valid == case["expected_valid"]),
            }
        )
    node_results = node_report["results"]
    parity = python_results == [
        {
            "case_id": item["case_id"],
            "sha256": item["sha256"],
            "schema_valid": item["schema_valid"],
            "passed": item["passed"],
        }
        for item in node_results
    ]
    return {
        "corpus_version": corpus["corpus_version"],
        "case_count": len(corpus["cases"]),
        "runner": node_report["runner"],
        "node_runtime": node_report["runtime"],
        "python_passed": all(item["passed"] for item in python_results),
        "node_passed": all(item["passed"] for item in node_results),
        "parity": parity,
        "scope": "bounded canonical-hash and schema-outcome corpus",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    receipt = build_receipt(args.root.resolve())
    args.output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["python_passed"] and receipt["node_passed"] and receipt["parity"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
