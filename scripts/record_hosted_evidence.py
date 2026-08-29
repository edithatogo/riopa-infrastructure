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
from typing import Any

LANES: dict[str, list[str]] = {
    "agent-user-workflows": [
        "uv",
        "run",
        "python",
        "scripts/validate_resilience_matrix.py",
    ],
    "performance-rehearsal": [
        "uv",
        "run",
        "python",
        "scripts/validate_resilience_matrix.py",
    ],
    "recovery-rollback": [
        "uv",
        "run",
        "pytest",
        "-q",
        "tests/test_recovery.py",
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
    "retrospective-replay": [
        "uv",
        "run",
        "pytest",
        "-q",
        "tests/test_campaign_consistency.py",
        "tests/test_wp010_performance_contract.py",
        "tests/test_publication.py",
        "tests/test_governance.py",
    ],
}


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def run_lane(lane: str, output_dir: Path) -> dict[str, Any]:
    command = LANES[lane]
    campaign_id = os.getenv("EVIDENCE_CAMPAIGN_ID", "adhoc-technical-preview")
    qualification_epoch = os.getenv("EVIDENCE_QUALIFICATION_EPOCH", campaign_id)
    operational_cycle_id = os.getenv("EVIDENCE_OPERATIONAL_CYCLE_ID") or datetime.now(UTC).strftime(
        "%G-W%V"
    )
    candidate_revision = os.getenv("EVIDENCE_CANDIDATE_REVISION") or None
    qualifying = os.getenv("EVIDENCE_QUALIFYING", "false").lower() == "true"
    if qualifying and lane not in {"operational-observation", "rc-soak-observation"}:
        raise ValueError("only beta and RC observation lanes may be qualifying")
    try:
        source_revision = subprocess.run(
            ["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True
        ).stdout.strip()
    except OSError, subprocess.CalledProcessError:
        source_revision = os.getenv("GITHUB_SHA", "local-uncommitted")
    if qualifying and lane == "rc-soak-observation" and candidate_revision != source_revision:
        raise ValueError(
            "qualifying RC observation requires candidate_revision to equal source_revision"
        )
    if lane == "rc-soak-observation" and candidate_revision != source_revision:
        raise ValueError(
            "rc-soak-observation requires EVIDENCE_CANDIDATE_REVISION to equal GITHUB_SHA"
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    started_at = _now()
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode == 0 and lane == "performance-rehearsal":
        benchmark = subprocess.run(
            [
                "uv",
                "run",
                "python",
                "examples/wp010-performance-benchmark/run.py",
                "--output",
                str(output_dir / "benchmark.json"),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        completed = subprocess.CompletedProcess(
            command,
            benchmark.returncode,
            completed.stdout + benchmark.stdout,
            completed.stderr + benchmark.stderr,
        )
    if completed.returncode == 0 and lane == "agent-user-workflows":
        workflow_run = subprocess.run(
            [
                "uv",
                "run",
                "python",
                "scripts/run_agent_user_workflows.py",
                "--output-dir",
                str(output_dir / "user-workflows"),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        completed = subprocess.CompletedProcess(
            command,
            workflow_run.returncode,
            completed.stdout + workflow_run.stdout,
            completed.stderr + workflow_run.stderr,
        )
    ended_at = _now()
    log = completed.stdout + completed.stderr
    log_path = output_dir / f"{lane}.log"
    log_path.write_text(log)
    log_digest = hashlib.sha256(log.encode()).hexdigest()
    classification = (
        "qualifying-rc-observation"
        if qualifying and lane == "rc-soak-observation"
        else "qualifying-beta-observation"
        if qualifying and lane == "operational-observation"
        else "hosted-retrospective-supplement"
        if lane == "retrospective-replay"
        else "hosted-technical-preview-drill"
    )
    campaign_activation = None
    if qualifying:
        authority = os.getenv("EVIDENCE_ACTIVATION_AUTHORITY", "").strip()
        activated_at = os.getenv("EVIDENCE_ACTIVATED_AT", "").strip()
        if not authority or not activated_at:
            raise ValueError(
                "qualifying observations require EVIDENCE_ACTIVATION_AUTHORITY and "
                "EVIDENCE_ACTIVATED_AT"
            )
        campaign_activation = {
            "status": "activated",
            "authority": authority,
            "activated_at": activated_at,
            "campaign_id": campaign_id,
        }
    receipt = {
        "schema_version": "1.1.0",
        "campaign_id": campaign_id,
        "qualification_epoch": qualification_epoch,
        "operational_cycle_id": operational_cycle_id,
        "candidate_revision": candidate_revision,
        "lane": lane,
        "classification": classification,
        "status": "passed" if completed.returncode == 0 else "failed",
        "command": command,
        "started_at": started_at,
        "ended_at": ended_at,
        "exit_code": completed.returncode,
        "source_revision": source_revision,
        "host": {
            "provider": "github-actions" if os.getenv("GITHUB_ACTIONS") else "local",
            "run_id": os.getenv("GITHUB_RUN_ID"),
            "run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
            "runner_name": os.getenv("RUNNER_NAME", platform.node()),
            "runner_os": os.getenv("RUNNER_OS", platform.system()),
            "architecture": platform.machine(),
        },
        "hosted_run_id": os.getenv("GITHUB_RUN_ID") if qualifying else None,
        "campaign_activation": campaign_activation,
        "log": {"path": log_path.name, "sha256": log_digest},
        "non_claims": [
            "This receipt is not production disaster-recovery qualification.",
            (
                "This receipt is hosted-system evidence, not a role-separated agent "
                "user/operator journey."
            ),
            "This receipt does not satisfy elapsed soak duration by itself.",
            "This receipt is not an accountable release-authority decision.",
            "Retrospective supplements do not count as elapsed beta or RC soak observations.",
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
