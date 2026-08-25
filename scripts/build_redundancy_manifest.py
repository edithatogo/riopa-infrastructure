"""Build a content-addressed manifest for replicated evidence bundles."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _bundle_digest(bundle_id: str, files: list[dict[str, object]]) -> str:
    payload = json.dumps(
        {"bundle_id": bundle_id, "files": files},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_manifest(root: Path, *, bundle_id: str) -> dict[str, object]:
    files = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        files.append(
            {
                "path": str(path.relative_to(root)),
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
            }
        )
    manifest = {
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
    manifest["bundle_sha256"] = _bundle_digest(bundle_id, files)
    return manifest


def validate_replication_receipts(
    manifest: dict[str, object], receipts: list[dict[str, object]]
) -> tuple[str, ...]:
    """Validate exact accepted-target receipts without contacting targets."""

    bundle_id = manifest.get("bundle_id")
    bundle_sha256 = manifest.get("bundle_sha256")
    if not isinstance(bundle_id, str) or not bundle_id:
        return ("manifest requires bundle_id",)
    if not isinstance(bundle_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", bundle_sha256):
        return ("manifest requires a bundle_sha256",)
    errors: list[str] = []
    targets = manifest.get("replication_targets")
    if not isinstance(targets, list):
        return ("manifest requires a replication_targets list",)
    required: set[str] = set()
    for target in targets:
        if not isinstance(target, dict) or not isinstance(target.get("kind"), str):
            errors.append("manifest replication target requires a kind")
            continue
        if target.get("required") is True:
            required.add(target["kind"])
    seen: set[str] = set()
    for receipt in receipts:
        if not isinstance(receipt, dict):
            errors.append("receipt must be an object")
            continue
        target = receipt.get("kind")
        if not isinstance(target, str) or target not in required:
            errors.append("receipt kind is not a required replication target")
            continue
        if target in seen:
            errors.append(f"duplicate accepted receipt for {target}")
            continue
        seen.add(target)
        if receipt.get("status") != "accepted":
            errors.append(f"{target} receipt is not accepted")
        if receipt.get("bundle_id") != bundle_id:
            errors.append(f"{target} receipt bundle_id does not match")
        if receipt.get("bundle_sha256") != bundle_sha256:
            errors.append(f"{target} receipt digest does not match")
        if not isinstance(receipt.get("locator"), str) or not receipt["locator"].strip():
            errors.append(f"{target} receipt requires a locator")
    errors.extend(f"missing accepted receipt for {target}" for target in sorted(required - seen))
    return tuple(dict.fromkeys(errors))


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
