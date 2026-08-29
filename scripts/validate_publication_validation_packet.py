#!/usr/bin/env python3
"""Validate the DOI-ready-but-unpublished validation packet boundary."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def validate_packet(packet: object, *, root: Path) -> tuple[str, ...]:
    root = root.resolve()
    if not isinstance(packet, dict):
        return ("publication packet must be an object",)
    errors: list[str] = []
    if packet.get("schema") != "riopa.publication-validation-packet.v1":
        errors.append("unexpected publication packet schema")
    if packet.get("status") != "doi-ready-preparation-only":
        errors.append("packet must remain preparation-only")
    if packet.get("publication_ready") is not False:
        errors.append("publication_ready must be false")
    contracts = packet.get("metadata_contracts")
    if not isinstance(contracts, list) or not contracts:
        errors.append("metadata_contracts must be non-empty")
    else:
        for path_value in contracts:
            if not isinstance(path_value, str) or not path_value.strip():
                errors.append(f"metadata contract is missing: {path_value}")
                continue
            candidate = Path(path_value)
            resolved = (root / candidate).resolve()
            if candidate.is_absolute() or ".." in candidate.parts or root not in resolved.parents:
                errors.append(f"metadata contract path escapes root: {path_value}")
            elif not resolved.is_file():
                errors.append(f"metadata contract is missing: {path_value}")
    pending = packet.get("pending_gates")
    pending_text = (
        " ".join(pending)
        if isinstance(pending, list) and all(isinstance(item, str) for item in pending)
        else ""
    )
    for phrase in (
        "protected artifact attestations",
        "accepted preservation",
        "external operator/user reproduction",
        "elapsed beta/RC qualification",
        "accountable release-authority decision",
    ):
        if phrase not in pending_text:
            errors.append(f"pending_gates omits {phrase}")
    claims = packet.get("non_claims")
    claims_text = (
        " ".join(claims)
        if isinstance(claims, list) and all(isinstance(item, str) for item in claims)
        else ""
    )
    if "not a DOI" not in claims_text or "external acceptance" not in claims_text:
        errors.append("non_claims must retain unpublished/external-acceptance boundaries")
    return tuple(errors)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    try:
        packet = json.loads(args.packet.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(f"unable to read packet: {exc}")
    errors = validate_packet(packet, root=args.root.resolve())
    for error in errors:
        print(error)
    if not errors:
        print("publication validation packet valid and unpublished")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
