#!/usr/bin/env python3
"""Validate the repository-owned v0.4.0 preservation receipt chain.

This checks local successor receipts and their content-addressed predecessors;
it does not contact providers or infer restore, authority, or stable-release
qualification.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_EXPECTED = {
    "huggingface": "published-and-anonymously-byte-reverified",
    "zenodo": "published-doi-and-anonymously-byte-reverified",
}
_EXPECTED_PATHS = {
    "huggingface": "docs/v0.4.0-release-mirror-20260829.json",
    "zenodo": "docs/v0.4.0-zenodo-preservation-20260829.json",
}
_STABLE_BOUNDARY = "The v0.4.0 receipts do not preserve an eventual stable-v1 candidate."


def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_reconciliation(record: object, *, root: Path) -> tuple[str, ...]:
    if not isinstance(record, dict):
        return ("preservation record must be a JSON object",)
    errors: list[str] = []
    if record.get("release") != "0.4.0" or record.get("channel") != "public-technical-preview":
        errors.append("record must describe the v0.4.0 public technical preview")
    receipts = record.get("verified_receipts")
    if not isinstance(receipts, list) or not receipts:
        return ("verified_receipts must be a non-empty list",)
    providers: dict[str, int] = {}
    for index, item in enumerate(receipts):
        prefix = f"verified_receipts[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        provider = item.get("provider")
        providers[str(provider)] = providers.get(str(provider), 0) + 1
        if provider not in _EXPECTED:
            errors.append(f"{prefix}.provider is not an expected public provider")
        elif item.get("result") != _EXPECTED[provider]:
            errors.append(f"{prefix}.result does not record byte re-verification")
        path_value = item.get("path")
        digest = item.get("sha256")
        if not isinstance(path_value, str) or Path(path_value).is_absolute():
            errors.append(f"{prefix}.path must be repository-relative")
            continue
        path = (root / path_value).resolve()
        try:
            path.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{prefix}.path escapes repository root")
            continue
        if not path.is_file():
            errors.append(f"{prefix}.path does not exist: {path_value}")
        elif not isinstance(digest, str) or not _SHA256.fullmatch(digest):
            errors.append(f"{prefix}.sha256 is not a lowercase SHA-256 digest")
        elif _digest(path) != digest:
            errors.append(f"{prefix}.sha256 does not match {path_value}")
        if provider in _EXPECTED_PATHS and path_value != _EXPECTED_PATHS[provider]:
            errors.append(f"{prefix}.path is not the canonical {provider} receipt")
        if path.is_file() and isinstance(provider, str):
            try:
                referenced = json.loads(path.read_text(encoding="utf-8"))
            except OSError, json.JSONDecodeError:
                errors.append(f"{prefix}.path is not a valid JSON receipt")
            else:
                if not isinstance(referenced, dict):
                    errors.append(f"{prefix}.path must contain a JSON object")
                elif provider == "huggingface":
                    mirror = referenced.get("mirror")
                    qualification = referenced.get("qualification")
                    if (
                        referenced.get("record_type") != "successor_release_mirror_receipt"
                        or referenced.get("release") != "0.4.0"
                        or referenced.get("channel") != "public-technical-preview"
                        or not isinstance(mirror, dict)
                        or mirror.get("provider") != "huggingface"
                        or not isinstance(qualification, dict)
                        or qualification.get("status") != "published_and_publicly_reverified"
                    ):
                        errors.append(f"{prefix} does not corroborate the Hugging Face receipt")
                elif provider == "zenodo":
                    deposit = referenced.get("deposit")
                    verification = referenced.get("public_verification")
                    if (
                        referenced.get("record_type") != "successor_zenodo_preservation_receipt"
                        or referenced.get("release") != "0.4.0"
                        or referenced.get("channel") != "public-technical-preview"
                        or not isinstance(deposit, dict)
                        or deposit.get("provider") != "zenodo"
                        or deposit.get("state") != "done"
                        or deposit.get("submitted") is not True
                        or not isinstance(verification, dict)
                        or verification.get("sha256sums_passed") is not True
                    ):
                        errors.append(f"{prefix} does not corroborate the Zenodo receipt")
    if set(providers) != set(_EXPECTED):
        errors.append("reconciliation must contain exactly one Hugging Face and one Zenodo receipt")
    elif len(receipts) != len(_EXPECTED) or any(count != 1 for count in providers.values()):
        errors.append("reconciliation must contain exactly one receipt per provider")
    nonclaims = record.get("nonclaims")
    if not isinstance(nonclaims, list) or _STABLE_BOUNDARY not in nonclaims:
        errors.append("record must retain the exact stable-v1 non-claim")
    return tuple(dict.fromkeys(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--record",
        type=Path,
        default=Path("docs/v0.4.0-preservation-wp006-reconciliation-20260829.json"),
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    record_path = args.record if args.record.is_absolute() else root / args.record
    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(f"unable to read preservation record: {exc}")
    if not isinstance(record, dict):
        errors = ("preservation record must be a JSON object",)
    else:
        errors = validate_reconciliation(record, root=root)
    result = {"schema": "riopa.v040-preservation-receipts-validation.v1", "errors": list(errors)}
    if not errors:
        result.update(
            {"status": "successor-receipts-and-digests-validated", "promotion_allowed": False}
        )
    if args.output:
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    for error in errors:
        print(error)
    if not errors:
        print("v0.4.0 preservation receipts valid")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
