"""Deterministic, local-only restore and rollback evidence harness.

The harness deliberately operates on a directory supplied by the caller and
never contacts a service or mutates a live deployment.  It is suitable for
producing reproducible drill evidence while operational qualification remains
pending.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RecoveryEvidence:
    operation: str
    source: str
    target: str
    digest: str
    status: str

    def as_dict(self) -> dict[str, str]:
        return {
            "operation": self.operation,
            "source": self.source,
            "target": self.target,
            "digest": self.digest,
            "status": self.status,
        }


def _digest_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def snapshot(source: Path, destination: Path) -> RecoveryEvidence:
    """Copy a local fixture tree and return its deterministic digest."""
    if not source.is_dir():
        raise ValueError(f"source must be a directory: {source}")
    if destination.exists():
        raise FileExistsError(destination)
    shutil.copytree(source, destination)
    return RecoveryEvidence(
        "snapshot", str(source), str(destination), _digest_tree(destination), "executed-local"
    )


def restore(snapshot_dir: Path, destination: Path, expected_digest: str) -> RecoveryEvidence:
    """Restore a snapshot into a new local directory, verifying its digest."""
    if not snapshot_dir.is_dir():
        raise ValueError(f"snapshot must be a directory: {snapshot_dir}")
    if destination.exists():
        raise FileExistsError(destination)
    actual = _digest_tree(snapshot_dir)
    if actual != expected_digest:
        raise ValueError(f"snapshot digest mismatch: expected {expected_digest}, got {actual}")
    shutil.copytree(snapshot_dir, destination)
    return RecoveryEvidence(
        "restore", str(snapshot_dir), str(destination), actual, "executed-local"
    )


def rollback(current: Path, prior: Path, destination: Path) -> RecoveryEvidence:
    """Materialise a prior local state as a rollback target."""
    if not current.is_dir() or not prior.is_dir():
        raise ValueError("current and prior states must be directories")
    if destination.exists():
        raise FileExistsError(destination)
    shutil.copytree(prior, destination)
    return RecoveryEvidence(
        "rollback", str(current), str(destination), _digest_tree(destination), "executed-local"
    )


def write_evidence(evidence: RecoveryEvidence, path: Path) -> None:
    """Write a stable JSON evidence record."""
    path.write_text(
        json.dumps(evidence.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
