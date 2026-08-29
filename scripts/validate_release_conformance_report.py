#!/usr/bin/env python3
"""Validate a machine-readable release conformance report and its bindings.

This validator checks the report's local content-addressed references.  It does
not verify signatures, publication, authority, or external execution.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from riopa_provenance.hashing import sha256_file

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_REVISION = re.compile(r"^[0-9a-f]{40}$")
_CHANNELS = {"technical-preview", "stable-candidate"}


def validate_report(report: dict[str, Any], *, root: Path) -> tuple[str, ...]:
    errors: list[str] = []
    if report.get("schema_version") != "1.0.0":
        errors.append("schema_version must be 1.0.0")
    if not isinstance(report.get("release"), str) or not report["release"]:
        errors.append("release must be a non-empty string")
    if report.get("channel") not in _CHANNELS:
        errors.append("channel must be technical-preview or stable-candidate")
    revision = report.get("source_revision")
    if not isinstance(revision, str) or not _REVISION.fullmatch(revision):
        errors.append("source_revision must be a 40-character lowercase Git revision")
    fixture_digest = report.get("fixture_sha256")
    if not isinstance(fixture_digest, str) or not _SHA256.fullmatch(fixture_digest):
        errors.append("fixture_sha256 must be a lowercase SHA-256 digest")
    bindings = report.get("evidence_bindings")
    if not isinstance(bindings, list) or not bindings:
        errors.append("evidence_bindings must be a non-empty list")
        bindings = []
    seen: set[str] = set()
    for index, binding in enumerate(bindings):
        prefix = f"evidence_bindings[{index}]"
        if not isinstance(binding, dict):
            errors.append(f"{prefix} must be an object")
            continue
        path_value = binding.get("path")
        if not isinstance(path_value, str) or not path_value or Path(path_value).is_absolute():
            errors.append(f"{prefix}.path must be a non-empty relative path")
            continue
        if path_value in seen:
            errors.append(f"{prefix}.path is duplicated")
        seen.add(path_value)
        path = (root / path_value).resolve()
        try:
            path.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{prefix}.path escapes repository root")
            continue
        if not path.is_file():
            errors.append(f"{prefix}.path does not exist: {path_value}")
            continue
        digest = binding.get("sha256")
        if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
            errors.append(f"{prefix}.sha256 must be a lowercase SHA-256 digest")
        elif sha256_file(path) != digest:
            errors.append(f"{prefix}.sha256 does not match {path_value}")
        if not isinstance(binding.get("evidence_id"), str) or not binding["evidence_id"]:
            errors.append(f"{prefix}.evidence_id must be non-empty")
    limitations = report.get("limitations")
    if (
        not isinstance(limitations, list)
        or not limitations
        or not all(isinstance(item, str) and item for item in limitations)
    ):
        errors.append("limitations must be a non-empty list of strings")
    interpretation = report.get("interpretation")
    if not isinstance(interpretation, str) or "not newly executed results" not in interpretation:
        errors.append("interpretation must preserve the copied-evidence boundary")
    return tuple(errors)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    try:
        report = json.loads(args.report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(f"unable to read report: {exc}")
    errors = validate_report(report, root=args.root.resolve())
    if errors:
        for error in errors:
            print(error)
        return 1
    print("release conformance report valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
