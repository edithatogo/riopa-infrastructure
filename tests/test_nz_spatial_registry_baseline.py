import json
from pathlib import Path

from riopa_provenance.registry import validate_registry

ROOT = Path(__file__).resolve().parents[1]


def test_bounded_registry_baseline_preserves_disabled_source_families() -> None:
    record = json.loads((ROOT / "docs/nz-spatial-registry-baseline-20260822.json").read_text())
    assert len(record["authorities"]) == 5
    disabled = {
        item["source_family"]
        for item in record["authorities"]
        if item["status"] == "disabled-pending-archive"
    }
    assert disabled == {"network-and-gtfs", "planning-and-eplan", "legal-status"}
    assert any("not a complete national" in claim for claim in record["non_claims"])


def test_linz_registry_configuration_remains_schema_valid() -> None:
    result = validate_registry(
        ROOT / "config/source-registry/nz-spatial-pilot.yaml",
        ROOT / "schemas/source-registry.schema.json",
    )
    assert result.valid, result.errors
