from __future__ import annotations

import pytest

from riopa_provenance.hashing import sha256_json
from riopa_provenance.linz_pipeline import (
    LinzPipelineError,
    initialise_linz_pipeline,
    ready_linz_jobs,
    record_linz_job_receipt,
)


def pipeline() -> dict[str, object]:
    return initialise_linz_pipeline(
        archive_plan_id="urn:riopa:linz-archive-plan:test",
        archive_plan_sha256="a" * 64,
        catalogue_items_sha256="b" * 64,
        shard_count=2,
        maximum_storage_bytes=100,
        maximum_egress_bytes=50,
    )


def receipt(state: dict[str, object], job_key: str, **overrides: object) -> dict[str, object]:
    jobs = state["jobs"]
    assert isinstance(jobs, dict)
    job = jobs[job_key]
    return {
        "job_key": job_key,
        "operation_key": job["operation_key"],
        "input_sha256": state["archive_plan_sha256"],
        "output_sha256": "c" * 64,
        "storage_bytes": 10,
        "egress_bytes": 5,
        "recorded_at": "2026-07-31T09:00:00Z",
        **overrides,
    }


def test_pipeline_exposes_only_dependency_ready_ci_jobs() -> None:
    state = pipeline()
    assert ready_linz_jobs(state) == [
        {
            "job_key": "catalogue:0",
            "stage": "catalogue",
            "shard": 0,
            "shard_count": 2,
            "operation_key": state["jobs"]["catalogue:0"]["operation_key"],
        }
    ]
    state = record_linz_job_receipt(state, receipt(state, "catalogue:0"))
    assert [(job["stage"], job["shard"]) for job in ready_linz_jobs(state)] == [
        ("details", 0),
        ("details", 1),
        ("services", 0),
        ("services", 1),
    ]


def test_pipeline_receipts_are_resumable_idempotent_and_conflict_safe() -> None:
    state = pipeline()
    catalogue_receipt = receipt(state, "catalogue:0")
    resumed = record_linz_job_receipt(state, catalogue_receipt)
    assert resumed["status"] == "in-progress"
    assert record_linz_job_receipt(resumed, catalogue_receipt) == resumed
    with pytest.raises(LinzPipelineError, match="conflicting receipt"):
        record_linz_job_receipt(
            resumed,
            {**catalogue_receipt, "output_sha256": "d" * 64},
        )


def test_pipeline_fails_closed_on_dependencies_and_resource_budgets() -> None:
    state = pipeline()
    with pytest.raises(LinzPipelineError, match="dependencies are incomplete"):
        record_linz_job_receipt(state, receipt(state, "details:0"))
    with pytest.raises(LinzPipelineError, match="storage budget"):
        record_linz_job_receipt(
            state,
            receipt(state, "catalogue:0", storage_bytes=101),
        )
    with pytest.raises(LinzPipelineError, match="egress budget"):
        record_linz_job_receipt(
            state,
            receipt(state, "catalogue:0", egress_bytes=51),
        )
    corrupted = pipeline()
    corrupted["jobs"]["details:0"]["dependencies"] = ["missing:0"]
    corrupted["state_sha256"] = sha256_json(corrupted, omit_keys={"state_sha256"})
    with pytest.raises(LinzPipelineError, match="invalid dependencies"):
        ready_linz_jobs(corrupted)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"shard_count": 0},
        {"maximum_storage_bytes": 0},
        {"archive_plan_sha256": "not-a-digest"},
    ],
)
def test_pipeline_rejects_unbounded_or_unbound_configuration(
    kwargs: dict[str, object],
) -> None:
    values = {
        "archive_plan_id": "urn:riopa:linz-archive-plan:test",
        "archive_plan_sha256": "a" * 64,
        "catalogue_items_sha256": "b" * 64,
        "shard_count": 2,
        "maximum_storage_bytes": 100,
        "maximum_egress_bytes": 50,
        **kwargs,
    }
    with pytest.raises(LinzPipelineError):
        initialise_linz_pipeline(**values)
