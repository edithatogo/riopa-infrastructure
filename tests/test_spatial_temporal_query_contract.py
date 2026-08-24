import json
from pathlib import Path

from riopa_provenance.transitions import select_temporal_records, validate_transition


def test_spatial_temporal_query_contract_is_bounded() -> None:
    root = Path(__file__).resolve().parents[1]
    contract = json.loads((root / "docs/spatial-temporal-query-contract-20260825.json").read_text())
    records = json.loads((root / contract["fixture"]).read_text())
    assert contract["status"] == "bounded-repository-contract"
    assert all(validate_transition(record) == () for record in records)
    assert len(select_temporal_records(records, perspective="valid_time", at="2021-06-01")) == 2
    assert len(select_temporal_records(records, perspective="recorded_time", at="2021-01-15")) == 1
    assert contract["promotion_allowed"] is False
    assert any("external" in gate for gate in contract["open_gates"])
