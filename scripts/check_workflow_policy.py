#!/usr/bin/env python3
"""Apply fail-closed security and reliability policy to GitHub workflows."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import yaml


class Yaml12SafeLoader(yaml.SafeLoader):
    """Safe loader that treats only true/false as booleans.

    PyYAML stores implicit resolvers on the class and subclasses initially share
    the same mutable mapping.  Copy both the mapping and each resolver list
    before customising it, otherwise importing this policy checker changes
    ``yaml.safe_load`` process-wide (and turns booleans in unrelated project
    files into strings).
    """


Yaml12SafeLoader.yaml_implicit_resolvers = {
    key: list(resolvers) for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}
for key, resolvers in list(Yaml12SafeLoader.yaml_implicit_resolvers.items()):
    Yaml12SafeLoader.yaml_implicit_resolvers[key] = [
        (tag, expression) for tag, expression in resolvers if tag != "tag:yaml.org,2002:bool"
    ]
Yaml12SafeLoader.add_implicit_resolver(
    "tag:yaml.org,2002:bool",
    re.compile(r"^(?:true|false)$", re.IGNORECASE),
    list("tTfF"),
)

DANGEROUS_RUN_CONTEXTS = (
    "${{ github.event.",
    "${{ github.head_ref",
    "${{ github.base_ref",
    "${{ github.ref_name",
)
ALLOWED_GLOBAL_PERMISSION = {"contents": "read"}
ALLOWED_SECURITY_WRITE = {"security-events"}


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _permission_errors(*, path: Path, job_id: str, job: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    permissions = _mapping(job.get("permissions"))
    writes = {str(key) for key, value in permissions.items() if str(value) == "write"}
    non_security_writes = writes - ALLOWED_SECURITY_WRITE
    if non_security_writes:
        if not job.get("environment"):
            errors.append(
                f"{path.relative_to(root)}: job {job_id!r} has write permissions "
                "without a protected environment"
            )
        condition = str(job.get("if", ""))
        if "refs/tags/" not in condition:
            errors.append(f"{path.relative_to(root)}: privileged job {job_id!r} is not tag-gated")
    return errors


def workflow_policy_errors(root: Path) -> list[str]:
    errors: list[str] = []
    workflow_root = root / ".github" / "workflows"
    paths = sorted((*workflow_root.glob("*.yml"), *workflow_root.glob("*.yaml")))
    if not paths:
        return ["no GitHub workflows found"]
    for path in paths:
        relative = path.relative_to(root)
        try:
            document = yaml.load(path.read_text(encoding="utf-8"), Loader=Yaml12SafeLoader)
        except yaml.YAMLError as exc:
            errors.append(f"{relative}: invalid YAML: {exc}")
            continue
        if not isinstance(document, dict):
            errors.append(f"{relative}: workflow root must be a mapping")
            continue
        triggers = document.get("on")
        if (
            isinstance(triggers, dict) and "pull_request_target" in triggers
        ) or triggers == "pull_request_target":
            errors.append(f"{relative}: pull_request_target is prohibited")
        if _mapping(document.get("permissions")) != ALLOWED_GLOBAL_PERMISSION:
            errors.append(f"{relative}: global permissions must be exactly contents: read")
        concurrency = _mapping(document.get("concurrency"))
        if not concurrency.get("group") or concurrency.get("cancel-in-progress") is not True:
            errors.append(f"{relative}: concurrency must cancel superseded runs")
        shell = str(_mapping(_mapping(document.get("defaults")).get("run")).get("shell", ""))
        if "-euo pipefail" not in shell:
            errors.append(f"{relative}: default shell must enable -euo pipefail")
        jobs = _mapping(document.get("jobs"))
        if not jobs:
            errors.append(f"{relative}: workflow has no jobs")
            continue
        for job_id, raw_job in jobs.items():
            if not isinstance(raw_job, dict):
                errors.append(f"{relative}: job {job_id!r} must be a mapping")
                continue
            timeout = raw_job.get("timeout-minutes")
            if not isinstance(timeout, int) or not 1 <= timeout <= 60:
                errors.append(f"{relative}: job {job_id!r} needs a 1-60 minute timeout")
            errors.extend(_permission_errors(path=path, job_id=str(job_id), job=raw_job, root=root))
            steps = raw_job.get("steps", [])
            if not isinstance(steps, list):
                errors.append(f"{relative}: job {job_id!r} steps must be a list")
                continue
            for index, raw_step in enumerate(steps, start=1):
                if not isinstance(raw_step, dict):
                    continue
                action = str(raw_step.get("uses", ""))
                if action.startswith("actions/checkout@"):
                    options = _mapping(raw_step.get("with"))
                    if options.get("persist-credentials") is not False:
                        errors.append(
                            f"{relative}: job {job_id!r} step {index} checkout must set "
                            "persist-credentials: false"
                        )
                command = str(raw_step.get("run", ""))
                for context in DANGEROUS_RUN_CONTEXTS:
                    if context in command:
                        errors.append(
                            f"{relative}: job {job_id!r} step {index} interpolates "
                            f"untrusted context into shell: {context}"
                        )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    errors = workflow_policy_errors(args.root.resolve())
    if errors:
        print("\n".join(errors))
        return 1
    print("GitHub workflow policy passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
