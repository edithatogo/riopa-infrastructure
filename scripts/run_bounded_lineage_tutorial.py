"""Run the offline lineage tutorial and its fail-closed troubleshooting path."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

from riopa_provenance.lineage import LineageError, LineageIndex


def run_tutorial(root: Path, output_dir: Path) -> dict[str, Any]:
    """Build a disposable index from the bundled synthetic manifest."""

    manifest = root / "examples/minimal/snapshot-manifest.json"
    output_dir.mkdir(parents=True, exist_ok=True)
    database = output_dir / "lineage.sqlite"
    index = LineageIndex(database)
    snapshot_id = index.import_manifest(manifest)
    snapshot = index.query(snapshot_id, question="why")

    missing = output_dir / "missing-manifest.json"
    try:
        index.import_manifest(missing)
    except LineageError as exc:
        failure = {"status": "failed-closed", "error": str(exc)}
    else:  # pragma: no cover - defensive guard for a broken validator
        raise RuntimeError("missing manifest unexpectedly imported")

    return {
        "status": "bounded-rehearsal",
        "snapshot_id": snapshot_id,
        "database": str(database),
        "query_answer_count": len(snapshot["answer"]),
        "troubleshooting": failure,
        "nonclaims": [
            "Synthetic fixture only; no live source or operational claim.",
            "The disposable SQLite index is not authoritative evidence.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.output_dir is None:
        with tempfile.TemporaryDirectory(prefix="riopa-lineage-tutorial-") as directory:
            report = run_tutorial(root, Path(directory))
    else:
        report = run_tutorial(root, args.output_dir.resolve())
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
