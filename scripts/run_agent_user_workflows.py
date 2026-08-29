#!/usr/bin/env python3
"""Run the two bounded agent-operated user journeys and emit a report."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

WORKFLOWS: dict[str, list[str]] = {
    "validate-and-orient": ["uv", "run", "riopa", "validate", "--root", "."],
    "build-and-verify-research-object": [
        "uv",
        "run",
        "riopa",
        "research-object",
        "--manifest",
        "examples/minimal/snapshot-manifest.json",
        "--output-dir",
        "{output_dir}/research-object",
    ],
}


def run(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for workflow_id, template in WORKFLOWS.items():
        command = [item.format(output_dir=str(output_dir)) for item in template]
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
        log_path = output_dir / f"{workflow_id}.log"
        log_path.write_text(completed.stdout + completed.stderr, encoding="utf-8")
        results.append(
            {
                "workflow_id": workflow_id,
                "command": command,
                "status": "passed" if completed.returncode == 0 else "failed",
                "exit_code": completed.returncode,
                "log": log_path.name,
            }
        )
    report = {
        "schema_version": "1.0.0",
        "report_id": "urn:riopa:evidence:agent-user-workflows:1.0.0",
        "classification": "owner-authorized-agent-workflows-not-independent-human-evidence",
        "workflows": results,
        "scope": "bounded-regional-public-datasets-only-non-operational-technical-preview",
        "non_claims": [
            "This report is not independent human review.",
            "This report is not external participant evidence.",
            "This report does not satisfy elapsed beta or RC soak duration.",
            "This report does not authorize promotion.",
            "Network, timetable, facility, national, clinical and dispatch claims remain disabled.",
        ],
    }
    (output_dir / "agent-user-workflows.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    report = run(args.output_dir)
    print(
        json.dumps(
            {
                "report_id": report["report_id"],
                "status": [item["status"] for item in report["workflows"]],
            }
        )
    )
    # When this file is executed directly, its directory is on ``sys.path``;
    # import the sibling validator without requiring ``scripts`` to be a package.
    from validate_agent_user_workflow_report import validate_report

    errors = validate_report(report)
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
