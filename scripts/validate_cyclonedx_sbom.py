#!/usr/bin/env python3
"""Strictly validate the repository's CycloneDX 1.6 JSON SBOM."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cyclonedx.schema import SchemaVersion
from cyclonedx.validation.json import JsonStrictValidator


def validate_sbom(path: Path) -> tuple[str, ...]:
    try:
        text = path.read_text(encoding="utf-8")
        payload = json.loads(text)
    except (OSError, json.JSONDecodeError) as exc:
        return (f"could not read CycloneDX JSON: {exc}",)
    if not isinstance(payload, dict):
        return ("CycloneDX document must be a JSON object",)
    if payload.get("specVersion") != "1.6":
        return ("CycloneDX specVersion must be 1.6",)
    if not isinstance(payload.get("components"), list) or not payload["components"]:
        return ("CycloneDX components must be a non-empty array",)
    result = JsonStrictValidator(SchemaVersion.V1_6).validate_str(text, all_errors=True)
    if result is None:
        return ()
    return tuple(str(error) for error in result)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sbom", type=Path)
    args = parser.parse_args()
    errors = validate_sbom(args.sbom)
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print(f"PASS strict CycloneDX 1.6 schema validation: {args.sbom}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
