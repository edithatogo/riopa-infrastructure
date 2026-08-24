#!/usr/bin/env python3
"""Build a conservative, content-bound v1 surface compatibility diff."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


class CompatibilityDiffError(ValueError):
    """Raised when the requested predecessor cannot be inspected safely."""


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise CompatibilityDiffError(result.stderr.strip() or "git command failed")
    return result.stdout


def _baseline_paths(root: Path, revision: str, prefix: str) -> set[str]:
    output = _git(root, "ls-tree", "-r", "--name-only", revision, prefix)
    return {line for line in output.splitlines() if line}


def _baseline_json(root: Path, revision: str, path: str) -> dict[str, Any]:
    try:
        payload = _git(root, "show", f"{revision}:{path}")
        value = json.loads(payload)
    except (CompatibilityDiffError, json.JSONDecodeError) as exc:
        raise CompatibilityDiffError(f"cannot load baseline JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CompatibilityDiffError(f"baseline JSON {path} must be an object")
    return value


def _current_json(root: Path, path: str) -> dict[str, Any]:
    try:
        value = json.loads((root / path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CompatibilityDiffError(f"cannot load current JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CompatibilityDiffError(f"current JSON {path} must be an object")
    return value


def _schema_surface(value: Any, pointer: str = "") -> dict[str, Any]:
    """Collect public schema properties, required fields, types and enums."""

    if not isinstance(value, dict):
        return {}
    result: dict[str, Any] = {}
    if "type" in value:
        result[f"{pointer}/type"] = value["type"]
    if "enum" in value:
        result[f"{pointer}/enum"] = value["enum"]
    required = value.get("required")
    if isinstance(required, list):
        result[f"{pointer}/required"] = sorted(item for item in required if isinstance(item, str))
    properties = value.get("properties")
    if isinstance(properties, dict):
        for name, child in sorted(properties.items()):
            if isinstance(name, str):
                child_pointer = f"{pointer}/properties/{name}"
                result[f"{child_pointer}/present"] = True
                result.update(_schema_surface(child, child_pointer))
    for keyword in ("items", "additionalProperties", "$defs"):
        child = value.get(keyword)
        if isinstance(child, dict):
            result.update(_schema_surface(child, f"{pointer}/{keyword}"))
    return result


def _change(path: str, kind: str, pointer: str, old: Any, new: Any) -> dict[str, Any]:
    return {"path": path, "kind": kind, "pointer": pointer, "old": old, "new": new}


def build_compatibility_diff(
    root: Path, *, baseline_revision: str, current_revision: str
) -> dict[str, Any]:
    """Compare the frozen predecessor tree with the current public surfaces."""

    schema_prefix = "schemas"
    module_prefix = "src/riopa_provenance"
    ontology_prefixes = ("docs/ontology", "bindings/typescript")
    baseline_schemas = {
        path
        for path in _baseline_paths(root, baseline_revision, schema_prefix)
        if path.endswith(".schema.json")
    }
    current_schemas = {
        path.relative_to(root).as_posix() for path in (root / schema_prefix).glob("*.schema.json")
    }
    schema_changes: list[dict[str, Any]] = []
    for path in sorted(baseline_schemas | current_schemas):
        if path not in baseline_schemas:
            schema_changes.append(_change(path, "schema-added", "", None, "present"))
            continue
        if path not in current_schemas:
            schema_changes.append(_change(path, "schema-removed", "", "present", None))
            continue
        old_surface = _schema_surface(_baseline_json(root, baseline_revision, path))
        new_surface = _schema_surface(_current_json(root, path))
        for pointer in sorted(set(old_surface) | set(new_surface)):
            old = old_surface.get(pointer)
            new = new_surface.get(pointer)
            if pointer not in old_surface:
                kind = "field-added" if pointer.endswith("/present") else "constraint-added"
                schema_changes.append(_change(path, kind, pointer, None, new))
            elif pointer not in new_surface:
                kind = "field-removed" if pointer.endswith("/present") else "constraint-removed"
                schema_changes.append(_change(path, kind, pointer, old, None))
            elif old != new:
                if pointer.endswith("/enum") and isinstance(old, list) and isinstance(new, list):
                    old_values, new_values = set(old), set(new)
                    kind = "constraint-added" if old_values <= new_values else "constraint-changed"
                else:
                    kind = "constraint-changed"
                schema_changes.append(_change(path, kind, pointer, old, new))

    baseline_modules = _baseline_paths(root, baseline_revision, module_prefix)
    current_modules = {
        path.relative_to(root).as_posix() for path in (root / module_prefix).glob("*.py")
    }
    module_changes = [
        _change(path, "module-added", "", None, "present")
        for path in sorted(current_modules - baseline_modules)
    ] + [
        _change(path, "module-removed", "", "present", None)
        for path in sorted(baseline_modules - current_modules)
    ]

    ontology_changes: list[dict[str, Any]] = []
    for prefix in ontology_prefixes:
        old_paths = _baseline_paths(root, baseline_revision, prefix)
        current_paths = {
            path.relative_to(root).as_posix()
            for path in (root / prefix).rglob("*")
            if path.is_file()
        }
        ontology_changes.extend(
            _change(path, "surface-added", "", None, "present")
            for path in sorted(current_paths - old_paths)
        )
        ontology_changes.extend(
            _change(path, "surface-removed", "", "present", None)
            for path in sorted(old_paths - current_paths)
        )

    breaking_kinds = {
        "schema-removed",
        "field-removed",
        "constraint-changed",
        "module-removed",
        "surface-removed",
    }
    breaking = [
        item
        for item in schema_changes + module_changes + ontology_changes
        if item["kind"] in breaking_kinds
    ]
    non_breaking = [
        item
        for item in schema_changes + module_changes + ontology_changes
        if item["kind"] not in breaking_kinds
    ]
    status = "no-unintended-breaking-changes" if not breaking else "review-required"
    return {
        "schema_version": "1.0.0",
        "evidence_id": "urn:riopa:evidence:v1-compatibility-diff:2026-08-25",
        "status": status,
        "baseline_revision": baseline_revision,
        "current_revision": current_revision,
        "surfaces": {
            "schemas": {"changes": schema_changes},
            "python_modules": {"changes": module_changes},
            "ontology_and_bindings": {"changes": ontology_changes},
        },
        "breaking_changes": breaking,
        "non_breaking_changes": non_breaking,
        "disposition": (
            "No removed public surface or changed schema constraint was observed."
            if not breaking
            else "Each listed breaking change requires an explicit migration disposition."
        ),
        "non_claims": [
            (
                "This path-level and schema-constraint diff does not prove runtime behavioural "
                "compatibility."
            ),
            "It does not qualify external clients, clean-room reproduction or release promotion.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--baseline-revision", required=True)
    parser.add_argument("--current-revision", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_compatibility_diff(
        args.root.resolve(),
        baseline_revision=args.baseline_revision,
        current_revision=args.current_revision,
    )
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "breaking": len(result["breaking_changes"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
