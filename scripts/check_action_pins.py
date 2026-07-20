#!/usr/bin/env python3
"""Reject mutable or ambiguous third-party GitHub Action references."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

USES_PATTERN = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)", re.MULTILINE)
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


def action_pin_errors(root: Path) -> list[str]:
    errors: list[str] = []
    workflow_root = root / ".github" / "workflows"
    for path in sorted((*workflow_root.glob("*.yml"), *workflow_root.glob("*.yaml"))):
        text = path.read_text(encoding="utf-8")
        for match in USES_PATTERN.finditer(text):
            reference = match.group(1).strip("\"'")
            line = text.count("\n", 0, match.start()) + 1
            location = f"{path.relative_to(root)}:{line}"
            if reference.startswith("./"):
                if ".." in Path(reference).parts:
                    errors.append(f"{location}: local action escapes repository: {reference}")
                continue
            if reference.startswith("docker://"):
                if "@sha256:" not in reference:
                    errors.append(f"{location}: container action is not digest-pinned: {reference}")
                continue
            if "@" not in reference:
                errors.append(f"{location}: action has no immutable ref: {reference}")
                continue
            action, ref = reference.rsplit("@", 1)
            if not action or not FULL_SHA.fullmatch(ref):
                errors.append(f"{location}: action is not pinned to a full commit SHA: {reference}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    errors = action_pin_errors(args.root.resolve())
    if errors:
        print("\n".join(errors))
        return 1
    print("All external GitHub Actions are immutable-SHA pinned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
