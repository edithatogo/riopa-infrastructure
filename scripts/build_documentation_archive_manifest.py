#!/usr/bin/env python3
"""Build a content-addressed documentation archive candidate manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

DOCUMENTS = (
    "docs/usage-guides-20260825.md",
    "docs/reference-index-20260825.json",
    "docs/bounded-lineage-tutorial-20260825.md",
    "docs/documentation-contract-20260824.json",
    "docs/documentation-support-readiness-20260825.json",
    "docs/single-developer-agent-panel-review-policy.md",
    "docs/operations-and-support.md",
)


def build(root: Path) -> dict[str, Any]:
    artifacts: list[dict[str, str]] = []
    for relative in DOCUMENTS:
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(relative)
        artifacts.append(
            {"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        )
    return {
        "manifest_id": "urn:riopa:documentation-archive:2026-08-25",
        "status": "repository-archive-candidate",
        "scope": "bounded regional public-datasets-only technical preview",
        "python": "3.14",
        "artifacts": artifacts,
        "publication": {
            "status": "not-published",
            "persistent_identifier": None,
            "requires_owner_decision": True,
        },
        "nonclaims": [
            "This candidate is not a release-candidate or stable-v1 documentation archive.",
            (
                "A manifest and local hashes do not prove external usability, publication "
                "or preservation acceptance."
            ),
            (
                "Owner-authorized agent-operated user/operator journey evidence and "
                "accountable release authority remain required."
            ),
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build(args.root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Documentation archive manifest written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
