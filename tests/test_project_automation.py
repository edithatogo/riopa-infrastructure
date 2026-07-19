from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_issue_graph_dry_run_resolves_parent_hierarchy() -> None:
    process = subprocess.run(
        [
            sys.executable,
            "scripts/create_issues.py",
            "--repo",
            "edithatogo/riopa-infrastructure",
            "--owner",
            "edithatogo",
            "--project-title",
            "RIOPA Stable v1.0 Roadmap",
            "--cross-repo",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert process.returncode == 0, process.stderr
    assert '"applied": false' in process.stdout
    assert '"action": "planned"' in process.stdout
