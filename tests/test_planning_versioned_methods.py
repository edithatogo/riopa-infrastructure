from pathlib import Path


def test_planning_methods_document_is_versioned_and_non_authoritative() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (root / "docs/planning-versioned-links-methods-20260825.md").read_text()
    assert "bounded candidate" in document
    assert "build_plan_source_intake" in document
    assert "build_planning_feasibility_record" in document
    assert "do not establish operative legal status" in document
    assert "accountable release authority remain open" in document
