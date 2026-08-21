#!/usr/bin/env python3
"""Validate the bounded v1 feature-freeze inventory against repository state."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def validate(record: dict[str, Any], root: Path) -> tuple[str, ...]:
    errors: list[str] = []
    if record.get("schema_version") != "1.0.0":
        errors.append("unsupported inventory schema version")
    candidate = record.get("release_candidate")
    if not isinstance(candidate, dict) or not candidate.get("version"):
        errors.append("release candidate version is required")
    source_of_truth = candidate.get("source_of_truth", []) if isinstance(candidate, dict) else []
    if not isinstance(source_of_truth, list) or not source_of_truth:
        errors.append("release candidate source of truth is required")
    else:
        for relative in source_of_truth:
            if not isinstance(relative, str) or not (root / relative).exists():
                errors.append(f"missing source-of-truth path: {relative}")
    surfaces = record.get("normative_surfaces")
    if not isinstance(surfaces, dict):
        errors.append("normative surfaces are required")
    else:
        for name, surface in surfaces.items():
            if name == "publication_formats":
                if not isinstance(surface, list) or not surface:
                    errors.append("publication formats must be a non-empty array")
                continue
            if not isinstance(surface, dict):
                errors.append(f"surface {name} must be an object")
                continue
            inventory_path = surface.get("directory") or surface.get("surface_inventory")
            if isinstance(inventory_path, str) and not (root / inventory_path).exists():
                errors.append(f"surface {name} path does not exist: {inventory_path}")
            for test_path in surface.get("contract_tests", []):
                if not isinstance(test_path, str) or not (root / test_path).exists():
                    errors.append(f"surface {name} test path does not exist: {test_path}")
    controls = record.get("frozen_controls")
    if not isinstance(controls, dict) or controls.get("python314_only") is not True:
        errors.append("Python 3.14-only freeze control is required")
    if (
        not isinstance(record.get("deferred_or_excluded"), list)
        or not record["deferred_or_excluded"]
    ):
        errors.append("deferred or excluded surfaces must be explicit")
    if (
        not isinstance(record.get("open_freeze_findings"), list)
        or not record["open_freeze_findings"]
    ):
        errors.append("open freeze findings must remain explicit")
    return tuple(errors)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    path = root / "docs/v1-feature-freeze-inventory-20260803.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    errors = validate(record, root)
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print("PASS bounded v1 feature-freeze inventory")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
