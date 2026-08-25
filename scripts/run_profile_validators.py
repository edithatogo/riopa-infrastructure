"""Run pinned repository-available profile validators and retain a receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
from importlib.metadata import version
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from validate_canonical_shacl import validate_fixture


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_report(root: Path) -> dict[str, Any]:
    schema_path = root / "schemas/source-record.schema.json"
    instance_path = root / "examples/minimal/source-record.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    instance = json.loads(instance_path.read_text(encoding="utf-8"))
    schema_errors = tuple(
        error.message
        for error in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(
            instance
        )
    )
    shacl = validate_fixture(
        root / "fixtures/canonical-crosswalk-golden.json",
        root / "docs/ontology/canonical-crosswalk.shacl.ttl",
    )
    return {
        "schema": "riopa.research-object-profile-validation.v1",
        "evidence_id": "urn:riopa:evidence:research-object-profile-validation:2026-08-25",
        "status": "bounded-tooling-validation",
        "runtime": {
            "python": "3.14 only",
            "jsonschema": version("jsonschema"),
            "pyshacl": version("pyshacl"),
            "rdflib": version("rdflib"),
        },
        "checks": [
            {
                "profile": "JSON Schema Draft 2020-12",
                "schema": str(schema_path.relative_to(root)),
                "schema_sha256": _sha256(schema_path),
                "instance": str(instance_path.relative_to(root)),
                "instance_sha256": _sha256(instance_path),
                "passed": not schema_errors,
                "errors": list(schema_errors),
            },
            {
                "profile": "RDF/SHACL canonical crosswalk fixture",
                "report": "docs/canonical-shacl-execution-report-20260825.json",
                "fixture_sha256": shacl["fixture_sha256"],
                "shape_sha256": shacl["shape_sha256"],
                "passed": shacl["conforms"],
                "errors": [] if shacl["conforms"] else [shacl["results_text"]],
            },
        ],
        "external_acceptance": False,
        "promotion_allowed": False,
        "open_gates": [
            "external profile-validator or non-Python implementation acceptance",
            "complete real-data release candidate",
            "signed preservation/deposition",
            "external reproduction and accountable release authority",
        ],
        "nonclaims": [
            "Repository-executed validators demonstrate bounded tooling compatibility only.",
            (
                "A passing local validator is not external semantic, publication or authority "
                "approval."
            ),
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build_report(args.root.resolve())
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if all(check["passed"] for check in report["checks"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
