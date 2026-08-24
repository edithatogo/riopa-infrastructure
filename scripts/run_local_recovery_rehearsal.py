#!/usr/bin/env python3
"""Execute the local snapshot, restore and rollback recovery harness.

This is repository-owned rehearsal evidence only. It never contacts a provider,
changes a deployment, or satisfies production RPO/RTO or independent-target
acceptance gates.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from riopa_provenance.recovery import restore, rollback, snapshot


def run(output: Path | None = None) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="riopa-recovery-") as directory:
        root = Path(directory)
        source = root / "source"
        source.mkdir()
        (source / "manifest.json").write_text('{"revision":"fixture-1"}\n', encoding="utf-8")
        (source / "payload.txt").write_text("bounded-fixture\n", encoding="utf-8")
        prior = root / "prior"
        prior.mkdir()
        (prior / "manifest.json").write_text('{"revision":"fixture-0"}\n', encoding="utf-8")
        current = root / "current"
        current.mkdir()
        (current / "manifest.json").write_text('{"revision":"fixture-1"}\n', encoding="utf-8")
        snap = snapshot(source, root / "snapshot")
        restored = restore(root / "snapshot", root / "restored", snap.digest)
        rolled_back = rollback(current, prior, root / "rolled-back")
        report: dict[str, object] = {
            "status": "passed",
            "classification": "repository-rehearsal-not-operational-evidence",
            "operations": [snap.as_dict(), restored.as_dict(), rolled_back.as_dict()],
            "safety": {
                "provider_contacted": False,
                "deployment_mutated": False,
                "independent_target": False,
            },
            "non_claims": [
                "This is not provider-backed backup or restore evidence.",
                (
                    "This is not a production-representative disaster-recovery exercise "
                    "or RPO/RTO receipt."
                ),
                "This does not satisfy independent target acceptance or release authority.",
            ],
        }
    if output is not None:
        output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run(args.output)
    print(json.dumps({"status": report["status"], "classification": report["classification"]}))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
