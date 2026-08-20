#!/usr/bin/env python3
"""Run a small, portable lint contract over GitHub workflow files.

This complements actionlint: it is intentionally dependency-light so the same
check runs locally and in the hosted quality job without downloading tools.
The deeper permission and shell-safety rules remain in check_workflow_policy.py.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def workflow_lint_errors(root: Path) -> list[str]:
    workflow_root = root / ".github" / "workflows"
    paths = sorted((*workflow_root.glob("*.yml"), *workflow_root.glob("*.yaml")))
    if not paths:
        return ["no GitHub workflows found"]
    errors: list[str] = []
    for path in paths:
        relative = path.relative_to(root)
        try:
            document = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            errors.append(f"{relative}: cannot parse workflow: {exc}")
            continue
        if not isinstance(document, dict):
            errors.append(f"{relative}: workflow root must be a mapping")
            continue
        if not isinstance(document.get("name"), str) or not document["name"].strip():
            errors.append(f"{relative}: workflow needs a non-empty name")
        triggers = document.get("on", document.get(True))
        if triggers is None:
            errors.append(f"{relative}: workflow needs an on trigger")
        if not isinstance(document.get("permissions"), dict):
            errors.append(f"{relative}: workflow needs explicit top-level permissions")
        jobs = document.get("jobs")
        if not isinstance(jobs, dict) or not jobs:
            errors.append(f"{relative}: workflow needs at least one job")
            continue
        for job_id, raw_job in jobs.items():
            job = _mapping(raw_job)
            if not isinstance(raw_job, dict):
                errors.append(f"{relative}: job {job_id!r} must be a mapping")
                continue
            timeout = job.get("timeout-minutes")
            if not isinstance(timeout, int) or not 1 <= timeout <= 60:
                errors.append(f"{relative}: job {job_id!r} needs timeout-minutes between 1 and 60")
            steps = job.get("steps")
            if not isinstance(steps, list) or not steps:
                errors.append(f"{relative}: job {job_id!r} needs non-empty steps")
                continue
            for index, raw_step in enumerate(steps, start=1):
                if not isinstance(raw_step, dict):
                    errors.append(f"{relative}: job {job_id!r} step {index} must be a mapping")
                    continue
                if (
                    not raw_step.get("name")
                    and not raw_step.get("uses")
                    and not raw_step.get("run")
                ):
                    errors.append(
                        f"{relative}: job {job_id!r} step {index} needs name, uses or run"
                    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    errors = workflow_lint_errors(args.root.resolve())
    if errors:
        print("\n".join(errors))
        return 1
    print("GitHub workflow lint passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
