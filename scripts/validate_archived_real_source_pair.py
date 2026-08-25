"""Validate two archived public-source capture packets without network access.

This is a candidate-evidence validator for the connector track. It proves that
the repository contains one national archived capture family and one council
planning capture set; it does not claim a fresh live capture, source authority,
preservation acceptance, or external reproduction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def build_packet(root: Path) -> dict[str, Any]:
    national_dir = root / "evidence/stats-nz-meshblock-2026-projection"
    national_manifest = national_dir / "records-manifest.json"
    national_records = national_dir / "capture-records.jsonl"
    council_dir = root / "evidence/wp007-real-slice"
    council_manifest = council_dir / "manifest.json"
    council_set = council_dir / "store/capture-sets/b973595d-0aaf-4b18-a594-db973507195b.json"

    required = (national_manifest, national_records, council_manifest, council_set)
    missing = [str(path.relative_to(root)) for path in required if not path.is_file()]
    if missing:
        raise ValueError(f"missing archived evidence: {', '.join(missing)}")

    national_manifest_value = _load(national_manifest)
    if national_manifest_value.get("record_type") != "archived_spatial_records_manifest":
        raise ValueError("national packet is not an archived spatial records manifest")
    national_count = 0
    for line in national_records.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        value = record.get("record", {})
        if value.get("source_id") != "urn:riopa:source:stats-nz:meshblock-2026":
            raise ValueError("national capture record has an unexpected source")
        if value.get("record_type") != "archived_http_capture":
            raise ValueError("national capture record is not an archived HTTP capture")
        national_count += 1
    if national_count == 0:
        raise ValueError("national packet has no capture records")

    council_manifest_value = _load(council_manifest)
    council_set_value = _load(council_set)
    if council_manifest_value.get("record_type") != "bounded_real_vertical_slice":
        raise ValueError("council packet is not the bounded real vertical slice")
    if council_set_value.get("source_id") != "urn:riopa:source:wcc:2024-district-plan-zones":
        raise ValueError("council capture set has an unexpected source")
    if not council_set_value.get("page_capture_ids"):
        raise ValueError("council capture set has no feature-page capture")

    files = [national_manifest, national_records, council_manifest, council_set]
    return {
        "schema": "riopa.connector-archived-real-source-pair.v1",
        "status": "archived-inputs-validated-live-acceptance-pending",
        "scope": "one national public source and one council planning source",
        "sources": {
            "national": {
                "source_id": "urn:riopa:source:stats-nz:meshblock-2026",
                "manifest": str(national_manifest.relative_to(root)),
                "capture_records": str(national_records.relative_to(root)),
                "capture_record_count": national_count,
            },
            "council_planning": {
                "source_id": "urn:riopa:source:wcc:2024-district-plan-zones",
                "manifest": str(council_manifest.relative_to(root)),
                "capture_set": str(council_set.relative_to(root)),
                "feature_count": council_set_value.get("feature_count"),
            },
        },
        "file_sha256": {str(path.relative_to(root)): _sha256(path) for path in files},
        "promotion_allowed": False,
        "open_gates": [
            "fresh live-source acceptance and rights qualification",
            "preservation target acceptance and anonymous restore",
            "hosted monitoring and external reproduction",
        ],
        "non_claims": [
            "Archived packets are not evidence of a current live endpoint.",
            "This packet does not establish national coverage, authority, or release approval.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    packet = build_packet(args.root.resolve())
    args.output.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
