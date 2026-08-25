from pathlib import Path

from scripts.validate_publication_citation_readiness import build_report


def test_bounded_citation_readiness_is_fail_closed() -> None:
    report = build_report(Path(__file__).resolve().parents[1])
    assert report["status"] == "bounded-citation-contract-validated"
    assert report["promotion_allowed"] is False
    assert all(report["checks"].values())
    assert any("external reproduction" in gate for gate in report["open_gates"])
