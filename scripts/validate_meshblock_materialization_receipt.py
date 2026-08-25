"""Validate the archived Meshblock materialization receipt and projection links."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_report(root: Path) -> dict[str, Any]:
    evidence = root / "evidence/stats-nz-meshblock-2026-projection"
    receipt_path = evidence / "materialization-receipt.json"
    records_manifest_path = evidence / "records-manifest.json"
    projection_path = evidence / "projection-records/sha256/64"
    projection_path /= "64a1cbce366794b2b802f04dbe2bf1dc5fbf813e5c5b159bcf0782af9adc511f.json"
    for path in (receipt_path, records_manifest_path, projection_path):
        if not path.is_file():
            raise ValueError(f"missing Meshblock evidence file: {path.relative_to(root)}")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    manifest = json.loads(records_manifest_path.read_text(encoding="utf-8"))
    projection = json.loads(projection_path.read_text(encoding="utf-8"))
    if receipt.get("record_type") != "spatial_materialization_receipt":
        raise ValueError("unexpected materialization receipt type")
    if manifest.get("projection_id") != receipt.get("projection_id"):
        raise ValueError("records manifest and materialization receipt disagree on projection")
    if projection.get("projection_id") != receipt.get("projection_id"):
        raise ValueError("projection record and materialization receipt disagree on projection")
    if receipt.get("geoparquet", {}).get("profile") != "GeoParquet 1.1.0":
        raise ValueError("materialization receipt is missing the GeoParquet profile")
    for kind in ("geoparquet", "duckdb", "quality_report"):
        value = receipt.get(kind) if kind != "quality_report" else receipt.get("quality_report")
        if not isinstance(value, dict) or len(str(value.get("sha256", ""))) != 64:
            raise ValueError(f"materialization receipt has no digest for {kind}")
    return {
        "schema": "riopa.meshblock-materialization-receipt-validation.v1",
        "status": "receipt-and-projection-links-validated",
        "projection_id": receipt["projection_id"],
        "receipt": str(receipt_path.relative_to(root)),
        "records_manifest": str(records_manifest_path.relative_to(root)),
        "projection_record": str(projection_path.relative_to(root)),
        "receipt_sha256": sha256(receipt_path),
        "promotion_allowed": False,
        "open_gates": [
            "bulk artifact restoration and independent target acceptance",
            "national authority and completeness evidence",
            "external reproduction and accountable release decision",
        ],
        "non_claims": [
            "This validates metadata and digest links; it does not restore bulk artifacts.",
            "The projection is not population, national authority, or operational evidence.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build_report(args.root.resolve())
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
