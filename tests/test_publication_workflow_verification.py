import json
from pathlib import Path


def test_publication_workflow_packet_covers_discovery_to_citation() -> None:
    root = Path(__file__).resolve().parents[1]
    packet = json.loads((root / "docs/publication-workflow-verification-20260825.json").read_text())
    assert packet["status"] == "bounded-local-verification"
    assert [item["name"] for item in packet["workflows"]] == [
        "discover",
        "install",
        "query",
        "reproduce",
        "cite",
    ]
    assert all(item["result"] == "pass" for item in packet["workflows"])
    for item in packet["workflows"]:
        evidence = item["evidence"]
        assert (root / evidence).exists()
    assert any("not external reproduction" in claim for claim in packet["nonclaims"])
