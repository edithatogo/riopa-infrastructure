"""Reproduce the bounded native-capture to derived-view migration offline."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from riopa_provenance.capture_migration import migrate_capture_jsonl, recover_capture
from riopa_provenance.hashing import sha256_file, sha256_json

SOURCE = "evidence/stats-nz-meshblock-2026-projection/capture-records.jsonl"
SCHEMA = "schemas/archived-capture-view.schema.json"


def build_evidence(root: Path) -> dict[str, Any]:
    source = root / SOURCE
    source_digest = sha256_file(source)
    validator = Draft202012Validator(json.loads((root / SCHEMA).read_text()))
    with tempfile.TemporaryDirectory() as folder:
        destination = Path(folder) / "views.jsonl"
        count = migrate_capture_jsonl(source, destination)
        native = [json.loads(line) for line in source.read_text().splitlines()]
        views = [json.loads(line) for line in destination.read_text().splitlines()]
        restored = []
        for view in views:
            validator.validate(view)
            restored.append(recover_capture(view))
        if native != restored or sha256_file(source) != source_digest:
            raise ValueError("migration did not preserve original records and source bytes")
        if migrate_capture_jsonl(source, destination) != count:
            raise ValueError("migration retry did not reproduce its record count")
        output_digest = sha256_file(destination)
    return {
        "evidence_id": "urn:riopa:evidence:archived-capture-migration:2026-09-12",
        "status": "bounded-real-archive-view-migration-reproduced",
        "source_contract": "archived_http_capture/1.0.0",
        "target_contract": "archived_capture_view/1.1.0-experimental",
        "source": SOURCE,
        "source_sha256": source_digest,
        "target_schema": SCHEMA,
        "target_schema_sha256": sha256_file(root / SCHEMA),
        "output_jsonl_sha256": output_digest,
        "restored_records_sha256": sha256_json(restored),
        "source_records_sha256": sha256_json(native),
        "record_count": count,
        "canonical_records_preserved": True,
        "original_file_bytes_preserved": True,
        "idempotent_retry": True,
        "promotion_allowed": False,
        "non_claims": [
            "This is a derived native-capture adapter, not provenance-event 1.1 publication.",
            "Evidence references do not grant rights, verify their contents or confer authority.",
            "Only one archived national capture family is exercised; no national bulk rebuild.",
            (
                "Broader cross-runtime, candidate qualification, operational and release "
                "gates remain open."
            ),
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(build_evidence(args.root), indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
