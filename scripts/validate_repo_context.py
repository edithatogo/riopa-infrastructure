#!/usr/bin/env python3
"""Validate the canonical single-developer/security/contribution context."""

from __future__ import annotations

import argparse
from pathlib import Path

REQUIRED_MARKERS = {
    "CONTRIBUTING.md": ("Conventional Commits", "Automated agents", "roadmap validate"),
    "SECURITY.md": ("private vulnerability reporting", "release blockers"),
    ".github/pull_request_template.md": ("Conductor track / issue", "Gate honesty"),
    "docs/solo-maintainer-security-context.md": (
        "single-person repository",
        "verify_github_main_protection.py",
        "Renovate app access",
    ),
    "docs/single-person-operating-model-20260821.md": (
        "one person",
        "owner-authorized agent observations",
        "accountable release authority",
    ),
    "docs/owner-accountable-authority-20260821.json": (
        "repository owner",
        "tier-promotion-not-authorized",
        "single-person-repository-agent-operated-workflows",
    ),
}


def context_errors(root: Path) -> list[str]:
    errors: list[str] = []
    for relative, markers in REQUIRED_MARKERS.items():
        path = root / relative
        if not path.is_file():
            errors.append(f"missing context file: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"{relative}: missing marker {marker!r}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    errors = context_errors(args.root.resolve())
    if errors:
        print("\n".join(errors))
        return 1
    print("Repository context contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
