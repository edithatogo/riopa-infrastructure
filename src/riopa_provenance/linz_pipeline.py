"""Content-bound, budgeted orchestration for the LINZ archival pipeline."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, cast

from .hashing import sha256_json


class LinzPipelineError(ValueError):
    """Raised when pipeline state cannot advance safely."""


_SHARDED_STAGES = {"details", "services", "payload"}
_STAGE_ORDER = ("catalogue", "details", "services", "planning", "payload", "federation")


def _job_key(stage: str, shard: int) -> str:
    return f"{stage}:{shard}"


def initialise_linz_pipeline(
    *,
    archive_plan_id: str,
    archive_plan_sha256: str,
    catalogue_items_sha256: str,
    shard_count: int,
    maximum_storage_bytes: int,
    maximum_egress_bytes: int,
) -> dict[str, Any]:
    """Create an independently resumable pipeline and deterministic CI jobs."""

    if shard_count < 1:
        raise LinzPipelineError("shard_count must be positive")
    if maximum_storage_bytes < 1 or maximum_egress_bytes < 0:
        raise LinzPipelineError("storage and egress budgets must be non-negative")
    for label, digest in {
        "archive plan": archive_plan_sha256,
        "catalogue items": catalogue_items_sha256,
    }.items():
        if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
            raise LinzPipelineError(f"{label} digest is not SHA-256")

    jobs: dict[str, dict[str, Any]] = {}
    for stage in _STAGE_ORDER:
        shards = range(shard_count) if stage in _SHARDED_STAGES else range(1)
        for shard in shards:
            key = _job_key(stage, shard)
            if stage == "catalogue":
                dependencies: list[str] = []
            elif stage in {"details", "services"}:
                dependencies = [_job_key("catalogue", 0)]
            elif stage == "planning":
                dependencies = [
                    _job_key(dependency_stage, dependency_shard)
                    for dependency_stage in ("details", "services")
                    for dependency_shard in range(shard_count)
                ]
            elif stage == "payload":
                dependencies = [_job_key("planning", 0)]
            else:
                dependencies = [
                    _job_key("payload", dependency_shard) for dependency_shard in range(shard_count)
                ]
            operation_seed = {
                "archive_plan_sha256": archive_plan_sha256,
                "catalogue_items_sha256": catalogue_items_sha256,
                "stage": stage,
                "shard": shard,
                "shard_count": shard_count,
            }
            jobs[key] = {
                "stage": stage,
                "shard": shard,
                "shard_count": shard_count,
                "operation_key": sha256_json(operation_seed),
                "dependencies": dependencies,
                "budgets": {
                    "maximum_storage_bytes": maximum_storage_bytes,
                    "maximum_egress_bytes": maximum_egress_bytes,
                },
                "status": "pending",
                "receipt": None,
            }

    state: dict[str, Any] = {
        "schema_version": "1.0.0",
        "record_type": "linz_archive_pipeline",
        "archive_plan_id": archive_plan_id,
        "archive_plan_sha256": archive_plan_sha256,
        "catalogue_items_sha256": catalogue_items_sha256,
        "shard_count": shard_count,
        "status": "pending",
        "jobs": jobs,
        "state_sha256": "",
    }
    state["state_sha256"] = sha256_json(state, omit_keys={"state_sha256"})
    return state


def ready_linz_jobs(state: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return the stable GitHub Actions matrix for currently runnable jobs."""

    _validate_state(state)
    jobs = cast(Mapping[str, Mapping[str, Any]], state["jobs"])
    ready = []
    for key in sorted(jobs):
        job = jobs[key]
        if job.get("status") != "pending":
            continue
        dependencies = job.get("dependencies", [])
        if all(jobs[dependency].get("status") == "complete" for dependency in dependencies):
            ready.append(
                {
                    "job_key": key,
                    "stage": job["stage"],
                    "shard": job["shard"],
                    "shard_count": job["shard_count"],
                    "operation_key": job["operation_key"],
                }
            )
    return ready


def record_linz_job_receipt(
    state: Mapping[str, Any],
    receipt: Mapping[str, Any],
) -> dict[str, Any]:
    """Advance one job after validating identity, dependencies, and budgets."""

    _validate_state(state)
    job_key = str(receipt.get("job_key") or "")
    jobs = state["jobs"]
    if not isinstance(jobs, Mapping) or job_key not in jobs:
        raise LinzPipelineError(f"receipt references unknown job: {job_key}")
    job = jobs[job_key]
    if not isinstance(job, Mapping):
        raise LinzPipelineError(f"pipeline job is invalid: {job_key}")
    required = {
        "job_key",
        "operation_key",
        "input_sha256",
        "output_sha256",
        "storage_bytes",
        "egress_bytes",
        "recorded_at",
    }
    missing = sorted(required - set(receipt))
    if missing:
        raise LinzPipelineError(f"pipeline receipt is missing fields: {missing}")
    if receipt["operation_key"] != job.get("operation_key"):
        raise LinzPipelineError("pipeline receipt operation key mismatch")
    if receipt["input_sha256"] != state.get("archive_plan_sha256"):
        raise LinzPipelineError("pipeline receipt input hash mismatch")
    output_digest = receipt["output_sha256"]
    if (
        not isinstance(output_digest, str)
        or len(output_digest) != 64
        or any(character not in "0123456789abcdef" for character in output_digest)
    ):
        raise LinzPipelineError("pipeline receipt output digest is not SHA-256")
    for field in ("storage_bytes", "egress_bytes"):
        if isinstance(receipt[field], bool) or not isinstance(receipt[field], int):
            raise LinzPipelineError(f"pipeline receipt {field} must be an integer")
        if receipt[field] < 0:
            raise LinzPipelineError(f"pipeline receipt {field} must be non-negative")
    budgets = job["budgets"]
    if receipt["storage_bytes"] > budgets["maximum_storage_bytes"]:
        raise LinzPipelineError("pipeline job exceeded its storage budget")
    if receipt["egress_bytes"] > budgets["maximum_egress_bytes"]:
        raise LinzPipelineError("pipeline job exceeded its egress budget")
    incomplete = [
        dependency
        for dependency in job["dependencies"]
        if jobs[dependency].get("status") != "complete"
    ]
    if incomplete:
        raise LinzPipelineError(f"pipeline job dependencies are incomplete: {incomplete}")

    normalised_receipt = dict(receipt)
    normalised_receipt["receipt_sha256"] = sha256_json(
        normalised_receipt, omit_keys={"receipt_sha256"}
    )
    existing = job.get("receipt")
    if existing is not None:
        if existing != normalised_receipt:
            raise LinzPipelineError(f"conflicting receipt for completed job: {job_key}")
        return dict(state)

    updated = cast(dict[str, Any], json.loads(json.dumps(state)))
    updated["jobs"][job_key]["status"] = "complete"
    updated["jobs"][job_key]["receipt"] = normalised_receipt
    statuses = {value["status"] for value in updated["jobs"].values()}
    updated["status"] = "complete" if statuses == {"complete"} else "in-progress"
    updated["state_sha256"] = sha256_json(updated, omit_keys={"state_sha256"})
    return updated


def _validate_state(state: Mapping[str, Any]) -> None:
    expected = sha256_json(state, omit_keys={"state_sha256"})
    if state.get("state_sha256") != expected:
        raise LinzPipelineError("LINZ pipeline state hash mismatch")
    jobs = state.get("jobs")
    if not isinstance(jobs, Mapping) or not jobs:
        raise LinzPipelineError("LINZ pipeline has no jobs")
    for key, job in jobs.items():
        if not isinstance(job, Mapping):
            raise LinzPipelineError(f"LINZ pipeline job is invalid: {key}")
        dependencies = job.get("dependencies")
        if not isinstance(dependencies, list) or any(
            not isinstance(dependency, str) or dependency not in jobs for dependency in dependencies
        ):
            raise LinzPipelineError(f"LINZ pipeline job has invalid dependencies: {key}")
