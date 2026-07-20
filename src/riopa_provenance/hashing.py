"""Canonical hashing helpers used by RIOPA records and validators."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import rfc8785


def canonical_json_bytes(value: Any) -> bytes:
    """Return RFC 8785 JSON Canonicalization Scheme bytes.

    Using a named canonicalisation standard is required for hashes that must be
    reproduced across Python, Rust, JavaScript, R, and other implementations.
    ``rfc8785`` rejects values that cannot be represented by the standard.
    """

    return rfc8785.dumps(value)


def sha256_bytes(value: bytes) -> str:
    """Return the lower-case SHA-256 hex digest of bytes."""

    return hashlib.sha256(value).hexdigest()


def sha256_json(value: Any, *, omit_keys: set[str] | None = None) -> str:
    """Hash a JSON-compatible value after optionally omitting top-level keys."""

    if omit_keys and isinstance(value, dict):
        value = {key: item for key, item in value.items() if key not in omit_keys}
    return sha256_bytes(canonical_json_bytes(value))


def sha256_file(path: str | Path) -> str:
    """Hash a file without loading it all into memory."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
