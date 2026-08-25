"""Validate the bounded real-data publication candidate without publishing it."""

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


def validate_candidate(root: Path) -> dict[str, Any]:
    candidate_path = root / "docs/publication-real-data-release-candidate-20260825.json"
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    if candidate.get("promotion_allowed") is not False:
        raise ValueError("real-data candidate must remain promotion-disabled")
    source = candidate.get("source_packet", {})
    manifest_path = root / source["manifest"]
    if sha256(manifest_path) != source.get("manifest_sha256"):
        raise ValueError("source manifest digest does not match candidate")
    artifact_receipts = candidate.get("artifacts", [])
    if not artifact_receipts:
        raise ValueError("candidate must list materialized artifacts")
    artifacts: list[dict[str, Any]] = []
    for receipt in artifact_receipts:
        path = root / receipt["path"]
        digest = sha256(path)
        if digest != receipt.get("sha256"):
            raise ValueError(f"artifact digest does not match candidate: {receipt['path']}")
        artifacts.append({"path": receipt["path"], "sha256": digest, "bytes": path.stat().st_size})
    return {
        "schema": "riopa.publication-real-data-release-candidate-validation.v1",
        "candidate_id": candidate["candidate_id"],
        "status": "digest-validated-promotion-disabled",
        "candidate": str(candidate_path.relative_to(root)),
        "source_manifest": str(manifest_path.relative_to(root)),
        "source_manifest_sha256": source["manifest_sha256"],
        "artifacts": artifacts,
        "promotion_allowed": False,
        "open_gates": candidate["open_gates"],
        "non_claims": [
            (
                "Digest validation is not a publication, preservation receipt, or external "
                "reproduction."
            ),
            "The bounded council slice is not coverage or national evidence.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = validate_candidate(args.root.resolve())
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
