from __future__ import annotations

import json
from pathlib import Path

from riopa_provenance.sdk import validate_crosswalk, validate_json_instance


def test_sdk_schema_report_is_deterministic() -> None:
    root = Path(__file__).resolve().parents[1]
    corpus = json.loads((root / "conformance/v1/corpus.json").read_text(encoding="utf-8"))
    case = next(item for item in corpus["cases"] if item["schema"] is not None)
    report = validate_json_instance(case["instance"], root / "conformance/v1" / case["schema"])
    assert report.valid is case["expected_valid"]
    assert report.errors == ()
    assert len(report.instance_sha256) == 64
    assert (
        validate_json_instance(case["instance"], root / "conformance/v1" / case["schema"]) == report
    )


def test_sdk_crosswalk_keeps_uncertain_claims_fail_closed() -> None:
    report = validate_crosswalk(
        {
            "mapping_id": "urn:riopa:mapping:example",
            "source_assertion": {"source_id": "source-1", "label": "Example"},
            "canonical_id": "urn:riopa:entity:example:1",
            "method": "bounded-fixture",
            "confidence": "unknown",
            "reviewer": "agent-panel-fixture",
            "valid_time": {"from": "2026-01-01", "to": None},
            "evidence": [],
        }
    )
    assert report.valid is False
    assert report.errors == ("uncertain mappings require at least one evidence reference",)
