"""Archive disposition, coverage, and bounded backfill planning for all LINZ items."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .hashing import sha256_file, sha256_json
from .linz_catalog import catalog_items_path, load_catalog_items
from .yaml_tools import load_yaml


class LinzArchivePlanError(RuntimeError):
    """Raised when an all-catalogue plan has gaps or contradictory policy."""


@dataclass(frozen=True)
class LinzArchivePlanSummary:
    """Compact plan and coverage result."""

    plan_id: str
    item_count: int
    unclassified_count: int
    payload_ready_count: int
    review_required_count: int
    metadata_only_count: int
    output_path: Path


def load_archive_policy(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    value = load_yaml(text) if source.suffix.lower() in {".yaml", ".yml"} else json.loads(text)
    if not isinstance(value, dict):
        raise LinzArchivePlanError("archive policy root must be an object")
    return value


def _flatten_strings(value: Any) -> set[str]:
    result: set[str] = set()
    if isinstance(value, str):
        result.add(value.casefold())
    elif isinstance(value, Mapping):
        for key, item in value.items():
            result.add(str(key).casefold())
            result.update(_flatten_strings(item))
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        for item in value:
            result.update(_flatten_strings(item))
    return result


def _service_keys(item: Mapping[str, Any]) -> set[str]:
    raw = item.get("raw") if isinstance(item.get("raw"), Mapping) else item
    keys = _flatten_strings(item.get("services", []))
    if isinstance(raw, Mapping):
        keys.update(_flatten_strings(raw.get("services", [])))
    # Koordinates detail responses may expose service URLs or capability labels
    # in several nested structures.  Restrict matching to recognised tokens.
    recognised = {
        "wfs",
        "wfs-changesets",
        "wmts",
        "xyz",
        "tiles",
        "export",
        "kart",
        "csw",
        "data-table",
        "spatial-query-vector",
        "spatial-query-grid",
        "spatial-query-tiles",
    }
    combined = " ".join(keys)
    return {token for token in recognised if token in keys or token in combined}


def _license_tokens(item: Mapping[str, Any]) -> set[str]:
    return _flatten_strings(item.get("license")) | _flatten_strings(
        item.get("raw", {}).get("license")
    )


def _categories(item: Mapping[str, Any]) -> tuple[str, ...]:
    value = item.get("categories") or item.get("raw", {}).get("categories") or []
    if isinstance(value, str):
        return (value.casefold(),)
    if isinstance(value, Sequence):
        return tuple(str(item).casefold() for item in value)
    return ()


def _estimated_size(item: Mapping[str, Any]) -> int | None:
    candidates: list[Any] = [
        item.get("size_bytes"),
        item.get("raw", {}).get("size_bytes"),
        item.get("raw", {}).get("data", {}).get("size_bytes")
        if isinstance(item.get("raw", {}).get("data"), Mapping)
        else None,
    ]
    for candidate in candidates:
        if isinstance(candidate, int) and not isinstance(candidate, bool) and candidate >= 0:
            return candidate
    return None


def _matches(item: Mapping[str, Any], rule: Mapping[str, Any]) -> bool:
    match = rule.get("match", {})
    if not isinstance(match, Mapping):
        raise LinzArchivePlanError(f"rule {rule.get('id')} match must be an object")
    item_type = str(item.get("item_type") or "unknown").casefold()
    kind = str(item.get("kind") or item.get("raw", {}).get("kind") or "unknown").casefold()
    services = _service_keys(item)
    licenses = _license_tokens(item)
    categories = _categories(item)

    item_types = {str(value).casefold() for value in match.get("item_types", [])}
    if item_types and item_type not in item_types:
        return False
    kinds = {str(value).casefold() for value in match.get("kinds", [])}
    if kinds and kind not in kinds:
        return False
    service_any = {str(value).casefold() for value in match.get("service_any", [])}
    if service_any and not (services & service_any):
        return False
    service_none = {str(value).casefold() for value in match.get("service_none", [])}
    if service_none and services & service_none:
        return False
    license_any = {str(value).casefold() for value in match.get("license_any", [])}
    if license_any and not any(token in " ".join(licenses) for token in license_any):
        return False
    prefixes = tuple(str(value).casefold() for value in match.get("category_prefixes", []))
    return not prefixes or any(category.startswith(prefixes) for category in categories)


def _validate_policy(policy: Mapping[str, Any]) -> None:
    if policy.get("schema_version") != "1.0.0":
        raise LinzArchivePlanError("archive policy schema_version must be 1.0.0")
    rules = policy.get("rules")
    if not isinstance(rules, list) or not rules:
        raise LinzArchivePlanError("archive policy requires at least one rule")
    ids: set[str] = set()
    for rule in rules:
        if not isinstance(rule, Mapping):
            raise LinzArchivePlanError("every archive policy rule must be an object")
        identifier = str(rule.get("id") or "")
        if not identifier:
            raise LinzArchivePlanError("archive policy rule has no id")
        if identifier in ids:
            raise LinzArchivePlanError(f"duplicate archive policy rule id: {identifier}")
        ids.add(identifier)
        if not rule.get("strategy"):
            raise LinzArchivePlanError(f"archive policy rule {identifier} has no strategy")
    fallback = policy.get("fallback")
    if not isinstance(fallback, Mapping) or not fallback.get("strategy"):
        raise LinzArchivePlanError("archive policy requires a fallback strategy")
    execution = policy.get("execution", {})
    if not isinstance(execution, Mapping):
        raise LinzArchivePlanError("archive policy execution must be an object")
    format_profiles = execution.get("format_profiles", {})
    if not isinstance(format_profiles, Mapping):
        raise LinzArchivePlanError("archive policy format_profiles must be an object")
    for rule in [*rules, fallback]:
        profiles: list[str] = []
        if rule.get("format_profile"):
            profiles.append(str(rule["format_profile"]))
        by_kind = rule.get("format_profile_by_kind", {})
        if by_kind and not isinstance(by_kind, Mapping):
            raise LinzArchivePlanError(
                f"rule {rule.get('id')} format_profile_by_kind must be an object"
            )
        if isinstance(by_kind, Mapping):
            profiles.extend(str(value) for value in by_kind.values())
        missing = sorted(profile for profile in profiles if profile not in format_profiles)
        if missing:
            raise LinzArchivePlanError(
                f"rule {rule.get('id')} references unknown format profiles: {missing}"
            )


def _rights_disposition(item: Mapping[str, Any], rule: Mapping[str, Any]) -> str:
    explicit = rule.get("rights_disposition")
    if explicit:
        return str(explicit)
    tokens = " ".join(_license_tokens(item))
    if any(value in tokens for value in ("cc-by", "creative commons attribution", "public-domain")):
        return "candidate-permitted-review-required"
    if tokens:
        return "review-required"
    return "unresolved"


def _execution_contract(
    item: Mapping[str, Any],
    rule: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    execution = policy.get("execution", {})
    if not isinstance(execution, Mapping):
        execution = {}
    kind = str(item.get("kind") or item.get("raw", {}).get("kind") or "unknown").casefold()
    profile = rule.get("format_profile")
    by_kind = rule.get("format_profile_by_kind", {})
    if profile is None and isinstance(by_kind, Mapping):
        profile = by_kind.get(kind)
    profiles = execution.get("format_profiles", {})
    preferences: dict[str, list[str]] = {}
    if profile is not None and isinstance(profiles, Mapping):
        raw_profile = profiles.get(str(profile), {})
        if isinstance(raw_profile, Mapping):
            preferences = {
                str(key): [str(value) for value in values]
                for key, values in raw_profile.items()
                if isinstance(values, Sequence) and not isinstance(values, (bytes, bytearray, str))
            }
    limit = execution.get("automatic_export_limit_bytes")
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
        limit = None
    return {
        "payload_methods": [str(value) for value in rule.get("payload_methods", [])],
        "format_profile": str(profile) if profile is not None else None,
        "format_preferences": preferences,
        "export_crs": execution.get("default_export_crs"),
        "automatic_export_limit_bytes": limit,
    }


def plan_catalog_archive(
    items: Iterable[Mapping[str, Any]],
    policy: Mapping[str, Any],
    *,
    catalog_snapshot_id: str,
    catalog_items_sha256: str,
    catalogue_complete: bool,
    planning_inputs_complete: bool = False,
) -> dict[str, Any]:
    """Assign every catalogue entry a deterministic archival disposition."""

    _validate_policy(policy)
    records = sorted(items, key=lambda item: str(item["catalog_item_id"]))
    rules = list(policy["rules"])
    fallback = dict(policy["fallback"])
    fallback_id = str(fallback.get("id") or "fallback")
    dispositions: list[dict[str, Any]] = []

    for item in records:
        selected = next((rule for rule in rules if _matches(item, rule)), fallback)
        selected_id = str(selected.get("id") or "fallback")
        strategy = str(selected["strategy"])
        estimated_size = _estimated_size(item)
        execution_contract = _execution_contract(item, selected, policy)
        rights = _rights_disposition(item, selected)
        blockers: list[str] = []
        if rights in {"review-required", "unresolved", "candidate-permitted-review-required"}:
            blockers.append("rights-review")
        if selected.get("requires_size_estimate") and estimated_size is None:
            blockers.append("size-assessment")
        automatic_limit = execution_contract["automatic_export_limit_bytes"]
        if (
            isinstance(automatic_limit, int)
            and isinstance(estimated_size, int)
            and estimated_size > automatic_limit
        ):
            blockers.append("automatic-export-size-limit")
        methods = set(execution_contract["payload_methods"])
        services = _service_keys(item)
        if "koordinates-export" in methods and "export" not in services:
            blockers.append("export-service-unavailable")
        if strategy == "unsupported-explicit-exception":
            blockers.append("unsupported-service")
        payload_status = "ready" if not blockers else "review-required"
        if strategy in {"metadata-only", "external-reference", "unsupported-explicit-exception"}:
            payload_status = "metadata-only" if not blockers else "review-required"
        identifier = str(item["catalog_item_id"])
        job_seed = {
            "catalog_item_id": identifier,
            "raw_sha256": item.get("raw_sha256"),
            "rule_id": selected_id,
            "strategy": strategy,
            "execution_contract": execution_contract,
        }
        dispositions.append(
            {
                "catalog_item_id": identifier,
                "source_catalog_id": item.get("source_catalog_id"),
                "item_type": item.get("item_type"),
                "kind": item.get("kind") or item.get("raw", {}).get("kind"),
                "name": item.get("name"),
                "url": item.get("url"),
                "raw_sha256": item.get("raw_sha256"),
                "rule_id": selected_id,
                "strategy": strategy,
                "tier": selected.get("tier", "T4"),
                "priority": selected.get("priority", "P3"),
                "cadence": selected.get("cadence", "manual-review"),
                "destinations": list(selected.get("destinations", ["github-metadata"])),
                "rights_disposition": rights,
                "estimated_size_bytes": estimated_size,
                "payload_status": payload_status,
                "blockers": sorted(blockers),
                "job_key": sha256_json(job_seed),
                "services": sorted(services),
                **execution_contract,
            }
        )

    if len(dispositions) != len(records):
        raise LinzArchivePlanError("not every catalogue item received a disposition")
    identifiers = [entry["catalog_item_id"] for entry in dispositions]
    if len(identifiers) != len(set(identifiers)):
        raise LinzArchivePlanError("archive plan contains duplicate catalogue identities")

    strategy_counts = Counter(entry["strategy"] for entry in dispositions)
    status_counts = Counter(entry["payload_status"] for entry in dispositions)
    type_counts = Counter(str(entry.get("item_type") or "unknown") for entry in dispositions)
    tier_counts = Counter(str(entry.get("tier") or "unknown") for entry in dispositions)
    unclassified = [entry for entry in dispositions if entry["rule_id"] == fallback_id]
    plan_seed = {
        "catalog_snapshot_id": catalog_snapshot_id,
        "catalog_items_sha256": catalog_items_sha256,
        "policy_id": policy.get("policy_id"),
        "policy_version": policy.get("policy_version"),
        "item_job_keys": [entry["job_key"] for entry in dispositions],
    }
    plan: dict[str, Any] = {
        "schema_version": "1.0.0",
        "record_type": "linz_archive_plan",
        "plan_id": f"urn:riopa:linz-archive-plan:{sha256_json(plan_seed)}",
        "catalog_snapshot_id": catalog_snapshot_id,
        "catalog_items_sha256": catalog_items_sha256,
        "policy_id": policy.get("policy_id"),
        "policy_version": policy.get("policy_version"),
        "scope": {
            "claim": (
                (
                    "every item in an unfiltered published-catalogue snapshot "
                    "has an explicit disposition"
                )
                if catalogue_complete
                else (
                    "every item in the supplied catalogue subset has an explicit "
                    "disposition; this is not a full-catalogue claim"
                )
            ),
            "catalogue_complete": catalogue_complete,
            "planning_inputs_complete": planning_inputs_complete,
            "payload_complete": False,
            "item_count": len(records),
            "unclassified_count": len(unclassified),
        },
        "coverage": {
            "by_strategy": dict(sorted(strategy_counts.items())),
            "by_payload_status": dict(sorted(status_counts.items())),
            "by_item_type": dict(sorted(type_counts.items())),
            "by_tier": dict(sorted(tier_counts.items())),
        },
        "dispositions": dispositions,
        "plan_sha256": "",
    }
    plan["plan_sha256"] = sha256_json(plan, omit_keys={"plan_sha256"})
    return plan


def write_archive_plan(
    items_path: str | Path,
    policy_path: str | Path,
    output_path: str | Path,
    *,
    catalog_snapshot_id: str,
    catalogue_complete: bool = False,
    planning_inputs_complete: bool = False,
) -> LinzArchivePlanSummary:
    """Create and persist an all-items archival plan."""

    items = load_catalog_items(items_path)
    policy = load_archive_policy(policy_path)
    plan = plan_catalog_archive(
        items,
        policy,
        catalog_snapshot_id=catalog_snapshot_id,
        catalog_items_sha256=sha256_file(items_path),
        catalogue_complete=catalogue_complete,
        planning_inputs_complete=planning_inputs_complete,
    )
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(plan, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    counts = plan["coverage"]["by_payload_status"]
    return LinzArchivePlanSummary(
        plan_id=plan["plan_id"],
        item_count=plan["scope"]["item_count"],
        unclassified_count=plan["scope"]["unclassified_count"],
        payload_ready_count=counts.get("ready", 0),
        review_required_count=counts.get("review-required", 0),
        metadata_only_count=counts.get("metadata-only", 0),
        output_path=destination,
    )


def write_archive_plan_from_snapshot(
    catalog_snapshot_manifest: str | Path,
    policy_path: str | Path,
    output_path: str | Path,
) -> LinzArchivePlanSummary:
    """Create a plan whose catalogue-complete claim is derived from signed evidence.

    The caller cannot promote an arbitrary JSONL file to catalogue-complete by
    assertion. The snapshot hash, item payload hash and size, and unfiltered
    published-catalogue flag must all verify first.
    """

    manifest_path = Path(catalog_snapshot_manifest).resolve()
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LinzArchivePlanError(f"cannot load catalogue snapshot: {manifest_path}") from exc
    if not isinstance(manifest, dict) or manifest.get("record_type") not in {
        "linz_catalog_snapshot",
        "linz_catalog_enriched_snapshot",
    }:
        raise LinzArchivePlanError("not a LINZ catalogue snapshot manifest")
    expected_manifest_hash = sha256_json(manifest, omit_keys={"manifest_sha256"})
    if manifest.get("manifest_sha256") != expected_manifest_hash:
        raise LinzArchivePlanError("LINZ catalogue snapshot manifest hash mismatch")
    items_descriptor = manifest.get("items")
    if not isinstance(items_descriptor, Mapping):
        raise LinzArchivePlanError("LINZ catalogue snapshot has no items descriptor")
    items_path = catalog_items_path(manifest_path)
    expected_items_hash = items_descriptor.get("sha256")
    expected_items_size = items_descriptor.get("size_bytes")
    if expected_items_hash != sha256_file(items_path):
        raise LinzArchivePlanError("LINZ catalogue items hash mismatch")
    if expected_items_size != items_path.stat().st_size:
        raise LinzArchivePlanError("LINZ catalogue items size mismatch")
    completeness = manifest.get("completeness")
    catalogue_complete = bool(
        isinstance(completeness, Mapping)
        and completeness.get("unfiltered_published_catalogue") is True
    )
    planning_inputs_complete = bool(
        manifest.get("record_type") == "linz_catalog_enriched_snapshot"
        and isinstance(manifest.get("detail_coverage"), Mapping)
        and manifest["detail_coverage"].get("complete") is True
        and isinstance(manifest.get("service_coverage"), Mapping)
        and manifest["service_coverage"].get("complete") is True
    )
    return write_archive_plan(
        items_path,
        policy_path,
        output_path,
        catalog_snapshot_id=str(manifest.get("snapshot_id") or ""),
        catalogue_complete=catalogue_complete,
        planning_inputs_complete=planning_inputs_complete,
    )


def load_archive_plan(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("record_type") != "linz_archive_plan":
        raise LinzArchivePlanError("not a LINZ archive plan")
    expected = sha256_json(value, omit_keys={"plan_sha256"})
    if value.get("plan_sha256") != expected:
        raise LinzArchivePlanError("LINZ archive plan hash mismatch")
    return value


def build_backfill_batches(
    plan: Mapping[str, Any],
    *,
    maximum_items: int = 25,
    maximum_estimated_bytes: int = 5 * 1024 * 1024 * 1024,
) -> list[dict[str, Any]]:
    """Pack eligible work into deterministic, bounded batches.

    Unknown-size payloads are isolated in one-item review batches so a bulk
    workflow cannot accidentally create an unbounded export.
    """

    if maximum_items < 1 or maximum_estimated_bytes < 1:
        raise ValueError("batch limits must be positive")
    eligible = [
        entry
        for entry in plan.get("dispositions", [])
        if entry.get("strategy") not in {"metadata-only", "external-reference"}
    ]
    eligible.sort(
        key=lambda entry: (
            str(entry.get("tier")),
            str(entry.get("priority")),
            str(entry.get("catalog_item_id")),
        )
    )
    # The internal tuple carries batch-level review reasons.  Unknown-size and
    # individually oversized jobs are isolated so an ordinary worker cannot
    # accidentally execute an unbounded export merely because a batch contains
    # one item.
    batches: list[tuple[list[dict[str, Any]], tuple[str, ...]]] = []
    current: list[dict[str, Any]] = []
    current_bytes = 0

    def flush_current() -> None:
        nonlocal current, current_bytes
        if current:
            batches.append((current, ()))
            current = []
            current_bytes = 0

    for entry in eligible:
        estimated = entry.get("estimated_size_bytes")
        if not isinstance(estimated, int):
            flush_current()
            batches.append(([dict(entry)], ("unknown-estimated-size",)))
            continue
        if estimated > maximum_estimated_bytes:
            flush_current()
            batches.append(([dict(entry)], ("estimated-size-exceeds-batch-limit",)))
            continue
        if current and (
            len(current) >= maximum_items or current_bytes + estimated > maximum_estimated_bytes
        ):
            flush_current()
        current.append(dict(entry))
        current_bytes += estimated
    flush_current()

    rendered: list[dict[str, Any]] = []
    for index, (entries, limit_reasons) in enumerate(batches, start=1):
        known_sizes = [
            int(entry["estimated_size_bytes"])
            for entry in entries
            if isinstance(entry.get("estimated_size_bytes"), int)
        ]
        estimated_total = sum(known_sizes) if len(known_sizes) == len(entries) else None
        oversize = bool(estimated_total is not None and estimated_total > maximum_estimated_bytes)
        reasons = set(limit_reasons)
        if len(entries) > maximum_items:
            reasons.add("item-count-exceeds-batch-limit")
        if oversize:
            reasons.add("estimated-size-exceeds-batch-limit")
        seed = {
            "jobs": [entry["job_key"] for entry in entries],
            "limit_reasons": sorted(reasons),
        }
        rendered.append(
            {
                "batch_id": f"urn:riopa:linz-backfill-batch:{sha256_json(seed)}",
                "sequence": index,
                "item_count": len(entries),
                "estimated_size_bytes": estimated_total,
                "oversize": oversize,
                "requires_review": bool(reasons) or any(entry.get("blockers") for entry in entries),
                "limit_reasons": sorted(reasons),
                "jobs": entries,
            }
        )
    return rendered


def write_backfill_batches(
    plan_path: str | Path,
    output_path: str | Path,
    *,
    maximum_items: int = 25,
    maximum_estimated_bytes: int = 5 * 1024 * 1024 * 1024,
) -> Path:
    plan = load_archive_plan(plan_path)
    batches = build_backfill_batches(
        plan,
        maximum_items=maximum_items,
        maximum_estimated_bytes=maximum_estimated_bytes,
    )
    by_strategy: dict[str, int] = defaultdict(int)
    for batch in batches:
        for job in batch["jobs"]:
            by_strategy[str(job["strategy"])] += 1
    document: dict[str, Any] = {
        "schema_version": "1.0.0",
        "record_type": "linz_backfill_batches",
        "plan_id": plan["plan_id"],
        "plan_sha256": plan["plan_sha256"],
        "limits": {
            "maximum_items": maximum_items,
            "maximum_estimated_bytes": maximum_estimated_bytes,
        },
        "batch_count": len(batches),
        "job_count": sum(batch["item_count"] for batch in batches),
        "jobs_by_strategy": dict(sorted(by_strategy.items())),
        "batches": batches,
        "document_sha256": "",
    }
    document["document_sha256"] = sha256_json(document, omit_keys={"document_sha256"})
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(document, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destination
