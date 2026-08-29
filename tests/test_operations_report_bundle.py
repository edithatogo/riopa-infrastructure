import pytest

from scripts.build_operations_report_bundle import OperationsReportError, build_bundle


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
