from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_documentation_archive_manifest_is_content_addressed(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "manifest.json"
    subprocess.run(
        [
            sys.executable,
            "scripts/build_documentation_archive_manifest.py",
            "--root",
            ".",
            "--output",
            str(output),
        ],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    manifest = json.loads(output.read_text(encoding="utf-8"))
    assert manifest["status"] == "repository-archive-candidate"
    assert manifest["publication"]["persistent_identifier"] is None
    assert len(manifest["artifacts"]) >= 5
    assert all(len(item["sha256"]) == 64 for item in manifest["artifacts"])
    assert "External user/operator evidence" in manifest["nonclaims"][2]
