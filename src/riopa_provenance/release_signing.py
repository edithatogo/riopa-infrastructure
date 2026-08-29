"""Content-bound release signing manifest planning and verification.

This module creates the deterministic input to a protected signing job.  It
does not access keys, create signatures, or publish artifacts.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any


class ReleaseSigningError(ValueError):
    """Raised when a signing manifest is incomplete or unsafe."""


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_REVISION = re.compile(r"^[0-9a-f]{40}$")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_release_signing_manifest(
    root: Path, *, revision: str, exclude: Iterable[str] = ()
) -> dict[str, Any]:
    """Build a sorted, unsigned candidate manifest for regular files in ``root``."""

    if not isinstance(revision, str) or not _REVISION.fullmatch(revision.strip()):
        raise ReleaseSigningError("source revision must be a 40-character lowercase Git SHA-1")
    revision = revision.strip()
    excluded = set(exclude)
    artifacts: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name in excluded:
            continue
        relative = path.relative_to(root).as_posix()
        artifacts.append({"path": relative, "sha256": _sha256(path), "size": path.stat().st_size})
    if not artifacts:
        raise ReleaseSigningError("at least one release artifact is required")
    return {
        "schema_version": "1.0.0",
        "manifest_id": f"urn:riopa:release-signing:{revision}",
        "revision": revision,
        "status": "unsigned-candidate",
        "artifacts": artifacts,
        "signing_policy": {
            "required": True,
            "scheme": "github-artifact-attestation",
            "protected_environment": "release",
            "key_material": "external-keyless-signer",
        },
        "verification": {
            "checksum_algorithm": "sha256",
            "attestation_required": True,
            "tag_binding_required": True,
        },
        "non_claims": [
            "This manifest is not a signature or signed release receipt.",
            "The protected release job must sign and independently verify every listed artifact.",
        ],
    }


def validate_release_signing_manifest(manifest: Mapping[str, Any] | None) -> tuple[str, ...]:
    """Validate the unsigned candidate contract without trusting signatures."""

    if not isinstance(manifest, Mapping):
        return ("manifest must be an object",)
    errors: list[str] = []
    for field in ("manifest_id", "revision", "status"):
        if not isinstance(manifest.get(field), str) or not str(manifest[field]).strip():
            errors.append(f"{field} is required")
    if not _REVISION.fullmatch(str(manifest.get("revision", ""))):
        errors.append("revision must be a 40-character lowercase Git SHA-1")
    if manifest.get("status") not in {"unsigned-candidate", "signed"}:
        errors.append("status must be unsigned-candidate or signed")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        errors.append("artifacts must be a non-empty array")
    else:
        paths: list[str] = []
        for artifact in artifacts:
            if not isinstance(artifact, Mapping):
                errors.append("each artifact must be an object")
                continue
            path = artifact.get("path")
            digest = artifact.get("sha256")
            path_text = path if isinstance(path, str) else ""
            unsafe_path = (
                not isinstance(path, str)
                or not path
                or path.startswith("/")
                or ".." in Path(path).parts
            )
            if unsafe_path:
                errors.append("artifact paths must be relative and traversal-free")
            elif path_text in paths:
                errors.append("artifact paths must be unique")
            else:
                paths.append(path_text)
            if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
                errors.append("each artifact requires a lowercase SHA-256 digest")
            if not isinstance(artifact.get("size"), int) or artifact["size"] < 0:
                errors.append("each artifact requires a non-negative size")
    policy = manifest.get("signing_policy")
    if not isinstance(policy, Mapping) or policy.get("required") is not True:
        errors.append("signing policy must require a signature")
    verification = manifest.get("verification")
    if (
        not isinstance(verification, Mapping)
        or verification.get("attestation_required") is not True
    ):
        errors.append("verification must require an attestation")
    if manifest.get("status") == "signed":
        signature = manifest.get("signature")
        if (
            not isinstance(signature, Mapping)
            or signature.get("status") != "verified"
            or not isinstance(signature.get("provider"), str)
            or not str(signature["provider"]).strip()
            or not isinstance(signature.get("attestation_id"), str)
            or not str(signature["attestation_id"]).strip()
        ):
            errors.append("signed manifests require a verified provider and attestation_id")
        else:
            if signature.get("revision") != manifest.get("revision"):
                errors.append("signed attestation revision must match the manifest revision")
            declared = signature.get("artifact_digests")
            if isinstance(artifacts, list) and all(isinstance(item, Mapping) for item in artifacts):
                expected = [
                    {"path": item.get("path"), "sha256": item.get("sha256")} for item in artifacts
                ]
                if declared != expected:
                    errors.append("signed attestation artifact digests must match the manifest")
    return tuple(dict.fromkeys(errors))
