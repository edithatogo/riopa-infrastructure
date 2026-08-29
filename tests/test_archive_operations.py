from copy import deepcopy

import pytest

from riopa_provenance.archive_operations import (
    ArchiveOperationsError,
    assemble_partial_release,
    build_coverage_report,
    build_delta_decision,
    validate_coverage_report,
)
from riopa_provenance.hashing import sha256_json


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


def resign(decision: dict[str, object]) -> None:
    decision["decision_sha256"] = sha256_json(
        {key: value for key, value in decision.items() if key != "decision_sha256"}
    )


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


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ({"owner_role": ""}, "owner_role"),
        ({"rights_status": "invented"}, "rights_status"),
        ({"availability_status": "invented"}, "availability_status"),
        ({"capture_kind": "historical"}, "capture_kind"),
        ({"schema": "not-an-object"}, "schema object"),
        ({"payload_sha256": "short"}, "64-character"),
        ({"payload_sha256": "z" * 64}, "hexadecimal"),
    ],
)
def test_delta_decision_rejects_malformed_observations(
    mutation: dict[str, object], message: str
) -> None:
    current = observation()
    current.update(mutation)
    with pytest.raises(ArchiveOperationsError, match=message):
        build_delta_decision(None, current, observed_at="2026-08-25T00:00:00Z")


def test_delta_decision_rejects_empty_time_and_identity_change() -> None:
    with pytest.raises(ArchiveOperationsError, match="observed_at"):
        build_delta_decision(None, observation(), observed_at="")
    with pytest.raises(ArchiveOperationsError, match="different endpoints"):
        build_delta_decision(
            observation("old-source"), observation(), observed_at="2026-08-25T00:00:00Z"
        )


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


def test_partial_release_rejects_self_hashed_semantically_invalid_decision() -> None:
    malformed = build_delta_decision(None, observation(), observed_at="2026-08-25T00:00:00Z")
    malformed["promotion_allowed"] = True
    resign(malformed)
    with pytest.raises(ArchiveOperationsError, match="prohibit promotion"):
        assemble_partial_release(
            [malformed], release_id="fixture-release", assembled_at="2026-08-25T01:00:00Z"
        )


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ({"record_type": "unknown"}, "archive delta decisions"),
        ({"action": "publish"}, "unsupported decision action"),
        ({"quarantine_reasons": "bad"}, "invalid quarantine reasons"),
        ({"action": "quarantine", "quarantine_reasons": []}, "lacks reasons"),
        ({"quarantine_reasons": ["unexpected"]}, "clear decision has"),
        ({"current_payload_sha256": None}, "lacks payload digest"),
        ({"current_payload_sha256": "bad"}, "64-character"),
    ],
)
def test_partial_release_rejects_invalid_decision_semantics(
    mutation: dict[str, object], message: str
) -> None:
    decision = build_delta_decision(None, observation(), observed_at="2026-08-25T00:00:00Z")
    decision.update(mutation)
    resign(decision)
    with pytest.raises(ArchiveOperationsError, match=message):
        assemble_partial_release(
            [decision], release_id="fixture-release", assembled_at="2026-08-25T01:00:00Z"
        )


def test_release_assembly_rejects_empty_and_duplicate_inputs() -> None:
    with pytest.raises(ArchiveOperationsError, match="non-empty"):
        assemble_partial_release([], release_id="", assembled_at="")
    with pytest.raises(ArchiveOperationsError, match="at least one"):
        assemble_partial_release([], release_id="fixture", assembled_at="2026-08-25")
    decision = build_delta_decision(None, observation(), observed_at="2026-08-25T00:00:00Z")
    with pytest.raises(ArchiveOperationsError, match="unique identities"):
        assemble_partial_release(
            [decision, decision], release_id="fixture", assembled_at="2026-08-25"
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


def test_coverage_report_rejects_empty_metadata_and_observations() -> None:
    with pytest.raises(ArchiveOperationsError, match="non-empty"):
        build_coverage_report([observation()], report_id="", generated_at="")
    with pytest.raises(ArchiveOperationsError, match="at least one"):
        build_coverage_report([], report_id="fixture", generated_at="2026-08-25")


def test_coverage_report_validator_binds_digest_and_boundaries() -> None:
    report = build_coverage_report(
        [observation()], report_id="fixture-coverage", generated_at="2026-08-25"
    )
    assert validate_coverage_report(report) == ()

    tampered = deepcopy(report)
    tampered["source_count"] = 2
    assert any("report_sha256" in error for error in validate_coverage_report(tampered))


def test_coverage_report_validator_rejects_promotion_and_national_percentage() -> None:
    report = build_coverage_report(
        [observation()], report_id="fixture-coverage", generated_at="2026-08-25"
    )
    report["promotion_allowed"] = True
    report["national_coverage_percentage"] = 100
    report["report_sha256"] = sha256_json(
        {key: value for key, value in report.items() if key != "report_sha256"}
    )
    errors = validate_coverage_report(report)
    assert "coverage reports must prohibit promotion" in errors
    assert "national coverage percentage must remain null" in errors
