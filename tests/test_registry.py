from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from riopa_provenance.registry import (
    import_district_plans_csv,
    load_registry,
    validate_registry,
    write_registry_json,
)


def test_pilot_registry_validates() -> None:
    root = Path(__file__).resolve().parents[1]
    result = validate_registry(
        root / "config/source-registry/nz-spatial-pilot.yaml",
        root / "schemas/source-registry.schema.json",
    )
    assert result.valid, result.errors


def test_registry_load_write_and_invalid_root(tmp_path: Path) -> None:
    source = tmp_path / "source.yaml"
    source.write_text("enabled: true\nname: example\n", encoding="utf-8")
    assert load_registry(source) == {"enabled": True, "name": "example"}

    output = write_registry_json({"z": 1, "a": 2}, tmp_path / "out.json")
    assert output.read_text(encoding="utf-8") == '{\n  "a": 2,\n  "z": 1\n}\n'

    bad = tmp_path / "bad.yaml"
    bad.write_text("- one\n- two\n", encoding="utf-8")
    with pytest.raises(ValueError, match="root must be an object"):
        load_registry(bad)


def test_district_plan_import_preserves_rows_and_classifies_endpoints(tmp_path: Path) -> None:
    source = tmp_path / "plans.csv"
    with source.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["Council", "Plan Name", "Plan URL", "GIS URL"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "Council": "Example District Council",
                "Plan Name": "Example District Plan",
                "Plan URL": "https://example.govt.nz/plan.pdf",
                "GIS URL": "https://maps.example.govt.nz/arcgis/rest/services/Plan/FeatureServer/0",
            }
        )

    registry = import_district_plans_csv(
        source,
        generated_at="2026-07-20T00:00:00Z",
        catalogue_url="https://catalogue.example/plans.csv",
    )

    item = registry["sources"][0]
    assert item["source_id"] == "urn:riopa:source:nz-council:example-district-council"
    assert [entry["mechanism"] for entry in item["endpoints"]] == [
        "web-resource",
        "arcgis-feature-service",
    ]
    assert item["discovery_metadata"]["source_row"]["Council"] == "Example District Council"


def test_district_plan_import_rejects_missing_authority_and_bad_url(tmp_path: Path) -> None:
    missing = tmp_path / "missing.csv"
    missing.write_text("Council,Plan URL\n,https://example.govt.nz/plan\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no authority"):
        import_district_plans_csv(
            missing,
            generated_at="2026-07-20T00:00:00Z",
            catalogue_url="https://catalogue.example/plans.csv",
        )

    bad = tmp_path / "bad.csv"
    bad.write_text("Council,Plan URL\nExample,not-a-url\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid plan URL"):
        import_district_plans_csv(
            bad,
            generated_at="2026-07-20T00:00:00Z",
            catalogue_url="https://catalogue.example/plans.csv",
        )


def test_validation_returns_schema_errors(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    invalid = tmp_path / "invalid.json"
    invalid.write_text(json.dumps({"schema_version": "1.0.0"}), encoding="utf-8")
    result = validate_registry(invalid, root / "schemas/source-registry.schema.json")
    assert not result.valid
    assert result.errors
