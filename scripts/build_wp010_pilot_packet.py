#!/usr/bin/env python3
"""Build a deterministic, rights-conservative WP-010 preservation packet."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

FILES = (
    "evidence/wp010-bounded-pilot/manifest.json",
    "docs/wp010-bounded-pilot-decision.md",
    "docs/bounded-pilot-review-protocol.md",
    "docs/independent-reproduction-protocol.md",
    "docs/external-dependency-register.md",
    "reports/wp010-facility-source-sensitivity.md",
    "reports/wp010-subagent-review-20260801.md",
    "config/source-registry/wp010-public-pilot-candidates.yaml",
    "conductor/tracks/facility_registry_20260719/index.md",
)


def build(root: Path, output: Path) -> str:
    output.parent.mkdir(parents=True, exist_ok=True)
    missing = [path for path in FILES if not (root / path).is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for relative in FILES:
            data = (root / relative).read_bytes()
            info = zipfile.ZipInfo(relative, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    return hashlib.sha256(output.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    digest = build(root, args.output.resolve())
    print(json.dumps({"packet": str(args.output.resolve()), "sha256": digest}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
