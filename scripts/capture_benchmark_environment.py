#!/usr/bin/env python3
"""Capture reproducibility metadata for the WP-010 benchmark contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _sha256(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"benchmark input is missing: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture() -> dict[str, Any]:
    try:
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise RuntimeError("benchmark environment capture requires a Git checkout") from exc
    workload = ROOT / "examples/wp010-performance-benchmark/workload.json"
    manifest = ROOT / "docs/national-workload-manifest-20260803.json"
    return {
        "schema_version": "1.0.0",
        "benchmark_id": "urn:riopa:benchmark:wp010:performance-contract:1.0.0",
        "repository_revision": revision,
        "python": sys.version.split()[0],
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "workload_sha256": _sha256(workload),
        "national_manifest_sha256": _sha256(manifest),
        "command": "python examples/wp010-performance-benchmark/run.py --output <path>",
        "network_contacted": False,
        "classification": "environment-capture-only",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(capture(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
