#!/usr/bin/env python3
"""Reconcile an issue-list export into a complete track evidence matrix.

The input is the JSON emitted by ``gh issue list --json number,title,labels,body,url``.
Only explicit track markers and labels are used; missing or ambiguous values are
represented as unresolved rather than guessed.
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACK_ROOT = ROOT / "conductor/tracks"


def _marker(issue: dict) -> str | None:
    body = issue.get("body") or ""
    match = re.search(r"riopa-issue-key:\s*([A-Za-z0-9_-]+)", body)
    if match:
        return match.group(1)
    match = re.match(r"\[([^]]+)]", issue.get("title") or "")
    return match.group(1) if match and match.group(1) in track_keys() else None


def track_keys() -> set[str]:
    return {p.name for p in TRACK_ROOT.iterdir() if p.is_dir()}


def _labels(issue: dict) -> set[str]:
    return {item["name"] for item in issue.get("labels", [])}


def _release(labels: set[str]) -> str | None:
    return next((x.split(":", 1)[1] for x in labels if x.startswith("release:")), None)


def _class(labels: set[str]) -> str:
    if "type:implementation" in labels:
        return "implementation"
    if "type:validation" in labels:
        return "validation"
    if "stability:operational" in labels:
        return "operational"
    if "stability:reference" in labels:
        return "reference"
    if {"rights-governance", "stability:governance", "risk:critical"} & labels:
        return "governance_or_rights"
    return "unresolved"


def reconcile(issues: list[dict], observed: str | None = None) -> dict:
    keys = track_keys()
    grouped: dict[str, list[dict]] = {key: [] for key in keys}
    for issue in issues:
        key = _marker(issue)
        if key in grouped:
            grouped[key].append(issue)
    rows = []
    for key in sorted(keys):
        linked = grouped[key]
        labels = set().union(*(_labels(i) for i in linked)) if linked else set()
        rows.append(
            {
                "track_key": key,
                "source": f"conductor/tracks/{key}",
                "issue_numbers": sorted(i["number"] for i in linked),
                "open_issue_count": len(linked),
                "release_tier": _release(labels),
                "evidence_status": "M1/open" if linked else "unresolved/no linked open issues",
                "blocker_class": _class(labels) if linked else "unresolved",
                "classification_basis": "linked issue labels and explicit riopa-issue-key marker"
                if linked
                else "no matching open issue",
            }
        )
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "generated_at": observed or date.today().isoformat(),
        "repository": "edithatogo/riopa-infrastructure",
        "source": "gh issue list --state open --limit 300 --json number,title,labels,body,url",
        "snapshot": {
            "open_issue_count": len(issues),
            "open_track_parent_count": sum(1 for i in issues if "type:track" in _labels(i)),
            "track_count": len(keys),
        },
        "classification": {
            "track_key": "riopa-issue-key marker, with verified title-prefix fallback",
            "evidence_status": "planning status only; content-bound evidence remains required",
            "blocker_class": "explicit issue labels; unresolved when absent",
        },
        "track_inventory": rows,
        "limitations": [
            "This reconciliation does not close issues or qualify tracks.",
            "External reproduction, operational soak and release authority remain separate gates.",
            "Rows with unresolved classifications require agent-panel evidence "
            "review before closure decisions.",
        ],
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--observed", default=None)
    args = parser.parse_args()
    payload = reconcile(json.loads(args.input.read_text(encoding="utf-8")), args.observed)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
