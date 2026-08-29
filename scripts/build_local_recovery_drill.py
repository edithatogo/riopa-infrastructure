#!/usr/bin/env python3
"""Build a deterministic, local-only recovery and rollback drill report."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

from riopa_provenance.recovery import restore, rollback, snapshot


def _write_fixture(path: Path, value: str) -> None:
    path.mkdir()
    (path / "state.json").write_text(
        json.dumps({"schema": "fixture-1", "state": value}, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def build_report() -> dict[str, Any]:
    """Execute snapshot, restore, rollback and tamper rejection in a temp tree."""

    with tempfile.TemporaryDirectory(prefix="riopa-recovery-drill-") as raw:
        root = Path(raw)
        source = root / "source"
        snapshot_dir = root / "snapshot"
        restored = root / "restored"
        current = root / "current"
        prior = root / "prior"
        rolled_back = root / "rolled-back"
        _write_fixture(source, "v1")
        _write_fixture(current, "v2")
        _write_fixture(prior, "v1")
        snapshot_evidence = snapshot(source, snapshot_dir)
        restore_evidence = restore(snapshot_dir, restored, snapshot_evidence.digest)
        rollback_evidence = rollback(current, prior, rolled_back)
        tampered = snapshot_dir / "state.json"
        original = tampered.read_text(encoding="utf-8")
        tampered.write_text(original + "tampered\n", encoding="utf-8")
        try:
            restore(snapshot_dir, root / "tampered-restore", snapshot_evidence.digest)
        except ValueError as error:
            tamper_rejected = "digest mismatch" in str(error)
        else:
            tamper_rejected = False

    return {
        "evidence_id": "OPS-LOCAL-RECOVERY-DRILL-20260825",
        "scope": "bounded-regional-public-datasets-only-technical-preview",
        "status": "passing-local-synthetic",
        "operations": [
            {"operation": snapshot_evidence.operation, "digest": snapshot_evidence.digest},
            {"operation": restore_evidence.operation, "digest": restore_evidence.digest},
            {"operation": rollback_evidence.operation, "digest": rollback_evidence.digest},
        ],
        "tamper_rejection": tamper_rejected,
        "fail_closed": tamper_rejected and restore_evidence.digest == snapshot_evidence.digest,
        "non_claims": [
            (
                "This is a repository-local synthetic drill, not hosted or production "
                "disaster recovery."
            ),
            (
                "It does not establish RPO/RTO, provider acceptance, preservation "
                "acceptance or release authority."
            ),
            (
                "Role-separated agent-operator and agent-user journey evidence remains "
                "mandatory for "
                "beta, RC and stable-v1."
            ),
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build_report()
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0 if report["fail_closed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
