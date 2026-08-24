#!/usr/bin/env python3
"""Build a content-light module coverage inventory from Coverage.py JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def build_inventory(coverage: dict[str, Any], *, root: Path) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    for filename, record in sorted(coverage.get("files", {}).items()):
        path = Path(filename)
        if path.parts[:2] != ("src", "riopa_provenance") or path.suffix != ".py":
            continue
        summary = record.get("summary", {})
        files.append(
            {
                "module": path.with_suffix("").as_posix().replace("/", "."),
                "path": path.as_posix(),
                "statements": summary.get("num_statements", 0),
                "covered_statements": summary.get("covered_lines", 0),
                "line_percent": summary.get("percent_covered", 0.0),
                "branches": summary.get("num_branches", 0),
                "covered_branches": summary.get("covered_branches", 0),
                "branch_percent": summary.get("percent_covered_display", "0.0"),
                "missing_lines": record.get("missing_lines", []),
            }
        )
    totals = coverage.get("totals", {})
    return {
        "schema_version": "1.0.0",
        "evidence_id": "urn:riopa:evidence:module-coverage-inventory:2026-08-25",
        "status": "measured-python314-full-suite",
        "command": (
            "uv run --extra dev --extra archive --extra spatial pytest "
            "--cov=riopa_provenance --cov-branch --cov-report=json"
        ),
        "runtime": "Python 3.14 only",
        "threshold": {"branch_aware_percent": 90.0, "stable_gate_unchanged": True},
        "totals": {
            "statements": totals.get("num_statements", 0),
            "covered_statements": totals.get("covered_lines", 0),
            "line_percent": totals.get("percent_covered", 0.0),
            "branches": totals.get("num_branches", 0),
            "covered_branches": totals.get("covered_branches", 0),
            "branch_percent": totals.get("percent_covered_display", "0.0"),
        },
        "files": files,
        "non_claims": [
            (
                "Coverage does not establish external conformance, rights, operational "
                "reliability or release readiness."
            ),
            (
                "Coverage inventory does not substitute for external operator/user evidence "
                "or elapsed soak."
            ),
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage-json", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    coverage = json.loads(args.coverage_json.read_text(encoding="utf-8"))
    inventory = build_inventory(coverage, root=root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(inventory["totals"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
