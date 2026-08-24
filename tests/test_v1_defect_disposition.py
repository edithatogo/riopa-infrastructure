import json
from pathlib import Path


def test_v1_defect_disposition_is_fail_closed_and_has_no_p2_exceptions() -> None:
    root = Path(__file__).resolve().parents[1]
    record = json.loads((root / "docs/v1-defect-disposition-20260825.json").read_text())
    assert record["status"] == "fail-closed-no-p2-exceptions"
    assert record["p2_exceptions"] == []
    assert {item["severity"] for item in record["dispositions"]} == {"P0", "P1"}
    assert all(item["status"] != "resolved" for item in record["dispositions"])
    assert record["non_claims"]
