#!/usr/bin/env python3
"""Build a bounded supermarket assertion snapshot from an archived payload."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from riopa_provenance.hashing import sha256_bytes
from riopa_provenance.supermarket_pilot import build_archived_supermarket_snapshot


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("payload", type=Path, help="local GeoJSON payload from an archive")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--registry-version", required=True)
    parser.add_argument("--licence", required=True)
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--payload-sha256", required=True)
    args = parser.parse_args()

    payload_bytes = args.payload.read_bytes()
    actual_digest = sha256_bytes(payload_bytes)
    if actual_digest != args.payload_sha256:
        parser.error(
            f"payload SHA-256 mismatch: expected {args.payload_sha256}, got {actual_digest}"
        )
    payload = json.loads(payload_bytes)
    snapshot = build_archived_supermarket_snapshot(
        payload,
        source_id=args.source_id,
        registry_version=args.registry_version,
        licence=args.licence,
        observed_at=args.observed_at,
        payload_sha256=args.payload_sha256,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {"output": str(args.output), "assertion_count": len(snapshot["assertions"])},
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
