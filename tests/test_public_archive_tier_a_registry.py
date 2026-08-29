from pathlib import Path

import yaml

from riopa_provenance.registry import validate_registry

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config/source-registry/public-archive-tier-a-20260829.yaml"


def test_public_archive_registry_is_valid_and_exactly_bounded() -> None:
    result = validate_registry(REGISTRY, ROOT / "schemas/source-registry.schema.json")
    assert result.valid, result.errors

    registry = yaml.safe_load(REGISTRY.read_text())
    sources = registry["sources"]
    assert len(sources) == 3
    assert {source["rights"]["spdx_or_uri"] for source in sources} == {
        "CC-BY-3.0-NZ",
        "CC-BY-4.0",
    }
    assert all(source["status"] == "active-public-archive" for source in sources)
    assert all(
        source["rights"]["redistribution_status"] == "attribution-required" for source in sources
    )


def test_each_public_archive_source_binds_payload_and_licence_receipt() -> None:
    registry = yaml.safe_load(REGISTRY.read_text())

    for source in registry["sources"]:
        endpoints = source["endpoints"]
        payloads = [
            endpoint for endpoint in endpoints if endpoint["mechanism"].startswith("arcgis")
        ]
        receipts = [endpoint for endpoint in endpoints if endpoint["mechanism"] == "web-resource"]
        assert len(payloads) == 1
        assert len(receipts) == 1
        assert payloads[0]["enabled"] is True
        assert receipts[0]["enabled"] is True
        assert payloads[0]["layer_ids"] in ([0], [1], [152])
