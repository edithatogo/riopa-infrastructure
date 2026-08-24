from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from riopa_provenance.capture import CaptureResult
from riopa_provenance.hashing import sha256_bytes
from riopa_provenance.web_archive import (
    WebArchiveError,
    WebArchivePolicy,
    package_capture_as_wacz,
)


def _capture(tmp_path: Path, payload: bytes = b"hello") -> CaptureResult:
    path = tmp_path / "object"
    path.write_bytes(payload)
    return CaptureResult(
        capture_id="urn:uuid:11111111-1111-1111-1111-111111111111",
        source_id="source",
        endpoint_id="endpoint",
        status_code=200,
        media_type="application/json",
        retrieved_at="2026-08-24T00:00:00Z",
        object_sha256=sha256_bytes(payload),
        size_bytes=len(payload),
        object_path=path,
        metadata_path=tmp_path / "metadata.json",
        request_fingerprint="f" * 64,
    )


def _policy(**overrides: object) -> WebArchivePolicy:
    values: dict[str, object] = {"enabled": True, "allowed_hosts": frozenset({"data.example"})}
    values.update(overrides)
    return WebArchivePolicy(**values)  # type: ignore[arg-type]


def test_wacz_is_deterministic_and_contains_digest_bound_record(tmp_path: Path) -> None:
    capture = _capture(tmp_path)
    first = package_capture_as_wacz(
        capture,
        target_url="https://data.example/records/1",
        output_path=tmp_path / "first.wacz",
        policy=_policy(),
    )
    second = package_capture_as_wacz(
        capture,
        target_url="https://data.example/records/1",
        output_path=tmp_path / "second.wacz",
        policy=_policy(),
    )
    assert first.warc_sha256 == second.warc_sha256
    assert first.package_sha256 == second.package_sha256
    assert first.path.read_bytes() == second.path.read_bytes()
    with zipfile.ZipFile(first.path) as archive:
        assert archive.namelist() == ["datapackage.json", "archive/data.warc"]
        warc = archive.read("archive/data.warc")
        assert b"WARC-Type: response" in warc
        assert b"WARC-Target-URI: https://data.example/records/1" in warc
        assert b"hello" in warc


@pytest.mark.parametrize(
    ("target_url", "message"),
    [
        ("http://data.example/records/1", "HTTPS"),
        ("https://user:pass@data.example/records/1", "userinfo"),
        ("https://other.example/records/1", "allowlisted"),
        ("https://data.example/records/1?token=secret", "secret query"),
    ],
)
def test_wacz_policy_rejects_unsafe_target(tmp_path: Path, target_url: str, message: str) -> None:
    with pytest.raises(WebArchiveError, match=message):
        package_capture_as_wacz(
            _capture(tmp_path),
            target_url=target_url,
            output_path=tmp_path / "archive.wacz",
            policy=_policy(),
        )


def test_wacz_policy_rejects_disabled_missing_or_mutated_capture(tmp_path: Path) -> None:
    capture = _capture(tmp_path)
    with pytest.raises(WebArchiveError, match="disabled"):
        package_capture_as_wacz(
            capture,
            target_url="https://data.example/records/1",
            output_path=tmp_path / "disabled.wacz",
            policy=_policy(enabled=False),
        )
    capture.object_path.write_bytes(b"mutated")
    with pytest.raises(WebArchiveError, match="digest"):
        package_capture_as_wacz(
            capture,
            target_url="https://data.example/records/1",
            output_path=tmp_path / "mutated.wacz",
            policy=_policy(),
        )
