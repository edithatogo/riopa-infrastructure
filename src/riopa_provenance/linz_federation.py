"""Deterministic GitHub, Hugging Face and Zenodo federation for all LINZ items.

GitHub is the code and control plane, Hugging Face is the living versioned
analytical mirror, and Zenodo is the immutable reviewed preservation/citation
layer.  This module only constructs and verifies staging artifacts; it never
uses remote credentials or publishes by itself.
"""

from __future__ import annotations

import json
import shutil
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .hashing import sha256_file, sha256_json
from .linz_catalog import load_catalog_items
from .linz_inventory import load_archive_plan
from .yaml_tools import load_yaml


class LinzFederationError(RuntimeError):
    """Raised when publication federation would omit or misbind catalogue items."""


@dataclass(frozen=True)
class LinzFederationStage:
    """Paths and counts produced by a deterministic federation stage."""

    root: Path
    manifest_path: Path
    item_count: int
    family_count: int
    github_path: Path
    hugging_face_path: Path
    zenodo_path: Path


def load_federation_policy(path: str | Path) -> dict[str, Any]:
    """Load and minimally validate a federation policy."""

    source = Path(path)
    text = source.read_text(encoding="utf-8")
    value = load_yaml(text) if source.suffix.lower() in {".yaml", ".yml"} else json.loads(text)
    if not isinstance(value, dict):
        raise LinzFederationError("federation policy root must be an object")
    required = {
        "schema_version",
        "policy_id",
        "policy_version",
        "repositories",
        "families",
        "fallback",
    }
    missing = sorted(required - set(value))
    if missing:
        raise LinzFederationError(f"federation policy is missing: {missing}")
    if value["schema_version"] != "1.0.0":
        raise LinzFederationError("federation policy schema_version must be 1.0.0")
    repositories = value.get("repositories")
    if not isinstance(repositories, Mapping):
        raise LinzFederationError("federation policy repositories must be an object")
    for key in ("github_control_plane", "hugging_face_umbrella", "zenodo_concept"):
        if not isinstance(repositories.get(key), str) or not repositories[key]:
            raise LinzFederationError(f"federation policy has no {key}")
    families = value.get("families")
    if not isinstance(families, list) or not families:
        raise LinzFederationError("federation policy requires at least one family")
    family_ids: set[str] = set()
    repositories_seen: set[str] = set()
    for family in families:
        if not isinstance(family, Mapping):
            raise LinzFederationError("every federation family must be an object")
        family_id = str(family.get("id") or "")
        repository = str(family.get("repository") or "")
        if not family_id or not repository:
            raise LinzFederationError("every federation family requires id and repository")
        if family_id in family_ids:
            raise LinzFederationError(f"duplicate federation family id: {family_id}")
        if repository in repositories_seen:
            raise LinzFederationError(f"duplicate federation repository: {repository}")
        family_ids.add(family_id)
        repositories_seen.add(repository)
    fallback = value.get("fallback")
    if (
        not isinstance(fallback, Mapping)
        or not fallback.get("id")
        or not fallback.get("repository")
    ):
        raise LinzFederationError("federation policy fallback requires id and repository")
    return value


def _search_text(item: Mapping[str, Any]) -> str:
    """Build a conservative searchable text projection from one catalogue item."""

    values: list[str] = []
    for key in ("name", "item_type", "kind"):
        value = item.get(key)
        if value is not None:
            values.append(str(value))
    for key in ("categories", "tags"):
        value = item.get(key)
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            values.extend(str(entry) for entry in value)
    raw = item.get("raw")
    if isinstance(raw, Mapping):
        for key in ("name", "title", "description", "kind"):
            value = raw.get(key)
            if isinstance(value, str):
                values.append(value)
    return " ".join(values).casefold()


def classify_family(item: Mapping[str, Any], policy: Mapping[str, Any]) -> tuple[str, str]:
    """Assign one deterministic data family, retaining a visible fallback."""

    text = _search_text(item)
    for family in policy["families"]:
        terms = [str(term).casefold() for term in family.get("match_any", [])]
        if terms and any(term in text for term in terms):
            return str(family["id"]), str(family["repository"])
    fallback = policy["fallback"]
    return str(fallback["id"]), str(fallback["repository"])


def _load_snapshot_manifest(path: str | Path) -> dict[str, Any]:
    source = Path(path).resolve()
    value = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("record_type") not in {
        "linz_catalog_snapshot",
        "linz_catalog_enriched_snapshot",
    }:
        raise LinzFederationError("not a LINZ catalogue snapshot manifest")
    expected = sha256_json(value, omit_keys={"manifest_sha256"})
    if value.get("manifest_sha256") != expected:
        raise LinzFederationError("LINZ catalogue snapshot manifest hash mismatch")
    for label in ("items", "csv"):
        descriptor = value.get(label)
        if not isinstance(descriptor, Mapping) or not isinstance(descriptor.get("path"), str):
            raise LinzFederationError(f"LINZ catalogue snapshot has no {label} file")
        candidate = (source.parent / str(descriptor["path"])).resolve()
        try:
            candidate.relative_to(source.parent)
        except ValueError as exc:
            raise LinzFederationError(f"catalogue {label} path escapes snapshot root") from exc
        if not candidate.is_file():
            raise LinzFederationError(f"catalogue {label} file is missing: {candidate}")
        if sha256_file(candidate) != descriptor.get("sha256"):
            raise LinzFederationError(f"catalogue {label} file hash mismatch")
        if candidate.stat().st_size != descriptor.get("size_bytes"):
            raise LinzFederationError(f"catalogue {label} file size mismatch")
    return value


def build_federation_manifest(
    catalog_snapshot_manifest: str | Path,
    archive_plan_path: str | Path,
    federation_policy_path: str | Path,
    output_path: str | Path,
    *,
    created_at: str,
) -> Path:
    """Bind every catalogue item to GitHub, Hugging Face and Zenodo topology."""

    snapshot_path = Path(catalog_snapshot_manifest).resolve()
    snapshot = _load_snapshot_manifest(snapshot_path)
    items_path = snapshot_path.parent / snapshot["items"]["path"]
    items = load_catalog_items(items_path)
    plan = load_archive_plan(archive_plan_path)
    policy = load_federation_policy(federation_policy_path)

    completeness = snapshot.get("completeness")
    if not isinstance(completeness, Mapping) or not completeness.get(
        "unfiltered_published_catalogue"
    ):
        raise LinzFederationError(
            "publication federation requires an unfiltered published-catalogue snapshot"
        )
    scope = plan.get("scope")
    if not isinstance(scope, Mapping) or not scope.get("catalogue_complete"):
        raise LinzFederationError(
            "publication federation requires an archive plan with catalogue_complete=true"
        )
    if plan.get("catalog_snapshot_id") != snapshot.get("snapshot_id"):
        raise LinzFederationError("archive plan targets a different catalogue snapshot")
    if plan.get("catalog_items_sha256") != snapshot["items"]["sha256"]:
        raise LinzFederationError("archive plan is bound to different catalogue items")

    item_by_id = {str(item["catalog_item_id"]): item for item in items}
    dispositions = plan.get("dispositions")
    if not isinstance(dispositions, list):
        raise LinzFederationError("archive plan has no dispositions")
    disposition_by_id: dict[str, Mapping[str, Any]] = {}
    for disposition in dispositions:
        if not isinstance(disposition, Mapping):
            raise LinzFederationError("archive disposition is not an object")
        identifier = str(disposition.get("catalog_item_id") or "")
        if not identifier or identifier in disposition_by_id:
            raise LinzFederationError(
                f"duplicate or empty archive disposition identity: {identifier}"
            )
        disposition_by_id[identifier] = disposition
    if set(item_by_id) != set(disposition_by_id):
        missing = sorted(set(item_by_id) - set(disposition_by_id))
        extra = sorted(set(disposition_by_id) - set(item_by_id))
        raise LinzFederationError(
            f"catalogue/archive-plan identity mismatch; missing={missing[:5]}, extra={extra[:5]}"
        )

    assignments: list[dict[str, Any]] = []
    family_counts: Counter[str] = Counter()
    family_repositories: dict[str, str] = {}
    for identifier in sorted(item_by_id):
        family_id, repository = classify_family(item_by_id[identifier], policy)
        disposition = disposition_by_id[identifier]
        family_counts[family_id] += 1
        family_repositories[family_id] = repository
        assignments.append(
            {
                "catalog_item_id": identifier,
                "family_id": family_id,
                "hugging_face_repository": repository,
                "strategy": disposition["strategy"],
                "payload_status": disposition["payload_status"],
            }
        )

    repositories = policy["repositories"]
    living_datasets = [
        {
            "family_id": "catalogue-and-coverage",
            "kind": "hugging-face-dataset",
            "repository": repositories["hugging_face_umbrella"],
            "scope": (
                "complete catalogue, source registry, plans, coverage, manifests "
                "and latest pointers"
            ),
            "contents": [
                "catalogue snapshots and diffs",
                "archive dispositions and exceptions",
                "rights and source registries",
                "family crosswalk and release manifests",
            ],
            "publication_status": "planned",
            "revision": None,
        }
    ]
    for family_id in sorted(family_counts):
        living_datasets.append(
            {
                "family_id": family_id,
                "kind": "hugging-face-dataset",
                "repository": family_repositories[family_id],
                "scope": f"living canonical and archived payload representations for {family_id}",
                "contents": [
                    "catalogue subset",
                    "archive dispositions",
                    "canonical payloads where rights and capability permit",
                    "checksums, provenance and quality reports",
                ],
                "publication_status": "planned",
                "revision": None,
            }
        )

    seed = {
        "snapshot_id": snapshot["snapshot_id"],
        "plan_id": plan["plan_id"],
        "policy_id": policy["policy_id"],
        "policy_version": policy["policy_version"],
        "assignments": assignments,
    }
    manifest: dict[str, Any] = {
        "schema_version": "1.0.0",
        "record_type": "linz_federation_manifest",
        "federation_id": f"urn:riopa:linz-federation:{sha256_json(seed)}",
        "catalog_snapshot_id": snapshot["snapshot_id"],
        "archive_plan_id": plan["plan_id"],
        "created_at": created_at,
        "policy": {
            "policy_id": policy["policy_id"],
            "policy_version": policy["policy_version"],
            "catalogue_completeness_required": True,
            "payload_rights_aware": True,
            "no_silent_omission": True,
            "planning_inputs_complete": bool(scope.get("planning_inputs_complete")),
            "payload_execution_requires_planning_inputs_complete": True,
            "github_role": policy["publication"]["github_role"],
            "hugging_face_role": policy["publication"]["hugging_face_role"],
            "zenodo_role": policy["publication"]["zenodo_role"],
        },
        "control_plane": {
            "kind": "github",
            "repository": repositories["github_control_plane"],
            "contents": [
                "connectors and orchestration",
                "source and rights registries",
                "Conductor tracks and issue graph",
                "schemas, tests and release manifests",
                "small fixtures but not bulk GIS payloads",
            ],
        },
        "living_datasets": living_datasets,
        "preservation": {
            "kind": "zenodo",
            "concept": repositories["zenodo_concept"],
            "concept_doi": None,
            "version_doi": None,
            "deposit_mode": policy["publication"]["zenodo_deposit_mode"],
            "contents": [
                "immutable catalogue and archive-plan snapshot",
                "release and family manifests",
                "canonical data or content-addressed references according to rights and size",
                "quality, provenance, methods, checksums and citation metadata",
            ],
            "publication_status": "planned",
        },
        "family_assignments": assignments,
        "coverage": {
            "catalogue_item_count": len(items),
            "assigned_item_count": len(assignments),
            "unassigned_item_count": len(items) - len(assignments),
            "families": dict(sorted(family_counts.items())),
            "archive_payload_status": plan["coverage"]["by_payload_status"],
            "archive_strategy": plan["coverage"]["by_strategy"],
            "planning_inputs_complete": bool(scope.get("planning_inputs_complete")),
        },
        "manifest_sha256": "",
    }
    manifest["manifest_sha256"] = sha256_json(manifest, omit_keys={"manifest_sha256"})
    destination = Path(output_path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destination


def _write_jsonl(path: Path, records: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records
    )
    path.write_text(payload, encoding="utf-8")


def _dataset_card(
    *,
    title: str,
    scope: str,
    snapshot_id: str,
    item_count: int,
    catalogue_complete: bool,
    payload_note: str,
) -> str:
    completeness = "yes" if catalogue_complete else "no; this is a documented family subset"
    return "\n".join(
        [
            "---",
            f"pretty_name: {json.dumps(title, ensure_ascii=False)}",
            "license: other",
            "task_categories:",
            "- other",
            "language:",
            "- en",
            "tags:",
            "- geospatial",
            "- new-zealand",
            "- provenance",
            "---",
            "",
            f"# {title}",
            "",
            scope,
            "",
            "## Release identity",
            "",
            f"- Catalogue snapshot: `{snapshot_id}`",
            f"- Catalogue entries represented here: **{item_count}**",
            f"- Catalogue-complete snapshot: **{completeness}**",
            "",
            "## Completeness and rights",
            "",
            (
                "The umbrella catalogue represents every item discovered in the captured "
                "LINZ Data Service catalogue. Payload completeness is reported "
                f"separately. {payload_note}"
            ),
            "",
            (
                "No missing, rights-uncertain, externally referenced, unsupported, or "
                "oversized item is silently removed from coverage: each has an explicit "
                "disposition in `archive-plan.json` or the family subset."
            ),
            "",
            "## Repository roles",
            "",
            (
                "- GitHub contains connector code, source definitions, schemas, tests, "
                "automation and release manifests."
            ),
            (
                "- Hugging Face contains the living, versioned analytical catalogue and "
                "permitted canonical payloads."
            ),
            (
                "- Zenodo contains reviewed immutable snapshots, citation metadata, "
                "checksums and preservation evidence."
            ),
            "",
            "## Reproducibility",
            "",
            (
                "Use the content hashes and identifiers in `federation-manifest.json`, "
                "`catalog-snapshot.manifest.json`, `archive-plan.json` and "
                "`checksums.sha256`. A Hugging Face revision or Zenodo DOI is recorded "
                "only after remote publication and verification."
            ),
            "",
        ]
    )


def _json_text(value: Any) -> str | None:
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _analytical_rows(
    items: Sequence[Mapping[str, Any]],
    dispositions: Mapping[str, Mapping[str, Any]],
    assignments: Mapping[str, Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    catalogue_rows: list[dict[str, Any]] = []
    disposition_rows: list[dict[str, Any]] = []
    for item in sorted(items, key=lambda value: str(value["catalog_item_id"])):
        identifier = str(item["catalog_item_id"])
        disposition = dispositions[identifier]
        assignment = assignments[identifier]
        catalogue_rows.append(
            {
                "catalog_item_id": identifier,
                "source_catalog_id": str(item.get("source_catalog_id") or ""),
                "item_type": item.get("item_type"),
                "kind": item.get("kind"),
                "name": item.get("name"),
                "url": item.get("url"),
                "url_html": item.get("url_html"),
                "first_published_at": item.get("first_published_at"),
                "published_at": item.get("published_at"),
                "updated_at": item.get("updated_at"),
                "raw_sha256": item.get("raw_sha256"),
                "detail_status": item.get("detail_status"),
                "service_status": item.get("service_status"),
                "family_id": assignment.get("family_id"),
                "hugging_face_repository": assignment.get("hugging_face_repository"),
                "license_json": _json_text(item.get("license")),
                "categories_json": _json_text(item.get("categories")),
                "tags_json": _json_text(item.get("tags")),
                "services_json": _json_text(item.get("services")),
                "raw_json": _json_text(item.get("raw")),
            }
        )
        disposition_rows.append(
            {
                "catalog_item_id": identifier,
                "rule_id": disposition.get("rule_id"),
                "strategy": disposition.get("strategy"),
                "tier": disposition.get("tier"),
                "priority": disposition.get("priority"),
                "cadence": disposition.get("cadence"),
                "rights_disposition": disposition.get("rights_disposition"),
                "payload_status": disposition.get("payload_status"),
                "estimated_size_bytes": disposition.get("estimated_size_bytes"),
                "job_key": disposition.get("job_key"),
                "format_profile": disposition.get("format_profile"),
                "export_crs": disposition.get("export_crs"),
                "automatic_export_limit_bytes": disposition.get("automatic_export_limit_bytes"),
                "payload_methods_json": _json_text(disposition.get("payload_methods")),
                "format_preferences_json": _json_text(disposition.get("format_preferences")),
                "destinations_json": _json_text(disposition.get("destinations")),
                "services_json": _json_text(disposition.get("services")),
                "blockers_json": _json_text(disposition.get("blockers")),
            }
        )
    return catalogue_rows, disposition_rows


def _write_analytical_bundle(
    root: Path,
    *,
    items: Sequence[Mapping[str, Any]],
    dispositions: Mapping[str, Mapping[str, Any]],
    assignments: Mapping[str, Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Write portable Parquet plus a self-contained DuckDB analytical bundle."""

    try:
        import duckdb
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError as exc:  # pragma: no cover - exercised by minimal installs
        raise LinzFederationError(
            "federation analytical outputs require the 'spatial' optional dependency"
        ) from exc

    catalogue_rows, disposition_rows = _analytical_rows(items, dispositions, assignments)
    catalogue_path = root / "catalogue-index.parquet"
    disposition_path = root / "archive-dispositions.parquet"
    pq.write_table(
        pa.Table.from_pylist(catalogue_rows),
        catalogue_path,
        compression="zstd",
        use_dictionary=True,
        write_statistics=True,
    )
    pq.write_table(
        pa.Table.from_pylist(disposition_rows),
        disposition_path,
        compression="zstd",
        use_dictionary=True,
        write_statistics=True,
    )
    database_path = root / "nz-spatial-archive.duckdb"
    connection = duckdb.connect(str(database_path))
    try:
        connection.execute(
            "CREATE TABLE catalogue AS SELECT * FROM read_parquet(?)", [str(catalogue_path)]
        )
        connection.execute(
            "CREATE TABLE archive_dispositions AS SELECT * FROM read_parquet(?)",
            [str(disposition_path)],
        )
        connection.execute(
            "CREATE VIEW archive_coverage AS "
            "SELECT payload_status, strategy, count(*) AS item_count "
            "FROM archive_dispositions GROUP BY ALL ORDER BY ALL"
        )
        connection.execute("CHECKPOINT")
    finally:
        connection.close()
    return {
        "catalogue_parquet": {
            "path": catalogue_path.name,
            "sha256": sha256_file(catalogue_path),
            "size_bytes": catalogue_path.stat().st_size,
        },
        "dispositions_parquet": {
            "path": disposition_path.name,
            "sha256": sha256_file(disposition_path),
            "size_bytes": disposition_path.stat().st_size,
        },
        "duckdb": {
            "path": database_path.name,
            "sha256": sha256_file(database_path),
            "size_bytes": database_path.stat().st_size,
        },
    }


def _write_publication_crosswalk(
    path: Path,
    *,
    federation_id: str,
    snapshot_id: str,
    archive_plan_id: str,
    github_repository: str,
    hugging_face_repository: str,
    zenodo_concept: str,
) -> None:
    document = {
        "schema_version": "1.0.0",
        "record_type": "linz_publication_crosswalk",
        "federation_id": federation_id,
        "catalog_snapshot_id": snapshot_id,
        "archive_plan_id": archive_plan_id,
        "github": {
            "repository": github_repository,
            "commit": None,
            "release": None,
        },
        "hugging_face": {
            "repository": hugging_face_repository,
            "revision": None,
        },
        "zenodo": {
            "concept": zenodo_concept,
            "concept_doi": None,
            "version_doi": None,
            "record_id": None,
        },
        "remote_publication_performed": False,
        "crosswalk_sha256": "",
    }
    document["crosswalk_sha256"] = sha256_json(document, omit_keys={"crosswalk_sha256"})
    path.write_text(
        json.dumps(document, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_checksums(root: Path) -> Path:
    files = sorted(
        path for path in root.rglob("*") if path.is_file() and path.name != "checksums.sha256"
    )
    lines = [f"{sha256_file(path)}  {path.relative_to(root).as_posix()}" for path in files]
    destination = root / "checksums.sha256"
    destination.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return destination


def stage_federation(
    catalog_snapshot_manifest: str | Path,
    archive_plan_path: str | Path,
    federation_manifest_path: str | Path,
    output_dir: str | Path,
    *,
    source_registry_path: str | Path | None = None,
    archive_policy_path: str | Path | None = None,
    federation_policy_path: str | Path | None = None,
) -> LinzFederationStage:
    """Stage deterministic target layouts without contacting remote services."""

    snapshot_path = Path(catalog_snapshot_manifest).resolve()
    snapshot = _load_snapshot_manifest(snapshot_path)
    items_path = snapshot_path.parent / snapshot["items"]["path"]
    csv_path = snapshot_path.parent / snapshot["csv"]["path"]
    items = load_catalog_items(items_path)
    item_by_id = {str(item["catalog_item_id"]): item for item in items}
    plan = load_archive_plan(archive_plan_path)
    dispositions_by_id = {
        str(item["catalog_item_id"]): item for item in plan.get("dispositions", [])
    }
    federation = json.loads(Path(federation_manifest_path).read_text(encoding="utf-8"))
    if (
        not isinstance(federation, dict)
        or federation.get("record_type") != "linz_federation_manifest"
    ):
        raise LinzFederationError("not a LINZ federation manifest")
    expected = sha256_json(federation, omit_keys={"manifest_sha256"})
    if federation.get("manifest_sha256") != expected:
        raise LinzFederationError("LINZ federation manifest hash mismatch")
    if federation.get("catalog_snapshot_id") != snapshot.get("snapshot_id"):
        raise LinzFederationError("federation manifest targets a different catalogue snapshot")
    if federation.get("archive_plan_id") != plan.get("plan_id"):
        raise LinzFederationError("federation manifest targets a different archive plan")
    assignment_by_id = {
        str(item["catalog_item_id"]): item for item in federation.get("family_assignments", [])
    }
    if set(item_by_id) != set(dispositions_by_id) or set(item_by_id) != set(assignment_by_id):
        raise LinzFederationError("staging inputs do not cover the same catalogue identities")
    planning_inputs_complete = bool(
        isinstance(plan.get("scope"), Mapping)
        and plan["scope"].get("planning_inputs_complete") is True
    )

    output = Path(output_dir).resolve()
    if output.exists():
        shutil.rmtree(output)
    github = output / "github"
    hugging_face = output / "hugging-face"
    zenodo = output / "zenodo"
    for directory in (github, hugging_face, zenodo):
        directory.mkdir(parents=True, exist_ok=True)

    common = {
        "catalog-snapshot.manifest.json": snapshot_path,
        "catalog-items.jsonl": items_path,
        "catalog-items.csv": csv_path,
        "archive-plan.json": Path(archive_plan_path).resolve(),
        "federation-manifest.json": Path(federation_manifest_path).resolve(),
    }
    for _name, source in common.items():
        if not source.is_file():
            raise LinzFederationError(f"federation input is missing: {source}")

    # GitHub is intentionally metadata/code-oriented; bulk payloads belong in data stores.
    control = github / "control-plane"
    control.mkdir(parents=True)
    for name in ("catalog-snapshot.manifest.json", "archive-plan.json", "federation-manifest.json"):
        shutil.copy2(common[name], control / name)
    for optional in (source_registry_path, archive_policy_path, federation_policy_path):
        if optional is not None:
            source = Path(optional).resolve()
            if not source.is_file():
                raise LinzFederationError(f"control-plane input is missing: {source}")
            shutil.copy2(source, control / source.name)
    umbrella_repository = next(
        dataset["repository"]
        for dataset in federation["living_datasets"]
        if dataset["family_id"] == "catalogue-and-coverage"
    )
    _write_publication_crosswalk(
        control / "publication-crosswalk.json",
        federation_id=federation["federation_id"],
        snapshot_id=snapshot["snapshot_id"],
        archive_plan_id=plan["plan_id"],
        github_repository=federation["control_plane"]["repository"],
        hugging_face_repository=umbrella_repository,
        zenodo_concept=federation["preservation"]["concept"],
    )
    (control / "README.md").write_text(
        _dataset_card(
            title="NZ Spatial Archive — LINZ control plane",
            scope=(
                "This staging area contains the content-bound control records for a "
                "catalogue-complete LINZ archival release."
            ),
            snapshot_id=snapshot["snapshot_id"],
            item_count=len(items),
            catalogue_complete=True,
            payload_note=(
                "Bulk source and canonical GIS payloads are deliberately excluded from "
                "the GitHub control plane."
            ),
        ),
        encoding="utf-8",
    )
    _write_checksums(control)

    umbrella = hugging_face / umbrella_repository.replace("/", "__")
    umbrella.mkdir(parents=True)
    for name, source in common.items():
        shutil.copy2(source, umbrella / name)
    umbrella_analytics = _write_analytical_bundle(
        umbrella,
        items=items,
        dispositions=dispositions_by_id,
        assignments=assignment_by_id,
    )
    _write_publication_crosswalk(
        umbrella / "publication-crosswalk.json",
        federation_id=federation["federation_id"],
        snapshot_id=snapshot["snapshot_id"],
        archive_plan_id=plan["plan_id"],
        github_repository=federation["control_plane"]["repository"],
        hugging_face_repository=umbrella_repository,
        zenodo_concept=federation["preservation"]["concept"],
    )
    (umbrella / "dataset-metadata.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "dataset_kind": "living-catalogue-and-coverage",
                "catalog_snapshot_id": snapshot["snapshot_id"],
                "catalogue_complete": True,
                "planning_inputs_complete": planning_inputs_complete,
                "payload_complete": bool(plan["scope"].get("payload_complete")),
                "item_count": len(items),
                "analytical_outputs": umbrella_analytics,
                "rights": "mixed-source-specific-see-archive-plan",
            },
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (umbrella / "README.md").write_text(
        _dataset_card(
            title="NZ Spatial Archive — complete LINZ catalogue",
            scope=(
                "A living, versioned catalogue, coverage registry and archival disposition "
                "for every entry captured from the LINZ Data Service catalogue."
            ),
            snapshot_id=snapshot["snapshot_id"],
            item_count=len(items),
            catalogue_complete=True,
            payload_note=(
                "Payload mirrors may be distributed across family repositories and may "
                "remain metadata-only where rights, capability, cost or size prevents "
                "redistribution."
            ),
        ),
        encoding="utf-8",
    )
    _write_checksums(umbrella)

    assignments_by_family: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for assignment in federation["family_assignments"]:
        assignments_by_family[str(assignment["family_id"])].append(assignment)
    datasets_by_family = {str(item["family_id"]): item for item in federation["living_datasets"]}
    for family_id in sorted(assignments_by_family):
        dataset = datasets_by_family[family_id]
        family_root = hugging_face / str(dataset["repository"]).replace("/", "__")
        family_root.mkdir(parents=True)
        assignments = sorted(
            assignments_by_family[family_id], key=lambda item: str(item["catalog_item_id"])
        )
        identifiers = [str(item["catalog_item_id"]) for item in assignments]
        family_items = [item_by_id[identifier] for identifier in identifiers]
        family_dispositions = [dispositions_by_id[identifier] for identifier in identifiers]
        _write_jsonl(family_root / "catalog-items.jsonl", family_items)
        _write_jsonl(family_root / "archive-dispositions.jsonl", family_dispositions)
        family_assignment_map = {str(item["catalog_item_id"]): item for item in assignments}
        family_disposition_map = {
            str(item["catalog_item_id"]): item for item in family_dispositions
        }
        family_analytics = _write_analytical_bundle(
            family_root,
            items=family_items,
            dispositions=family_disposition_map,
            assignments=family_assignment_map,
        )
        _write_publication_crosswalk(
            family_root / "publication-crosswalk.json",
            federation_id=federation["federation_id"],
            snapshot_id=snapshot["snapshot_id"],
            archive_plan_id=plan["plan_id"],
            github_repository=federation["control_plane"]["repository"],
            hugging_face_repository=str(dataset["repository"]),
            zenodo_concept=federation["preservation"]["concept"],
        )
        (family_root / "family-manifest.json").write_text(
            json.dumps(
                {
                    "schema_version": "1.0.0",
                    "family_id": family_id,
                    "repository": dataset["repository"],
                    "catalog_snapshot_id": snapshot["snapshot_id"],
                    "archive_plan_id": plan["plan_id"],
                    "item_count": len(family_items),
                    "catalog_item_ids": identifiers,
                    "planning_inputs_complete": planning_inputs_complete,
                    "analytical_outputs": family_analytics,
                },
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        (family_root / "README.md").write_text(
            _dataset_card(
                title=f"NZ LINZ archive — {family_id}",
                scope=str(dataset["scope"]),
                snapshot_id=snapshot["snapshot_id"],
                item_count=len(family_items),
                catalogue_complete=False,
                payload_note=(
                    "This family repository contains the catalogue subset and disposition "
                    "records now; permitted payload objects are added by idempotent "
                    "archive workers and remain bound to these identities and hashes."
                ),
            ),
            encoding="utf-8",
        )
        _write_checksums(family_root)

    # Zenodo receives a compact, immutable release object. Large payloads may be
    # content-addressed external components rather than duplicated blindly.
    release = zenodo / "linz-catalogue-release"
    release.mkdir(parents=True)
    for name, source in common.items():
        shutil.copy2(source, release / name)
    for name in (
        "catalogue-index.parquet",
        "archive-dispositions.parquet",
        "nz-spatial-archive.duckdb",
        "dataset-metadata.json",
    ):
        shutil.copy2(umbrella / name, release / name)
    _write_publication_crosswalk(
        release / "publication-crosswalk.json",
        federation_id=federation["federation_id"],
        snapshot_id=snapshot["snapshot_id"],
        archive_plan_id=plan["plan_id"],
        github_repository=federation["control_plane"]["repository"],
        hugging_face_repository=umbrella_repository,
        zenodo_concept=federation["preservation"]["concept"],
    )
    (release / "CITATION.cff").write_text(
        "cff-version: 1.2.0\n"
        "message: Cite the version DOI recorded after reviewed Zenodo publication.\n"
        "title: NZ Spatial Archive — LINZ catalogue release\n"
        "type: dataset\n"
        "authors:\n"
        "  - family-names: Mordaunt\n"
        "    given-names: Dylan\n",
        encoding="utf-8",
    )
    (release / "README.md").write_text(
        _dataset_card(
            title="NZ Spatial Archive — immutable LINZ catalogue release",
            scope=(
                "A DOI-ready preservation object binding the complete catalogue snapshot, "
                "archive plan, family topology and checksums."
            ),
            snapshot_id=snapshot["snapshot_id"],
            item_count=len(items),
            catalogue_complete=True,
            payload_note=(
                "Large payload deposits may be split into related versioned deposits while "
                "this release remains the authoritative catalogue and crosswalk."
            ),
        ),
        encoding="utf-8",
    )
    (release / "zenodo.json").write_text(
        json.dumps(
            {
                "title": "NZ Spatial Archive — LINZ catalogue release",
                "upload_type": "dataset",
                "description": (
                    "Catalogue-complete, rights-aware archival disposition for the "
                    "LINZ Data Service."
                ),
                "creators": [{"name": "Mordaunt, Dylan"}],
                "access_right": "open",
                "notes": "Payload rights are source-specific and recorded per catalogue item.",
                "keywords": [
                    "New Zealand",
                    "LINZ",
                    "geospatial",
                    "provenance",
                    "research data",
                ],
                "related_identifiers": [],
            },
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    _write_checksums(release)

    stage_manifest: dict[str, Any] = {
        "schema_version": "1.0.0",
        "record_type": "linz_federation_stage",
        "federation_id": federation["federation_id"],
        "catalog_snapshot_id": snapshot["snapshot_id"],
        "archive_plan_id": plan["plan_id"],
        "item_count": len(items),
        "family_count": len(assignments_by_family),
        "targets": {
            "github": {
                "path": github.relative_to(output).as_posix(),
                "sha256": sha256_file(control / "checksums.sha256"),
            },
            "hugging_face": {
                "path": hugging_face.relative_to(output).as_posix(),
                "repository_count": 1 + len(assignments_by_family),
                "umbrella_analytical_outputs": umbrella_analytics,
            },
            "zenodo": {
                "path": zenodo.relative_to(output).as_posix(),
                "sha256": sha256_file(release / "checksums.sha256"),
            },
        },
        "planning_inputs_complete": planning_inputs_complete,
        "remote_publication_performed": False,
        "stage_sha256": "",
    }
    stage_manifest["stage_sha256"] = sha256_json(stage_manifest, omit_keys={"stage_sha256"})
    stage_manifest_path = output / "federation-stage.manifest.json"
    stage_manifest_path.write_text(
        json.dumps(stage_manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return LinzFederationStage(
        root=output,
        manifest_path=stage_manifest_path,
        item_count=len(items),
        family_count=len(assignments_by_family),
        github_path=github,
        hugging_face_path=hugging_face,
        zenodo_path=zenodo,
    )
