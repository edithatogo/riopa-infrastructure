import pytest

from scripts.build_operations_report_bundle import (
    OperationsReportError,
    build_bundle,
    validate_bundle,
)


def test_bundle_is_deterministic_and_marks_missing_components_pending() -> None:
    payload = {"slo": {"observations": 3}, "capacity": None}
    first = build_bundle(payload, report_id="ops-2026-w35", generated_at="2026-08-29T00:00:00Z")
    second = build_bundle(payload, report_id="ops-2026-w35", generated_at="2026-08-29T00:00:00Z")
    assert first == second
    assert first["components"]["slo"]["status"] == "candidate-input"
    assert first["components"]["capacity"] == {"status": "pending", "content_sha256": None}
    assert first["promotion_allowed"] is False
    assert first["publication_status"] == "candidate-not-published"


@pytest.mark.parametrize(
    ("payload", "message"),
    [({"slo": []}, "slo report"), ({"incident": "missing"}, "incident report")],
)
def test_bundle_rejects_non_object_components(payload: dict[str, object], message: str) -> None:
    with pytest.raises(OperationsReportError, match=message):
        build_bundle(payload, report_id="ops", generated_at="2026-08-29")


def test_bundle_rejects_empty_identity() -> None:
    with pytest.raises(OperationsReportError, match="non-empty"):
        build_bundle({}, report_id="", generated_at="")


def test_bundle_validator_binds_self_digest_and_boundaries() -> None:
    bundle = build_bundle({"slo": {"observations": 1}}, report_id="ops", generated_at="2026-08-29")
    assert validate_bundle(bundle) == ()
    tampered = dict(bundle)
    tampered["promotion_allowed"] = True
    assert any("promotion_allowed" in error for error in validate_bundle(tampered))


def test_bundle_validator_rejects_bad_component_digest() -> None:
    bundle = build_bundle({"slo": {"observations": 1}}, report_id="ops", generated_at="2026-08-29")
    bundle["components"]["slo"]["content_sha256"] = "bad"
    assert any("candidate input requires" in error for error in validate_bundle(bundle))
