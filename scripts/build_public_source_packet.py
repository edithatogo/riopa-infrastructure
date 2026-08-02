#!/usr/bin/env python3
"""Build a content-addressed public-source packet without fetching payloads.

The packet deliberately separates metadata discovery from acquisition.  A
negative receipt is emitted when authority, rights, or availability is not
resolved; callers must never treat it as evidence of a usable source.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def build_packet(output: Path, sources: list[dict[str, Any]]) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    captured_at = datetime.now(UTC).isoformat()
    entries: list[dict[str, Any]] = []
    for source in sources:
        required = {"source_id", "landing_url", "status"}
        missing = sorted(required - source.keys())
        if missing:
            raise ValueError(f"source entry missing required fields: {', '.join(missing)}")
        status = str(source["status"])
        if status not in {"metadata-only", "blocked", "approved-pending-capture", "captured"}:
            raise ValueError(f"unsupported source status: {status}")
        entry = dict(source)
        entry.setdefault("authority", None)
        entry.setdefault("terms_url", None)
        entry.setdefault("version", None)
        entry.setdefault("retrieved_at", None)
        entry.setdefault("payload_sha256", None)
        entry.setdefault("limitations", [])
        if status != "captured":
            entry["payload_sha256"] = None
            entry["negative_receipt"] = True
            entry.setdefault("limitations", []).append(
                "Payload not acquired; authority, rights or availability gate remains open."
            )
        else:
            if not entry["payload_sha256"]:
                raise ValueError("captured source requires payload_sha256")
            entry["negative_receipt"] = False
        entries.append(entry)

    manifest = {
        "schema_version": "1.0.0",
        "record_type": "riopa_public_source_packet",
        "packet_id": "public-source-packet-20260802",
        "captured_at": captured_at,
        "scope": "bounded-public-data-technical-preview",
        "payloads_acquired": any(not e["negative_receipt"] for e in entries),
        "sources": entries,
        "non_claims": [
            "Metadata and negative receipts do not establish authority or permission.",
            "This packet does not support operational, national-completeness or safety claims.",
        ],
    }
    digest_view = dict(manifest)
    digest_view.pop("captured_at", None)
    encoded = json.dumps(digest_view, ensure_ascii=False, sort_keys=True, indent=2).encode()
    manifest["manifest_sha256"] = hashlib.sha256(encoded).hexdigest()
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    for entry in entries:
        if entry["negative_receipt"]:
            receipt = {
                "schema_version": "1.0.0",
                "record_type": "riopa_public_source_negative_receipt",
                "source_id": entry["source_id"],
                "landing_url": entry["landing_url"],
                "status": entry["status"],
                "recorded_at": captured_at,
                "reason": entry["limitations"][-1],
                "resolution_required": ["authority", "terms_url", "version", "payload_sha256"],
                "non_claim": "No source payload was acquired or approved.",
            }
            safe_id = entry["source_id"].replace(":", "_").replace("/", "_")
            (output / f"negative-receipt-{safe_id}.json").write_text(
                json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metadata", type=Path, help="JSON list of source metadata entries")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sources = json.loads(args.metadata.read_text(encoding="utf-8"))
    if not isinstance(sources, list):
        raise SystemExit("metadata must be a JSON array")
    print(json.dumps(build_packet(args.output, sources), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
