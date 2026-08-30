#!/usr/bin/env python3
"""Prepare a bounded Tasman public candidate on Actions; do not publish it."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from riopa_provenance.hashing import sha256_file, sha256_json
from riopa_provenance.tasman_public_packet import build_tasman_public_packet


def prepare(work: Path) -> dict[str, Any]:
    store = work / "store"
    receipts = list(store.glob("tasman-receipt-*.json"))
    if len(receipts) != 1:
        raise ValueError("expected exactly one Tasman capture receipt")
    receipt = json.loads(receipts[0].read_text())
    if receipt.get("status") != "captured":
        raise ValueError("Tasman acquisition is incomplete")
    digest = sha256_json(receipt, omit_keys={"semantic_sha256"})
    if (
        receipt.get("semantic_sha256") != digest
        or receipts[0].name != f"tasman-receipt-{digest}.json"
    ):
        raise ValueError("capture receipt integrity mismatch")
    capture_set = store / receipt["zones"]["manifest_path"]
    if not capture_set.resolve().is_relative_to(store.resolve()):
        raise ValueError("capture set escapes the store")
    if sha256_file(capture_set) != receipt["zones"]["manifest_sha256"]:
        raise ValueError("capture set does not match capture receipt")
    output = work / "tasman-public-candidate"
    manifest = build_tasman_public_packet(
        store, capture_set, receipt["selected_item"]["rights_capture_id"], output
    )
    verified_set = json.loads((output / "capture-set.json").read_text())
    if (
        receipt["source_id"] != manifest["source_id"]
        or receipt["zones"]["feature_count"] != verified_set["feature_count"]
    ):
        raise ValueError("receipt summary differs from verified packet")
    report = {
        "schema_version": "1.0.0",
        "source_id": manifest["source_id"],
        "status": "prepared-not-published",
        "manifest_sha256": sha256_file(output / "manifest.json"),
        "capture_set_id": manifest["capture_set_id"],
        "feature_count": verified_set["feature_count"],
        "file_count": len(manifest["files"]),
        "file_bytes": sum(item["bytes"] for item in manifest["files"]),
        "licence": manifest["licence"],
        "attribution": manifest["attribution"],
        "non_claims": [
            "No public payload upload or anonymous payload acceptance yet.",
            "No canonical/materialised rebuild or operative legal status claimed.",
        ],
    }
    evidence = work / "public"
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "tasman-packet-preparation.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.work), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
