"""Canonical hashing helpers used by profile examples and validators."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def canonical_json_bytes(value: Any) -> bytes:
    """Return deterministic UTF-8 JSON bytes for hashing.

    The candidate v1 profile uses sorted keys, compact separators, UTF-8 and
    unescaped Unicode. Production v1 should either freeze this algorithm or
    adopt a named JSON canonicalisation standard before stable release.
    """

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_json(value: Any, *, omit_keys: set[str] | None = None) -> str:
    """Hash a JSON-compatible value after optionally omitting top-level keys."""

    if omit_keys and isinstance(value, dict):
        value = {key: item for key, item in value.items() if key not in omit_keys}
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def sha256_file(path: str | Path) -> str:
    """Hash a file without loading it all into memory."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
