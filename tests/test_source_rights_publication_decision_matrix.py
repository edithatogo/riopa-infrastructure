import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_decision_matrix_is_permissive_without_licence_laundering() -> None:
    matrix = json.loads(
        (ROOT / "docs/source-rights-publication-decision-matrix-20260829.json").read_text()
    )

    assert set(matrix["tiers"]) == {"A", "B", "C", "D", "E"}
    assert matrix["policy"]["default"] == "public-metadata-and-receipts"
    rules = " ".join(matrix["policy"]["rules"])
    assert "exact-item licence" in rules
    assert "Authority, completeness, freshness, privacy, safety and legal effect" in rules

    by_source = {decision["source"]: decision for decision in matrix["decisions"]}
    assert by_source["Stats NZ produced material and declared datasets"]["tier"] == "A"
    assert by_source["OpenStreetMap data"]["tier"] == "A"
    assert by_source["Greater Wellington GIS data"]["tier"] == "A"
    assert by_source["LINZ Data Service items"]["tier"] == "B"
    assert by_source["Churton Park Village Supermarket catalogue record"]["tier"] == "A"
    assert by_source["NZ ambulance prototype and provider location candidates"]["tier"] == "A"
    assert all(decision["contingency"] for decision in matrix["decisions"])
    assert all(decision["non_claims"] for decision in matrix["decisions"])


def test_churton_registry_uses_exact_arcgis_item_licence() -> None:
    registry = yaml.safe_load(
        (ROOT / "config/source-registry/wp010-public-pilot-candidates.yaml").read_text()
    )
    churton = next(source for source in registry["sources"] if "churton" in source["source_id"])

    assert churton["status"] == "staged-rights-cleared"
    assert churton["rights"]["spdx_or_uri"] == "CC-BY-3.0-NZ"
    assert churton["rights"]["redistribution_status"] == "attribution-required"
    assert churton["endpoints"][0]["enabled"] is False
    assert "aed53628016540388abfbe018da439b6" in churton["rights"]["notes"]


def test_linz_catalogue_does_not_confer_payload_rights() -> None:
    registry = yaml.safe_load((ROOT / "config/source-registry/nz-spatial-pilot.yaml").read_text())
    linz = registry["sources"][0]

    assert linz["rights"]["redistribution_status"] == "item-licence-required"
    assert "restricted LINZ products do not inherit" in linz["rights"]["notes"]
