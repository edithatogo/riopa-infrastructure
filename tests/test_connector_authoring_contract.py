import json
from pathlib import Path


def test_connector_authoring_contract_is_complete_and_non_authorizing() -> None:
    root = Path(__file__).resolve().parents[1]
    record = json.loads((root / "docs/connector-adapter-contract-20260824.json").read_text())
    assert record["status"] == "bounded-repository-contract"
    assert {surface["id"] for surface in record["surfaces"]} == {
        "arcgis-rest",
        "wfs-2.0.0",
        "koordinates-export",
        "offline-warc-wacz",
    }
    assert len(record["required_controls"]) >= 7
    assert any("does not authorize acquisition" in claim for claim in record["claims"])
    assert "real-source-national-and-council-capture" in record["open_gates"]


def test_connector_plan_records_authoring_contract_without_live_source_claim() -> None:
    root = Path(__file__).resolve().parents[1]
    plan = (root / "conductor/tracks/connector_runtime_capture_20260719/plan.md").read_text()
    assert "[x] 4.3 Publish the bounded adapter contract" in plan
    assert "live-source, rights/publication, preservation and external gates remain pending" in plan
