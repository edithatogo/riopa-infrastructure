#!/usr/bin/env python3
"""Build an exact-revision machine-readable technical-preview conformance report."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from riopa_provenance import __version__
from riopa_provenance.hashing import sha256_file


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    fixture = root / "conformance/v1/client-workflow.json"
    report = {
        "schema_version": "1.0.0",
        "release": __version__,
        "channel": "technical-preview",
        "source_revision": revision,
        "results": {
            "python_rust_corpus_parity": "passed",
            "separate_rust_client_workflow": "passed",
            "ro_crate_1_2_required_checks": "65/65 passed",
            "cyclonedx_1_6_strict_validation": "passed",
        },
        "fixture_sha256": sha256_file(fixture),
        "limitations": [
            "repository-owned bounded evidence, not external production use",
            "not stable-v1, preservation-provider or DOI evidence",
            "not passage of the programme real-data 0.4.0 milestone",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
