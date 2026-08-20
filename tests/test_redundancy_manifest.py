from __future__ import annotations

import json
from pathlib import Path

from scripts.build_redundancy_manifest import build_manifest


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
