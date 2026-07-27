from __future__ import annotations

import json
from pathlib import Path

import scripts.verify_codex_handoff as verifier


def test_digest_and_manifest_loading(tmp_path: Path) -> None:
    payload = tmp_path / "payload.txt"
    payload.write_text("evidence\n", encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"files": []}), encoding="utf-8")
    assert len(verifier.digest(payload)) == 64
    assert verifier.load_manifest(manifest)["files"] == []


def test_missing_manifest_path_is_reported(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path
    manifest = root / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "expected_branch": "main",
                "expected_minimum_commit_count": 0,
                "files": [
                    {
                        "path": "missing.txt",
                        "size_bytes": 1,
                        "sha256": "0" * 64,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(verifier, "candidate_paths", lambda *_: set())
    errors = verifier.verify(root, manifest)
    assert "missing or escaping path: missing.txt" in errors
