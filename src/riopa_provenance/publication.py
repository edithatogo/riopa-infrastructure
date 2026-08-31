"""Rights-aware publication federation planning and deterministic staging.

This module never uploads by itself.  It produces a fail-closed, content-bound
plan and deterministic target staging directories suitable for separately
authenticated GitHub, Hugging Face, and Zenodo publisher jobs.
"""

from __future__ import annotations

import json
import mimetypes
import re
import shutil
from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any, cast

from .crate import verify_research_object
from .hashing import sha256_file, sha256_json
from .validation import load_json, resolve_local_reference, validate_instance


class PublicationError(ValueError):
    """Raised when a publication plan or stage violates release policy."""


def validate_correction_package(package: Mapping[str, Any] | None) -> tuple[str, ...]:
    """Validate a correction/supersession package without contacting targets."""
    if not isinstance(package, Mapping):
        return ("correction package must be an object",)
    errors: list[str] = []
    required_fields = (
        "evidence_id",
        "status",
        "correction_policy",
        "bounded_example",
        "required_correction_record_fields",
        "qualification",
    )
    errors.extend(
        f"missing correction package field: {field}"
        for field in required_fields
        if field not in package
    )
    policy = package.get("correction_policy")
    if isinstance(policy, Mapping):
        for field in ("immutable_predecessors", "successor_required", "silent_mutation_forbidden"):
            if policy.get(field) is not True:
                errors.append(f"correction policy must require {field}")
        if (
            not isinstance(policy.get("notification_targets"), list)
            or not policy["notification_targets"]
        ):
            errors.append("correction policy requires notification targets")
    example = package.get("bounded_example")
    if isinstance(example, Mapping):
        predecessor = example.get("predecessor")
        successor = example.get("successor")
        digest = re.compile(r"^[0-9a-f]{64}$")
        for label, record in (("predecessor", predecessor), ("successor", successor)):
            if not isinstance(record, Mapping):
                errors.append(f"bounded example requires {label}")
                continue
            if not isinstance(record.get("doi"), str) or not record["doi"].strip():
                errors.append(f"bounded example {label} requires an identifier")
            if not isinstance(record.get("sha256"), str) or not digest.fullmatch(record["sha256"]):
                errors.append(f"bounded example {label} requires a SHA-256 digest")
        if (
            isinstance(predecessor, Mapping)
            and isinstance(successor, Mapping)
            and predecessor.get("sha256") == successor.get("sha256")
        ):
            errors.append("successor digest must differ from predecessor digest")
    required = package.get("required_correction_record_fields")
    if not isinstance(required, list) or not required:
        errors.append("required correction record fields must be a non-empty array")
    return tuple(dict.fromkeys(errors))


DEFAULT_TARGETS: tuple[dict[str, Any], ...] = (
    {
        "target_id": "github",
        "kind": "github-release",
        "repository": "edithatogo/nz-spatial-archive",
        "required": True,
        "environment": "github-release",
        "identifier": None,
        "revision": None,
    },
    {
        "target_id": "hugging-face",
        "kind": "hugging-face-dataset",
        "repository": "edithatogo/nz-spatial-archive",
        "required": True,
        "environment": "hugging-face-publication",
        "identifier": None,
        "revision": None,
    },
    {
        "target_id": "zenodo",
        "kind": "zenodo-deposit",
        "repository": "NZ Spatial Archive",
        "required": True,
        "environment": "zenodo-publication",
        "identifier": None,
        "revision": None,
    },
)

_RIGHTS_TO_DECISION = {
    "open": "publish",
    "attribution-required": "publish",
    "share-alike": "publish",
    "metadata-only": "metadata-only",
    "local-only": "local-only",
    "prohibited": "withhold",
    "review-required": "review-required",
    "unknown": "review-required",
}

_GLOBAL_TO_DECISION = {
    "allowed": "publish",
    "allowed-with-attribution": "publish",
    "share-alike-required": "publish",
    "metadata-only": "metadata-only",
    "local-only": "local-only",
    "prohibited": "withhold",
    "review-required": "review-required",
    "mixed": "review-required",
}

_DECISION_PRECEDENCE = {
    "publish": 0,
    "metadata-only": 1,
    "local-only": 2,
    "withhold": 3,
    "review-required": 4,
}


def _media_type(path: Path) -> str | None:
    known = {
        ".parquet": "application/vnd.apache.parquet",
        ".duckdb": "application/vnd.duckdb",
        ".jsonld": "application/ld+json",
        ".cff": "text/yaml",
    }
    return known.get(path.suffix.lower()) or mimetypes.guess_type(path.name)[0]


def _most_restrictive(decisions: Sequence[str]) -> str:
    if not decisions:
        return "review-required"
    return max(decisions, key=_DECISION_PRECEDENCE.__getitem__)


def _narrow_decision(inherited: str, proposed: str, *, context: str) -> str:
    """Apply a reviewed decision without permitting it to widen inherited rights."""

    if _DECISION_PRECEDENCE[proposed] < _DECISION_PRECEDENCE[inherited]:
        raise PublicationError(
            f"{context} would widen inherited rights from {inherited} to {proposed}"
        )
    return _most_restrictive([inherited, proposed])


def _artifact_rights_decision(
    artifact: Mapping[str, Any] | None,
    source_ids: Sequence[str],
    rights_by_source: Mapping[str, Mapping[str, Any]],
    global_status: str,
) -> tuple[str, list[str], list[str]]:
    """Resolve rights from artifact override, sources, then global policy."""

    decisions: list[str] = []
    basis: list[str] = []
    attributions: list[str] = []
    override = artifact.get("rights_ref") if isinstance(artifact, Mapping) else None
    candidate_ids = [str(override)] if isinstance(override, str) and override else list(source_ids)
    if override:
        basis.append(f"Artifact rights_ref points to {override}.")
    for source_id in candidate_ids:
        record = rights_by_source.get(source_id)
        if record is None:
            decisions.append("review-required")
            basis.append(f"No rights record exists for source {source_id}.")
            continue
        status = str(record.get("redistribution_status", "unknown"))
        decisions.append(_RIGHTS_TO_DECISION.get(status, "review-required"))
        basis.append(f"Rights record {source_id} redistribution status is {status}.")
        attribution = record.get("attribution")
        if isinstance(attribution, str) and attribution:
            attributions.append(attribution)
    if not decisions:
        mapped = _GLOBAL_TO_DECISION.get(global_status, "review-required")
        decisions.append(mapped)
        basis.append(f"Global publication decision is {global_status}.")
    return _most_restrictive(decisions), basis, sorted(set(attributions))


def _load_object(path: Path) -> dict[str, Any]:
    value = load_json(path)
    if not isinstance(value, dict):
        raise PublicationError(f"expected JSON object in {path}")
    return value


def _plan_schema(root: Path) -> dict[str, Any]:
    candidates = [root / "schemas" / "publication-plan.schema.json"]
    candidates.extend(
        parent / "schemas" / "publication-plan.schema.json" for parent in root.parents
    )
    schema_path = next((candidate for candidate in candidates if candidate.is_file()), None)
    if schema_path is None:
        raise PublicationError("publication-plan.schema.json was not found")
    return _load_object(schema_path)


def _artifact_maps(
    root: Path, manifest: Mapping[str, Any]
) -> tuple[dict[str, dict[str, Any]], set[str]]:
    by_path: dict[str, dict[str, Any]] = {}
    source_ids: set[str] = set()
    for reference in manifest.get("artifacts", []):
        record = _load_object(resolve_local_reference(root, str(reference)))
        payload_path = record.get("path")
        if isinstance(payload_path, str):
            by_path[payload_path] = record
        source_id = record.get("source_id")
        if isinstance(source_id, str):
            source_ids.add(source_id)
    return by_path, source_ids


def build_publication_plan(
    research_object_dir: str | Path,
    output_path: str | Path,
    *,
    targets: Sequence[Mapping[str, Any]] = DEFAULT_TARGETS,
    overrides: Mapping[str, str] | None = None,
    target_overrides: Mapping[str, Mapping[str, str]] | None = None,
) -> Path:
    """Create a deterministic, fail-closed publication plan for a research object."""

    root = Path(research_object_dir).resolve()
    verification = verify_research_object(root)
    if not verification.valid:
        raise PublicationError(
            "research object verification failed: " + "; ".join(verification.errors)
        )
    manifest = _load_object(root / "snapshot-manifest.json")
    rights = _load_object(resolve_local_reference(root, manifest["rights_inventory"]))
    artifacts_by_path, all_artifact_sources = _artifact_maps(root, manifest)
    rights_by_source = {
        item["source_id"]: item for item in rights.get("sources", []) if item.get("source_id")
    }
    target_records = [dict(item) for item in targets]
    target_ids = [str(item["target_id"]) for item in target_records]
    if len(target_ids) != len(set(target_ids)):
        raise PublicationError("publication targets must have unique target_id values")

    override_values = dict(overrides or {})
    permitted_overrides = set(_DECISION_PRECEDENCE)
    unknown_override = set(override_values.values()) - permitted_overrides
    if unknown_override:
        raise PublicationError(f"unsupported publication override: {sorted(unknown_override)}")
    target_override_values = {
        str(target_id): dict(decisions) for target_id, decisions in (target_overrides or {}).items()
    }
    unknown_targets = set(target_override_values) - set(target_ids)
    if unknown_targets:
        raise PublicationError(
            f"publication overrides reference unknown targets: {sorted(unknown_targets)}"
        )
    unknown_target_decisions = {
        decision
        for decisions in target_override_values.values()
        for decision in decisions.values()
        if decision not in permitted_overrides
    }
    if unknown_target_decisions:
        raise PublicationError(
            f"unsupported target publication override: {sorted(unknown_target_decisions)}"
        )

    assets: list[dict[str, Any]] = []
    blockers: list[str] = []
    seen_paths: set[str] = set()
    for relative in sorted(
        path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()
    ):
        seen_paths.add(relative)
        path = resolve_local_reference(root, relative)
        artifact = artifacts_by_path.get(relative)
        if artifact is None:
            classification = (
                "software-evidence"
                if relative.startswith("schemas/") or relative in {"CITATION.cff"}
                else "metadata"
            )
            source_ids: list[str] = []
            decision = "publish"
            basis = ["RIOPA release metadata or software evidence is public by default."]
            attributions: list[str] = []
        else:
            source_id = artifact.get("source_id")
            source_ids = [source_id] if isinstance(source_id, str) else sorted(all_artifact_sources)
            classification = "source-payload" if isinstance(source_id, str) else "derived-payload"
            decision, basis, attributions = _artifact_rights_decision(
                artifact,
                source_ids,
                rights_by_source,
                str(rights.get("publication_decision", "review-required")),
            )

        if relative in override_values:
            decision = _narrow_decision(
                decision,
                override_values[relative],
                context=f"path override for {relative}",
            )
            basis.append("A path-specific reviewed publication override was supplied.")
        if decision == "review-required":
            blockers.append(f"{relative}: rights review is required")
        target_decisions: dict[str, str] = {}
        for target_id in target_ids:
            target_decision = decision
            target_override = target_override_values.get(target_id, {}).get(relative)
            if target_override is not None:
                target_decision = _narrow_decision(
                    decision,
                    target_override,
                    context=f"target override for {target_id}/{relative}",
                )
                basis.append(
                    f"A reviewed {target_id} target decision narrows publication to "
                    f"{target_decision}."
                )
            target_decisions[target_id] = target_decision
            if target_decision == "review-required":
                blockers.append(f"{relative}: {target_id} rights review is required")
        asset_targets = [
            target_id
            for target_id, target_decision in target_decisions.items()
            if target_decision in {"publish", "metadata-only"}
        ]
        digest = sha256_file(path)
        assets.append(
            {
                "asset_id": (
                    "urn:riopa:publication-asset:"
                    f"{sha256_json({'path': relative, 'sha256': digest})}"
                ),
                "path": relative,
                "sha256": digest,
                "size_bytes": path.stat().st_size,
                "media_type": _media_type(path),
                "classification": classification,
                "rights_decision": decision,
                "target_decisions": target_decisions,
                "source_ids": source_ids,
                "target_ids": asset_targets,
                "decision_basis": basis,
                "attribution": sorted(set(attributions)),
            }
        )

    configured_paths = set(override_values)
    configured_paths.update(
        path for decisions in target_override_values.values() for path in decisions
    )
    unknown_paths = configured_paths - seen_paths
    if unknown_paths:
        raise PublicationError(
            f"publication overrides reference unknown asset paths: {sorted(unknown_paths)}"
        )
    status = "review-required" if blockers else "ready"
    publication_seed = {
        "snapshot_id": manifest["snapshot_id"],
        "snapshot_version": manifest["snapshot_version"],
        "targets": target_records,
    }
    plan: dict[str, Any] = {
        "schema_version": "1.0.0",
        "record_type": "publication_plan",
        "publication_id": f"urn:riopa:publication:{sha256_json(publication_seed)}",
        "snapshot_id": manifest["snapshot_id"],
        "snapshot_version": manifest["snapshot_version"],
        "created_at": manifest["created_at"],
        "source_research_object": {
            "bundle_manifest_sha256": sha256_file(root / "bundle-manifest.json"),
            "snapshot_manifest_sha256": sha256_file(root / "snapshot-manifest.json"),
        },
        "policy": {
            "fail_closed": True,
            "verified_research_object_required": True,
            "mutable_identifier_policy": "record-after-publication",
        },
        "targets": target_records,
        "assets": assets,
        "status": status,
        "blockers": sorted(set(blockers)),
        "plan_sha256": "",
    }
    plan["plan_sha256"] = sha256_json(plan, omit_keys={"plan_sha256"})
    errors = validate_instance(plan, _plan_schema(root))
    if errors:
        raise PublicationError("generated publication plan is invalid: " + "; ".join(errors))
    destination = Path(output_path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def validate_publication_plan(
    plan_path: str | Path, research_object_dir: str | Path
) -> tuple[str, ...]:
    """Validate plan schema, self-hash, and binding to exact research-object bytes."""

    path = Path(plan_path).resolve()
    root = Path(research_object_dir).resolve()
    errors: list[str] = []
    try:
        plan = _load_object(path)
        errors.extend(validate_instance(plan, _plan_schema(root)))
    except (OSError, json.JSONDecodeError, PublicationError, ValueError) as exc:
        return (str(exc),)
    expected_plan_hash = sha256_json(plan, omit_keys={"plan_sha256"})
    if plan.get("plan_sha256") != expected_plan_hash:
        errors.append("publication plan hash mismatch")
    verification = verify_research_object(root)
    errors.extend(f"research object: {item}" for item in verification.errors)
    if (root / "bundle-manifest.json").is_file() and plan["source_research_object"].get(
        "bundle_manifest_sha256"
    ) != sha256_file(root / "bundle-manifest.json"):
        errors.append("publication plan is bound to a different bundle manifest")
    if (root / "snapshot-manifest.json").is_file() and plan["source_research_object"].get(
        "snapshot_manifest_sha256"
    ) != sha256_file(root / "snapshot-manifest.json"):
        errors.append("publication plan is bound to a different snapshot manifest")
    for asset in plan.get("assets", []):
        try:
            asset_path = resolve_local_reference(root, asset["path"])
        except (KeyError, ValueError) as exc:
            errors.append(f"invalid asset path: {exc}")
            continue
        if not asset_path.is_file():
            errors.append(f"publication asset is missing: {asset.get('path')}")
            continue
        if asset_path.stat().st_size != asset.get("size_bytes"):
            errors.append(f"publication asset size mismatch: {asset['path']}")
        if sha256_file(asset_path) != asset.get("sha256"):
            errors.append(f"publication asset hash mismatch: {asset['path']}")
    return tuple(errors)


def stage_publication(
    plan_path: str | Path,
    research_object_dir: str | Path,
    output_dir: str | Path,
) -> Path:
    """Create target staging in a fresh, disjoint directory; never replace data."""

    root = Path(research_object_dir).resolve()
    plan_file = Path(plan_path).resolve()
    requested_output = Path(output_dir).absolute()
    if any(path.is_symlink() for path in (requested_output, *requested_output.parents)):
        raise PublicationError("publication staging output must not use symlinks")
    output = requested_output.resolve()
    if (
        output.is_relative_to(root)
        or root.is_relative_to(output)
        or plan_file.is_relative_to(output)
    ):
        raise PublicationError("publication staging output must be disjoint from its inputs")
    if output.exists():
        raise PublicationError("publication staging output must be a fresh directory")
    errors = validate_publication_plan(plan_file, root)
    if errors:
        raise PublicationError("publication plan validation failed: " + "; ".join(errors))
    plan = _load_object(plan_file)
    if plan["status"] != "ready":
        raise PublicationError(
            f"publication plan status is {plan['status']}; resolve blockers before staging"
        )
    output.mkdir(parents=True, exist_ok=False)

    for target in plan["targets"]:
        target_id = target["target_id"]
        target_root = output / target_id
        target_root.mkdir(parents=True)
        staged_assets: list[dict[str, Any]] = []
        for asset in plan["assets"]:
            if target_id not in asset["target_ids"]:
                continue
            source = resolve_local_reference(root, asset["path"])
            target_decision = asset.get("target_decisions", {}).get(
                target_id, asset["rights_decision"]
            )
            if target_decision == "publish":
                destination = target_root / asset["path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
                staged_path = asset["path"]
            elif target_decision == "metadata-only":
                staged_path = f"withheld/{asset['path']}.metadata.json"
                destination = target_root / staged_path
                destination.parent.mkdir(parents=True, exist_ok=True)
                descriptor = {
                    "asset_id": asset["asset_id"],
                    "original_path": asset["path"],
                    "sha256": asset["sha256"],
                    "size_bytes": asset["size_bytes"],
                    "media_type": asset["media_type"],
                    "rights_decision": "metadata-only",
                    "source_ids": asset["source_ids"],
                    "decision_basis": asset["decision_basis"],
                }
                destination.write_text(
                    json.dumps(descriptor, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )
            else:  # schema prevents this path from being target-addressable
                raise PublicationError(
                    f"unsafe target assignment for {asset['path']}: {target_decision}"
                )
            staged_assets.append(
                {
                    "source_asset_id": asset["asset_id"],
                    "path": staged_path,
                    "sha256": sha256_file(destination),
                    "size_bytes": destination.stat().st_size,
                }
            )
        target_manifest = {
            "schema_version": "1.0.0",
            "publication_id": plan["publication_id"],
            "snapshot_id": plan["snapshot_id"],
            "snapshot_version": plan["snapshot_version"],
            "target": target,
            "source_plan_sha256": plan["plan_sha256"],
            "assets": sorted(staged_assets, key=lambda item: item["path"]),
        }
        target_manifest["manifest_sha256"] = sha256_json(target_manifest)
        (target_root / "publication-target-manifest.json").write_text(
            json.dumps(target_manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    crosswalk = {
        "schema_version": "1.0.0",
        "publication_id": plan["publication_id"],
        "snapshot_id": plan["snapshot_id"],
        "snapshot_version": plan["snapshot_version"],
        "plan_sha256": plan["plan_sha256"],
        "targets": [
            {
                "target_id": target["target_id"],
                "kind": target["kind"],
                "repository": target["repository"],
                "identifier": target.get("identifier"),
                "revision": target.get("revision"),
                "target_manifest_sha256": sha256_file(
                    output / target["target_id"] / "publication-target-manifest.json"
                ),
            }
            for target in plan["targets"]
        ],
    }
    crosswalk["crosswalk_sha256"] = sha256_json(crosswalk)
    (output / "publication-crosswalk.json").write_text(
        json.dumps(crosswalk, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return output


def _publication_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PublicationError(f"publication {field} must be a non-empty string")
    return value


def _normalise_publication_receipt(
    receipt: Mapping[str, Any], plan_sha256: str, target_id: str
) -> dict[str, Any]:
    if not isinstance(receipt, Mapping):
        raise PublicationError("publication receipt must be an object")
    required = {
        "target_id",
        "operation_key",
        "plan_sha256",
        "identifier",
        "revision",
        "recorded_at",
    }
    missing = sorted(required - set(receipt))
    if missing:
        raise PublicationError(f"publication receipt is missing fields: {missing}")
    for field in required:
        _publication_text(receipt[field], field)
    if receipt["target_id"] != target_id:
        raise PublicationError("publication receipt target mismatch")
    if receipt["plan_sha256"] != plan_sha256:
        raise PublicationError("publication receipt plan hash mismatch")
    operation_key = sha256_json({"plan_sha256": plan_sha256, "target_id": target_id})
    if receipt["operation_key"] != operation_key:
        raise PublicationError("publication receipt operation key mismatch")
    try:
        recorded_at = datetime.fromisoformat(receipt["recorded_at"])
    except ValueError as error:
        raise PublicationError(
            "publication receipt recorded_at must be an ISO timestamp"
        ) from error
    if recorded_at.tzinfo is None or recorded_at.utcoffset() is None:
        raise PublicationError("publication receipt recorded_at must include a timezone")
    digest = sha256_json(receipt, omit_keys={"receipt_sha256"})
    if "receipt_sha256" in receipt and receipt["receipt_sha256"] != digest:
        raise PublicationError("publication receipt hash mismatch")
    return {**receipt, "receipt_sha256": digest}


def validate_publication_state(state: Mapping[str, Any]) -> None:
    """Validate a restored journal, including its nested receipts and routing state.

    Hashes establish consistency, not authenticity or provider-side acceptance.
    Opaque identifier/revision text is retained; this does not prove immutability.
    """
    if not isinstance(state, Mapping):
        raise PublicationError("publication state must be an object")
    if state.get("state_sha256") != sha256_json(state, omit_keys={"state_sha256"}):
        raise PublicationError("publication state hash mismatch")
    if state.get("schema_version") != "1.0.0" or state.get("record_type") != "publication_state":
        raise PublicationError("unsupported publication state schema")
    _publication_text(state.get("publication_id"), "publication_id")
    plan_sha256 = _publication_text(state.get("plan_sha256"), "plan_sha256")
    if re.fullmatch(r"[0-9a-f]{64}", plan_sha256) is None:
        raise PublicationError("publication state plan hash must be a SHA-256 digest")
    targets = state.get("targets")
    if not isinstance(targets, Mapping) or not targets:
        raise PublicationError("publication state requires a non-empty targets object")
    statuses: set[str] = set()
    for target_id, target in targets.items():
        _publication_text(target_id, "target_id")
        if not isinstance(target, Mapping):
            raise PublicationError("publication target state must be an object")
        operation_key = sha256_json({"plan_sha256": plan_sha256, "target_id": target_id})
        if target.get("operation_key") != operation_key:
            raise PublicationError("publication target operation key mismatch")
        if "receipt" not in target:
            raise PublicationError("publication target state requires receipt field")
        receipt = target["receipt"]
        expected_status = "pending" if receipt is None else "published"
        if target.get("status") != expected_status:
            raise PublicationError("publication target status and receipt disagree")
        if receipt is not None:
            normalised = _normalise_publication_receipt(receipt, plan_sha256, target_id)
            if receipt != normalised:
                raise PublicationError("stored publication receipt requires its content hash")
        statuses.add(expected_status)
    expected = "in-progress" if len(statuses) > 1 else next(iter(statuses))
    if state.get("status") != expected:
        raise PublicationError("publication aggregate status and targets disagree")


def initialise_publication_state(plan: Mapping[str, Any]) -> dict[str, Any]:
    """Create a resumable target journal bound to one exact publication plan."""

    if plan.get("status") != "ready":
        raise PublicationError("publication state requires a ready plan")
    plan_sha256 = str(plan.get("plan_sha256") or "")
    if plan_sha256 != sha256_json(plan, omit_keys={"plan_sha256"}):
        raise PublicationError("publication state requires a content-bound plan")
    target_records = plan.get("targets", [])
    if not isinstance(target_records, list) or any(
        not isinstance(target, Mapping) for target in target_records
    ):
        raise PublicationError("publication plan targets must be an array of objects")
    target_ids = [
        _publication_text(target.get("target_id"), "target_id") for target in target_records
    ]
    if len(target_ids) != len(set(target_ids)):
        raise PublicationError("publication state targets must be unique")
    targets = {
        str(target["target_id"]): {
            "status": "pending",
            "operation_key": sha256_json(
                {"plan_sha256": plan_sha256, "target_id": target["target_id"]}
            ),
            "receipt": None,
        }
        for target in target_records
    }
    if not targets:
        raise PublicationError("publication state requires at least one target")
    state: dict[str, Any] = {
        "schema_version": "1.0.0",
        "record_type": "publication_state",
        "publication_id": plan["publication_id"],
        "plan_sha256": plan_sha256,
        "status": "pending",
        "targets": targets,
        "state_sha256": "",
    }
    state["state_sha256"] = sha256_json(state, omit_keys={"state_sha256"})
    validate_publication_state(state)
    return state


def record_publication_receipt(
    state: Mapping[str, Any],
    receipt: Mapping[str, Any],
) -> dict[str, Any]:
    """Reconcile a recorded provider receipt without asserting remote verification."""

    validate_publication_state(state)
    if not isinstance(receipt, Mapping):
        raise PublicationError("publication receipt must be an object")
    target_id = _publication_text(receipt.get("target_id"), "target_id")
    targets = state.get("targets")
    if not isinstance(targets, Mapping) or target_id not in targets:
        raise PublicationError(f"receipt references unknown target: {target_id}")
    target = targets[target_id]
    if not isinstance(target, Mapping):
        raise PublicationError(f"invalid target state: {target_id}")
    normalised_receipt = _normalise_publication_receipt(receipt, state["plan_sha256"], target_id)
    existing = target.get("receipt")
    if existing is not None:
        if existing != normalised_receipt:
            raise PublicationError(
                f"conflicting publication receipt for completed target: {target_id}"
            )
        return dict(state)

    updated = cast(dict[str, Any], json.loads(json.dumps(state)))
    updated["targets"][target_id]["status"] = "published"
    updated["targets"][target_id]["receipt"] = normalised_receipt
    statuses = {item["status"] for item in updated["targets"].values()}
    updated["status"] = "published" if statuses == {"published"} else "in-progress"
    updated["state_sha256"] = sha256_json(updated, omit_keys={"state_sha256"})
    return updated


def reconcile_publication_receipts(
    state: Mapping[str, Any], receipts: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    """Apply a receipt batch deterministically across all publication targets.

    Receipts are sorted by target identifier before reconciliation.  Identical
    replayed receipts are idempotent; a conflicting receipt for a target is
    rejected by :func:`record_publication_receipt`.  The operation never
    contacts a remote target and keeps every receipt bound to the same plan
    hash and operation key.
    """

    validate_publication_state(state)
    if not isinstance(receipts, Sequence) or isinstance(receipts, (str, bytes)):
        raise PublicationError("publication receipts must be an array")
    receipt_target_ids = [
        receipt.get("target_id") for receipt in receipts if isinstance(receipt, Mapping)
    ]
    if any(
        not isinstance(target_id, str) or not target_id.strip() for target_id in receipt_target_ids
    ):
        raise PublicationError(
            "publication receipt batch target_id values must be non-empty strings"
        )
    if len(receipt_target_ids) != len(set(receipt_target_ids)):
        raise PublicationError("publication receipt batch target_id values must be unique")
    ordered = sorted(
        receipts,
        key=lambda item: str(item.get("target_id", "")) if isinstance(item, Mapping) else "",
    )
    result = dict(state)
    for receipt in ordered:
        if not isinstance(receipt, Mapping):
            raise PublicationError("publication receipts must contain objects")
        result = record_publication_receipt(result, receipt)
    return result


def build_publication_resume_plan(
    plan: Mapping[str, Any],
    state: Mapping[str, Any],
    receipts: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """Project receipt reconciliation against the caller's exact expected plan.

    This pure helper checks a ready plan's content binding, not its full schema,
    current rights, authenticity or provider state. A missing receipt never
    establishes that a release/deposit is absent or that another write is safe.
    The existing journal APIs remain available for compatibility.
    """
    if not isinstance(plan, Mapping):
        raise PublicationError("expected publication plan must be an object")
    _publication_text(plan.get("publication_id"), "publication_id")
    expected = initialise_publication_state(plan)
    validate_publication_state(state)
    for field in ("publication_id", "plan_sha256"):
        if state[field] != expected[field]:
            raise PublicationError(f"publication resume {field} differs from expected plan")
    if set(state["targets"]) != set(expected["targets"]):
        raise PublicationError("publication resume target set differs from expected plan")
    # Journal validation already recomputes every operation key from the now
    # matched plan hash and target identity.
    # Detach even the no-op/replay result so callers cannot mutate input journals.
    reconciled = cast(
        dict[str, Any], json.loads(json.dumps(reconcile_publication_receipts(state, receipts)))
    )
    targets = []
    for target_id, target in sorted(reconciled["targets"].items()):
        receipt = target["receipt"]
        targets.append(
            {
                "target_id": target_id,
                "operation_key": target["operation_key"],
                "disposition": "receipt-recorded"
                if receipt is not None
                else "provider-reconciliation-required",
                "receipt_sha256": receipt["receipt_sha256"] if receipt is not None else None,
                "remote_write_authorized": False,
            }
        )
    projection = {
        "schema_version": "1.0.0",
        "record_type": "publication_resume_projection",
        "publication_id": expected["publication_id"],
        "plan_sha256": expected["plan_sha256"],
        "input_state_sha256": state["state_sha256"],
        "reconciled_state_sha256": reconciled["state_sha256"],
        "reconciled_state": reconciled,
        "targets": targets,
        "remote_write_authorized": False,
        "non_claims": [
            "Receipt presence is not live provider acceptance or immutable revision verification.",
            "Missing receipts require provider reconciliation before any separately "
            "authorized write.",
            "No current rights, full plan schema, release qualification or publication authority "
            "is established by this projection.",
        ],
    }
    return {**projection, "projection_sha256": sha256_json(projection)}
