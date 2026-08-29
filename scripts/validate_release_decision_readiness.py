#!/usr/bin/env python3
"""Validate the non-authorising release-decision readiness projection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def validate_readiness(payload: object) -> tuple[str, ...]:
    if not isinstance(payload, dict):
        return ("readiness projection must be a JSON object",)
    errors: list[str] = []
    if payload.get("schema") != "riopa.release-decision-readiness.v1":
        errors.append("unexpected readiness schema")
    if payload.get("non_assertive") is not True:
        errors.append("readiness projection must be non-assertive")
    if payload.get("release_ready") is not False:
        errors.append("release_ready must be false")
    if payload.get("release_authority") != "pending":
        errors.append("release_authority must remain pending")
    tracks = payload.get("tracks")
    if not isinstance(tracks, list) or not tracks:
        errors.append("tracks must be a non-empty list")
        tracks = []
    identifiers: set[str] = set()
    for index, track in enumerate(tracks):
        prefix = f"tracks[{index}]"
        if not isinstance(track, dict):
            errors.append(f"{prefix} must be an object")
            continue
        track_id = track.get("track_id")
        if not isinstance(track_id, str) or not track_id.strip():
            errors.append(f"{prefix}.track_id must be non-empty")
        elif track_id in identifiers:
            errors.append(f"{prefix}.track_id must be unique")
        else:
            identifiers.add(track_id)
        if track.get("release_authority") != "pending":
            errors.append(f"{prefix}.release_authority must remain pending")
        blockers = track.get("blockers")
        if (
            not isinstance(blockers, list)
            or not blockers
            or not all(isinstance(item, str) and item.strip() for item in blockers)
        ):
            errors.append(f"{prefix}.blockers must be non-empty strings")
        if (
            not isinstance(track.get("release_decision_ref"), str)
            or not track["release_decision_ref"].strip()
        ):
            errors.append(f"{prefix}.release_decision_ref must be non-empty")
    limitations = payload.get("limitations")
    if not isinstance(limitations, list) or not limitations:
        errors.append("limitations must be non-empty")
    return tuple(dict.fromkeys(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("projection", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.projection.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(f"unable to read projection: {exc}")
    errors = validate_readiness(payload)
    for error in errors:
        print(error)
    if not errors:
        print("release-decision readiness projection valid and non-authorising")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
