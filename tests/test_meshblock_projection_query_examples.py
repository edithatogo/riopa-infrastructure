from pathlib import Path


def test_meshblock_query_examples_are_packet_bound_and_fail_closed() -> None:
    root = Path(__file__).resolve().parents[1]
    text = (root / "docs/meshblock-projection-query-examples-20260826.md").read_text()

    assert "evidence/stats-nz-meshblock-2026-projection/records-manifest.json" in text
    projection_id = "urn:riopa:projection:sha256:" + (
        "64a1cbce366794b2b802f04dbe2bf1dc5fbf813e5c5b159bcf0782af9adc511f"
    )
    assert projection_id in text
    assert "3f2dc0a4d95a4fcb495551098d58fc5bce9c9202" in text
    assert "must not contact the live ArcGIS URL" in text
    assert "does not satisfy" in text
    assert "national completeness" in text
