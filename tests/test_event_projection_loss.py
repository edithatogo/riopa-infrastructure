import json
import shutil
from pathlib import Path

import pytest

from riopa_provenance.crate import _openlineage_projection, _prov_projection
from riopa_provenance.hashing import sha256_json
from scripts.build_event_projection_loss_evidence import build_evidence


def test_recorded_field_loss_and_retained_values_reproduce():
    assert build_evidence(Path(".")) == json.loads(
        Path("docs/event-projection-loss-evidence-20260912.json").read_text()
    )


def test_new_schema_field_requires_explicit_disposition(tmp_path):
    (tmp_path / "schemas").mkdir()
    schema = json.loads(Path("schemas/provenance-event.schema.json").read_text())
    schema["properties"]["new_evidence"] = {"type": "string"}
    (tmp_path / "schemas/provenance-event.schema.json").write_text(json.dumps(schema))
    with pytest.raises(ValueError, match="unclassified"):
        build_evidence(tmp_path)


def test_status_collision_and_omitted_semantics_require_native_evidence(tmp_path):
    base = tmp_path / "source"
    shutil.copytree("examples/minimal", base)
    manifest = json.loads((base / "snapshot-manifest.json").read_text())
    event_path = base / manifest["provenance_events"][0]
    event = json.loads(event_path.read_text())
    event["status"] = "partial"
    event["event_hash"] = sha256_json(event, omit_keys={"event_hash"})
    event_path.write_text(json.dumps(event))
    before = _openlineage_projection(manifest, base)
    prov_before = _prov_projection(manifest, base)
    event["status"] = "reviewed"
    event["agents"] = []
    event["rights_refs"] = ["urn:test:changed-rights"]
    event["activity"]["activity_id"] = "urn:test:changed-activity"
    event["event_hash"] = sha256_json(event, omit_keys={"event_hash"})
    event_path.write_text(json.dumps(event))
    after = _openlineage_projection(manifest, base)
    assert before["events"][0]["eventType"] == after["events"][0]["eventType"] == "OTHER"
    # Only the digest distinguishes these native changes. It is not an inverse.
    left = before["events"][0]["run"]["facets"]["riopa_provenance"].pop("eventHash")
    right = after["events"][0]["run"]["facets"]["riopa_provenance"].pop("eventHash")
    assert left != right
    assert before == after
    assert _prov_projection(manifest, base) == prov_before


@pytest.mark.parametrize(
    "status,expected",
    [
        ("started", "START"),
        ("succeeded", "COMPLETE"),
        ("failed", "FAIL"),
        ("partial", "OTHER"),
        ("cancelled", "ABORT"),
        ("reviewed", "OTHER"),
    ],
)
def test_every_native_status_mapping(tmp_path, status, expected):
    base = tmp_path / "source"
    shutil.copytree("examples/minimal", base)
    manifest = json.loads((base / "snapshot-manifest.json").read_text())
    event_path = base / manifest["provenance_events"][0]
    event = json.loads(event_path.read_text())
    event["status"] = status
    event["event_hash"] = sha256_json(event, omit_keys={"event_hash"})
    event_path.write_text(json.dumps(event))
    assert _openlineage_projection(manifest, base)["events"][0]["eventType"] == expected


def test_retained_field_drift_fails_qualification(monkeypatch):
    import scripts.build_event_projection_loss_evidence as builder

    original = builder._openlineage_projection

    def changed(manifest, base):
        result = original(manifest, base)
        result["events"][0]["run"]["facets"]["riopa_provenance"]["sequence"] += 1
        return result

    monkeypatch.setattr(builder, "_openlineage_projection", changed)
    with pytest.raises(ValueError, match="projected value mismatch: sequence"):
        builder.build_evidence(Path("."))
