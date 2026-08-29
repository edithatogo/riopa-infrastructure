import hashlib
import json
from pathlib import Path

import pytest

from scripts.verify_hf_release_mirror import verify


def test_verify_checks_each_expected_byte(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    payloads = {"one.txt": b"one", "release-metadata.json": b"metadata"}
    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_text(
        json.dumps(
            {
                "release": "v0.4.0",
                "assets": [{"name": "one.txt", "sha256": hashlib.sha256(b"one").hexdigest()}],
            }
        ),
        encoding="utf-8",
    )
    mirror_path = tmp_path / "mirror.json"
    mirror_path.write_text(
        json.dumps(
            {
                "source_publication_receipt": {
                    "sha256": hashlib.sha256(receipt_path.read_bytes()).hexdigest()
                },
                "mirror": {
                    "repository": "owner/dataset",
                    "commit": "abc123",
                    "path": "releases/v0.4.0",
                    "release_metadata_sha256": hashlib.sha256(
                        payloads["release-metadata.json"]
                    ).hexdigest(),
                },
                "qualification": {"does_not_establish": ["preservation acceptance"]},
            }
        ),
        encoding="utf-8",
    )

    def fake_fetch(url: str) -> bytes:
        return payloads[url.rsplit("/", 1)[-1].split("?", 1)[0]]

    monkeypatch.setattr("scripts.verify_hf_release_mirror.fetch_bytes", fake_fetch)
    report = verify(receipt_path, mirror_path)
    assert report["verified_file_count"] == 2
    assert report["verified_files"] == ["one.txt", "release-metadata.json"]


def test_verify_fails_on_source_receipt_drift(tmp_path: Path) -> None:
    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_text(json.dumps({"release": "v0.4.0", "assets": []}), encoding="utf-8")
    mirror_path = tmp_path / "mirror.json"
    mirror_path.write_text(
        json.dumps(
            {
                "source_publication_receipt": {"sha256": "0" * 64},
                "mirror": {
                    "repository": "owner/dataset",
                    "commit": "abc123",
                    "path": "releases/v0.4.0",
                    "release_metadata_sha256": "0" * 64,
                },
                "qualification": {"does_not_establish": []},
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="historical publication receipt"):
        verify(receipt_path, mirror_path)
