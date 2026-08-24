"""Small, deterministic Python SDK for the bounded conformance contract.

The SDK deliberately exposes validation results rather than a release
certificate.  It is suitable for producer-side checks and local fixtures;
independent implementations, external exercises and signed publication
remain separate evidence gates.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .canonical import validate_crosswalk_contract
from .hashing import sha256_json


@dataclass(frozen=True)
class ValidationReport:
    """Content-addressed result of one bounded validation operation."""

    valid: bool
    errors: tuple[str, ...]
    instance_sha256: str
    validator: str = "riopa-python-reference-1.0"


def canonical_instance_hash(instance: Any) -> str:
    """Return the stable hash used by the language-neutral corpus."""

    return sha256_json(instance)


def validate_json_instance(
    instance: Any, schema: Mapping[str, Any] | str | Path
) -> ValidationReport:
    """Validate one JSON instance against a Draft 2020-12 schema.

    ``schema`` may be an in-memory mapping or a repository-relative file path.
    Errors are sorted by JSON path so reports are deterministic across runs.
    """

    schema_data: Mapping[str, Any]
    if isinstance(schema, (str, Path)):
        schema_data = json.loads(Path(schema).read_text(encoding="utf-8"))
    else:
        schema_data = schema
    validator = Draft202012Validator(schema_data, format_checker=FormatChecker())
    errors = tuple(
        f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in sorted(
            validator.iter_errors(instance), key=lambda item: list(item.absolute_path)
        )
    )
    return ValidationReport(
        valid=not errors,
        errors=errors,
        instance_sha256=canonical_instance_hash(instance),
    )


def validate_crosswalk(instance: Mapping[str, Any]) -> ValidationReport:
    """Validate a canonical crosswalk using the bounded semantic contract."""

    errors = validate_crosswalk_contract(instance)
    return ValidationReport(
        valid=not errors,
        errors=errors,
        instance_sha256=canonical_instance_hash(instance),
    )
