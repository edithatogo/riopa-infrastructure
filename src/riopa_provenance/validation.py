"""Schema, reference-closure, payload, and integrity validation.

The validator is deliberately manifest-driven.  A snapshot may use arbitrary
filenames and directory layouts; its role in the snapshot determines the
normative schema.  This avoids the brittle v0.2 behaviour where only the
bundled ``examples/minimal`` filenames were validated.
"""

from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .hashing import sha256_file, sha256_json


@dataclass(frozen=True)
class ValidationResult:
    """Validation outcome for one logical unit."""

    path: Path
    schema: Path | None
    errors: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return not self.errors


@dataclass(frozen=True)
class ManifestReference:
    """A local manifest reference and the schema expected for its contents."""

    reference: str
    schema_name: str | None
    role: str


LEGACY_EXAMPLE_SCHEMA_MAP: Mapping[str, str] = {
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

ROLE_SCHEMAS: Mapping[str, str] = {
    "source": "source-record.schema.json",
    "artifact": "artifact.schema.json",
    "provenance_event": "provenance-event.schema.json",
    "transformation": "transformation-run.schema.json",
    "materialization": "materialization.schema.json",
    "quality_report": "quality-report.schema.json",
    "rights_inventory": "rights-inventory.schema.json",
    "methods_facts": "methods-facts.schema.json",
}

# Domain records are extensible.  Stable records should declare ``record_type``;
# these signatures preserve compatibility with the v0.2 synthetic example.
DOMAIN_SCHEMA_BY_RECORD_TYPE: Mapping[str, str] = {
    "spatial_feature_link": "spatial-feature-link.schema.json",
    "source_registry": "source-registry.schema.json",
    "publication_plan": "publication-plan.schema.json",
    "http_capture": "http-capture.schema.json",
    "arcgis_layer_capture_set": "arcgis-capture-set.schema.json",
    "wfs_feature_type_capture_set": "wfs-capture-set.schema.json",
    "spatial_materialization_quality": "spatial-materialization-quality.schema.json",
    "linz_layer_state": "linz-layer-state.schema.json",
    "linz_changeset_application": "linz-changeset-application.schema.json",
    "governance_decision": "governance-decision.schema.json",
}
DOMAIN_SCHEMA_SIGNATURES: tuple[tuple[frozenset[str], str], ...] = (
    (
        frozenset({"link_id", "feature_version_id", "provision_version_ids"}),
        "spatial-feature-link.schema.json",
    ),
    (frozenset({"registry_id", "sources"}), "source-registry.schema.json"),
    (frozenset({"publication_id", "targets", "assets"}), "publication-plan.schema.json"),
    (frozenset({"capture_id", "request", "response", "object"}), "http-capture.schema.json"),
    (
        frozenset({"capture_set_id", "metadata_capture_id", "page_capture_ids"}),
        "arcgis-capture-set.schema.json",
    ),
    (
        frozenset({"capture_set_id", "capabilities_capture_id", "type_name"}),
        "wfs-capture-set.schema.json",
    ),
    (
        frozenset({"source_id", "layer_id", "geoparquet", "duckdb"}),
        "spatial-materialization-quality.schema.json",
    ),
    (
        frozenset({"type_name", "changeset_type_name", "current_revision", "baseline"}),
        "linz-layer-state.schema.json",
    ),
    (
        frozenset({"application_id", "from_revision", "semantic_digest_after"}),
        "linz-changeset-application.schema.json",
    ),
)


def load_json(path: str | Path) -> Any:
    """Load UTF-8 JSON from *path*."""

    return json.loads(Path(path).read_text(encoding="utf-8"))


def _json_pointer(parts: Iterable[Any]) -> str:
    encoded = [str(part).replace("~", "~0").replace("/", "~1") for part in parts]
    return "/" + "/".join(encoded) if encoded else "<root>"


def validate_instance(instance: Any, schema: dict[str, Any]) -> tuple[str, ...]:
    """Validate *instance* with JSON Schema draft 2020-12."""

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(instance),
        key=lambda item: (list(item.absolute_path), item.message),
    )
    return tuple(f"{_json_pointer(error.absolute_path)}: {error.message}" for error in errors)


def _integrity_errors(instance: Any, schema_path: Path) -> list[str]:
    if not isinstance(instance, dict):
        return []
    errors: list[str] = []
    name = schema_path.name
    if name == "provenance-event.schema.json":
        expected = sha256_json(instance, omit_keys={"event_hash"})
        if instance.get("event_hash") != expected:
            errors.append(
                f"event_hash mismatch: expected {expected}, found {instance.get('event_hash')}"
            )
    elif name in {
        "snapshot-manifest.schema.json",
        "arcgis-capture-set.schema.json",
        "wfs-capture-set.schema.json",
    }:
        expected = sha256_json(instance, omit_keys={"manifest_sha256"})
        if instance.get("manifest_sha256") != expected:
            errors.append(
                "manifest_sha256 mismatch: "
                f"expected {expected}, found {instance.get('manifest_sha256')}"
            )
    elif name == "linz-layer-state.schema.json":
        expected = sha256_json(instance, omit_keys={"state_sha256"})
        if instance.get("state_sha256") != expected:
            errors.append(
                f"state_sha256 mismatch: expected {expected}, found {instance.get('state_sha256')}"
            )
    elif name == "linz-changeset-application.schema.json":
        expected = sha256_json(instance, omit_keys={"receipt_sha256"})
        if instance.get("receipt_sha256") != expected:
            errors.append(
                "receipt_sha256 mismatch: "
                f"expected {expected}, found {instance.get('receipt_sha256')}"
            )
    return errors


def validate_file(instance_path: Path, schema_path: Path) -> ValidationResult:
    """Schema- and integrity-validate one JSON file."""

    try:
        instance = load_json(instance_path)
        schema = load_json(schema_path)
    except (OSError, json.JSONDecodeError) as exc:
        return ValidationResult(instance_path, schema_path, (str(exc),))

    errors = [*validate_instance(instance, schema), *_integrity_errors(instance, schema_path)]
    return ValidationResult(instance_path, schema_path, tuple(errors))


def resolve_local_reference(base: Path, reference: str) -> Path:
    """Resolve a bundle-local path and reject absolute/traversing/symlink escapes."""

    candidate = Path(reference)
    if candidate.is_absolute():
        raise ValueError(f"absolute reference is not portable: {reference}")
    if not reference or reference in {".", "./"}:
        raise ValueError(f"reference does not identify a file: {reference!r}")
    resolved_base = base.resolve()
    resolved = (resolved_base / candidate).resolve()
    try:
        resolved.relative_to(resolved_base)
    except ValueError as exc:
        raise ValueError(f"reference escapes bundle root: {reference}") from exc
    return resolved


_resolve_local_reference = resolve_local_reference


def manifest_reference_specs(manifest: Mapping[str, Any]) -> list[ManifestReference]:
    """Return local metadata references and their normative roles/schemas."""

    specs: list[ManifestReference] = []
    for entry in manifest.get("sources", []):
        if isinstance(entry, Mapping) and isinstance(entry.get("source_record"), str):
            specs.append(
                ManifestReference(entry["source_record"], ROLE_SCHEMAS["source"], "source")
            )
    for role, key in (
        ("artifact", "artifacts"),
        ("provenance_event", "provenance_events"),
        ("transformation", "transformations"),
        ("materialization", "materializations"),
    ):
        for reference in manifest.get(key, []):
            if isinstance(reference, str):
                specs.append(ManifestReference(reference, ROLE_SCHEMAS[role], role))
    for role in ("quality_report", "rights_inventory", "methods_facts"):
        reference = manifest.get(role)
        if isinstance(reference, str) and reference:
            specs.append(ManifestReference(reference, ROLE_SCHEMAS[role], role))
    for reference in manifest.get("domain_records", []):
        if isinstance(reference, str):
            specs.append(ManifestReference(reference, None, "domain_record"))
    return specs


def manifest_references(manifest: Mapping[str, Any]) -> list[str]:
    """Return every local metadata reference declared by a manifest."""

    return [spec.reference for spec in manifest_reference_specs(manifest)]


def _domain_schema_name(instance: Any) -> str | None:
    if not isinstance(instance, Mapping):
        return None
    record_type = instance.get("record_type")
    if isinstance(record_type, str) and record_type in DOMAIN_SCHEMA_BY_RECORD_TYPE:
        return DOMAIN_SCHEMA_BY_RECORD_TYPE[record_type]
    keys = frozenset(instance)
    matches = [schema for signature, schema in DOMAIN_SCHEMA_SIGNATURES if signature <= keys]
    return matches[0] if len(matches) == 1 else None


def _duplicates(values: Iterable[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def _load_and_validate_references(
    base: Path,
    specs: list[ManifestReference],
    schema_dir: Path,
    errors: list[str],
) -> dict[str, Any]:
    loaded: dict[str, Any] = {}
    for duplicate in sorted(_duplicates(spec.reference for spec in specs)):
        errors.append(f"duplicate local reference in manifest: {duplicate}")

    for spec in specs:
        if spec.reference in loaded:
            continue
        try:
            path = resolve_local_reference(base, spec.reference)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if not path.is_file():
            errors.append(f"missing referenced file: {spec.reference}")
            continue
        try:
            instance = load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"could not read referenced JSON {spec.reference}: {exc}")
            continue
        loaded[spec.reference] = instance
        schema_name = spec.schema_name or _domain_schema_name(instance)
        if schema_name is None:
            errors.append(
                f"cannot determine schema for {spec.role} reference {spec.reference}; "
                "declare a supported record_type or add a schema mapping"
            )
            continue
        schema_path = schema_dir / schema_name
        if not schema_path.is_file():
            errors.append(f"missing schema {schema_name} for {spec.reference}")
            continue
        try:
            schema = load_json(schema_path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"could not read schema {schema_name}: {exc}")
            continue
        for error in validate_instance(instance, schema):
            errors.append(f"{spec.reference} {error}")
        for error in _integrity_errors(instance, schema_path):
            errors.append(f"{spec.reference} {error}")
    return loaded


def _validate_artifact_payloads(
    base: Path,
    artifacts: list[dict[str, Any]],
    errors: list[str],
) -> None:
    for artifact in artifacts:
        if artifact.get("payload_status") != "included":
            continue
        artifact_id = artifact.get("artifact_id", "<unknown artifact>")
        reference = artifact.get("path")
        if not isinstance(reference, str) or not reference:
            errors.append(f"included artifact {artifact_id} has no local path")
            continue
        try:
            payload = resolve_local_reference(base, reference)
        except ValueError as exc:
            errors.append(f"included artifact {artifact_id}: {exc}")
            continue
        if not payload.is_file():
            errors.append(f"included artifact {artifact_id} payload is missing: {reference}")
            continue
        actual_size = payload.stat().st_size
        actual_hash = sha256_file(payload)
        if artifact.get("size_bytes") != actual_size:
            errors.append(
                f"included artifact {artifact_id} size mismatch: "
                f"expected {artifact.get('size_bytes')}, found {actual_size}"
            )
        if artifact.get("sha256") != actual_hash:
            errors.append(
                f"included artifact {artifact_id} hash mismatch: "
                f"expected {artifact.get('sha256')}, found {actual_hash}"
            )
        if artifact.get("verification_status") != "verified":
            errors.append(f"included artifact {artifact_id} must have verification_status=verified")


def artifact_payload_references(base: Path, artifacts: Iterable[Mapping[str, Any]]) -> list[str]:
    """Return verified local paths declared as included artifact payloads.

    The caller should first run closure validation.  This function still checks
    path safety and uniqueness so packaging code cannot accidentally copy an
    undeclared path outside the snapshot root.
    """

    refs: list[str] = []
    seen: set[str] = set()
    for artifact in artifacts:
        if artifact.get("payload_status") != "included":
            continue
        reference = artifact.get("path")
        if not isinstance(reference, str):
            continue
        resolve_local_reference(base, reference)
        if reference not in seen:
            refs.append(reference)
            seen.add(reference)
    return refs


def _validate_event_streams(
    events: list[dict[str, Any]],
    known_entities: set[str],
    errors: list[str],
) -> set[str]:
    streams: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    capture_activity_ids: set[str] = set()

    for event in events:
        stream = str(event.get("stream_id", ""))
        partition = str(event.get("partition_id", "default"))
        streams[(stream, partition)].append(event)
        if str(event.get("event_type", "")).startswith("capture."):
            activity_id = event.get("activity", {}).get("activity_id")
            if activity_id:
                capture_activity_ids.add(str(activity_id))
        for entity_id in [*event.get("inputs", []), *event.get("outputs", [])]:
            if entity_id not in known_entities:
                errors.append(
                    f"event {event.get('event_id')} references undeclared entity {entity_id}"
                )

    for (stream_id, partition_id), members in sorted(streams.items()):
        by_sequence: dict[int, dict[str, Any]] = {}
        for event in members:
            sequence = event.get("sequence")
            if not isinstance(sequence, int):
                continue
            if sequence in by_sequence:
                errors.append(
                    f"stream {stream_id}/{partition_id} has duplicate sequence {sequence}"
                )
            else:
                by_sequence[sequence] = event
        sequences = sorted(by_sequence)
        if sequences and sequences != list(range(sequences[0], sequences[-1] + 1)):
            errors.append(f"stream {stream_id}/{partition_id} has sequence gaps: {sequences}")
        if sequences and sequences[0] != 0:
            errors.append(
                f"stream {stream_id}/{partition_id} begins at sequence {sequences[0]}, expected 0"
            )
        previous_hash: str | None = None
        for sequence in sequences:
            event = by_sequence[sequence]
            if event.get("previous_event_hash") != previous_hash:
                errors.append(
                    f"event {event.get('event_id')} previous hash mismatch: "
                    f"expected {previous_hash}, found {event.get('previous_event_hash')}"
                )
            expected_event_hash = sha256_json(event, omit_keys={"event_hash"})
            if event.get("event_hash") != expected_event_hash:
                errors.append(
                    f"event {event.get('event_id')} hash mismatch: "
                    f"expected {expected_event_hash}, found {event.get('event_hash')}"
                )
            previous_hash = event.get("event_hash")

    event_ids = {event.get("event_id") for event in events}
    for event in events:
        for parent in event.get("causal_parent_event_ids", []):
            if parent not in event_ids:
                errors.append(
                    f"event {event.get('event_id')} has undeclared causal parent {parent}"
                )
    return capture_activity_ids


def validate_manifest_closure(
    manifest_path: str | Path,
    *,
    schema_dir: str | Path | None = None,
) -> ValidationResult:
    """Validate a closed, coherent snapshot rooted at *manifest_path*.

    This includes JSON Schema validation for the manifest and every referenced
    metadata record, content validation for included payloads, referential
    integrity, event stream integrity, and canonical manifest/event hashes.
    """

    path = Path(manifest_path).resolve()
    errors: list[str] = []
    try:
        manifest = load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        return ValidationResult(path, None, (str(exc),))
    if not isinstance(manifest, dict):
        return ValidationResult(path, None, ("manifest root must be an object",))

    schemas = (
        Path(schema_dir).resolve() if schema_dir is not None else _find_schema_dir(path.parent)
    )
    manifest_schema = schemas / "snapshot-manifest.schema.json"
    if not manifest_schema.is_file():
        errors.append(f"missing snapshot schema: {manifest_schema}")
    else:
        try:
            errors.extend(validate_instance(manifest, load_json(manifest_schema)))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"could not read snapshot schema: {exc}")

    expected_manifest_hash = sha256_json(manifest, omit_keys={"manifest_sha256"})
    if manifest.get("manifest_sha256") != expected_manifest_hash:
        errors.append(
            "manifest hash does not match canonical content: "
            f"expected {expected_manifest_hash}, found {manifest.get('manifest_sha256')}"
        )

    base = path.parent
    specs = manifest_reference_specs(manifest)
    loaded = _load_and_validate_references(base, specs, schemas, errors)

    source_records: list[dict[str, Any]] = []
    for entry in manifest.get("sources", []):
        if not isinstance(entry, Mapping):
            continue
        reference = entry.get("source_record")
        record = loaded.get(reference) if isinstance(reference, str) else None
        if not isinstance(record, dict):
            continue
        source_records.append(record)
        if record.get("source_id") != entry.get("source_id"):
            errors.append(
                f"source ID mismatch for {reference}: manifest={entry.get('source_id')} "
                f"record={record.get('source_id')}"
            )

    def records(key: str) -> list[dict[str, Any]]:
        return [
            loaded[ref]
            for ref in manifest.get(key, [])
            if isinstance(ref, str) and isinstance(loaded.get(ref), dict)
        ]

    artifacts = records("artifacts")
    transformations = records("transformations")
    materializations = records("materializations")
    events = records("provenance_events")

    source_ids = {str(item["source_id"]) for item in source_records if item.get("source_id")}
    artifact_ids_list = [str(item["artifact_id"]) for item in artifacts if item.get("artifact_id")]
    run_ids_list = [str(item["run_id"]) for item in transformations if item.get("run_id")]
    materialization_ids_list = [
        str(item["materialization_id"])
        for item in materializations
        if item.get("materialization_id")
    ]
    event_ids_list = [str(item["event_id"]) for item in events if item.get("event_id")]

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
    _validate_artifact_payloads(base, artifacts, errors)

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

    quality_reference = manifest.get("quality_report")
    rights_reference = manifest.get("rights_inventory")
    facts_reference = manifest.get("methods_facts")
    quality = loaded.get(quality_reference) if isinstance(quality_reference, str) else None
    rights = loaded.get(rights_reference) if isinstance(rights_reference, str) else None
    facts = loaded.get(facts_reference) if isinstance(facts_reference, str) else None
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
    if isinstance(snapshot_id, str):
        known_entities.add(snapshot_id)
    for record, id_key in (
        (quality, "report_id"),
        (rights, "inventory_id"),
        (facts, "methods_facts_id"),
    ):
        if isinstance(record, dict) and record.get(id_key):
            known_entities.add(str(record[id_key]))

    capture_activity_ids = _validate_event_streams(events, known_entities, errors)
    declared_capture_ids = {
        str(capture_id)
        for entry in manifest.get("sources", [])
        if isinstance(entry, Mapping)
        for capture_id in entry.get("capture_ids", [])
    }
    for capture_id in sorted(declared_capture_ids - capture_activity_ids):
        errors.append(f"manifest capture ID has no capture event: {capture_id}")

    return ValidationResult(base / ".bundle-integrity", manifest_schema, tuple(errors))


def _find_schema_dir(start: Path) -> Path:
    for candidate in (start, *start.parents):
        schema_dir = candidate / "schemas"
        if schema_dir.is_dir():
            return schema_dir.resolve()
    # A caller may validate a copied bundle fixture outside the repository.
    package_root = Path(__file__).resolve().parents[2]
    packaged = package_root / "schemas"
    if packaged.is_dir():
        return packaged.resolve()
    raise FileNotFoundError(f"could not find schemas directory above {start}")


def validate_schema_directory(schema_dir: str | Path) -> list[ValidationResult]:
    """Meta-validate every JSON Schema in a directory."""

    directory = Path(schema_dir).resolve()
    results: list[ValidationResult] = []
    ids: dict[str, Path] = {}
    for schema_path in sorted(directory.glob("*.schema.json")):
        errors: list[str] = []
        try:
            schema = load_json(schema_path)
            Draft202012Validator.check_schema(schema)
            schema_id = schema.get("$id") if isinstance(schema, dict) else None
            if not isinstance(schema_id, str) or not schema_id:
                errors.append("schema has no non-empty $id")
            elif schema_id in ids:
                errors.append(f"duplicate $id also used by {ids[schema_id].name}: {schema_id}")
            else:
                ids[schema_id] = schema_path
        except Exception as exc:  # jsonschema exposes multiple schema error types
            errors.append(str(exc))
        results.append(ValidationResult(schema_path, None, tuple(errors)))
    if not results:
        results.append(ValidationResult(directory, None, ("no schemas found",)))
    return results


def discover_manifests(root: str | Path) -> list[Path]:
    """Discover snapshot manifests while excluding generated/build directories."""

    root_path = Path(root).resolve()
    ignored = {".git", ".venv", ".pytest_cache", ".mypy_cache", ".ruff_cache", "dist", "build"}
    manifests: list[Path] = []
    for path in root_path.rglob("snapshot-manifest.json"):
        if ignored.intersection(path.relative_to(root_path).parts):
            continue
        manifests.append(path)
    return sorted(manifests)


def validate_bundle(
    root: str | Path,
    *,
    manifests: Iterable[str | Path] | None = None,
) -> list[ValidationResult]:
    """Validate schemas and every discovered or explicitly supplied snapshot."""

    root_path = Path(root).resolve()
    schema_dir = root_path / "schemas"
    results = validate_schema_directory(schema_dir)

    # Keep the canonical example contract explicit while validation of every
    # actual snapshot remains manifest-driven.  This catches accidental loss
    # of a documentation fixture or its schema with clear diagnostics.
    example_dir = root_path / "examples" / "minimal"
    if example_dir.is_dir():
        for example_name, schema_name in LEGACY_EXAMPLE_SCHEMA_MAP.items():
            example_path = example_dir / example_name
            schema_path = schema_dir / schema_name
            if not example_path.is_file():
                results.append(ValidationResult(example_path, schema_path, ("missing example",)))
            elif not schema_path.is_file():
                results.append(ValidationResult(example_path, schema_path, ("missing schema",)))
            else:
                results.append(validate_file(example_path, schema_path))

    selected = (
        [Path(item).resolve() for item in manifests]
        if manifests is not None
        else discover_manifests(root_path)
    )
    if not selected:
        results.append(
            ValidationResult(root_path / "snapshot-manifest.json", None, ("no manifests found",))
        )
        return results
    for manifest_path in selected:
        results.append(validate_file(manifest_path, schema_dir / "snapshot-manifest.schema.json"))
        results.append(validate_manifest_closure(manifest_path, schema_dir=schema_dir))
    return results
