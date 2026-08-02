#!/usr/bin/env python3
"""Run a bounded public-source recovery verification in a hosted runner."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request
from pathlib import Path

REPOSITORY_PATTERN = re.compile(r"[A-Za-z0-9_.-]{1,100}/[A-Za-z0-9_.-]{1,100}")
REVISION_PATTERN = re.compile(r"[0-9a-f]{40}")


def validate_source(repository: str, revision: str) -> None:
    """Restrict downloads to an exact public GitHub repository and commit."""
    if REPOSITORY_PATTERN.fullmatch(repository) is None:
        raise ValueError("repository must be a plain owner/name identifier")
    if REVISION_PATTERN.fullmatch(revision) is None:
        raise ValueError("revision must be a 40-character lowercase Git SHA")


def validate_archive_members(members: list[tarfile.TarInfo], destination: Path) -> None:
    """Reject members that could escape the extraction directory."""
    root = destination.resolve()
    for member in members:
        target = (destination / member.name).resolve()
        if target != root and root not in target.parents:
            raise ValueError(f"unsafe archive member: {member.name}")
        if member.issym() or member.islnk():
            raise ValueError(f"archive links are not accepted: {member.name}")


def run(repository: str, revision: str, output: Path | None) -> dict[str, object]:
    validate_source(repository, revision)
    started = time.monotonic()
    source_url = f"https://codeload.github.com/{repository}/tar.gz/{revision}"
    with urllib.request.urlopen(source_url, timeout=120) as response:  # noqa: S310
        archive = response.read()

    with tempfile.TemporaryDirectory(prefix="riopa-hf-recovery-") as temp_dir:
        destination = Path(temp_dir)
        archive_path = destination / "source.tar.gz"
        archive_path.write_bytes(archive)
        with tarfile.open(archive_path, mode="r:gz") as tar:
            members = tar.getmembers()
            validate_archive_members(members, destination)
            tar.extractall(destination, filter="data")  # noqa: S202

        roots = sorted(path for path in destination.iterdir() if path.is_dir())
        if len(roots) != 1:
            raise ValueError("source archive must contain exactly one top-level directory")
        checkout = roots[0]
        required = (
            "pyproject.toml",
            "conductor/tracks",
            "scripts/validate_all_track_panel.py",
            "docs/panel-reports/20260802/manifest.json",
        )
        missing = [path for path in required if not (checkout / path).exists()]
        command = [
            sys.executable,
            "scripts/validate_all_track_panel.py",
            "docs/panel-reports/20260802/adversarial-analyst.json",
            "docs/panel-reports/20260802/evidence-auditor.json",
            "docs/panel-reports/20260802/reproducer.json",
            "--tracks-root",
            "conductor/tracks",
            "--synthesis",
            "docs/panel-reports/20260802/orchestrator-synthesis.json",
        ]
        completed = subprocess.run(  # noqa: S603
            command,
            cwd=checkout,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )

    result = "passed" if not missing and completed.returncode == 0 else "failed"
    receipt: dict[str, object] = {
        "schema": "riopa.hf-hosted-recovery.v1",
        "repository": repository,
        "revision": revision,
        "source_url": source_url,
        "archive_sha256": hashlib.sha256(archive).hexdigest(),
        "archive_bytes": len(archive),
        "archive_members": len(members),
        "required_paths_missing": missing,
        "validator_returncode": completed.returncode,
        "validator_stdout": completed.stdout.strip(),
        "validator_stderr": completed.stderr.strip(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "result": result,
        "non_claims": [
            "not production disaster recovery",
            "not national-scale performance",
            "not external user or operator evidence",
            "not release authority",
        ],
    }
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if output is not None:
        output.write_text(rendered)
    print(rendered, end="")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", default="edithatogo/riopa-infrastructure")
    parser.add_argument("--revision", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    receipt = run(args.repository, args.revision, args.output)
    return 0 if receipt["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
