"""Verify both directions of the bounded capture migration across Python and Node."""

import argparse
import json
import subprocess
from pathlib import Path

from riopa_provenance.capture_migration import migrate_capture, recover_capture
from riopa_provenance.hashing import sha256_file, sha256_json


def build_evidence(root: Path) -> dict:
    source_path = root / "evidence/stats-nz-meshblock-2026-projection/capture-records.jsonl"
    sources = [json.loads(line) for line in source_path.read_text().splitlines()]
    views = [migrate_capture(source) for source in sources]
    requests = [{"operation": "migrate", "value": source} for source in sources]
    requests += [{"operation": "recover", "value": view} for view in views]
    results = json.loads(
        subprocess.run(
            ["node", "scripts/capture_migration_node.mjs"],
            cwd=root,
            input=json.dumps(requests),
            text=True,
            capture_output=True,
            check=True,
        ).stdout
    )
    expected = [{"accepted": True, "value": value} for value in views + sources]
    if (
        results != expected
        or [recover_capture(item["value"]) for item in results[: len(sources)]] != sources
    ):
        raise ValueError("cross-runtime migration or recovery mismatch")
    paths = [
        "scripts/capture_migration_node.mjs",
        "src/riopa_provenance/capture_migration.py",
        "schemas/archived-capture-view.schema.json",
        "tests/test_capture_migration_parity.py",
    ]
    return {
        "evidence_id": "urn:riopa:evidence:archived-capture-parity:2026-09-12",
        "scope": "structured native capture objects and experimental derived views",
        "source_sha256": sha256_file(source_path),
        "record_count": len(sources),
        "source_records_sha256": sha256_json(sources),
        "views_sha256": sha256_json(views),
        "python_to_node_recovery": True,
        "node_to_python_recovery": True,
        "identical_migration_values_and_hashes": True,
        "artifacts": {path: sha256_file(root / path) for path in paths},
        "promotion_allowed": False,
        "non_claims": [
            "No full event-profile parity, independent reproduction or release approval.",
            "Node runner consumes generated structured requests, not untrusted JSONL storage.",
            "References are declarations; no rights or publication approval is conferred.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(build_evidence(Path(".")), indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
