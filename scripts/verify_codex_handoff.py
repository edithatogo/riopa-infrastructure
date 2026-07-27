#!/usr/bin/env python3
"""Verify the working-tree portion of the Codex handoff manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "handoff" / "CODEX_HANDOFF_MANIFEST.json"


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_manifest(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Handoff manifest must be a JSON object")
    return value


def candidate_paths(root: Path, manifest_path: Path) -> set[str]:
    output = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root,
    )
    relative_manifest = manifest_path.relative_to(root).as_posix()
    return {
        item.decode()
        for item in output.split(b"\0")
        if item and item.decode() != relative_manifest and (root / item.decode()).is_file()
    }


def verify(root: Path, manifest_path: Path) -> list[str]:
    errors: list[str] = []
    manifest = load_manifest(manifest_path)
    raw_files = manifest.get("files")
    if not isinstance(raw_files, list):
        return ["manifest files must be an array"]

    declared: set[str] = set()
    for value in raw_files:
        if not isinstance(value, dict):
            errors.append("manifest file entry is not an object")
            continue
        relative = str(value.get("path", ""))
        if not relative or relative in declared:
            errors.append(f"missing or duplicate path: {relative!r}")
            continue
        declared.add(relative)
        path = root / relative
        try:
            resolved = path.resolve(strict=True)
            resolved.relative_to(root.resolve())
        except (FileNotFoundError, ValueError):
            errors.append(f"missing or escaping path: {relative}")
            continue
        if not path.is_file() or path.is_symlink():
            errors.append(f"not a regular in-tree file: {relative}")
            continue
        expected_size = value.get("size_bytes")
        expected_digest = value.get("sha256")
        if path.stat().st_size != expected_size:
            errors.append(f"size mismatch: {relative}")
        if digest(path) != expected_digest:
            errors.append(f"digest mismatch: {relative}")

    actual = candidate_paths(root, manifest_path)
    for relative in sorted(actual - declared):
        errors.append(f"undeclared working-tree file: {relative}")
    for relative in sorted(declared - actual):
        errors.append(f"declared file is not tracked/unignored: {relative}")

    if (root / ".git").is_dir():
        branch = subprocess.check_output(
            ["git", "branch", "--show-current"], cwd=root, text=True
        ).strip()
        expected_branch = str(manifest.get("expected_branch", ""))
        if branch != expected_branch:
            errors.append(f"branch mismatch: expected {expected_branch}, found {branch}")
        count = int(
            subprocess.check_output(
                ["git", "rev-list", "--count", "HEAD"], cwd=root, text=True
            ).strip()
        )
        minimum = int(manifest.get("expected_minimum_commit_count", 0))
        # The manifest is produced immediately before the final handoff commit.
        if count + 1 < minimum:
            errors.append(f"commit count {count} cannot reach expected minimum {minimum}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = args.manifest.resolve()
    errors = verify(root, manifest)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"PASS: {manifest.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
