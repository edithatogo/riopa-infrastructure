from copy import deepcopy

import pytest

from riopa_provenance.archive_operations import (
    ArchiveOperationsError,
    assemble_partial_release,
    build_coverage_report,
    build_delta_decision,
)


def observation(source_id: str = "linz-addresses") -> dict[str, object]:
    return {
        "authority_id": "linz",
        "source_id": source_id,
        "endpoint_id": "wfs",
        "layer_type": "addresses",
        "legal_status": "official-source-declared",
        "rights_status": "permitted",
        "quality_status": "not-independently-verified",
        "time_depth": "current-only",
        "operational_disposition": "controlled-wave-candidate",
        "owner_role": "Spatial data lead",
        "availability_status": "healthy",
        "capture_kind": "current",
        "payload_sha256": "a" * 64,
        "schema": {"geometry": "Point", "id": "string"},
        "capabilities": {"paging": True, "format": "application/json"},
    }


def test_delta_decision_detects_change_without_claiming_promotion() -> None:
    previous = observation()
    current = observation()
    current["payload_sha256"] = "b" * 64
    decision = build_delta_decision(previous, current, observed_at="2026-08-25T00:00:00Z")
    assert decision["action"] == "store-delta"
    assert decision["payload_changed"] is True
    assert decision["quarantine_reasons"] == []
    assert decision["promotion_allowed"] is False


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        ({"rights_status": "unknown"}, "rights:unknown"),
        ({"availability_status": "degraded"}, "availability:degraded"),
        ({"schema": {"geometry": "Polygon"}}, "schema:unresolved-drift"),
        ({"capabilities": {"paging": False}}, "capability:unresolved-drift"),
    ],
)
def test_delta_decision_quarantines_unsafe_or_drifted_observation(
    mutation: dict[str, object], reason: str
) -> None:
    previous = observation()
    current = deepcopy(previous)
    current.update(mutation)
    decision = build_delta_decision(previous, current, observed_at="2026-08-25T00:00:00Z")
    assert decision["action"] == "quarantine"
    assert reason in decision["quarantine_reasons"]


def test_reconstructed_backfill_requires_explicit_reconstruction_time() -> None:
    current = observation()
    current["capture_kind"] = "reconstructed-backfill"
    with pytest.raises(ArchiveOperationsError, match="reconstructed_at"):
        build_delta_decision(None, current, observed_at="2026-08-25T00:00:00Z")


def test_partial_release_excludes_quarantine_and_binds_decision_digests() -> None:
    clear = build_delta_decision(None, observation(), observed_at="2026-08-25T00:00:00Z")
    unsafe_row = observation("linz-parcels")
    unsafe_row["rights_status"] = "restricted"
    unsafe = build_delta_decision(None, unsafe_row, observed_at="2026-08-25T00:00:00Z")
    release = assemble_partial_release(
        [unsafe, clear], release_id="fixture-release", assembled_at="2026-08-25T01:00:00Z"
    )
    assert release["partial"] is True
    assert [row["identity_key"] for row in release["included"]] == ["linz-addresses:wfs"]
    assert release["excluded"][0]["reasons"] == ["rights:restricted"]
    assert release["promotion_allowed"] is False

    tampered = deepcopy(clear)
    tampered["action"] = "quarantine"
    with pytest.raises(ArchiveOperationsError, match="digest mismatch"):
        assemble_partial_release(
            [tampered], release_id="fixture-release", assembled_at="2026-08-25T01:00:00Z"
        )


def test_coverage_report_is_multidimensional_and_bounded() -> None:
    second = observation("linz-parcels")
    second.update(
        {
            "layer_type": "cadastral",
            "rights_status": "restricted",
            "availability_status": "not-observed",
            "operational_disposition": "manual-review-exception",
            "time_depth": "historical-series-declared",
        }
    )
    report = build_coverage_report(
        [second, observation()], report_id="fixture-coverage", generated_at="2026-08-25T01:00:00Z"
    )
    assert report["source_count"] == 2
    assert report["dimensions"]["rights_status"] == {"permitted": 1, "restricted": 1}
    assert report["dimensions"]["layer_type"] == {"addresses": 1, "cadastral": 1}
    assert report["national_coverage_percentage"] is None
    assert report["promotion_allowed"] is False


def test_coverage_report_rejects_duplicate_source_identity() -> None:
    with pytest.raises(ArchiveOperationsError, match="unique identities"):
        build_coverage_report(
            [observation(), observation()], report_id="fixture", generated_at="2026-08-25"
        )
