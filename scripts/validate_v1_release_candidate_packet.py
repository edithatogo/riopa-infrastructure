#!/usr/bin/env python3
"""Validate the fail-closed structure of the v1 release-candidate packet."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

_REVISION = re.compile(r"^[0-9a-f]{40}$")


def validate_packet(packet: dict[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if packet.get("schema") != "riopa.v1-release-candidate-packet.v1":
        errors.append("unexpected packet schema")
    if packet.get("status") != "preparation-only":
        errors.append("packet must remain preparation-only")
    for field in ("release_ready", "promotion_allowed"):
        if packet.get(field) is not False:
            errors.append(f"{field} must be false")
    candidate = packet.get("candidate")
    if not isinstance(candidate, dict):
        errors.append("candidate must be an object")
    else:
        if not isinstance(candidate.get("revision"), str) or not _REVISION.fullmatch(
            candidate["revision"]
        ):
            errors.append("candidate revision must be a 40-character lowercase Git revision")
        if candidate.get("revision_binding") != "exact-commit-at-packet-construction":
            errors.append("candidate revision binding must be exact")
        if candidate.get("signing_manifest_status") != "unsigned-candidate":
            errors.append("candidate signing status must remain unsigned-candidate")
    required = packet.get("required_external_or_elapsed_evidence")
    if not isinstance(required, list) or not required:
        errors.append("required_external_or_elapsed_evidence must be non-empty")
    else:
        text = " ".join(str(item) for item in required)
        for phrase in ("30-day exact-RC soak", "preservation", "accountable release-authority"):
            if phrase not in text:
                errors.append(f"required evidence omits {phrase}")
    nonclaims = packet.get("non_claims")
    if (
        not isinstance(nonclaims, list)
        or not nonclaims
        or not any("not a signed release candidate" in str(item) for item in nonclaims)
    ):
        errors.append("non_claims must retain the unsigned-candidate boundary")
    return tuple(errors)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    args = parser.parse_args()
    try:
        packet = json.loads(args.packet.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(f"unable to read packet: {exc}")
    if not isinstance(packet, dict):
        print("packet must be a JSON object")
        return 1
    errors = validate_packet(packet)
    for error in errors:
        print(error)
    if not errors:
        print("v1 release-candidate packet valid and promotion-disabled")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
