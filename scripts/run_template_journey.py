"""Run a deterministic, read-only template onboarding/release journey rehearsal."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.check_template_drift import build_template_drift_report


def run_template_journey(root: str | Path) -> dict[str, Any]:
    """Check documented onboarding/release prerequisites without mutating files."""

    repository = Path(root).resolve()
    if not repository.is_dir():
        raise ValueError(f"repository root does not exist: {repository}")
    contract = repository / "docs/repository-template-contract-20260822.json"
    if not contract.is_file():
        raise ValueError("repository-template contract is missing")
    drift = build_template_drift_report(repository, contract)
    checks = [
        {
            "step": "template-contract",
            "status": "pass",
            "detail": "versioned template contract is present",
        },
        {
            "step": "scaffold-drift",
            "status": "pass" if drift["status"] == "aligned" else "fail",
            "detail": drift["status"],
        },
        {
            "step": "issue-configuration",
            "status": "pass" if (repository / "project/issues.yaml").is_file() else "fail",
            "detail": "generated issue graph present",
        },
        {
            "step": "release-scaffolding",
            "status": "pass"
            if (repository / ".github/workflows/release.yml").is_file()
            else "fail",
            "detail": "release workflow present; execution is not performed",
        },
    ]
    return {
        "schema_version": "1.0.0",
        "record_type": "repository_template_journey_rehearsal",
        "repository": repository.name,
        "checks": checks,
        "status": "pass" if all(item["status"] == "pass" for item in checks) else "fail",
        "mutations_performed": [],
        "journey_class": "local-read-only-rehearsal",
        "external_gates": [
            "clean onboarding in another repository",
            "independent reproduction",
            "external-user feedback",
            "release authority",
        ],
        "promotion_allowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(run_template_journey(args.root), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Template journey rehearsal written to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
