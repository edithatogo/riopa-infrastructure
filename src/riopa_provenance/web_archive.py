"""Offline WARC/WACZ packaging for already-captured response bytes.

This module deliberately does not fetch URLs.  It packages one verified
content-addressed capture, so web-archive evidence cannot be mistaken for a
live-source acquisition or a rights/publication decision.
"""

from __future__ import annotations

import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

from .capture import CaptureError, CaptureResult
from .hashing import canonical_json_bytes, sha256_bytes


class WebArchiveError(CaptureError):
    """Raised when an offline web-archive package cannot be built safely."""


@dataclass(frozen=True)
class WebArchivePolicy:
    """Explicit controls for packaging a captured response."""

    enabled: bool
    allowed_hosts: frozenset[str]
    max_payload_bytes: int = 512 * 1024 * 1024
    secret_query_keys: frozenset[str] = frozenset(
        {"key", "api_key", "apikey", "token", "access_token", "signature", "sig"}
    )

    def __post_init__(self) -> None:
        if not self.allowed_hosts:
            raise ValueError("allowed_hosts must not be empty")
        if self.max_payload_bytes < 1:
            raise ValueError("max_payload_bytes must be positive")


@dataclass(frozen=True)
class WACZArchive:
    """Digest-bound result of one deterministic WACZ package."""

    path: Path
    record_id: str
    warc_sha256: str
    package_sha256: str
    payload_sha256: str


def _validate_target_url(url: str, policy: WebArchivePolicy) -> None:
    parsed = urlsplit(url)
    host = parsed.hostname.casefold() if parsed.hostname else ""
    if parsed.scheme != "https" or not host or parsed.username or parsed.password:
        raise WebArchiveError("web-archive target must be an HTTPS URL without userinfo")
    if host not in {item.casefold() for item in policy.allowed_hosts}:
        raise WebArchiveError(f"web-archive target host is not allowlisted: {host}")
    query_keys = {key.casefold() for key, _ in parse_qsl(parsed.query, keep_blank_values=True)}
    if query_keys.intersection({item.casefold() for item in policy.secret_query_keys}):
        raise WebArchiveError("web-archive target URL contains a secret query key")


def _warc_record(capture: CaptureResult, target_url: str, payload: bytes) -> tuple[str, bytes]:
    record_id = f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, capture.capture_id)}"
    media_type = capture.media_type or "application/octet-stream"
    http_payload = (
        f"HTTP/1.1 {capture.status_code} Captured\r\n"
        f"Content-Type: {media_type}\r\n"
        f"Content-Length: {len(payload)}\r\n"
        f"\r\n"
    ).encode("ascii") + payload
    payload_digest = sha256_bytes(payload)
    block_digest = sha256_bytes(http_payload)
    headers = (
        "WARC/1.1\r\n"
        "WARC-Type: response\r\n"
        f"WARC-Date: {capture.retrieved_at}\r\n"
        f"WARC-Record-ID: <{record_id}>\r\n"
        f"WARC-Target-URI: {target_url}\r\n"
        f"WARC-Payload-Digest: sha256:{payload_digest}\r\n"
        f"WARC-Block-Digest: sha256:{block_digest}\r\n"
        "Content-Type: application/http; msgtype=response\r\n"
        f"Content-Length: {len(http_payload)}\r\n"
        "\r\n"
    ).encode("ascii")
    return record_id, headers + http_payload + b"\r\n\r\n"


def package_capture_as_wacz(
    capture: CaptureResult,
    *,
    target_url: str,
    output_path: str | Path,
    policy: WebArchivePolicy,
) -> WACZArchive:
    """Package one verified capture as a deterministic, single-record WACZ."""

    if not policy.enabled:
        raise WebArchiveError("WARC/WACZ packaging is disabled by policy")
    _validate_target_url(target_url, policy)
    object_path = capture.object_path
    if not object_path.is_file():
        raise WebArchiveError(f"captured object is missing: {object_path}")
    payload = object_path.read_bytes()
    payload_sha256 = sha256_bytes(payload)
    if payload_sha256 != capture.object_sha256:
        raise WebArchiveError("captured object digest does not match capture metadata")
    if len(payload) > policy.max_payload_bytes:
        raise WebArchiveError("captured object exceeds web-archive payload limit")

    record_id, warc = _warc_record(capture, target_url, payload)
    warc_sha256 = sha256_bytes(warc)
    package = {
        "profile": "data-package",
        "resources": [
            {
                "name": "data.warc",
                "path": "archive/data.warc",
                "mediatype": "application/warc",
                "bytes": len(warc),
                "hash": f"sha256:{warc_sha256}",
            }
        ],
    }
    package_bytes = canonical_json_bytes(package) + b"\n"
    path = Path(output_path)
    if path.exists():
        raise WebArchiveError(f"web-archive output already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data, media_type in (
            ("datapackage.json", package_bytes, "application/json"),
            ("archive/data.warc", warc, "application/warc"),
        ):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            info.comment = media_type.encode("ascii")
            archive.writestr(info, data)
    return WACZArchive(
        path=path,
        record_id=record_id,
        warc_sha256=warc_sha256,
        package_sha256=sha256_bytes(package_bytes),
        payload_sha256=payload_sha256,
    )
