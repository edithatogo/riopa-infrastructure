"""Deterministic, local-only restore and rollback evidence harness.

The harness deliberately operates on a directory supplied by the caller and
never contacts a service or mutates a live deployment.  It is suitable for
producing reproducible drill evidence while operational qualification remains
pending.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any


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


_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_EXERCISE_STATUSES = frozenset({"planned", "executed-local", "executed-hosted", "failed"})


def validate_exercise_report(report: Mapping[str, Any] | None) -> tuple[str, ...]:
    """Validate a digest-bound restore/DR report without asserting its outcome.

    ``executed-local`` and ``executed-hosted`` are evidence classifications,
    not production qualification.  The validator therefore requires explicit
    scope, hashes, timestamps and RPO/RTO fields while preserving failed runs.
    """

    if not isinstance(report, Mapping):
        return ("exercise report must be an object",)
    errors: list[str] = []
    required = ("exercise_id", "operation", "status", "source_revision", "started_at", "ended_at")
    for field in required:
        if not isinstance(report.get(field), str) or not str(report[field]).strip():
            errors.append(f"{field} is required")
    if report.get("operation") not in {"restore", "rollback", "correction", "withdrawal"}:
        errors.append("operation is unsupported")
    if report.get("status") not in _EXERCISE_STATUSES:
        errors.append("status is unsupported")
    for field in ("recovery_point_sha256", "restored_object_sha256", "raw_log_sha256"):
        value = report.get(field)
        if not isinstance(value, str) or not _DIGEST.fullmatch(value):
            errors.append(f"{field} must be a lowercase SHA-256 digest")
    timings = report.get("timings")
    if not isinstance(timings, Mapping):
        errors.append("timings are required")
    else:
        for field in ("rpo_seconds", "rto_seconds"):
            value = timings.get(field)
            if not isinstance(value, (int, float)) or value < 0:
                errors.append(f"timings.{field} must be non-negative")
    scope = report.get("scope")
    invalid_scope = (
        not isinstance(scope, list)
        or not scope
        or any(not isinstance(item, str) or not item for item in scope)
    )
    if invalid_scope:
        errors.append("scope must be a non-empty string array")
    if report.get("status") == "failed" and not isinstance(report.get("failure_reason"), str):
        errors.append("failed exercises require failure_reason")
    if report.get("status") == "executed-hosted" and report.get("hosted_run_id") in (None, ""):
        errors.append("hosted exercises require hosted_run_id")
    return tuple(dict.fromkeys(errors))


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
