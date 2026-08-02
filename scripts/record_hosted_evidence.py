#!/usr/bin/env python3
"""Run a bounded evidence lane and emit a content-bound hosted receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
from datetime import UTC, datetime
from pathlib import Path

LANES: dict[str, list[str]] = {
    "recovery-rollback": [
        "uv",
        "run",
        "pytest",
        "-q",
        "tests/test_publication.py",
        "tests/test_linz_pipeline.py",
    ],
    "agent-clean-room": [
        "uv",
        "run",
        "pytest",
        "-q",
        "tests/test_wp010_benchmark.py",
    ],
    "scale-smoke": [
        "uv",
        "run",
        "pytest",
        "-q",
        "tests/test_accessibility.py",
        "tests/test_facility_location.py",
    ],
    "operational-observation": [
        "uv",
        "run",
        "pytest",
        "-q",
        "tests/test_campaign_consistency.py",
    ],
    "rc-soak-observation": ["scripts/ci_quality.sh"],
}


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def run_lane(lane: str, output_dir: Path) -> dict:
    command = LANES[lane]
    output_dir.mkdir(parents=True, exist_ok=True)
    started_at = _now()
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    ended_at = _now()
    log = completed.stdout + completed.stderr
    log_path = output_dir / f"{lane}.log"
    log_path.write_text(log)
    log_digest = hashlib.sha256(log.encode()).hexdigest()
    receipt = {
        "schema_version": "1.0.0",
        "lane": lane,
        "classification": "hosted-technical-preview-drill",
        "status": "passed" if completed.returncode == 0 else "failed",
        "command": command,
        "started_at": started_at,
        "ended_at": ended_at,
        "exit_code": completed.returncode,
        "source_revision": os.getenv("GITHUB_SHA", "local-uncommitted"),
        "host": {
            "provider": "github-actions" if os.getenv("GITHUB_ACTIONS") else "local",
            "run_id": os.getenv("GITHUB_RUN_ID"),
            "run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
            "runner_name": os.getenv("RUNNER_NAME", platform.node()),
            "runner_os": os.getenv("RUNNER_OS", platform.system()),
            "architecture": platform.machine(),
        },
        "log": {"path": log_path.name, "sha256": log_digest},
        "non_claims": [
            "This receipt is not production disaster-recovery qualification.",
            "This receipt is not external operator or external user evidence.",
            "This receipt does not satisfy elapsed soak duration by itself.",
            "This receipt is not an accountable release-authority decision.",
        ],
    }
    receipt_path = output_dir / f"{lane}.receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("lane", choices=sorted(LANES))
    parser.add_argument("--output-dir", type=Path, default=Path("dist/hosted-evidence"))
    args = parser.parse_args()
    return 0 if run_lane(args.lane, args.output_dir)["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
