import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_publication_findings_are_resolved_without_erasing_open_gates() -> None:
    record = json.loads(
        (ROOT / "docs/publication-deviations-limitations-20260825.json").read_text(encoding="utf-8")
    )
    assert record["status"] == "resolved-with-explicit-open-gates"
    assert {finding["disposition"] for finding in record["findings"]} == {"pass-with-limitations"}
    assert record["promotion_allowed"] is False
    assert any("external" in gate for gate in record["open_gates"])
    assert any("preservation" in gate for gate in record["open_gates"])
    assert any("90-day" in gate for gate in record["open_gates"])
