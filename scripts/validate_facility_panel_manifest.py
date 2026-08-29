#!/usr/bin/env python3
"""Fail-closed validation for a content-bound facility agent-panel manifest.

The validator checks the evidence shape only.  It never treats a panel result
as factual facility adjudication, external participation, preservation
acceptance or release authority.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

SHA256 = re.compile(r"^[0-9a-f]{64}$")
REVISION = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_PANEL_FIELDS = {
    "role",
    "session_id",
    "model_identity",
    "environment",
    "commands",
    "results",
    "findings",
    "dissent",
    "remediation",
    "rerun_outcome",
}
EXPECTED_ROLES = {"methods", "provenance", "governance", "reproducibility"}


def _required_text(value: Any, field: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} must be a non-empty string")


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{path}: cannot read JSON ({exc})"]
    if not isinstance(manifest, dict):
        return ["manifest must be an object"]
    if manifest.get("schema") != "riopa.facility-panel-manifest.v1":
        errors.append("unexpected manifest schema")
    for field in ("manifest_id", "packet_id", "source_revision", "packet_sha256", "evaluated_at"):
        _required_text(manifest.get(field), field, errors)
    if not REVISION.fullmatch(str(manifest.get("source_revision", ""))):
        errors.append("source_revision must be a 40-character lowercase Git SHA-1")
    if not SHA256.fullmatch(str(manifest.get("packet_sha256", ""))):
        errors.append("packet_sha256 must be a 64-character lowercase SHA-256")
    panel = manifest.get("panel")
    if not isinstance(panel, list) or not panel:
        errors.append("panel must be a non-empty list")
        panel = []
    roles: list[str] = []
    session_ids: list[str] = []
    model_identities: list[str] = []
    for index, member in enumerate(panel):
        prefix = f"panel[{index}]"
        if not isinstance(member, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = REQUIRED_PANEL_FIELDS - member.keys()
        errors.extend(f"{prefix}: missing {field}" for field in sorted(missing))
        _required_text(member.get("role"), f"{prefix}.role", errors)
        _required_text(member.get("session_id"), f"{prefix}.session_id", errors)
        _required_text(member.get("model_identity"), f"{prefix}.model_identity", errors)
        for field in ("commands", "findings", "dissent", "remediation"):
            if not isinstance(member.get(field), list):
                errors.append(f"{prefix}.{field} must be a list")
        if not isinstance(member.get("results"), dict) or not member["results"]:
            errors.append(f"{prefix}.results must be a non-empty object")
        if not isinstance(member.get("rerun_outcome"), str) or not member["rerun_outcome"].strip():
            errors.append(f"{prefix}.rerun_outcome must be a non-empty string")
        environment = member.get("environment")
        if not isinstance(environment, dict) or not environment:
            errors.append(f"{prefix}.environment must be a non-empty object")
        roles.append(str(member.get("role", "")))
        session_ids.append(str(member.get("session_id", "")))
        model_identities.append(str(member.get("model_identity", "")))
        digests = member.get("artifact_digests")
        if not isinstance(digests, list) or not digests:
            errors.append(f"{prefix}.artifact_digests must be a non-empty list")
        else:
            for digest_index, digest in enumerate(digests):
                if not isinstance(digest, dict) or not isinstance(digest.get("path"), str):
                    errors.append(
                        f"{prefix}.artifact_digests[{digest_index}] must include path and sha256"
                    )
                elif not SHA256.fullmatch(str(digest.get("sha256", ""))):
                    errors.append(f"{prefix}.artifact_digests[{digest_index}].sha256 is invalid")
    if len(roles) != len(set(roles)):
        errors.append("panel roles must be unique")
    if set(roles) != EXPECTED_ROLES:
        errors.append(
            "panel roles must be exactly methods, provenance, governance and reproducibility"
        )
    if len(session_ids) != len(set(session_ids)):
        errors.append("panel session_id values must be unique")
    if len(model_identities) != len(set(model_identities)):
        errors.append("panel model_identity values must be unique")
    if not isinstance(manifest.get("synthesis"), dict) or not manifest["synthesis"]:
        errors.append("synthesis must be a non-empty object")
    if manifest.get("promotion_allowed") is not False:
        errors.append("promotion_allowed must be false")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    errors = validate(args.manifest)
    if errors:
        print("\n".join(errors))
        return 1
    print("PASS facility panel manifest shape")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
