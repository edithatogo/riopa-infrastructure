from __future__ import annotations

import json
from pathlib import Path

from scripts.build_redundancy_manifest import build_manifest, validate_replication_receipts


def test_manifest_is_content_addressed_and_fail_closed(tmp_path: Path) -> None:
    (tmp_path / "receipt.json").write_text('{"status":"success"}\n', encoding="utf-8")
    manifest = build_manifest(tmp_path, bundle_id="run-1")
    assert manifest["schema"] == "riopa.evidence-redundancy-manifest.v1"
    assert manifest["files"][0]["sha256"]
    targets = {target["kind"]: target for target in manifest["replication_targets"]}
    assert targets["github-actions-artifact"]["required"] is True
    assert targets["huggingface-dataset"]["status"] == "pending-credential"
    assert targets["zenodo"]["status"] == "pending-credential"


def test_manifest_output_round_trips(tmp_path: Path) -> None:
    (tmp_path / "receipt.json").write_text("{}", encoding="utf-8")
    output = tmp_path / "manifest.json"
    manifest = build_manifest(tmp_path, bundle_id="run-2")
    output.write_text(json.dumps(manifest), encoding="utf-8")
    assert json.loads(output.read_text(encoding="utf-8"))["bundle_id"] == "run-2"


def test_replication_receipts_require_exact_accepted_target_digests(tmp_path: Path) -> None:
    (tmp_path / "receipt.json").write_text("{}", encoding="utf-8")
    manifest = build_manifest(tmp_path, bundle_id="run-3")
    receipts = [
        {
            "kind": target,
            "status": "accepted",
            "bundle_id": "run-3",
            "bundle_sha256": manifest["bundle_sha256"],
            "locator": f"https://example.test/{target}",
        }
        for target in ("github-actions-artifact", "huggingface-dataset", "zenodo")
    ]
    assert validate_replication_receipts(manifest, receipts) == ()
    tampered = list(receipts)
    tampered[-1] = {**tampered[-1], "bundle_sha256": "0" * 64}
    assert any(
        "zenodo receipt digest" in error
        for error in validate_replication_receipts(manifest, tampered)
    )
