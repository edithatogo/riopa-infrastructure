from pathlib import Path

import pytest

from riopa_provenance.release_signing import (
    ReleaseSigningError,
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


def test_build_release_signing_manifest_rejects_empty_inputs(tmp_path: Path) -> None:
    with pytest.raises(ReleaseSigningError, match="source revision"):
        build_release_signing_manifest(tmp_path, revision=" ")
    with pytest.raises(ReleaseSigningError, match="at least one"):
        build_release_signing_manifest(tmp_path, revision="a" * 40)
    with pytest.raises(ReleaseSigningError, match="40-character"):
        build_release_signing_manifest(tmp_path, revision="not-a-revision")
    with pytest.raises(ReleaseSigningError, match="40-character"):
        build_release_signing_manifest(tmp_path, revision=None)  # type: ignore[arg-type]


def test_build_release_signing_manifest_honours_exclusions(tmp_path: Path) -> None:
    (tmp_path / "release.tar.gz").write_bytes(b"payload")
    (tmp_path / "signature.sig").write_bytes(b"signature")
    manifest = build_release_signing_manifest(
        tmp_path, revision="a" * 40, exclude=("signature.sig",)
    )
    assert [item["path"] for item in manifest["artifacts"]] == ["release.tar.gz"]


def test_release_signing_manifest_rejects_missing_contract_sections() -> None:
    errors = validate_release_signing_manifest(
        {
            "manifest_id": "urn:test",
            "revision": "a" * 40,
            "status": "signed",
            "artifacts": [],
        }
    )
    assert "artifacts must be a non-empty array" in errors
    assert "signing policy must require a signature" in errors
    assert "verification must require an attestation" in errors


def test_release_signing_manifest_rejects_non_object_and_invalid_status() -> None:
    assert validate_release_signing_manifest(None) == ("manifest must be an object",)
    errors = validate_release_signing_manifest(
        {
            "manifest_id": "urn:test",
            "revision": "a" * 40,
            "status": "pending",
            "artifacts": ["release.tar.gz"],
            "signing_policy": {"required": True},
            "verification": {"attestation_required": True},
        }
    )
    assert "status must be unsigned-candidate or signed" in errors
    assert "each artifact must be an object" in errors


def test_signed_manifest_requires_verified_attestation_binding() -> None:
    manifest = {
        "manifest_id": "urn:test",
        "revision": "a" * 40,
        "status": "signed",
        "artifacts": [{"path": "release.tar.gz", "sha256": "b" * 64, "size": 1}],
        "signing_policy": {"required": True},
        "verification": {"attestation_required": True},
    }
    errors = validate_release_signing_manifest(manifest)
    assert "signed manifests require a verified provider and attestation_id" in errors
    manifest["signature"] = {
        "status": "verified",
        "provider": "github",
        "attestation_id": "attestation-1",
        "revision": manifest["revision"],
        "artifact_digests": [{"path": "release.tar.gz", "sha256": "b" * 64}],
    }
    assert validate_release_signing_manifest(manifest) == ()


def test_signed_manifest_rejects_attestation_drift() -> None:
    manifest = {
        "manifest_id": "urn:test",
        "revision": "a" * 40,
        "status": "signed",
        "artifacts": [{"path": "release.tar.gz", "sha256": "b" * 64, "size": 1}],
        "signing_policy": {"required": True},
        "verification": {"attestation_required": True},
        "signature": {
            "status": "verified",
            "provider": "github",
            "attestation_id": "attestation-1",
            "revision": "c" * 40,
            "artifact_digests": [{"path": "release.tar.gz", "sha256": "c" * 64}],
        },
    }
    errors = validate_release_signing_manifest(manifest)
    assert "signed attestation revision must match the manifest revision" in errors
    assert "signed attestation artifact digests must match the manifest" in errors


def test_signed_manifest_with_malformed_artifacts_returns_errors() -> None:
    manifest = {
        "manifest_id": "urn:test",
        "revision": "a" * 40,
        "status": "signed",
        "artifacts": None,
        "signing_policy": {"required": True},
        "verification": {"attestation_required": True},
        "signature": {
            "status": "verified",
            "provider": "github",
            "attestation_id": "attestation-1",
            "revision": "a" * 40,
            "artifact_digests": [],
        },
    }
    errors = validate_release_signing_manifest(manifest)
    assert "artifacts must be a non-empty array" in errors
