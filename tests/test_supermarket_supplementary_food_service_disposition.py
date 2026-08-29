import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_food_service_packet_is_content_addressed_and_not_a_supermarket_registry() -> None:
    record = json.loads(
        (ROOT / "docs/supermarket-supplementary-food-service-disposition-20260829.json").read_text()
    )
    source = record["source"]
    validation = record["archive_validation"]
    assert len(source["archive_revision"]) == 40
    assert len(source["payload_sha256"]) == 64
    assert validation["record_count"] == 13650
    assert validation["exact_supermarket_type_count"] == 0
    assert record["disposition"]["supermarket_registry_input"] is False
    assert record["disposition"]["promotion_allowed"] is False


def test_food_service_disposition_preserves_no_inference_boundary() -> None:
    record = json.loads(
        (ROOT / "docs/supermarket-supplementary-food-service-disposition-20260829.json").read_text()
    )
    non_claims = " ".join(record["non_claims"])
    assert "not a supermarket registry" in non_claims
    assert "No supermarket records are inferred" in non_claims
