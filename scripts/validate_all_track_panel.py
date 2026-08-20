#!/usr/bin/env python3
"""Validate three content-bound, all-track agent-panel lens reports."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROLES = {"reproducer", "adversarial-analyst", "evidence-auditor"}
DISPOSITIONS = {"pass", "pass-with-limitations", "fail"}
SHA256 = re.compile(r"^[0-9a-f]{64}$")
REVISION = re.compile(r"^[0-9a-f]{40}$")


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: report must be an object")
    return value


def validate(
    reports: list[Path], tracks_root: Path, synthesis_path: Path | None = None
) -> list[str]:
    errors: list[str] = []
    if len(reports) != 3:
        return ["exactly three all-track lens reports are required"]
    try:
        values = [_load(path) for path in reports]
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [str(exc)]
    expected_tracks = {path.parent.name for path in tracks_root.glob("*/metadata.json")}
    roles = [value.get("role") for value in values]
    if set(roles) != ROLES or len(roles) != len(set(roles)):
        errors.append("roles must be unique and exactly match the panel contract")
    for field, pattern in (("source_revision", REVISION), ("bundle_sha256", SHA256)):
        observed = {str(value.get(field, "")) for value in values}
        if len(observed) != 1 or not pattern.fullmatch(next(iter(observed), "")):
            errors.append(f"reports must share one valid {field}")
    for value in values:
        if value.get("schema") != "riopa.track-panel-lens.v1":
            errors.append(f"{value.get('role')}: unexpected schema")
        entries = value.get("tracks")
        if not isinstance(entries, list):
            errors.append(f"{value.get('role')}: tracks must be a list")
            continue
        actual_tracks = {entry.get("track_id") for entry in entries if isinstance(entry, dict)}
        if actual_tracks != expected_tracks or len(entries) != len(expected_tracks):
            errors.append(f"{value.get('role')}: track set does not match Conductor")
        for entry in entries:
            if not isinstance(entry, dict):
                errors.append(f"{value.get('role')}: track entry must be an object")
                continue
            track_id = entry.get("track_id", "<unknown>")
            if entry.get("disposition") not in DISPOSITIONS:
                errors.append(f"{value.get('role')}:{track_id}: invalid disposition")
            if not isinstance(entry.get("scope"), str) or not entry["scope"].strip():
                errors.append(f"{value.get('role')}:{track_id}: missing scope")
            for field in ("findings", "evidence_refs", "dissent"):
                if not isinstance(entry.get(field), list):
                    errors.append(f"{value.get('role')}:{track_id}: {field} must be a list")
    if synthesis_path is not None:
        try:
            synthesis = _load(synthesis_path)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            errors.append(str(exc))
        else:
            if synthesis.get("schema") != "riopa.track-panel-synthesis.v1":
                errors.append("synthesis: unexpected schema")
            if not isinstance(synthesis.get("orchestrator_identity"), str):
                errors.append("synthesis: missing orchestrator_identity")
            for field in ("source_revision", "bundle_sha256"):
                if synthesis.get(field) != values[0].get(field):
                    errors.append(f"synthesis: {field} does not match lens reports")
            entries = synthesis.get("tracks")
            if not isinstance(entries, list):
                errors.append("synthesis: tracks must be a list")
            else:
                actual_tracks = {
                    entry.get("track_id") for entry in entries if isinstance(entry, dict)
                }
                if actual_tracks != expected_tracks or len(entries) != len(expected_tracks):
                    errors.append("synthesis: track set does not match Conductor")
                lens_by_track = {
                    value["role"]: {
                        entry["track_id"]: entry["disposition"] for entry in value["tracks"]
                    }
                    for value in values
                }
                for entry in entries:
                    if not isinstance(entry, dict):
                        errors.append("synthesis: track entry must be an object")
                        continue
                    track_id = entry.get("track_id", "<unknown>")
                    expected_lenses = {
                        role: dispositions[track_id] for role, dispositions in lens_by_track.items()
                    }
                    if entry.get("lens_dispositions") != expected_lenses:
                        errors.append(f"synthesis:{track_id}: lens dispositions disagree")
                    if entry.get("final_disposition") != "not-qualified":
                        errors.append(
                            f"synthesis:{track_id}: M6 disposition must remain not-qualified"
                        )
                    if not isinstance(entry.get("blockers"), list) or not entry["blockers"]:
                        errors.append(f"synthesis:{track_id}: blockers must be non-empty")
                    for field in ("recommendation", "contingency"):
                        if not isinstance(entry.get(field), str) or not entry[field].strip():
                            errors.append(f"synthesis:{track_id}: missing {field}")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("reports", nargs="+", type=Path)
    parser.add_argument("--tracks-root", required=True, type=Path)
    parser.add_argument("--synthesis", type=Path)
    args = parser.parse_args()
    errors = validate(args.reports, args.tracks_root, args.synthesis)
    if errors:
        for error in errors:
            print(error)
        return 1
    print("PASS all-track agent-panel lens integrity")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
