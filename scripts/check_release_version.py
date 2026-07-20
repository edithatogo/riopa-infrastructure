#!/usr/bin/env python3
"""Verify a release tag exactly matches the package version."""

from __future__ import annotations

import argparse
import tomllib
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--pyproject", type=Path, default=Path("pyproject.toml"))
    args = parser.parse_args()
    version = tomllib.loads(args.pyproject.read_text(encoding="utf-8"))["project"]["version"]
    expected = f"v{version}"
    if args.tag != expected:
        print(f"release tag {args.tag!r} does not match package version {expected!r}")
        return 1
    print(f"Release tag matches package version: {expected}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
