import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def _record() -> dict:
    return json.loads((ROOT / "docs/nz-spatial-archive-rights-capability-health-20260830.json").read_text())


def test_archive_only_record_is_fail_closed() -> None:
    record = _record()
    assert "no live endpoint contact" in record["observation_basis"]
    assert len(record["sources"]) == 5
    assert all(source["source_health"] == "not-observed" for source in record["sources"])
    assert record["disposition"]["promotion_allowed"] is False
    assert record["disposition"]["public_payload_materialisation_allowed"] is False
    assert record["disposition"]["network_timetable_facility_national_authoritative_claims_enabled"] is False


def test_archive_only_record_matches_schema() -> None:
    record = _record()
    schema = json.loads((ROOT / "schemas/nz-spatial-archive-rights-capability-health.schema.json").read_text())
    assert list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(record)) == []
