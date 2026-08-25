"""Build a deterministic semantic-loss and migration findings ledger."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def build_findings(matrix_path: str | Path) -> dict[str, Any]:
    """Translate recorded compatibility observations into fail-closed findings."""

    matrix = json.loads(Path(matrix_path).read_text(encoding="utf-8"))
    implementations = matrix.get("implementations", [])
    rust = next((item for item in implementations if item.get("language") == "Rust"), None)
    compatibility = matrix.get("compatibility", {})
    findings = [
        {
            "finding_id": "migration-corpus",
            "category": "migration",
            "status": "resolved" if compatibility.get("migration_cases_included") else "open",
            "evidence": "conformance/v1/corpus.json",
        },
        {
            "finding_id": "rust-corpus-parity",
            "category": "semantic-loss",
            "status": "open" if not rust or not rust.get("parity") else "resolved",
            "evidence": "docs/ontology/interoperability-compatibility-matrix-20260825.json",
            "limitation": "Typed Rust model does not yet parse the JSON corpus.",
        },
        {
            "finding_id": "external-producer-consumer",
            "category": "interoperability",
            "status": "open"
            if compatibility.get("external_producer_consumer") != "observed-pass"
            else "resolved",
            "evidence": "external evidence not present in the repository matrix",
        },
        {
            "finding_id": "standards-round-trip",
            "category": "semantic-loss",
            "status": "open"
            if compatibility.get("standards_round_trip") != "observed-pass"
            else "resolved",
            "evidence": "docs/interoperability-standards-roundtrip-contract-20260825.json",
        },
    ]
    return {
        "schema_version": "1.0.0",
        "record_type": "interoperability_findings_ledger",
        "matrix_version": matrix.get("matrix_version"),
        "findings": findings,
        "resolution_policy": "Only recorded observed-pass evidence can resolve a finding.",
        "open_finding_count": sum(item["status"] == "open" for item in findings),
        "promotion_allowed": False,
        "non_claims": [
            "This is a repository-owned findings ledger, not independent conformance evidence.",
            "Open findings remain open when evidence is absent or not observed.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--matrix",
        default="docs/ontology/interoperability-compatibility-matrix-20260825.json",
    )
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(build_findings(args.matrix), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Interoperability findings written to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
