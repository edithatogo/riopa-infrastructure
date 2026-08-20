#!/usr/bin/env python3
"""Generate non-assertive panel qualification templates for every Conductor track."""

from __future__ import annotations

import json
from pathlib import Path

ROLES = ["adversarial-analyst", "evidence-auditor", "reproducer"]


def generate(tracks_root: Path, output: Path) -> None:
    entries = []
    for metadata_path in sorted(tracks_root.glob("*/metadata.json")):
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        entries.append(
            {
                "track_id": metadata["track_id"],
                "source": str(metadata_path.parent),
                "status": "pending",
                "disposition": None,
                "evidence_refs": [],
                "required_roles": ROLES,
                "release_decision_ref": "docs/release-authority-decision-draft-20260801.md",
                "notes": (
                    "Template only. Populate from content-bound panel execution; "
                    "do not infer a result from missing evidence."
                ),
            }
        )
    payload = {
        "schema": "riopa.panel-qualification-template.v1",
        "generated_from": "conductor/tracks/*/metadata.json",
        "scope": "all open Conductor tracks",
        "non_assertive": True,
        "tracks": entries,
    }
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    generate(
        root / "conductor" / "tracks",
        root / "docs" / "panel-qualification-report-templates-20260801.json",
    )
