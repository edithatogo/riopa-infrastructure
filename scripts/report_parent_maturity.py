#!/usr/bin/env python3
"""Report Conductor parent-track maturity without promoting any track."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def build_report() -> dict[str, Any]:
    tracks = []
    for metadata_path in sorted((ROOT / "conductor/tracks").glob("*/metadata.json")):
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise RuntimeError(f"could not read {metadata_path}: {exc}") from exc
        missing = sorted({"track_id", "status", "maturity_target"} - metadata.keys())
        if missing:
            raise RuntimeError(f"{metadata_path} is missing required fields: {missing}")
        tracks.append(
            {
                "track_id": metadata["track_id"],
                "status": metadata["status"],
                "current_maturity": metadata.get("current_maturity", "M1"),
                "maturity_target": metadata["maturity_target"],
                "v1_critical": metadata.get("v1_critical", False),
            }
        )
    below_target = [item for item in tracks if item["current_maturity"] != item["maturity_target"]]
    return {
        "schema_version": "1.0.0",
        "evidence_id": "urn:riopa:evidence:parent-track-maturity:2026-08-03",
        "classification": "fail-closed-maturity-inventory",
        "track_count": len(tracks),
        "below_target_count": len(below_target),
        "tracks": tracks,
        "shared_blockers": [
            "incomplete track-specific implementation and compatibility evidence",
            "owner-authorized agent-operated user and operator workflows",
            "elapsed beta/RC soak and production recovery qualification",
            "national-scale performance and cost measurements",
            "signed preservation and accountable release-authority decisions",
        ],
        "promotion_rule": (
            "No parent track is promoted to M6 by inventory or panel recommendation alone; "
            "each track requires its own evidence contract and applicable external/elapsed gates."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = build_report()
        args.output.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    except (OSError, RuntimeError) as exc:
        print(f"parent maturity report failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
