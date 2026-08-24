import json
from pathlib import Path

from scripts.build_interoperability_matrix import build_matrix


def test_bounded_interoperability_matrix_records_observed_and_open_tools() -> None:
    root = Path(__file__).resolve().parents[1]
    matrix = build_matrix(root)
    assert matrix["compatibility"]["python_node_parity"] is True
    tools = {item["tool"]: item for item in matrix["implementations"]}
    assert tools["riopa-python-reference"]["status"] == "observed-pass"
    assert tools["conformance_node.mjs"]["status"] == "observed-pass"
    assert tools["rust-reference"]["status"] == "not-implemented"


def test_preserved_matrix_is_non_assertive() -> None:
    root = Path(__file__).resolve().parents[1]
    matrix = json.loads(
        (root / "docs/ontology/interoperability-compatibility-matrix-20260825.json").read_text()
    )
    assert matrix["compatibility"]["external_producer_consumer"] == "not-observed"
    assert any("not an independent review" in claim for claim in matrix["non_claims"])
