#!/usr/bin/env python3
"""Build a fail-closed release-decision readiness projection.

This is a planning projection, not an approval or qualification result. Missing
matrix rows and panel evidence are surfaced as blockers rather than inferred.
"""

from __future__ import annotations

import json
from pathlib import Path


def generate(manifest_path: Path, matrix_path: Path, output: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    matrix_by_track = {row["track_key"]: row for row in matrix.get("track_inventory", [])}
    tracks = []
    for template in manifest["tracks"]:
        track_id = template["track_id"]
        row = matrix_by_track.get(track_id)
        blockers = ["panel qualification pending", "release-authority decision pending"]
        if row is None:
            blockers.append("open-issue evidence matrix has no row for this track")
        else:
            if row.get("evidence_status", "").lower().endswith("open"):
                blockers.append(f"track evidence status: {row['evidence_status']}")
            if row.get("blocker_class"):
                blockers.append(f"matrix blocker class: {row['blocker_class']}")
        tracks.append(
            {
                "track_id": track_id,
                "panel_status": template["status"],
                "disposition": template["disposition"],
                "matrix_entry": row,
                "blockers": blockers,
                "release_authority": "pending",
                "release_decision_ref": template["release_decision_ref"],
            }
        )
    payload = {
        "schema": "riopa.release-decision-readiness.v1",
        "generated_from": [str(manifest_path), str(matrix_path)],
        "non_assertive": True,
        "release_ready": False,
        "release_authority": "pending",
        "tracks": tracks,
        "limitations": [
            "This projection does not qualify tracks or grant release authority.",
            "Missing matrix rows are blockers and require reconciliation before closure.",
        ],
    }
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    generate(
        root / "docs/panel-qualification-report-templates-20260801.json",
        root / "docs/open-issue-track-evidence-matrix-20260801.json",
        root / "docs/release-decision-readiness-20260801.json",
    )
