"""Deterministic, verifiable research-object packaging for RIOPA snapshots."""

from __future__ import annotations

import json
import shutil
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .hashing import sha256_file
from .methods import generate_methods_markdown
from .validation import (
    artifact_payload_references,
    load_json,
    manifest_references,
    resolve_local_reference,
    validate_manifest_closure,
)

INTEGRITY_FILES = {"bundle-manifest.json", "checksums.sha256"}
GENERATED_METADATA_FILES = {
    "README.md",
    "methods.md",
    "CITATION.cff",
    "datacite-metadata.json",
    "prov.jsonld",
    "openlineage-events.json",
    "ro-crate-metadata.json",
    *INTEGRITY_FILES,
}
RO_CRATE_PROFILE = "https://w3id.org/ro/crate/1.2"
RO_CRATE_CONTEXT = f"{RO_CRATE_PROFILE}/context"


@dataclass(frozen=True)
class ResearchObjectVerification:
    root: Path
    errors: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return not self.errors


def _load(path: Path) -> dict[str, Any]:
    value = load_json(path)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object in {path}")
    return value


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _safe_source(base: Path, reference: str) -> Path:
    try:
        return resolve_local_reference(base, reference)
    except ValueError as exc:
        raise ValueError(str(exc).replace("reference ", "bundle reference ", 1)) from exc


def _file_entity(path: str, actual_path: Path | None = None) -> dict[str, Any]:
    entity: dict[str, Any] = {
        "@id": path,
        "@type": "File",
        "name": Path(path).name,
    }
    if actual_path is not None and actual_path.is_file():
        entity.update(
            {
                "contentSize": actual_path.stat().st_size,
                "sha256": sha256_file(actual_path),
            }
        )
    return entity


def _software_id(run: Mapping[str, Any]) -> str:
    implementation = run["implementation"]
    return f"{implementation['repository']}#commit-{implementation['commit']}"


def _unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _current_package_files(output: Path) -> list[str]:
    return sorted(
        path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file()
    )


def _load_manifest_records(
    manifest: Mapping[str, Any], base: Path, key: str
) -> list[dict[str, Any]]:
    return [_load(_safe_source(base, reference)) for reference in manifest.get(key, [])]


def build_ro_crate(manifest_path: str | Path, output_dir: str | Path) -> Path:
    """Build an RO-Crate 1.2 metadata projection for files currently in *output_dir*.

    Integrity files are declared even when this function is called before they
    are generated.  Their hashes are intentionally not embedded in the crate,
    avoiding a checksum/metadata circular dependency.  The final bundle
    manifest and checksum inventory bind the completed crate instead.
    """

    manifest_file = Path(manifest_path).resolve()
    base = manifest_file.parent
    manifest = _load(manifest_file)
    out = Path(output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    declared = [
        "snapshot-manifest.json",
        *manifest_references(manifest),
        "methods.md",
        "README.md",
        "CITATION.cff",
        "datacite-metadata.json",
        "prov.jsonld",
        "openlineage-events.json",
        "ro-crate-metadata.json",
        "bundle-manifest.json",
        "checksums.sha256",
    ]
    # Include copied payloads and schemas or other extensions already present.
    has_parts = _unique([*declared, *_current_package_files(out)])

    root: dict[str, Any] = {
        "@id": "./",
        "@type": "Dataset",
        "name": manifest["title"],
        "description": manifest.get("description", ""),
        "datePublished": manifest["created_at"],
        "version": manifest["snapshot_version"],
        "identifier": [manifest["snapshot_id"]]
        + (
            [f"https://doi.org/{manifest['citation']['doi']}"]
            if manifest["citation"].get("doi")
            else []
        ),
        "license": manifest["citation"].get("licence"),
        "creator": [
            {"@id": f"#creator-{index}"}
            for index, _ in enumerate(manifest["citation"]["creators"], start=1)
        ],
        "publisher": {"@id": "#publisher"},
        "hasPart": [{"@id": value} for value in has_parts],
        "conformsTo": {"@id": RO_CRATE_PROFILE},
        "subjectOf": [
            {"@id": "methods.md"},
            {"@id": manifest["quality_report"]},
            {"@id": manifest["rights_inventory"]},
            {"@id": "bundle-manifest.json"},
            {"@id": "checksums.sha256"},
        ],
    }

    graph: list[dict[str, Any]] = [
        {
            "@id": "ro-crate-metadata.json",
            "@type": "CreativeWork",
            "about": {"@id": "./"},
            "conformsTo": {"@id": RO_CRATE_PROFILE},
        },
        root,
        {
            "@id": "#publisher",
            "@type": "Organization",
            "name": manifest["citation"]["publisher"],
        },
        {
            "@id": RO_CRATE_PROFILE,
            "@type": "Profile",
            "name": "RO-Crate Metadata Specification 1.2",
        },
    ]

    for index, creator in enumerate(manifest["citation"]["creators"], start=1):
        graph.append({"@id": f"#creator-{index}", "@type": "Person", "name": creator})

    graph_ids = {str(entity["@id"]) for entity in graph}
    for relative in has_parts:
        if relative in graph_ids:
            continue
        actual = out / relative
        graph.append(_file_entity(relative, actual if actual.is_file() else None))
        graph_ids.add(relative)

    for entry in manifest["sources"]:
        record = _load(_safe_source(base, entry["source_record"]))
        publisher_id = f"{record['source_id']}#publisher"
        graph.extend(
            [
                {
                    "@id": record["source_id"],
                    "@type": "Dataset",
                    "name": record["name"],
                    "publisher": {"@id": publisher_id},
                    "url": record["access"]["landing_page"],
                    "mainEntityOfPage": {"@id": entry["source_record"]},
                    "spatialCoverage": record.get("spatial_coverage"),
                    "temporalCoverage": record.get("temporal_coverage"),
                    "conditionsOfAccess": record["rights"]["access_status"],
                    "license": record["rights"].get("spdx_or_uri"),
                },
                {
                    "@id": publisher_id,
                    "@type": "Organization",
                    "name": record["publisher"]["name"],
                    "url": record["publisher"].get("url"),
                },
            ]
        )
        root["hasPart"].append({"@id": record["source_id"]})

    for reference in manifest.get("artifacts", []):
        artifact = _load(_safe_source(base, reference))
        location = artifact.get("uri") or artifact.get("path")
        payload_property_id = f"{artifact['artifact_id']}#payload-status"
        verification_property_id = f"{artifact['artifact_id']}#verification-status"
        graph.append(
            {
                "@id": artifact["artifact_id"],
                "@type": "MediaObject",
                "name": artifact.get("logical_id") or artifact["artifact_id"],
                "encodingFormat": artifact["media_type"],
                "contentSize": artifact["size_bytes"],
                "sha256": artifact["sha256"],
                "contentUrl": location,
                "isPartOf": {"@id": "./"},
                "mainEntityOfPage": {"@id": reference},
                "additionalProperty": [
                    {"@id": payload_property_id},
                    {"@id": verification_property_id},
                ],
            }
        )
        graph.extend(
            [
                {
                    "@id": payload_property_id,
                    "@type": "PropertyValue",
                    "name": "payload_status",
                    "value": artifact["payload_status"],
                },
                {
                    "@id": verification_property_id,
                    "@type": "PropertyValue",
                    "name": "verification_status",
                    "value": artifact["verification_status"],
                },
            ]
        )
        root["hasPart"].append({"@id": artifact["artifact_id"]})

    software_seen: set[str] = set()
    for reference in manifest.get("transformations", []):
        run = _load(_safe_source(base, reference))
        software_id = _software_id(run)
        if software_id not in software_seen:
            implementation = run["implementation"]
            graph.append(
                {
                    "@id": software_id,
                    "@type": ["File", "SoftwareSourceCode"],
                    "name": implementation.get("package") or implementation["repository"],
                    "codeRepository": implementation["repository"],
                    "version": implementation.get("package_version"),
                    "identifier": [implementation["commit"]]
                    + ([implementation["swhid"]] if implementation.get("swhid") else []),
                }
            )
            root["hasPart"].append({"@id": software_id})
            software_seen.add(software_id)
        graph.append(
            {
                "@id": run["run_id"],
                "@type": "CreateAction",
                "name": run["run_type"],
                "actionStatus": run["status"],
                "startTime": run["started_at"],
                "endTime": run["ended_at"],
                "instrument": {"@id": software_id},
                "object": [{"@id": value} for value in run["inputs"]],
                "result": [{"@id": value} for value in run["outputs"]],
                "mainEntityOfPage": {"@id": reference},
            }
        )

    for reference in manifest.get("provenance_events", []):
        event = _load(_safe_source(base, reference))
        graph.append(
            {
                "@id": event["event_id"],
                "@type": "Action",
                "name": event["event_type"],
                "actionStatus": event["status"],
                "startTime": event["occurred_at"],
                "endTime": event["recorded_at"],
                "object": [{"@id": value} for value in event["inputs"]],
                "result": [{"@id": value} for value in event["outputs"]],
                "mainEntityOfPage": {"@id": reference},
                "identifier": event["event_hash"],
            }
        )

    for reference in manifest.get("materializations", []):
        item = _load(_safe_source(base, reference))
        reproducibility_property_id = f"{item['materialization_id']}#reproducibility-class"
        graph.append(
            {
                "@id": item["materialization_id"],
                "@type": "Dataset",
                "name": f"{item['format']} materialisation",
                "encodingFormat": item["media_type"],
                "isBasedOn": {"@id": item["artifact_id"]},
                "creator": {"@id": item["generated_by"]},
                "mainEntityOfPage": {"@id": reference},
                "additionalProperty": {"@id": reproducibility_property_id},
            }
        )
        graph.append(
            {
                "@id": reproducibility_property_id,
                "@type": "PropertyValue",
                "name": "reproducibility_class",
                "value": item.get("reproducibility_class"),
            }
        )
        root["hasPart"].append({"@id": item["materialization_id"]})

    for record_key, id_key, label in (
        ("quality_report", "report_id", "RIOPA quality report"),
        ("rights_inventory", "inventory_id", "RIOPA rights inventory"),
        ("methods_facts", "methods_facts_id", "RIOPA machine-readable methods facts"),
    ):
        reference = manifest.get(record_key)
        if not reference:
            continue
        record = _load(_safe_source(base, reference))
        graph.append(
            {
                "@id": record[id_key],
                "@type": "CreativeWork",
                "name": label,
                "about": {"@id": record["subject_id"]},
                "dateCreated": record.get("generated_at"),
                "mainEntityOfPage": {"@id": reference},
            }
        )

    crate = {"@context": RO_CRATE_CONTEXT, "@graph": graph}
    path = out / "ro-crate-metadata.json"
    _write_json(path, crate)
    return path


def _citation_cff(manifest: Mapping[str, Any]) -> dict[str, Any]:
    authors: list[dict[str, str]] = []
    for creator in manifest["citation"]["creators"]:
        parts = str(creator).strip().split()
        if len(parts) > 1:
            authors.append({"given-names": " ".join(parts[:-1]), "family-names": parts[-1]})
        else:
            authors.append({"name": str(creator)})
    citation: dict[str, Any] = {
        "cff-version": "1.2.0",
        "message": "If you use this dataset, please cite it using this metadata.",
        "title": manifest["title"],
        "type": "dataset",
        "version": manifest["snapshot_version"],
        "date-released": str(manifest["created_at"])[:10],
        "authors": authors,
    }
    if manifest["citation"].get("doi"):
        citation["doi"] = manifest["citation"]["doi"]
    if manifest["citation"].get("repository"):
        citation["repository-code"] = manifest["citation"]["repository"]
    if manifest["citation"].get("licence"):
        citation["license"] = manifest["citation"]["licence"]
    return citation


def _datacite_metadata(manifest: Mapping[str, Any]) -> dict[str, Any]:
    attributes: dict[str, Any] = {
        "creators": [{"name": name} for name in manifest["citation"]["creators"]],
        "titles": [{"title": manifest["title"]}],
        "publisher": manifest["citation"]["publisher"],
        "publicationYear": manifest["citation"]["publication_year"],
        "types": {"resourceTypeGeneral": "Dataset"},
        "schemaVersion": "http://datacite.org/schema/kernel-4",
        "version": manifest["snapshot_version"],
        "descriptions": [
            {
                "description": manifest.get("description", ""),
                "descriptionType": "Abstract",
            }
        ],
        "rightsList": [{"rights": manifest["citation"].get("licence", "Source-specific")}],
    }
    if manifest["citation"].get("doi"):
        attributes["doi"] = manifest["citation"]["doi"]
    if manifest["citation"].get("repository"):
        attributes["url"] = manifest["citation"]["repository"]
    return {"data": {"type": "dois", "attributes": attributes}}


def _prov_projection(manifest: Mapping[str, Any], base: Path) -> dict[str, Any]:
    graph: list[dict[str, Any]] = []
    for reference in manifest.get("artifacts", []):
        artifact = _load(_safe_source(base, reference))
        graph.append(
            {
                "@id": artifact["artifact_id"],
                "@type": "prov:Entity",
                "dcterms:format": artifact["media_type"],
                "riopa:sha256": artifact["sha256"],
            }
        )
    for reference in manifest.get("transformations", []):
        run = _load(_safe_source(base, reference))
        graph.append(
            {
                "@id": run["run_id"],
                "@type": "prov:Activity",
                "prov:startedAtTime": run["started_at"],
                "prov:endedAtTime": run["ended_at"],
                "prov:used": [{"@id": value} for value in run["inputs"]],
                "riopa:generated": [{"@id": value} for value in run["outputs"]],
                "prov:wasAssociatedWith": {"@id": _software_id(run)},
            }
        )
        for output in run["outputs"]:
            existing = next((item for item in graph if item.get("@id") == output), None)
            if existing is None:
                graph.append({"@id": output, "prov:wasGeneratedBy": {"@id": run["run_id"]}})
            else:
                existing["prov:wasGeneratedBy"] = {"@id": run["run_id"]}
    return {
        "@context": {
            "prov": "http://www.w3.org/ns/prov#",
            "dcterms": "http://purl.org/dc/terms/",
            "riopa": "https://w3id.org/riopa/terms/",
        },
        "@graph": graph,
    }


def _openlineage_projection(manifest: Mapping[str, Any], base: Path) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    type_map = {
        "started": "START",
        "succeeded": "COMPLETE",
        "failed": "FAIL",
        "partial": "OTHER",
        "cancelled": "ABORT",
        "reviewed": "OTHER",
    }
    for reference in manifest.get("provenance_events", []):
        event = _load(_safe_source(base, reference))
        events.append(
            {
                "eventTime": event["recorded_at"],
                "eventType": type_map.get(event["status"], "OTHER"),
                "run": {
                    "runId": event["event_id"],
                    "facets": {
                        "riopa_provenance": {
                            "_producer": "https://github.com/edithatogo/riopa-infrastructure",
                            "_schemaURL": "https://w3id.org/riopa/schema/openlineage-facet/v1",
                            "eventHash": event["event_hash"],
                            "streamId": event["stream_id"],
                            "sequence": event["sequence"],
                        }
                    },
                },
                "job": {
                    "namespace": event["stream_id"],
                    "name": event["activity"]["activity_type"],
                },
                "inputs": [{"namespace": "riopa", "name": value} for value in event["inputs"]],
                "outputs": [{"namespace": "riopa", "name": value} for value in event["outputs"]],
                "producer": "https://github.com/edithatogo/riopa-infrastructure",
                "schemaURL": "https://openlineage.io/spec/2-0-2/OpenLineage.json",
            }
        )
    return {
        "projection": "candidate-openlineage-2.0.2",
        "disclaimer": "Interoperability projection; native RIOPA events remain normative.",
        "events": events,
    }


def validate_provenance_projections(
    prov: Mapping[str, Any] | None, openlineage: Mapping[str, Any] | None
) -> tuple[str, ...]:
    """Validate bounded PROV and OpenLineage projection envelopes.

    This checks shape and referential uniqueness only.  It deliberately does
    not claim standards conformance, semantic equivalence or signed evidence.
    """

    if not isinstance(prov, Mapping):
        return ("PROV projection must be an object",)
    if not isinstance(openlineage, Mapping):
        return ("OpenLineage projection must be an object",)
    errors: list[str] = []
    context = prov.get("@context")
    if not isinstance(context, Mapping) or context.get("prov") != "http://www.w3.org/ns/prov#":
        errors.append("PROV projection must declare the W3C PROV namespace")
    graph = prov.get("@graph")
    if not isinstance(graph, list) or not graph:
        errors.append("PROV projection graph must be non-empty")
    else:
        ids: list[str] = []
        for item in graph:
            if (
                not isinstance(item, Mapping)
                or not isinstance(item.get("@id"), str)
                or not item["@id"].strip()
            ):
                errors.append("PROV graph entries require a non-empty string @id")
                continue
            if item["@id"] in ids:
                errors.append("PROV graph identifiers must be unique")
            ids.append(item["@id"])
    if not str(openlineage.get("projection", "")).startswith("candidate-openlineage-"):
        errors.append("OpenLineage projection must declare a candidate version")
    if not isinstance(openlineage.get("disclaimer"), str) or not openlineage["disclaimer"].strip():
        errors.append("OpenLineage projection requires a disclaimer")
    events = openlineage.get("events")
    if not isinstance(events, list):
        errors.append("OpenLineage events must be an array")
    else:
        for event in events:
            if not isinstance(event, Mapping):
                errors.append("OpenLineage events must be objects")
                continue
            if event.get("eventType") not in {"START", "COMPLETE", "FAIL", "ABORT", "OTHER"}:
                errors.append("OpenLineage eventType is unsupported")
            for field in ("run", "job", "inputs", "outputs", "producer", "schemaURL"):
                if field not in event:
                    errors.append(f"OpenLineage event requires {field}")
            run = event.get("run")
            if (
                not isinstance(run, Mapping)
                or not isinstance(run.get("runId"), str)
                or not run["runId"].strip()
            ):
                errors.append("OpenLineage event run requires a non-empty runId")
            job = event.get("job")
            if (
                not isinstance(job, Mapping)
                or not isinstance(job.get("namespace"), str)
                or not job["namespace"].strip()
                or not isinstance(job.get("name"), str)
                or not job["name"].strip()
            ):
                errors.append("OpenLineage event job requires namespace and name")
            for field in ("inputs", "outputs"):
                values = event.get(field)
                if not isinstance(values, list):
                    errors.append(f"OpenLineage event {field} must be an array")
                elif any(
                    not isinstance(value, Mapping)
                    or not isinstance(value.get("namespace"), str)
                    or not isinstance(value.get("name"), str)
                    or not value["namespace"].strip()
                    or not value["name"].strip()
                    for value in values
                ):
                    errors.append(f"OpenLineage event {field} require namespace and name")
            for field in ("producer", "schemaURL"):
                if not isinstance(event.get(field), str) or not event[field].strip():
                    errors.append(f"OpenLineage event {field} must be a non-empty string")
    return tuple(dict.fromkeys(errors))


def _research_object_readme(manifest: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            f"# {manifest['title']}",
            "",
            f"Snapshot: `{manifest['snapshot_id']}`  ",
            f"Version: `{manifest['snapshot_version']}`  ",
            f"Manifest SHA-256: `{manifest['manifest_sha256']}`",
            "",
            manifest.get("description", ""),
            "",
            "This directory is a deterministic RIOPA research-object projection. "
            "`snapshot-manifest.json` identifies the release; `ro-crate-metadata.json` "
            "describes its entities; `methods.md` is generated from evidence; "
            "`bundle-manifest.json` and `checksums.sha256` bind the package files.",
            "",
            "`prov.jsonld` and `openlineage-events.json` are interoperability projections; "
            "the native RIOPA records remain normative.",
            "",
            "Source rights and restrictions remain in `rights-inventory.json` and the "
            "source records. Presence in this package does not broaden source licences.",
            "",
        ]
    )


def _copy_schema_directory(manifest_file: Path, output: Path) -> None:
    candidates = [
        candidate / "schemas" for candidate in (manifest_file.parent, *manifest_file.parents)
    ]
    source = next((candidate for candidate in candidates if candidate.is_dir()), None)
    if source is None:
        return
    shutil.copytree(source, output / "schemas", dirs_exist_ok=True)


def build_research_object(
    manifest_path: str | Path,
    output_dir: str | Path,
    *,
    clean: bool = True,
) -> Path:
    """Build a deterministic, self-contained RIOPA research object."""

    manifest_file = Path(manifest_path).resolve()
    source_base = manifest_file.parent
    output = Path(output_dir).resolve()
    if output == source_base:
        raise ValueError("output directory must differ from the manifest directory")

    closure = validate_manifest_closure(manifest_file)
    if not closure.valid:
        raise ValueError("manifest closure failed: " + "; ".join(closure.errors))

    manifest = _load(manifest_file)
    artifacts = _load_manifest_records(manifest, source_base, "artifacts")
    if clean and output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)

    shutil.copy2(manifest_file, output / "snapshot-manifest.json")
    for reference in _unique(
        [*manifest_references(manifest), *artifact_payload_references(source_base, artifacts)]
    ):
        source = _safe_source(source_base, reference)
        destination = output / reference
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    _copy_schema_directory(manifest_file, output)

    (output / "methods.md").write_text(generate_methods_markdown(manifest_file), encoding="utf-8")
    (output / "README.md").write_text(_research_object_readme(manifest), encoding="utf-8")
    (output / "CITATION.cff").write_text(
        yaml.safe_dump(_citation_cff(manifest), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    _write_json(output / "datacite-metadata.json", _datacite_metadata(manifest))
    _write_json(output / "prov.jsonld", _prov_projection(manifest, source_base))
    _write_json(output / "openlineage-events.json", _openlineage_projection(manifest, source_base))

    # Build the crate after all non-integrity files exist.  It declares, but
    # does not hash, the two integrity files generated next.
    build_ro_crate(manifest_file, output)

    files_for_manifest = sorted(
        path for path in output.rglob("*") if path.is_file() and path.name not in INTEGRITY_FILES
    )
    bundle_manifest = {
        "schema_version": "1.0.0",
        "snapshot_id": manifest["snapshot_id"],
        "snapshot_version": manifest["snapshot_version"],
        "generated_at": manifest["created_at"],
        "generator": "riopa-provenance",
        "files": [
            {
                "path": path.relative_to(output).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in files_for_manifest
        ],
    }
    _write_json(output / "bundle-manifest.json", bundle_manifest)

    checksum_files = sorted(
        path for path in output.rglob("*") if path.is_file() and path.name != "checksums.sha256"
    )
    checksum_text = "".join(
        f"{sha256_file(path)}  {path.relative_to(output).as_posix()}\n" for path in checksum_files
    )
    (output / "checksums.sha256").write_text(checksum_text, encoding="utf-8")

    verification = verify_research_object(output)
    if not verification.valid:
        raise ValueError(
            "built research object failed verification: " + "; ".join(verification.errors)
        )
    return output


def _parse_checksums(path: Path, errors: list[str]) -> dict[str, str]:
    entries: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        errors.append(f"could not read checksums.sha256: {exc}")
        return entries
    for line_number, line in enumerate(lines, start=1):
        if not line:
            continue
        try:
            digest, reference = line.split("  ", 1)
        except ValueError:
            errors.append(f"invalid checksum line {line_number}: {line!r}")
            continue
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            errors.append(f"invalid SHA-256 on checksum line {line_number}")
            continue
        if reference in entries:
            errors.append(f"duplicate checksum reference: {reference}")
            continue
        entries[reference] = digest
    return entries


def verify_research_object(root: str | Path) -> ResearchObjectVerification:
    """Verify package closure, checksums, RO-Crate file coverage, and snapshot integrity."""

    directory = Path(root).resolve()
    errors: list[str] = []
    if not directory.is_dir():
        return ResearchObjectVerification(directory, ("research object directory does not exist",))

    required = {
        "snapshot-manifest.json",
        "bundle-manifest.json",
        "checksums.sha256",
        "ro-crate-metadata.json",
        "methods.md",
        "README.md",
        "CITATION.cff",
        "datacite-metadata.json",
        "prov.jsonld",
        "openlineage-events.json",
    }
    actual_files = set(_current_package_files(directory))
    for missing in sorted(required - actual_files):
        errors.append(f"missing required research-object file: {missing}")

    bundle_entries: dict[str, Mapping[str, Any]] = {}
    bundle_path = directory / "bundle-manifest.json"
    if bundle_path.is_file():
        try:
            bundle = _load(bundle_path)
            for entry in bundle.get("files", []):
                reference = entry.get("path")
                if not isinstance(reference, str):
                    errors.append("bundle manifest contains an entry without a string path")
                    continue
                if reference in bundle_entries:
                    errors.append(f"duplicate bundle manifest path: {reference}")
                    continue
                bundle_entries[reference] = entry
                try:
                    path = resolve_local_reference(directory, reference)
                except ValueError as exc:
                    errors.append(f"bundle manifest: {exc}")
                    continue
                if not path.is_file():
                    errors.append(f"bundle manifest references missing file: {reference}")
                    continue
                if entry.get("size_bytes") != path.stat().st_size:
                    errors.append(f"bundle manifest size mismatch: {reference}")
                if entry.get("sha256") != sha256_file(path):
                    errors.append(f"bundle manifest hash mismatch: {reference}")
            expected_bundle_paths = actual_files - INTEGRITY_FILES
            if set(bundle_entries) != expected_bundle_paths:
                missing_bundle_paths = sorted(expected_bundle_paths - set(bundle_entries))
                unexpected_bundle_paths = sorted(set(bundle_entries) - expected_bundle_paths)
                if missing_bundle_paths:
                    errors.append(f"bundle manifest omits files: {', '.join(missing_bundle_paths)}")
                if unexpected_bundle_paths:
                    errors.append(
                        "bundle manifest lists unexpected files: "
                        f"{', '.join(unexpected_bundle_paths)}"
                    )
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"could not validate bundle manifest: {exc}")

    checksums_path = directory / "checksums.sha256"
    checksums = _parse_checksums(checksums_path, errors) if checksums_path.is_file() else {}
    expected_checksum_paths = actual_files - {"checksums.sha256"}
    if set(checksums) != expected_checksum_paths:
        missing_checksum_paths = sorted(expected_checksum_paths - set(checksums))
        unexpected_checksum_paths = sorted(set(checksums) - expected_checksum_paths)
        if missing_checksum_paths:
            errors.append(f"checksum inventory omits files: {', '.join(missing_checksum_paths)}")
        if unexpected_checksum_paths:
            errors.append(
                f"checksum inventory lists unexpected files: {', '.join(unexpected_checksum_paths)}"
            )
    for reference, expected in checksums.items():
        try:
            path = resolve_local_reference(directory, reference)
        except ValueError as exc:
            errors.append(f"checksum inventory: {exc}")
            continue
        if not path.is_file():
            errors.append(f"checksum inventory references missing file: {reference}")
        elif sha256_file(path) != expected:
            errors.append(f"checksum mismatch: {reference}")

    crate_path = directory / "ro-crate-metadata.json"
    if crate_path.is_file():
        try:
            crate = _load(crate_path)
            graph = crate.get("@graph", [])
            graph_ids = {
                str(item["@id"])
                for item in graph
                if isinstance(item, Mapping) and isinstance(item.get("@id"), str)
            }
            uncovered = sorted(actual_files - graph_ids)
            if uncovered:
                errors.append(f"RO-Crate graph omits package files: {', '.join(uncovered)}")
            root_entities = [
                item for item in graph if isinstance(item, Mapping) and item.get("@id") == "./"
            ]
            if len(root_entities) != 1:
                errors.append("RO-Crate must contain exactly one root dataset entity")
            else:
                has_parts = {
                    str(item.get("@id"))
                    for item in root_entities[0].get("hasPart", [])
                    if isinstance(item, Mapping)
                }
                missing_parts = sorted(actual_files - has_parts - {"ro-crate-metadata.json"})
                if missing_parts:
                    errors.append(f"RO-Crate root omits package parts: {', '.join(missing_parts)}")
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"could not validate RO-Crate metadata: {exc}")

    manifest_path = directory / "snapshot-manifest.json"
    schema_dir = directory / "schemas"
    if manifest_path.is_file():
        closure = validate_manifest_closure(
            manifest_path, schema_dir=schema_dir if schema_dir.is_dir() else None
        )
        errors.extend(f"snapshot closure: {error}" for error in closure.errors)

    return ResearchObjectVerification(directory, tuple(errors))
