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
    parser.add_argument(
        "--evidence",
        action="append",
        type=Path,
        default=[],
        help="repository evidence receipt to bind into the report (repeatable)",
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    fixture = root / "conformance/v1/client-workflow.json"
    evidence = args.evidence or [
        root / "docs/rust-corpus-parity-20260825.json",
        root / "docs/separate-rust-client-workflow-20260829.json",
        root / "docs/wp006-external-rocrate-validation-20260829.json",
    ]
    missing = [str(path) for path in evidence if not path.is_file()]
    if missing:
        parser.error("evidence receipt not found: " + ", ".join(missing))
    evidence_bindings = []
    for path in evidence:
        payload = json.loads(path.read_text(encoding="utf-8"))
        evidence_bindings.append(
            {
                "path": str(path.relative_to(root)),
                "sha256": sha256_file(path),
                "evidence_id": payload.get("evidence_id") or payload.get("receipt_id"),
                "recorded_status": payload.get("status"),
                "subject": payload.get("subject"),
                "remediation": payload.get("remediation"),
            }
        )
    report = {
        "schema_version": "1.0.0",
        "release": __version__,
        "channel": "technical-preview",
        "source_revision": revision,
        "fixture_sha256": sha256_file(fixture),
        "evidence_bindings": evidence_bindings,
        "interpretation": "Evidence inventory; recorded statuses are copied from the bound receipts and are not newly executed results.",
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
