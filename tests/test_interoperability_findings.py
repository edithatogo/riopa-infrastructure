import json
from pathlib import Path

from scripts.build_interoperability_findings import build_findings


def test_interoperability_findings_ledger_is_fail_closed() -> None:
    root = Path(__file__).resolve().parents[1]
    path = root / "docs/ontology/interoperability-compatibility-matrix-20260825.json"
    report = build_findings(path)
    assert report["open_finding_count"] >= 1
    assert report["promotion_allowed"] is False
    statuses = {item["finding_id"]: item["status"] for item in report["findings"]}
    assert statuses["migration-corpus"] == "resolved"
    assert statuses["external-producer-consumer"] == "open"


def test_interoperability_findings_preserve_matrix_version(tmp_path: Path) -> None:
    matrix = tmp_path / "matrix.json"
    matrix.write_text(
        json.dumps(
            {
                "matrix_version": "test",
                "implementations": [],
                "compatibility": {},
            }
        ),
        encoding="utf-8",
    )
    report = build_findings(matrix)
    assert report["matrix_version"] == "test"
    assert report["open_finding_count"] == 4
