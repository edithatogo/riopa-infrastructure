#!/usr/bin/env python3
"""Build the bounded cross-tool/version compatibility matrix."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
from pathlib import Path
from typing import Any

from scripts.verify_conformance_parity import build_receipt


def _node_version(root: Path) -> str:
    result = subprocess.run(
        ["node", "--version"], cwd=root, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def build_matrix(root: Path) -> dict[str, Any]:
    receipt = build_receipt(root)
    corpus = json.loads((root / "conformance/v1/corpus.json").read_text(encoding="utf-8"))
    return {
        "matrix_version": "1.0.0",
        "corpus_version": receipt["corpus_version"],
        "scope": receipt["scope"],
        "environment": {
            "python": platform.python_version(),
            "node": _node_version(root),
        },
        "implementations": [
            {
                "tool": "riopa-python-reference",
                "language": "Python",
                "status": "observed-pass",
                "cases": receipt["case_count"],
                "parity": receipt["python_passed"],
            },
            {
                "tool": "conformance_node.mjs",
                "language": "JavaScript",
                "status": "observed-pass",
                "cases": receipt["case_count"],
                "parity": receipt["node_passed"],
            },
            {
                "tool": "rust-reference",
                "language": "Rust",
                "status": "not-implemented",
                "cases": 0,
                "parity": False,
            },
        ],
        "compatibility": {
            "python_node_parity": receipt["parity"],
            "migration_cases_included": any(
                item["case_id"].startswith("canonical-profile-migration")
                for item in corpus["cases"]
            ),
            "external_producer_consumer": "not-observed",
            "standards_round_trip": "not-observed",
        },
        "non_claims": [
            "This is a bounded repository-owned matrix, not an independent review.",
            "Rust, standards round-trips and external producer/consumer exercises remain open.",
            "The matrix does not establish release, operational or preservation acceptance.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    matrix = build_matrix(args.root.resolve())
    args.output.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(matrix, sort_keys=True))
    return 0 if matrix["compatibility"]["python_node_parity"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
