from pathlib import Path

from riopa_provenance.hashing import (
    canonical_json_bytes,
    sha256_file,
    sha256_json,
    verify_file_digests,
)


def test_canonical_hash_is_key_order_independent() -> None:
    left = {"b": 2, "a": 1}
    right = {"a": 1, "b": 2}
    assert canonical_json_bytes(left) == canonical_json_bytes(right)
    assert sha256_json(left) == sha256_json(right)


def test_verify_file_digests_reports_mismatch_and_missing(tmp_path: Path) -> None:
    payload = tmp_path / "payload.bin"
    payload.write_bytes(b"stable")
    assert verify_file_digests({"payload.bin": sha256_file(payload)}, root=tmp_path) == ()
    failures = verify_file_digests(
        {"payload.bin": "0" * 64, "missing": "1" * 64, "../escape": "2" * 64},
        root=tmp_path,
    )
    assert any("digest mismatch" in item for item in failures)
    assert any("missing" in item for item in failures)
    assert any("unsafe path" in item for item in failures)
