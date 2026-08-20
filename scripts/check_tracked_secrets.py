#!/usr/bin/env python3
"""Fail closed on high-confidence credentials in tracked repository files."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

PATTERNS = (
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}")),
    ("Hugging Face token", re.compile(r"hf_[A-Za-z0-9]{20,}")),
    ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
)


def tracked_paths(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    return [root / item for item in result.stdout.decode().split("\0") if item]


def secret_findings(root: Path) -> list[str]:
    findings: list[str] = []
    for path in tracked_paths(root):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError, UnicodeDecodeError:
            continue
        for label, pattern in PATTERNS:
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                findings.append(f"{path.relative_to(root)}:{line}: {label}")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    findings = secret_findings(args.root.resolve())
    if findings:
        print("\n".join(findings))
        return 1
    print("Tracked-secret scan passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
