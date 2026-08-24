from pathlib import Path

from riopa_provenance.release_signing import (
    build_release_signing_manifest,
    validate_release_signing_manifest,
)


def test_build_release_signing_manifest_is_content_bound_and_sorted(tmp_path: Path) -> None:
    (tmp_path / "z.txt").write_text("z", encoding="utf-8")
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    manifest = build_release_signing_manifest(tmp_path, revision="a" * 40)
    assert [item["path"] for item in manifest["artifacts"]] == ["a.txt", "z.txt"]
    assert manifest["status"] == "unsigned-candidate"
    assert validate_release_signing_manifest(manifest) == ()


def test_release_signing_manifest_rejects_unsafe_or_unverified_artifacts() -> None:
    manifest = {
        "manifest_id": "urn:test",
        "revision": "a" * 40,
        "status": "unsigned-candidate",
        "artifacts": [
            {"path": "../secret", "sha256": "A" * 64, "size": -1},
            {"path": "release.tar.gz", "sha256": "b" * 64, "size": 1},
            {"path": "release.tar.gz", "sha256": "c" * 64, "size": 1},
        ],
        "signing_policy": {"required": True},
        "verification": {"attestation_required": False},
    }
    errors = validate_release_signing_manifest(manifest)
    assert any("traversal-free" in error for error in errors)
    assert any("lowercase SHA-256" in error for error in errors)
    assert any("unique" in error for error in errors)
    assert any("require an attestation" in error for error in errors)
