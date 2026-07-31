#!/usr/bin/env python3
"""Build a byte-deterministic reviewer handoff for the WP-010 benchmark."""

from __future__ import annotations

import argparse
import hashlib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples" / "wp010-synthetic-benchmark"
FIXED_TIME = (2026, 7, 31, 0, 0, 0)


def build(output: Path) -> str:
    output.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(path for path in SOURCE.rglob("*") if path.is_file())
    with zipfile.ZipFile(output, "w") as archive:
        for path in files:
            relative = path.relative_to(SOURCE).as_posix()
            info = zipfile.ZipInfo(relative, FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compresslevel=9)
    return hashlib.sha256(output.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    digest = build(args.output.resolve())
    print(f"{digest}  {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
