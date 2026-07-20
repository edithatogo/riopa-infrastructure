"""Generate publication-ready methods text from a snapshot manifest."""

from __future__ import annotations

import json
import shlex
from collections import Counter
from pathlib import Path
from typing import Any, cast


def _load(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _resolve(base: Path, ref: str) -> Path:
    path = Path(ref)
    return path if path.is_absolute() else base / path


def _display_doi(value: str | None) -> str:
    return value if value else "not yet assigned"


def _fact(facts: dict[str, Any], key: str, fallback: str) -> str:
    value = facts.get(key)
    return value if isinstance(value, str) and value.strip() else fallback


def _bullets(values: list[str], *, empty: str = "None recorded.") -> list[str]:
    return [f"- {value}" for value in values] or [f"- {empty}"]


def generate_methods_markdown(manifest_path: str | Path) -> str:
    """Generate a detailed methods supplement from a valid candidate manifest.

    The generator reports absent evidence explicitly. It never invents parameter values,
    licences, dates, quality results, legal status, computational environments or claims.
    """

    manifest_file = Path(manifest_path).resolve()
    base = manifest_file.parent
    manifest = _load(manifest_file)

    sources: list[dict[str, Any]] = []
    for entry in manifest["sources"]:
        source_record = _load(_resolve(base, entry["source_record"]))
        sources.append({"entry": entry, "record": source_record})

    artifacts = [_load(_resolve(base, ref)) for ref in manifest.get("artifacts", [])]
    events = [_load(_resolve(base, ref)) for ref in manifest.get("provenance_events", [])]
    transformations = [_load(_resolve(base, ref)) for ref in manifest.get("transformations", [])]
    materializations = [_load(_resolve(base, ref)) for ref in manifest.get("materializations", [])]
    quality = _load(_resolve(base, manifest["quality_report"]))
    rights = _load(_resolve(base, manifest["rights_inventory"]))
    facts = (
        _load(_resolve(base, manifest["methods_facts"])) if manifest.get("methods_facts") else {}
    )

    coverage = manifest.get("coverage", {})
    citation = manifest["citation"]
    source_dates = [item["record"]["discovered_at"] for item in sources]
    source_date_min = min(source_dates) if source_dates else "not recorded"
    source_date_max = max(source_dates) if source_dates else "not recorded"

    implementation_refs = []
    for run in transformations:
        impl = run["implementation"]
        ref = impl.get("swhid") or impl.get("commit")
        implementation_refs.append(f"{impl['repository']}@{ref}")

    quality_counts = Counter(result["status"] for result in quality["results"])
    quality_summary = (
        ", ".join(f"{count} {status}" for status, count in sorted(quality_counts.items()))
        or "no metric results"
    )

    rights_lines = []
    for item in rights.get("sources", []):
        restrictions = item.get("restrictions", [])
        rights_lines.append(
            f"- **{item['source_id']}** — redistribution: "
            f"`{item['redistribution_status']}`; licence status: "
            f"`{item['licence_status']}`; licence: "
            f"{item.get('licence') or item.get('spdx_or_uri') or 'not recorded'}; "
            f"reviewed: {item.get('reviewed_at') or 'not recorded'}; attribution: "
            f"{item.get('attribution') or 'not recorded'}; restrictions: "
            f"{'; '.join(restrictions) if restrictions else 'none declared'}."
        )

    source_lines = []
    for item in sources:
        record = item["record"]
        entry = item["entry"]
        source_lines.append(
            f"- **{record['name']}** (`{record['source_id']}`), published by "
            f"{record['publisher']['name']}; source class: `{record['source_type']}`; "
            f"authoritativeness: `{record.get('authoritativeness', 'not recorded')}`; "
            f"access mechanism: {record['access']['mechanism']}; "
            f"declared captures: {len(entry['capture_ids'])}; redistribution status: "
            f"`{record['rights']['redistribution_status']}`."
        )

    artifact_lines = []
    for artifact in artifacts:
        location = artifact.get("path") or artifact.get("uri") or "not recorded"
        artifact_lines.append(
            f"- `{artifact['artifact_id']}` — {artifact['media_type']}, "
            f"{artifact['size_bytes']} bytes, SHA-256 `{artifact['sha256']}`, "
            f"payload status `{artifact['payload_status']}`, verification "
            f"`{artifact['verification_status']}`, location `{location}`."
        )

    run_lines = []
    for run in transformations:
        impl = run["implementation"]
        environment = run.get("environment", {})
        run_lines.append(
            f"- `{run['run_id']}`: `{run['run_type']}` using "
            f"`{impl['repository']}@{impl['commit']}`; command "
            f"`{shlex.join(run['invocation']['command'])}`; parameters "
            f"`{json.dumps(run['invocation']['parameters'], sort_keys=True, ensure_ascii=False)}`; "
            f"determinism `{run['determinism']['class']}`; container digest "
            f"`{environment.get('container_digest') or 'not recorded'}`; lockfile digest "
            f"`{environment.get('lockfile_sha256') or 'not recorded'}`."
        )

    event_lines = []
    for event in events:
        event_lines.append(
            f"- sequence {event['sequence']}: `{event['event_type']}` "
            f"(`{event['status']}`), event `{event['event_id']}`, "
            f"recorded {event['recorded_at']}, hash `{event['event_hash']}`, "
            f"previous `{event.get('previous_event_hash') or 'GENESIS'}`."
        )

    materialization_lines = []
    for item in materializations:
        losses = item["fidelity"].get("losses", [])
        materialization_lines.append(
            f"- `{item['format']}` (`{item['materialization_id']}`), purpose: "
            f"{item['fidelity']['purpose']}; artifact: `{item['artifact_id']}`; "
            f"generated by `{item['generated_by']}`; reproducibility: "
            f"`{item.get('reproducibility_class', 'not recorded')}`; known losses: "
            f"{'; '.join(losses) if losses else 'none declared'}."
        )

    implementation_summary = (
        ", ".join(implementation_refs) if implementation_refs else "no declared transformation"
    )
    sentence = (
        f"We used RIOPA dataset snapshot `{manifest['snapshot_id']}` "
        f"(version `{manifest['snapshot_version']}`, DOI {_display_doi(citation.get('doi'))}), "
        f"assembled from {len(sources)} declared source(s) and {len(artifacts)} artifact "
        f"record(s), transformed using {implementation_summary}, and released with a "
        f"{len(events)}-event hash-linked provenance stream, source-level rights review, "
        f"quality evidence, canonical manifest hash `{manifest['manifest_sha256']}`, and "
        "machine-generated methods metadata."
    )

    event_window = (
        f"{events[0]['recorded_at']} to {events[-1]['recorded_at']}" if events else "not recorded"
    )
    artifact_status = Counter(artifact["payload_status"] for artifact in artifacts)
    artifact_status_text = (
        ", ".join(f"{count} {status}" for status, count in sorted(artifact_status.items()))
        or "none"
    )

    return "\n".join(
        [
            f"# Methods: {manifest['title']}",
            "",
            "> Generated from machine-readable release evidence. Exact identifiers, "
            "versions, dates, parameters, hashes, rights decisions and counts must be changed "
            "in the source records rather than edited only in this document.",
            "",
            "## Citable methods statement",
            "",
            sentence,
            "",
            "## Study scope and design",
            "",
            manifest.get("description", "No description was recorded."),
            "",
            "## Data sources",
            "",
            *source_lines,
            "",
            f"Source-discovery records span {source_date_min} to {source_date_max}.",
            "",
            "## Acquisition and archival capture",
            "",
            _fact(
                facts,
                "acquisition",
                "Acquisition details were not supplied beyond the source and capture records.",
            ),
            "",
            "## Inclusion, exclusion and missing-data handling",
            "",
            _fact(
                facts, "exclusions", "No explicit inclusion or exclusion statement was recorded."
            ),
            "",
            _fact(facts, "missing_data", "No explicit missing-data statement was recorded."),
            "",
            "## Harmonisation and transformation",
            "",
            _fact(facts, "harmonisation", "No additional harmonisation statement was recorded."),
            "",
            *run_lines,
            "",
            "## Spatial and temporal handling",
            "",
            f"Spatial coverage: {coverage.get('spatial') or 'not recorded'}. "
            f"Valid-time coverage: {coverage.get('valid_time_from') or 'not recorded'} to "
            f"{coverage.get('valid_time_to') or 'not recorded'}. Retrieval-time coverage: "
            f"{coverage.get('retrieval_time_from') or 'not recorded'} to "
            f"{coverage.get('retrieval_time_to') or 'not recorded'}.",
            "",
            _fact(
                facts, "spatial_handling", "No additional spatial-handling statement was recorded."
            ),
            "",
            _fact(
                facts,
                "temporal_handling",
                "No additional temporal-handling statement was recorded.",
            ),
            "",
            "## Artifacts and materialisations",
            "",
            f"Artifact payload status summary: {artifact_status_text}.",
            "",
            *artifact_lines,
            "",
            *materialization_lines,
            "",
            "## Provenance and integrity",
            "",
            f"The declared event stream covers {event_window}. Events are ordered by sequence "
            "and linked through canonical SHA-256 hashes. The snapshot manifest is hashed after "
            "omitting its own `manifest_sha256` field.",
            "",
            *event_lines,
            "",
            "## Quality assurance",
            "",
            f"Overall quality status: **{quality['overall_status']}** ({quality_summary}).",
            "",
            _fact(facts, "quality_notes", "No additional quality notes were recorded."),
            "",
            "## Rights, ethics, governance and privacy",
            "",
            f"Publication decision: **{rights['publication_decision']}**.",
            "",
            *rights_lines,
            "",
            _fact(
                facts,
                "governance",
                "No additional governance statement was recorded; source-level rights still apply.",
            ),
            "",
            _fact(facts, "privacy", "No explicit privacy statement was recorded."),
            "",
            "## Computational reproducibility",
            "",
            _fact(
                facts,
                "reproducibility",
                "The release records code identity, environment, inputs, outputs and quality "
                "evidence; achieved reproducibility is reported per materialisation.",
            ),
            "",
            _fact(
                facts,
                "software_hardware",
                "No additional software or hardware statement was recorded.",
            ),
            "",
            _fact(facts, "stochasticity", "No stochasticity statement was recorded."),
            "",
            "## AI assistance",
            "",
            _fact(facts, "ai_assistance", "No AI-assistance statement was recorded."),
            "",
            "## Deviations from the declared protocol",
            "",
            *_bullets(facts.get("deviations", [])),
            "",
            "## Limitations",
            "",
            *_bullets(facts.get("limitations", [])),
            "",
            "## Availability and citation",
            "",
            f"Repository: {citation.get('repository') or 'not recorded'}. "
            f"Publisher: {citation['publisher']}. Publication year: "
            f"{citation['publication_year']}. DOI: {_display_doi(citation.get('doi'))}. "
            f"Licence statement: {citation.get('licence') or 'not recorded'}.",
            "",
            f"Conforms to: {', '.join(manifest['conforms_to'])}.",
            "",
        ]
    )
