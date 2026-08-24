import json
from pathlib import Path


def test_v1_non_v1_feature_disposition_is_fail_closed() -> None:
    record = json.loads(
        (
            Path(__file__).resolve().parents[1] / "docs/v1-non-v1-feature-disposition-20260825.json"
        ).read_text()
    )
    assert record["status"] == "formally-deferred"
    assert record["scope"].startswith("bounded regional public-datasets-only")
    assert {item["status"] for item in record["dispositions"]} >= {
        "deferred",
        "excluded",
        "blocked",
    }
    assert all(item["reopen_when"] for item in record["dispositions"])
    assert record["non_claims"]
