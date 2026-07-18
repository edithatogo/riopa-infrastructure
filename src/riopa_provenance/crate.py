"""RO-Crate 1.3 and deterministic research-object packaging for RIOPA snapshots."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from .hashing import sha256_file
from .methods import generate_methods_markdown
from .validation import manifest_references, validate_manifest_closure


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _safe_source(base: Path, reference: str) -> Path:
    candidate = Path(reference)
    if candidate.is_absolute():
        raise ValueError(f"absolute bundle reference is not portable: {reference}")
    resolved = (base / candidate).resolve()
    try:
        resolved.relative_to(base.resolve())
    except ValueError as exc:
        raise ValueError(f"bundle reference escapes source directory: {reference}") from exc
    return resolved


def _file_entity(path: str, actual_path: Path) -> dict[str, Any]:
    return {
        "@id": path,
        "@type": "File",
        "name": Path(path).name,
        "contentSize": actual_path.stat().st_size,
        "sha256": sha256_file(actual_path),
    }


def _software_id(run: dict[str, Any]) -> str:
    implementation = run["implementation"]
    return f"{implementation['repository']}#commit-{implementation['commit']}"


def build_ro_crate(manifest_path: str | Path, output_dir: str | Path) -> Path:
    """Build the RO-Crate metadata projection for a snapshot and copied metadata files."""

    manifest_file = Path(manifest_path).resolve()
    base = manifest_file.parent
    manifest = _load(manifest_file)
    out = Path(output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    local_refs = manifest_references(manifest)
    has_parts = [
        "snapshot-manifest.json",
        *local_refs,
        "methods.md",
        "README.md",
        "bundle-manifest.json",
        "checksums.sha256",
    ]
    has_parts = list(dict.fromkeys(has_parts))

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
        "conformsTo": [{"@id": value} for value in manifest["conforms_to"]],
        "subjectOf": [
            {"@id": "methods.md"},
            {"@id": manifest["quality_report"]},
            {"@id": manifest["rights_inventory"]},
        ],
    }

    graph: list[dict[str, Any]] = [
        {
            "@id": "ro-crate-metadata.json",
            "@type": "CreativeWork",
            "about": {"@id": "./"},
            "conformsTo": {"@id": "https://w3id.org/ro/crate/1.3"},
        },
        root,
        {
            "@id": "#publisher",
            "@type": "Organization",
            "name": manifest["citation"]["publisher"],
        },
    ]

    for index, creator in enumerate(manifest["citation"]["creators"], start=1):
        graph.append({"@id": f"#creator-{index}", "@type": "Person", "name": creator})

    # Describe the copied metadata files themselves with actual package hashes.
    for relative in has_parts:
        actual = out / relative
        if actual.is_file():
            graph.append(_file_entity(relative, actual))

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

    for reference in manifest.get("artifacts", []):
        artifact = _load(_safe_source(base, reference))
        location = artifact.get("uri") or artifact.get("path")
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
                    {
                        "@type": "PropertyValue",
                        "name": "payload_status",
                        "value": artifact["payload_status"],
                    },
                    {
                        "@type": "PropertyValue",
                        "name": "verification_status",
                        "value": artifact["verification_status"],
                    },
                ],
            }
        )

    software_seen: set[str] = set()
    for reference in manifest.get("transformations", []):
        run = _load(_safe_source(base, reference))
        software_id = _software_id(run)
        if software_id not in software_seen:
            implementation = run["implementation"]
            graph.append(
                {
                    "@id": software_id,
                    "@type": "SoftwareSourceCode",
                    "name": implementation.get("package") or implementation["repository"],
                    "codeRepository": implementation["repository"],
                    "version": implementation.get("package_version"),
                    "identifier": [implementation["commit"]]
                    + ([implementation["swhid"]] if implementation.get("swhid") else []),
                }
            )
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
        graph.append(
            {
                "@id": item["materialization_id"],
                "@type": "Dataset",
                "name": f"{item['format']} materialisation",
                "encodingFormat": item["media_type"],
                "isBasedOn": {"@id": item["artifact_id"]},
                "creator": {"@id": item["generated_by"]},
                "mainEntityOfPage": {"@id": reference},
                "additionalProperty": {
                    "@type": "PropertyValue",
                    "name": "reproducibility_class",
                    "value": item.get("reproducibility_class"),
                },
            }
        )

    quality = _load(_safe_source(base, manifest["quality_report"]))
    graph.append(
        {
            "@id": quality["report_id"],
            "@type": "CreativeWork",
            "name": "RIOPA quality report",
            "about": {"@id": quality["subject_id"]},
            "dateCreated": quality["generated_at"],
            "mainEntityOfPage": {"@id": manifest["quality_report"]},
        }
    )
    rights = _load(_safe_source(base, manifest["rights_inventory"]))
    graph.append(
        {
            "@id": rights["inventory_id"],
            "@type": "CreativeWork",
            "name": "RIOPA rights inventory",
            "about": {"@id": rights["subject_id"]},
            "dateCreated": rights["generated_at"],
            "mainEntityOfPage": {"@id": manifest["rights_inventory"]},
        }
    )
    if manifest.get("methods_facts"):
        facts = _load(_safe_source(base, manifest["methods_facts"]))
        graph.append(
            {
                "@id": facts["methods_facts_id"],
                "@type": "CreativeWork",
                "name": "RIOPA machine-readable methods facts",
                "about": {"@id": facts["subject_id"]},
                "mainEntityOfPage": {"@id": manifest["methods_facts"]},
            }
        )

    crate = {
        "@context": "https://w3id.org/ro/crate/1.3/context",
        "@graph": graph,
    }
    path = out / "ro-crate-metadata.json"
    _write_json(path, crate)
    return path


def _research_object_readme(manifest: dict[str, Any]) -> str:
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
            "`bundle-manifest.json` and `checksums.sha256` verify the package files.",
            "",
            "Source rights and restrictions remain in `rights-inventory.json` and the "
            "source records. Presence in this package does not broaden source licences.",
            "",
        ]
    )


def build_research_object(
    manifest_path: str | Path,
    output_dir: str | Path,
    *,
    clean: bool = True,
) -> Path:
    """Build a deterministic, self-contained metadata research object.

    Referenced raw payloads are copied only when they are themselves manifest references.
    Artifact records may intentionally describe remote, restricted or not-bundled payloads.
    """

    manifest_file = Path(manifest_path).resolve()
    source_base = manifest_file.parent
    output = Path(output_dir).resolve()
    if output == source_base:
        raise ValueError("output directory must differ from the manifest directory")

    closure = validate_manifest_closure(manifest_file)
    if not closure.valid:
        raise ValueError("manifest closure failed: " + "; ".join(closure.errors))

    manifest = _load(manifest_file)
    if clean and output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)

    shutil.copy2(manifest_file, output / "snapshot-manifest.json")
    for reference in manifest_references(manifest):
        source = _safe_source(source_base, reference)
        destination = output / reference
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    (output / "methods.md").write_text(generate_methods_markdown(manifest_file), encoding="utf-8")
    (output / "README.md").write_text(_research_object_readme(manifest), encoding="utf-8")

    # Build RO-Crate after files exist so file entities can carry package hashes.
    build_ro_crate(manifest_file, output)

    files_for_manifest = sorted(
        path for path in output.rglob("*") if path.is_file() and path.name != "bundle-manifest.json"
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
    return output
