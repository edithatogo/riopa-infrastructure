#!/usr/bin/env python3
"""Build a deterministic, candidate-only operations report bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from riopa_provenance.hashing import sha256_json  # noqa: E402

COMPONENTS = ("slo", "incident", "capacity", "preservation")


class OperationsReportError(ValueError):
    """Raised when a report bundle input is malformed."""


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
