#!/usr/bin/env python3
"""Validate the bounded owner-authorized agent workflow report shape."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

_CLASSIFICATION = "owner-authorized-agent-workflows-not-independent-human-evidence"


def validate_report(report: dict[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if report.get("schema_version") != "1.0.0":
        errors.append("schema_version must be 1.0.0")
    if report.get("classification") != _CLASSIFICATION:
        errors.append("classification must preserve the non-independent-human boundary")
    workflows = report.get("workflows")
    if not isinstance(workflows, list) or len(workflows) != 2:
        errors.append("workflows must contain exactly two entries")
        workflows = []
    identifiers: set[str] = set()
    for index, workflow in enumerate(workflows):
        prefix = f"workflows[{index}]"
        if not isinstance(workflow, dict):
            errors.append(f"{prefix} must be an object")
            continue
        workflow_id = workflow.get("workflow_id")
        if not isinstance(workflow_id, str) or not workflow_id.strip():
            errors.append(f"{prefix}.workflow_id must be non-empty")
        elif workflow_id in identifiers:
            errors.append(f"{prefix}.workflow_id must be unique")
        else:
            identifiers.add(workflow_id)
        if not isinstance(workflow.get("command"), list) or not workflow["command"]:
            errors.append(f"{prefix}.command must be non-empty")
        if workflow.get("status") not in {"passed", "failed"}:
            errors.append(f"{prefix}.status must be passed or failed")
        if not isinstance(workflow.get("exit_code"), int):
            errors.append(f"{prefix}.exit_code must be an integer")
    nonclaims = report.get("non_claims")
    text = " ".join(str(item) for item in nonclaims) if isinstance(nonclaims, list) else ""
    if "not external participant evidence" not in text:
        errors.append("non_claims must retain the external participant boundary")
    if "does not authorize promotion" not in text:
        errors.append("non_claims must retain the promotion boundary")
    return tuple(dict.fromkeys(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    try:
        report = json.loads(args.report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(f"unable to read report: {exc}")
    if not isinstance(report, dict):
        print("report must be a JSON object")
        return 1
    errors = validate_report(report)
    for error in errors:
        print(error)
    if not errors:
        print("agent workflow report valid and promotion-disabled")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
