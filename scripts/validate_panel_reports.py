#!/usr/bin/env python3
"""Fail-closed validation for a three-agent qualification panel.

Reports are JSON and must agree on the frozen revision and bundle digest.  This
tool only establishes panel concordance; it never promotes a release.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROLES = {"reproducer", "adversarial-reviewer", "evidence-auditor"}


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
        errors.append("panel roles must be unique and exactly reproducer, adversarial-reviewer, evidence-auditor")
    for field in ("source_revision", "bundle_sha256"):
        values = {str(report.get(field, "")) for report in reports}
        if "" in values:
            errors.append(f"missing {field}")
        elif len(values) != 1:
            errors.append(f"panel reports disagree on {field}")
    for report in reports:
        if report.get("disposition") not in {"pass", "pass-with-limitations", "fail"}:
            errors.append("disposition must be pass, pass-with-limitations or fail")
        if report.get("dissent") is None:
            errors.append("dissent must be recorded, including an empty list")
    if any(report.get("disposition") == "fail" for report in reports):
        errors.append("a failing panel report prevents concordance")
    return sorted(set(errors))


def main() -> int:
    errors = validate([Path(arg) for arg in sys.argv[1:]])
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("PASS panel report concordance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
