"""Detect repository-template drift without mutating the checkout."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def build_template_drift_report(root: Path, contract_path: Path) -> dict[str, Any]:
    """Return a deterministic, read-only scaffold and boundary report."""

    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    required = contract["required_scaffolding"]
    missing = sorted(path for path in required if not (root / path).exists())
    generated = sorted(
        path for path in contract["generated_boundaries"]["generated"] if (root / path).exists()
    )
    protected = sorted(
        path
        for path in contract["generated_boundaries"]["never_overwrite"]
        if (root / path).exists()
    )
    return {
        "record_type": "repository_template_drift_report",
        "template_id": contract["template_id"],
        "status": "drift" if missing else "aligned",
        "required_scaffolding": sorted(required),
        "missing_scaffolding": missing,
        "generated_boundaries_present": generated,
        "never_overwrite_present": protected,
        "safe_upgrade": not missing,
        "mutations_performed": [],
        "non_claims": [
            "This report detects repository-owned scaffold drift only.",
            "A safe upgrade is a recommendation; no local customisation or generated "
            "file is overwritten.",
        ],
    }


def main() -> int:
    root = Path.cwd()
    contract = root / "docs/repository-template-contract-20260822.json"
    print(json.dumps(build_template_drift_report(root, contract), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
