#!/usr/bin/env python3
"""Validate the machine-readable inventory of claimed publication profiles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED_PROFILES = {
    "json-schema",
    "rdf-shacl",
    "ro-crate",
    "prov-o",
    "openlineage",
    "cyclonedx",
    "dsse-in-toto",
}
ALLOWED_STATUSES = {
    "bounded-pass",
    "bounded-roundtrip",
    "bounded-unsigned-roundtrip",
    "hosted-schema-pass",
    "independently-tool-validated",
}


def validate(path: Path) -> list[str]:
    try:
        value: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{path}: cannot read JSON ({exc})"]
    errors: list[str] = []
    if not isinstance(value, dict) or value.get("schema") != "riopa.profile-validator-inventory.v1":
        errors.append("unexpected inventory schema")
    profiles = value.get("profiles") if isinstance(value, dict) else None
    if not isinstance(profiles, list):
        return errors + ["profiles must be a list"]
    ids = [item.get("id") for item in profiles if isinstance(item, dict)]
    if set(ids) != REQUIRED_PROFILES or len(ids) != len(REQUIRED_PROFILES):
        errors.append("profiles must contain each required claimed profile exactly once")
    for index, item in enumerate(profiles):
        prefix = f"profiles[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field in ("id", "standard", "validator", "version", "command", "status"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                errors.append(f"{prefix}.{field} must be a non-empty string")
        if item.get("status") not in ALLOWED_STATUSES:
            errors.append(f"{prefix}.status is outside the bounded status vocabulary")
        if not isinstance(item.get("independent_implementation"), bool):
            errors.append(f"{prefix}.independent_implementation must be boolean")
    if value.get("promotion_allowed") is not False:
        errors.append("promotion_allowed must be false")
    for field in ("open_gates", "nonclaims"):
        if not isinstance(value.get(field), list) or not value[field]:
            errors.append(f"{field} must be a non-empty list")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inventory", type=Path)
    args = parser.parse_args()
    errors = validate(args.inventory)
    if errors:
        print("\n".join(errors))
        return 1
    print("PASS profile validator inventory shape")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
