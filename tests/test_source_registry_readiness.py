from pathlib import Path

import pytest

from riopa_provenance.registry import classify_connector_readiness, load_registry


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
