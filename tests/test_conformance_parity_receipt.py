import json
from pathlib import Path

from scripts.verify_conformance_parity import build_receipt


def test_bounded_conformance_receipt_matches_python_and_node() -> None:
    root = Path(__file__).resolve().parents[1]
    receipt = build_receipt(root)
    assert receipt["case_count"] > 0
    assert receipt["python_passed"] is True
    assert receipt["node_passed"] is True
    assert receipt["parity"] is True
    corpus_version = json.loads((root / "conformance/v1/corpus.json").read_text())["corpus_version"]
    assert corpus_version == receipt["corpus_version"]
