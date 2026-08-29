#!/usr/bin/env python3
"""Build a deterministic, candidate-only operations report bundle."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from riopa_provenance.hashing import sha256_json  # noqa: E402

COMPONENTS = ("slo", "incident", "capacity", "preservation")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class OperationsReportError(ValueError):
    """Raised when a report bundle input is malformed."""


def validate_bundle(bundle: object) -> tuple[str, ...]:
    """Validate a candidate bundle's structure and self-digest."""

    if not isinstance(bundle, dict):
        return ("report bundle must be an object",)
    errors: list[str] = []
    if bundle.get("schema_version") != "1.0.0":
        errors.append("schema_version must be 1.0.0")
    if bundle.get("record_type") != "operations_report_bundle":
        errors.append("record_type must be operations_report_bundle")
    if bundle.get("publication_status") != "candidate-not-published":
        errors.append("publication_status must remain candidate-not-published")
    if bundle.get("promotion_allowed") is not False:
        errors.append("promotion_allowed must be false")
    supplied = bundle.get("bundle_sha256")
    unsigned = {key: value for key, value in bundle.items() if key != "bundle_sha256"}
    if not isinstance(supplied, str) or not _SHA256.fullmatch(supplied):
        errors.append("bundle_sha256 must be a lowercase SHA-256 digest")
    elif supplied != sha256_json(unsigned):
        errors.append("bundle_sha256 does not match bundle content")
    components = bundle.get("components")
    if not isinstance(components, dict) or set(components) != set(COMPONENTS):
        errors.append("components must contain exactly the four report categories")
    else:
        for name in COMPONENTS:
            component = components[name]
            if not isinstance(component, dict):
                errors.append(f"components.{name} must be an object")
                continue
            status = component.get("status")
            digest = component.get("content_sha256")
            if status == "pending" and digest is not None:
                errors.append(f"components.{name} pending content digest must be null")
            elif status == "candidate-input" and (
                not isinstance(digest, str) or not _SHA256.fullmatch(digest)
            ):
                errors.append(f"components.{name} candidate input requires a SHA-256 digest")
            elif status not in {"pending", "candidate-input"}:
                errors.append(f"components.{name} has unsupported status")
    nonclaims = bundle.get("nonclaims")
    if not isinstance(nonclaims, list) or not any(
        isinstance(item, str) and "not independently qualified" in item for item in nonclaims
    ):
        errors.append("nonclaims must retain the unqualified-input boundary")
    return tuple(dict.fromkeys(errors))


def build_bundle(payload: dict[str, Any], *, report_id: str, generated_at: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise OperationsReportError("report inputs must be an object")
    if not report_id.strip() or not generated_at.strip():
        raise OperationsReportError("report_id and generated_at must be non-empty")
    components: dict[str, dict[str, Any]] = {}
    for name in COMPONENTS:
        value = payload.get(name)
        if value is None:
            components[name] = {"status": "pending", "content_sha256": None}
            continue
        if not isinstance(value, dict):
            raise OperationsReportError(f"{name} report must be an object or null")
        components[name] = {
            "status": "candidate-input",
            "content_sha256": sha256_json(value),
        }
    bundle: dict[str, Any] = {
        "schema_version": "1.0.0",
        "record_type": "operations_report_bundle",
        "report_id": report_id.strip(),
        "generated_at": generated_at.strip(),
        "components": components,
        "publication_status": "candidate-not-published",
        "promotion_allowed": False,
        "nonclaims": [
            "Missing components are pending, not evidence of healthy operations.",
            "Candidate inputs are content-addressed but not independently qualified measurements.",
            "This bundle does not establish hosted SLO history, preservation acceptance "
            "or release authority.",
        ],
    }
    bundle["bundle_sha256"] = sha256_json(bundle)
    return bundle


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON object containing report components")
    parser.add_argument("--report-id", required=True)
    parser.add_argument("--generated-at", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    rendered = (
        json.dumps(
            build_bundle(payload, report_id=args.report_id, generated_at=args.generated_at),
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
