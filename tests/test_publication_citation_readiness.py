from pathlib import Path

from scripts.validate_publication_citation_readiness import build_report


def test_bounded_citation_readiness_is_fail_closed() -> None:
    report = build_report(Path(__file__).resolve().parents[1])
    assert report["status"] == "bounded-citation-contract-validated"
    assert report["promotion_allowed"] is False
    assert all(report["checks"].values())
    assert any("external reproduction" in gate for gate in report["open_gates"])


def test_citation_readiness_rejects_non_hex_revision(monkeypatch) -> None:
    import scripts.validate_publication_citation_readiness as module

    original = module.json.loads

    def loads(value):
        result = original(value)
        if isinstance(result, dict) and "software_revision" in result:
            result["software_revision"] = "x" * 40
        return result

    monkeypatch.setattr(module.json, "loads", loads)
    report = build_report(Path(__file__).resolve().parents[1])
    assert report["status"] == "citation-contract-invalid"
    assert report["checks"]["revision_is_content_bound"] is False


def test_citation_readiness_rejects_unknown_hex_revision(monkeypatch) -> None:
    import scripts.validate_publication_citation_readiness as module

    original = module.json.loads

    def loads(value):
        result = original(value)
        if isinstance(result, dict) and "software_revision" in result:
            result["software_revision"] = "0" * 40
        return result

    monkeypatch.setattr(module.json, "loads", loads)
    report = build_report(Path(__file__).resolve().parents[1])
    assert report["status"] == "citation-contract-invalid"
    assert report["checks"]["revision_is_content_bound"] is False
