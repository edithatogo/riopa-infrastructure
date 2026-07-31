"""Validation and comparison helpers for brownfield repository adapters."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator, FormatChecker

from .hashing import sha256_json


class AdapterMappingError(ValueError):
    """Raised when an adapter mapping is invalid or semantically incomplete."""


def load_adapter_mapping(path: str | Path, *, schema_path: str | Path) -> dict[str, Any]:
    """Load one adapter mapping and enforce schema plus classification coverage."""

    mapping = cast(dict[str, Any], json.loads(Path(path).read_text(encoding="utf-8")))
    schema = cast(dict[str, Any], json.loads(Path(schema_path).read_text(encoding="utf-8")))
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(mapping),
        key=lambda item: list(item.absolute_path),
    )
    if errors:
        detail = "; ".join(
            f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
            for error in errors
        )
        raise AdapterMappingError(detail)
    required_classes = {"exact", "approximate", "extension-only", "unmapped"}
    observed = {item["classification"] for item in mapping["mappings"]}
    missing = sorted(required_classes - observed)
    if missing:
        raise AdapterMappingError(f"adapter mapping omits classifications: {missing}")
    mapping["mapping_sha256"] = sha256_json(mapping)
    return mapping


def cross_repository_mapping_report(mappings: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Build a deterministic summary without treating approximation as equivalence."""

    ordered = sorted(mappings, key=lambda item: item["repository"])
    repositories = [item["repository"] for item in ordered]
    if len(repositories) != len(set(repositories)):
        raise AdapterMappingError("repository mappings must be unique")
    return {
        "schema_version": "1.0.0",
        "record_type": "cross_repository_adapter_report",
        "repositories": [
            {
                "repository": mapping["repository"],
                "source_revision": mapping["source_revision"],
                "profile_version": mapping["profile_version"],
                "mapping_sha256": mapping["mapping_sha256"],
                "classification_counts": {
                    classification: sum(
                        item["classification"] == classification for item in mapping["mappings"]
                    )
                    for classification in (
                        "exact",
                        "approximate",
                        "extension-only",
                        "unmapped",
                    )
                },
            }
            for mapping in ordered
        ],
    }
