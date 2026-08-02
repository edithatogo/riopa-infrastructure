#!/usr/bin/env python3
"""Materialize bounded summaries from immutable Hugging Face food packets."""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from pathlib import Path
from typing import Any

PACKETS = {
    "osm-new-zealand-food-service": "d834601efedada86be03dee2ff7a90d0fa37c0a2",
    "marlborough-food-premise-licences": "b31703eb0dbdaa6aa05b6a84df5fe46e57e37ee0",
    "hamilton-food-premise-register": "3d3d0f4eb3065bcfb28e1c05cb8c7012a58df433",
}


def fetch(source_id: str, revision: str, name: str) -> bytes:
    url = f"https://huggingface.co/datasets/edithatogo/riopa-public-data-archive/resolve/{revision}/snapshots/{source_id}/{name}"
    with urllib.request.urlopen(url, timeout=120) as response:
        return response.read()


def summarize(source_id: str, revision: str) -> dict[str, Any]:
    manifest = json.loads(fetch(source_id, revision, "manifest.json"))
    payload = fetch(source_id, revision, "payload")
    expected = manifest.get("payload", {}).get("sha256")
    observed = hashlib.sha256(payload).hexdigest()
    if expected and expected != observed:
        raise ValueError(f"{source_id}: payload digest mismatch")
    value = json.loads(payload)
    if isinstance(value, list):
        records = value
        null_geometry = 0
    else:
        records = value.get("features", [])
        null_geometry = sum(item.get("geometry") is None for item in records)
    return {
        "source_id": source_id,
        "packet_revision": revision,
        "payload_sha256": observed,
        "record_count": len(records),
        "null_geometry_count": null_geometry,
        "source_assertions_only": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = {
        "evidence_id": "facility-source-materialization-20260803",
        "status": "materialized-source-summaries-non-authoritative",
        "sources": [summarize(source_id, revision) for source_id, revision in PACKETS.items()],
        "claims": {
            "authoritative_registry": False,
            "national_completeness": False,
            "reconciliation_qualification": "pending",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
