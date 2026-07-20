"""Source-registry loading, validation, and conservative CSV import helpers."""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator, FormatChecker

from .yaml_tools import load_yaml


@dataclass(frozen=True)
class RegistryValidationResult:
    """Result returned by :func:`validate_registry`."""

    path: Path
    valid: bool
    errors: tuple[str, ...]


def _json_compatible(value: Any) -> Any:
    """Round-trip a value through JSON to reject non-JSON YAML types."""

    return json.loads(json.dumps(value, ensure_ascii=False, allow_nan=False))


def load_registry(path: str | Path) -> dict[str, Any]:
    """Load a JSON or YAML source registry and require a mapping root."""

    source = Path(path)
    if source.suffix.casefold() == ".json":
        value = json.loads(source.read_text(encoding="utf-8"))
    else:
        value = load_yaml(source)
    value = _json_compatible(value)
    if not isinstance(value, dict):
        raise ValueError(f"source registry root must be an object: {source}")
    return value


def validate_registry(
    registry_path: str | Path,
    schema_path: str | Path,
) -> RegistryValidationResult:
    """Validate a registry against the normative JSON Schema."""

    registry_file = Path(registry_path)
    errors: list[str] = []
    try:
        registry = load_registry(registry_file)
        schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        for error in sorted(validator.iter_errors(registry), key=lambda item: list(item.path)):
            location = "/".join(str(part) for part in error.absolute_path) or "$"
            errors.append(f"{location}: {error.message}")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(str(exc))
    return RegistryValidationResult(registry_file, not errors, tuple(errors))


def write_registry_json(registry: dict[str, Any], output_path: str | Path) -> Path:
    """Write a registry deterministically as UTF-8 JSON."""

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destination


def _first(row: dict[str, str], *names: str) -> str | None:
    normalised = {key.strip().casefold().replace(" ", "_"): value for key, value in row.items()}
    for name in names:
        value = normalised.get(name)
        if value is not None and value.strip():
            return value.strip()
    return None


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return slug or "unknown"


def _mechanism(url: str) -> str:
    lowered = url.casefold()
    if "/featureserver" in lowered:
        return "arcgis-feature-service"
    if "/mapserver" in lowered:
        return "arcgis-map-service"
    if "service=wfs" in lowered or lowered.rstrip("/").endswith("/wfs"):
        return "wfs"
    if "service=wms" in lowered or lowered.rstrip("/").endswith("/wms"):
        return "wms"
    return "web-resource"


def import_district_plans_csv(
    csv_path: str | Path,
    *,
    generated_at: str,
    catalogue_url: str,
) -> dict[str, Any]:
    """Import a heterogeneous district-plan catalogue conservatively.

    The importer deliberately preserves the source row in ``discovery_metadata``
    and creates only endpoint assertions supported by an explicit URL.  It does
    not infer that a web viewer is a redistributable GIS service.
    """

    sources: list[dict[str, Any]] = []
    seen: set[str] = set()
    with Path(csv_path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("district-plan CSV has no header")
        for row_number, row in enumerate(reader, start=2):
            cleaned = {str(key): str(value or "").strip() for key, value in row.items()}
            authority = _first(
                cleaned,
                "authority",
                "council",
                "local_authority",
                "territorial_authority",
                "organisation",
                "organization",
            )
            name = _first(cleaned, "plan_name", "district_plan", "name", "plan")
            plan_url = _first(cleaned, "plan_url", "url", "website", "document_url")
            gis_url = _first(cleaned, "gis_url", "map_url", "arcgis_url", "service_url")
            if not authority:
                raise ValueError(f"district-plan CSV row {row_number} has no authority")
            source_id = f"urn:riopa:source:nz-council:{_slug(authority)}"
            if source_id in seen:
                source_id = f"{source_id}:row-{row_number}"
            seen.add(source_id)
            endpoints: list[dict[str, Any]] = []
            for index, (label, url) in enumerate((("plan", plan_url), ("gis", gis_url)), start=1):
                if not url:
                    continue
                parsed = urlsplit(url)
                if parsed.scheme not in {"http", "https"} or not parsed.hostname:
                    raise ValueError(f"district-plan CSV row {row_number} has invalid {label} URL")
                endpoints.append(
                    {
                        "endpoint_id": f"{source_id}:endpoint:{label}-{index}",
                        "mechanism": _mechanism(url),
                        "url": url,
                        "enabled": True,
                        "authentication": {"type": "none"},
                        "capture_strategy": (
                            "metadata-only"
                            if label == "gis" and _mechanism(url) == "web-resource"
                            else "download-whole"
                        ),
                        "capabilities": [
                            "planning-document" if label == "plan" else "spatial-discovery"
                        ],
                    }
                )
            sources.append(
                {
                    "source_id": source_id,
                    "name": name or f"{authority} district plan",
                    "publisher": {"name": authority},
                    "jurisdiction": "New Zealand",
                    "source_family": "nz-council-district-plan",
                    "status": "candidate",
                    "rights": {
                        "access_status": "public" if endpoints else "unknown",
                        "redistribution_status": "review-required",
                    },
                    "endpoints": endpoints,
                    "discovery_metadata": {
                        "catalogue_url": catalogue_url,
                        "csv_row": row_number,
                        "source_row": cleaned,
                    },
                }
            )
    return {
        "schema_version": "1.0.0",
        "record_type": "source_registry",
        "registry_id": "urn:riopa:registry:nz-district-plans:imported",
        "generated_at": generated_at,
        "catalogue_url": catalogue_url,
        "sources": sources,
    }
