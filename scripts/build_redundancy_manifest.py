"""Build a content-addressed manifest for replicated evidence bundles."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(root: Path, *, bundle_id: str) -> dict[str, object]:
    files = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        files.append({"path": str(path.relative_to(root)), "sha256": sha256(path), "bytes": path.stat().st_size})
    return {
        "schema": "riopa.evidence-redundancy-manifest.v1",
        "bundle_id": bundle_id,
        "created_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "source": "github-actions-artifact",
        "replication_targets": [
            {"kind": "github-actions-artifact", "required": True, "status": "created"},
            {"kind": "huggingface-dataset", "required": True, "status": "pending-credential"},
            {"kind": "zenodo", "required": True, "status": "pending-credential"},
        ],
        "files": files,
        "non_claims": [
            "A manifest does not prove that a replication target accepted the bundle.",
            "Pending targets must be verified by a later receipt before preservation is qualified.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--bundle-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = build_manifest(args.root, bundle_id=args.bundle_id)
    args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
