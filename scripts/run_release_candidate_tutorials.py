"""Execute every repository tutorial against one immutable candidate revision.

This is a repository-owned rehearsal. It does not promote the revision to RC
or stable status and cannot replace external user/operator evidence.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

try:
    from scripts.run_bounded_lineage_tutorial import run_tutorial
except ModuleNotFoundError:  # Direct ``python scripts/...`` execution.
    from run_bounded_lineage_tutorial import run_tutorial


TUTORIALS = ("docs/bounded-lineage-tutorial-20260825.md",)


def candidate_revision(root: Path) -> str:
    """Return the exact repository revision used for the rehearsal."""

    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    revision = result.stdout.strip()
    if not revision:
        raise RuntimeError("git returned an empty candidate revision")
    return revision


def run_release_candidate_tutorials(root: Path, output_dir: Path) -> dict[str, Any]:
    """Run all registered tutorials in disposable output locations."""

    revision = candidate_revision(root)
    output_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    for tutorial in TUTORIALS:
        with tempfile.TemporaryDirectory(prefix="riopa-rc-tutorial-", dir=output_dir) as directory:
            report = run_tutorial(root, Path(directory))
        if report["status"] != "bounded-rehearsal":
            raise RuntimeError(f"tutorial did not complete bounded rehearsal: {tutorial}")
        results.append(
            {
                "tutorial": tutorial,
                "status": "pass",
                "query_answer_count": report["query_answer_count"],
                "troubleshooting_status": report["troubleshooting"]["status"],
            }
        )
    return {
        "status": "repository-candidate-rehearsal",
        "candidate_revision": revision,
        "tutorials": results,
        "promotion_eligible": False,
        "nonclaims": [
            "This is not release-candidate or stable-v1 evidence.",
            "An agent or repository rehearsal cannot replace factual external user/operator evidence.",
            "Elapsed RC soak and accountable release-authority approval remain open.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.output_dir is None:
        with tempfile.TemporaryDirectory(prefix="riopa-rc-tutorials-") as directory:
            report = run_release_candidate_tutorials(root, Path(directory))
    else:
        report = run_release_candidate_tutorials(root, args.output_dir.resolve())
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
