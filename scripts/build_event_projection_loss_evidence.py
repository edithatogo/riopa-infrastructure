"""Qualify native-event field retention and loss in existing projection builders."""

import argparse
import json
from pathlib import Path

from riopa_provenance.crate import _openlineage_projection, _prov_projection
from riopa_provenance.hashing import sha256_file, sha256_json

# Every native event property must receive an explicit disposition. New schema
# fields fail qualification until their mapping has been reviewed.
EXACT = {
    "event_id": "run.runId",
    "stream_id": "run.facets.riopa_provenance.streamId",
    "sequence": "run.facets.riopa_provenance.sequence",
    "recorded_at": "eventTime",
    "event_hash": "run.facets.riopa_provenance.eventHash",
    "inputs": "inputs[].name",
    "outputs": "outputs[].name",
}
OMITTED = {
    "schema_version",
    "event_type",
    "occurred_at",
    "agents",
    "parameters",
    "environment",
    "schema_refs",
    "classification_refs",
    "rights_refs",
    "quality_refs",
    "valid_time",
    "previous_event_hash",
    "signature_ref",
    "diagnostics",
}


def build_evidence(root: Path) -> dict:
    schema_path = root / "schemas/provenance-event.schema.json"
    fields = set(json.loads(schema_path.read_text())["properties"])
    if fields != set(EXACT) | OMITTED | {"status", "activity"}:
        raise ValueError("unclassified native event schema field")
    base = root / "examples/minimal"
    manifest = json.loads((base / "snapshot-manifest.json").read_text())
    projected = _openlineage_projection(manifest, base)
    native = [json.loads((base / name).read_text()) for name in manifest["provenance_events"]]
    if len(native) != len(projected["events"]):
        raise ValueError("event projection count mismatch")
    for source, target in zip(native, projected["events"], strict=True):
        for field, path in EXACT.items():
            if field in {"inputs", "outputs"}:
                value = [item["name"] for item in target[field]]
            else:
                value = target
                for key in path.split("."):
                    value = value[key]
            if value != source[field]:
                raise ValueError(f"projected value mismatch: {field}")
        if target["job"]["name"] != source["activity"]["activity_type"]:
            raise ValueError("activity type mapping mismatch")
    mapping = {}
    for field in sorted(fields):
        if field in EXACT:
            mapping[field] = {"classification": "exact-value", "path": EXACT[field]}
        elif field == "status":
            mapping[field] = {
                "classification": "many-to-one",
                "path": "eventType",
                "loss": "partial and reviewed both become OTHER",
            }
        elif field == "activity":
            mapping[field] = {
                "classification": "partial",
                "path": "job.name",
                "loss": (
                    "only activity_type retained; identity, name, description "
                    "and extensions omitted"
                ),
            }
        else:
            mapping[field] = {"classification": "omitted", "path": None}
    paths = [
        "src/riopa_provenance/crate.py",
        "schemas/provenance-event.schema.json",
        "tests/test_event_projection_loss.py",
    ]
    return {
        "evidence_id": "urn:riopa:evidence:event-projection-loss:2026-09-12",
        "scope": "native-event fields in bundled synthetic reference projections",
        "artifacts": {path: sha256_file(root / path) for path in paths},
        "native_events_sha256": sha256_json(native),
        "event_count": len(native),
        "openlineage_sha256": sha256_json(projected),
        "prov_sha256": sha256_json(_prov_projection(manifest, base)),
        "openlineage_fields": mapping,
        "prov_native_event_fields": (
            "none: PROV builder reads artifacts and transformation runs, not native events"
        ),
        "standalone_native_event_recovery": False,
        "promotion_allowed": False,
        "non_claims": [
            "Exact values are not certification of target-standard semantics.",
            "The event hash binds omitted content but cannot reconstruct it or verify a signature.",
            "Retain native evidence for rights, agents, chain verification and event recovery.",
            (
                "Artifact/transformation field qualification, full event parity "
                "and RC approval remain open."
            ),
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(build_evidence(Path(".")), indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
