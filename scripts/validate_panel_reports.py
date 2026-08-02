#!/usr/bin/env python3
"""Fail-closed validation for a three-agent qualification panel.

Reports are JSON and must agree on the frozen revision and bundle digest.  This
tool only establishes panel concordance; it never promotes a release.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROLES = {"reproducer", "adversarial-analyst", "evidence-auditor"}
PANEL_TEMPLATE_STATUSES = {"pending", "in-progress", "complete"}
SHA256 = re.compile(r"^[0-9a-f]{64}$")
REVISION = re.compile(r"^[0-9a-f]{40}$")


def validate_template_manifest(path: Path, tracks_root: Path) -> list[str]:
    """Validate the track-wide template without treating templates as results."""
    errors: list[str] = []
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{path}: cannot read template manifest ({exc})"]
    entries = manifest.get("tracks") if isinstance(manifest, dict) else None
    if not isinstance(entries, list) or not entries:
        return ["template manifest must contain a non-empty tracks list"]
    expected = {
        p.name for p in tracks_root.iterdir() if p.is_dir() and (p / "metadata.json").exists()
    }
    actual = {e.get("track_id") for e in entries if isinstance(e, dict)}
    if actual != expected:
        errors.append("template manifest track set does not match conductor tracks")
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("each template entry must be an object")
            continue
        if entry.get("status") not in PANEL_TEMPLATE_STATUSES:
            errors.append(f"{entry.get('track_id', '<unknown>')}: invalid panel status")
        if entry.get("status") == "pending" and entry.get("disposition") is not None:
            errors.append(
                f"{entry.get('track_id', '<unknown>')}: pending template cannot claim disposition"
            )
        if entry.get("release_decision_ref") != "docs/release-authority-decision-draft-20260801.md":
            errors.append(f"{entry.get('track_id', '<unknown>')}: missing release decision linkage")
        if entry.get("required_roles") != sorted(ROLES):
            errors.append(f"{entry.get('track_id', '<unknown>')}: required panel roles mismatch")
    return sorted(set(errors))


def validate(paths: list[Path]) -> list[str]:
    errors: list[str] = []
    if len(paths) != 3:
        return ["exactly three panel reports are required"]
    reports = []
    for path in paths:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: cannot read JSON ({exc})")
            continue
        if not isinstance(value, dict):
            errors.append(f"{path}: report must be an object")
            continue
        reports.append(value)
    roles = [str(report.get("role", "")) for report in reports]
    if set(roles) != ROLES or len(roles) != len(set(roles)):
        errors.append(
            "panel roles must be unique and exactly reproducer, "
            "adversarial-analyst, evidence-auditor"
        )
    for field in ("source_revision", "bundle_sha256"):
        values = {str(report.get(field, "")) for report in reports}
        if "" in values:
            errors.append(f"missing {field}")
        elif len(values) != 1:
            errors.append(f"panel reports disagree on {field}")
    for report in reports:
        for field in ("report_id", "track_id", "scope", "evaluated_at"):
            if not isinstance(report.get(field), str) or not report[field].strip():
                errors.append(f"missing {field}")
        if not isinstance(report.get("findings"), list):
            errors.append("findings must be a list")
        if not isinstance(report.get("evidence_refs"), list):
            errors.append("evidence_refs must be a list")
        if not REVISION.fullmatch(str(report.get("source_revision", ""))):
            errors.append("source_revision must be a 40-character lowercase Git SHA-1")
        if not SHA256.fullmatch(str(report.get("bundle_sha256", ""))):
            errors.append("bundle_sha256 must be a 64-character lowercase SHA-256")
        if report.get("disposition") not in {"pass", "pass-with-limitations", "fail"}:
            errors.append("disposition must be pass, pass-with-limitations or fail")
        if report.get("dissent") is None:
            errors.append("dissent must be recorded, including an empty list")
    if any(report.get("disposition") == "fail" for report in reports):
        errors.append("a failing panel report prevents concordance")
    return sorted(set(errors))


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "--template-manifest":
        if len(args) != 4 or args[2] != "--tracks-root":
            print("usage: --template-manifest PATH --tracks-root PATH", file=sys.stderr)
            return 2
        errors = validate_template_manifest(Path(args[1]), Path(args[3]))
    else:
        errors = validate([Path(arg) for arg in args])
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("PASS panel report concordance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
