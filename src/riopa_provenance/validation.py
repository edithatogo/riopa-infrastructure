"""Schema, reference-closure and integrity validation for the reference bundle."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .hashing import sha256_json


@dataclass(frozen=True)
class ValidationResult:
    path: Path
    schema: Path | None
    errors: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return not self.errors


EXAMPLE_SCHEMA_MAP = {
    "source-record.json": "source-record.schema.json",
    "artifact-raw.json": "artifact.schema.json",
    "artifact-canonical.json": "artifact.schema.json",
    "provenance-event.json": "provenance-event.schema.json",
    "provenance-event-transformation.json": "provenance-event.schema.json",
    "provenance-event-snapshot.json": "provenance-event.schema.json",
    "transformation-run.json": "transformation-run.schema.json",
    "materialization.json": "materialization.schema.json",
    "quality-report.json": "quality-report.schema.json",
    "rights-inventory.json": "rights-inventory.schema.json",
    "methods-facts.json": "methods-facts.schema.json",
    "snapshot-manifest.json": "snapshot-manifest.schema.json",
    "spatial-feature-link.json": "spatial-feature-link.schema.json",
}


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_instance(instance: Any, schema: dict[str, Any]) -> tuple[str, ...]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda item: list(item.path))
    return tuple(
        f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in errors
    )


def validate_file(instance_path: Path, schema_path: Path) -> ValidationResult:
    try:
        instance = load_json(instance_path)
        schema = load_json(schema_path)
    except (OSError, json.JSONDecodeError) as exc:
        return ValidationResult(instance_path, schema_path, (str(exc),))

    errors = list(validate_instance(instance, schema))
    if instance_path.name.startswith("provenance-event") and not errors:
        expected = sha256_json(instance, omit_keys={"event_hash"})
        actual = instance.get("event_hash")
        if actual != expected:
            errors.append(f"event_hash mismatch: expected {expected}, found {actual}")
    if instance_path.name == "snapshot-manifest.json" and not errors:
        expected = sha256_json(instance, omit_keys={"manifest_sha256"})
        actual = instance.get("manifest_sha256")
        if actual != expected:
            errors.append(f"manifest_sha256 mismatch: expected {expected}, found {actual}")
    return ValidationResult(instance_path, schema_path, tuple(errors))


def _resolve_local_reference(base: Path, reference: str) -> Path:
    """Resolve a bundle-local reference and reject absolute/path-traversal references."""

    candidate = Path(reference)
    if candidate.is_absolute():
        raise ValueError(f"absolute reference is not portable: {reference}")
    resolved = (base / candidate).resolve()
    try:
        resolved.relative_to(base.resolve())
    except ValueError as exc:
        raise ValueError(f"reference escapes bundle root: {reference}") from exc
    return resolved


def manifest_references(manifest: dict[str, Any]) -> list[str]:
    """Return every local file reference declared by a snapshot manifest."""

    refs = [entry["source_record"] for entry in manifest.get("sources", [])]
    refs.extend(manifest.get("artifacts", []))
    refs.extend(manifest.get("provenance_events", []))
    refs.extend(manifest.get("transformations", []))
    refs.extend(manifest.get("materializations", []))
    refs.extend(manifest.get("domain_records", []))
    for key in ("quality_report", "rights_inventory", "methods_facts"):
        value = manifest.get(key)
        if value:
            refs.append(value)
    return refs


def _load_references(base: Path, references: list[str], errors: list[str]) -> dict[str, Any]:
    loaded: dict[str, Any] = {}
    for reference in references:
        if reference in loaded:
            errors.append(f"duplicate local reference in manifest: {reference}")
            continue
        try:
            path = _resolve_local_reference(base, reference)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if not path.is_file():
            errors.append(f"missing referenced file: {reference}")
            continue
        try:
            loaded[reference] = load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"could not read referenced JSON {reference}: {exc}")
    return loaded


def _duplicates(values: list[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def validate_manifest_closure(manifest_path: str | Path) -> ValidationResult:
    """Validate that a manifest forms a closed, internally coherent research snapshot."""

    path = Path(manifest_path).resolve()
    errors: list[str] = []
    try:
        manifest = load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        return ValidationResult(path, None, (str(exc),))

    expected_manifest_hash = sha256_json(manifest, omit_keys={"manifest_sha256"})
    if manifest.get("manifest_sha256") != expected_manifest_hash:
        errors.append(
            "manifest hash does not match canonical content: "
            f"expected {expected_manifest_hash}, found {manifest.get('manifest_sha256')}"
        )

    base = path.parent
    loaded = _load_references(base, manifest_references(manifest), errors)

    source_records: list[dict[str, Any]] = []
    for entry in manifest.get("sources", []):
        record = loaded.get(entry["source_record"])
        if not isinstance(record, dict):
            continue
        source_records.append(record)
        if record.get("source_id") != entry.get("source_id"):
            errors.append(
                f"source ID mismatch for {entry['source_record']}: "
                f"manifest={entry.get('source_id')} record={record.get('source_id')}"
            )

    artifacts = [
        loaded[ref] for ref in manifest.get("artifacts", []) if isinstance(loaded.get(ref), dict)
    ]
    transformations = [
        loaded[ref]
        for ref in manifest.get("transformations", [])
        if isinstance(loaded.get(ref), dict)
    ]
    materializations = [
        loaded[ref]
        for ref in manifest.get("materializations", [])
        if isinstance(loaded.get(ref), dict)
    ]
    events = [
        loaded[ref]
        for ref in manifest.get("provenance_events", [])
        if isinstance(loaded.get(ref), dict)
    ]

    source_ids = {record.get("source_id") for record in source_records if record.get("source_id")}
    artifact_ids_list = [item.get("artifact_id") for item in artifacts if item.get("artifact_id")]
    run_ids_list = [item.get("run_id") for item in transformations if item.get("run_id")]
    materialization_ids_list = [
        item.get("materialization_id")
        for item in materializations
        if item.get("materialization_id")
    ]
    event_ids_list = [item.get("event_id") for item in events if item.get("event_id")]

    for label, values in (
        ("artifact_id", artifact_ids_list),
        ("run_id", run_ids_list),
        ("materialization_id", materialization_ids_list),
        ("event_id", event_ids_list),
    ):
        for value in sorted(_duplicates(values)):
            errors.append(f"duplicate {label}: {value}")

    artifact_ids = set(artifact_ids_list)
    run_ids = set(run_ids_list)

    for artifact in artifacts:
        source_id = artifact.get("source_id")
        if source_id and source_id not in source_ids:
            errors.append(
                f"artifact {artifact.get('artifact_id')} references undeclared source {source_id}"
            )

    for run in transformations:
        for input_id in run.get("inputs", []):
            if input_id not in artifact_ids and input_id not in source_ids:
                errors.append(f"run {run.get('run_id')} has undeclared input {input_id}")
        for output_id in run.get("outputs", []):
            if output_id not in artifact_ids:
                errors.append(f"run {run.get('run_id')} has undeclared output {output_id}")

    snapshot_id = manifest.get("snapshot_id")
    for item in materializations:
        if item.get("snapshot_id") != snapshot_id:
            errors.append(
                f"materialisation {item.get('materialization_id')} targets "
                f"{item.get('snapshot_id')}, expected {snapshot_id}"
            )
        if item.get("artifact_id") not in artifact_ids:
            errors.append(
                f"materialisation {item.get('materialization_id')} references undeclared artifact "
                f"{item.get('artifact_id')}"
            )
        if item.get("generated_by") not in run_ids:
            errors.append(
                f"materialisation {item.get('materialization_id')} references undeclared run "
                f"{item.get('generated_by')}"
            )

    quality = loaded.get(manifest.get("quality_report"))
    rights = loaded.get(manifest.get("rights_inventory"))
    facts = loaded.get(manifest.get("methods_facts")) if manifest.get("methods_facts") else None
    for label, record in (
        ("quality report", quality),
        ("rights inventory", rights),
        ("methods facts", facts),
    ):
        if isinstance(record, dict) and record.get("subject_id") != snapshot_id:
            errors.append(
                f"{label} subject {record.get('subject_id')} does not match snapshot {snapshot_id}"
            )

    if isinstance(rights, dict):
        for item in rights.get("sources", []):
            if item.get("source_id") not in source_ids:
                errors.append(
                    f"rights inventory references undeclared source {item.get('source_id')}"
                )

    known_entities = set(source_ids) | artifact_ids | run_ids | set(materialization_ids_list)
    known_entities.add(snapshot_id)
    if isinstance(quality, dict):
        known_entities.add(quality.get("report_id"))
    if isinstance(rights, dict):
        known_entities.add(rights.get("inventory_id"))
    if isinstance(facts, dict):
        known_entities.add(facts.get("methods_facts_id"))
    known_entities.discard(None)

    previous_hash: str | None = None
    stream_id: str | None = None
    capture_activity_ids: set[str] = set()
    for index, event in enumerate(events):
        if event.get("sequence") != index:
            errors.append(
                f"event {event.get('event_id')} sequence {event.get('sequence')} "
                f"!= list index {index}"
            )
        if stream_id is None:
            stream_id = event.get("stream_id")
        elif event.get("stream_id") != stream_id:
            errors.append(
                f"event {event.get('event_id')} uses stream {event.get('stream_id')}, "
                f"expected {stream_id}"
            )
        if event.get("previous_event_hash") != previous_hash:
            errors.append(
                f"event {event.get('event_id')} previous hash mismatch: "
                f"expected {previous_hash}, found {event.get('previous_event_hash')}"
            )
        expected_event_hash = sha256_json(event, omit_keys={"event_hash"})
        if event.get("event_hash") != expected_event_hash:
            errors.append(
                f"event {event.get('event_id')} hash mismatch: expected {expected_event_hash}, "
                f"found {event.get('event_hash')}"
            )
        previous_hash = event.get("event_hash")
        if str(event.get("event_type", "")).startswith("capture."):
            activity_id = event.get("activity", {}).get("activity_id")
            if activity_id:
                capture_activity_ids.add(activity_id)
        for entity_id in [*event.get("inputs", []), *event.get("outputs", [])]:
            if entity_id not in known_entities:
                errors.append(
                    f"event {event.get('event_id')} references undeclared entity {entity_id}"
                )

    declared_capture_ids = {
        capture_id
        for entry in manifest.get("sources", [])
        for capture_id in entry.get("capture_ids", [])
    }
    for capture_id in sorted(declared_capture_ids - capture_activity_ids):
        errors.append(f"manifest capture ID has no capture event: {capture_id}")

    return ValidationResult(base / ".bundle-integrity", None, tuple(errors))


def validate_bundle(root: str | Path) -> list[ValidationResult]:
    root_path = Path(root).resolve()
    schema_dir = root_path / "schemas"
    example_dir = root_path / "examples" / "minimal"
    results: list[ValidationResult] = []

    for example_name, schema_name in EXAMPLE_SCHEMA_MAP.items():
        example_path = example_dir / example_name
        schema_path = schema_dir / schema_name
        if not example_path.exists():
            results.append(ValidationResult(example_path, schema_path, ("missing example",)))
            continue
        if not schema_path.exists():
            results.append(ValidationResult(example_path, schema_path, ("missing schema",)))
            continue
        results.append(validate_file(example_path, schema_path))

    for schema_path in sorted(schema_dir.glob("*.schema.json")):
        try:
            Draft202012Validator.check_schema(load_json(schema_path))
            results.append(ValidationResult(schema_path, None, ()))
        except Exception as exc:  # jsonschema exposes several schema error types
            results.append(ValidationResult(schema_path, None, (str(exc),)))

    results.append(validate_manifest_closure(example_dir / "snapshot-manifest.json"))
    return results
