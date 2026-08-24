from pathlib import Path

import pytest

from riopa_provenance.registry import (
    build_source_change_event,
    classify_connector_readiness,
    load_registry,
)


def test_pilot_registry_readiness_is_declared_and_fail_closed() -> None:
    root = Path(__file__).resolve().parents[1]
    registry = load_registry(root / "config/source-registry/nz-spatial-pilot.yaml")
    report = classify_connector_readiness(registry)
    assert report["endpoint_count"] == 5
    statuses = {item["status"] for item in report["endpoints"]}
    assert statuses == {"metadata-rehearsal-ready", "credential-or-operator-required"}
    assert all("does not contact endpoints" in claim for claim in report["non_claims"][:1])


def test_readiness_rejects_malformed_endpoint() -> None:
    with pytest.raises(ValueError, match="endpoint_id"):
        classify_connector_readiness({"sources": [{"source_id": "source", "endpoints": [{}]}]})


def test_readiness_does_not_promote_unknown_authentication() -> None:
    report = classify_connector_readiness(
        {
            "registry_id": "registry",
            "sources": [
                {
                    "source_id": "source",
                    "endpoints": [
                        {
                            "endpoint_id": "endpoint",
                            "mechanism": "wfs",
                            "enabled": True,
                            "authentication": {"type": "future-auth"},
                        }
                    ],
                }
            ],
        }
    )
    assert report["endpoints"][0]["status"] == "unresolved"


def test_source_change_event_preserves_identity_and_digest_only_differences() -> None:
    previous = {
        "source_id": "source",
        "endpoint_id": "endpoint",
        "source_version": "2026-01",
        "locator": "https://example.test/archive/1",
        "payload_sha256": "a" * 64,
        "schema_sha256": "b" * 64,
        "rights_status": "review-required",
    }
    current = {**previous, "source_version": "2026-02", "payload_sha256": "c" * 64}
    event = build_source_change_event(previous, current, observed_at="2026-08-25T00:00:00Z")
    assert event["change_type"] == "changed"
    assert event["changed_fields"] == ["source_version", "payload_sha256"]
    assert event["identity_key"] == "source:endpoint:2026-02"
    assert event["event_id"].startswith("urn:riopa:event:source-change:")
    assert event["promotion_allowed"] is False


def test_source_change_event_rejects_cross_endpoint_comparison() -> None:
    observation = {
        "source_id": "source",
        "endpoint_id": "endpoint",
        "source_version": "1",
        "locator": "https://example.test",
    }
    with pytest.raises(ValueError, match="same endpoint"):
        build_source_change_event(
            {**observation, "endpoint_id": "other"}, observation, observed_at="now"
        )
