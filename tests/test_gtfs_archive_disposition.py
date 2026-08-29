import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_gtfs_disposition_is_immutable_and_fail_closed() -> None:
    record = json.loads((ROOT / "docs/gtfs-archive-disposition-20260829.json").read_text())
    assert len(record["archive_revision"]) == 40
    assert len(record["sources"]) == 2
    assert all(source["payload_present"] is False for source in record["sources"])
    assert record["disposition"]["network_claims_enabled"] is False
    assert record["disposition"]["timetable_claims_enabled"] is False
    assert record["disposition"]["promotion_allowed"] is False
