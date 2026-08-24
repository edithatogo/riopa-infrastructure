# Bounded RIOPA usage guides

This guide is the repository-owned handoff for the current Python 3.14,
public-datasets-only, regional technical-preview scope. It is not a
production, clinical, dispatch, national or authoritative-data guide.

## User guide

Start with the [architecture](architecture.md) and [change and impact
queries](change-and-impact-queries.md). Use the Python package and synthetic
fixtures to inspect contracts and provenance. Treat every result as bounded by
the evidence envelope returned by the query or report.

## Operator guide

Run `uv sync --extra dev`, then `bash scripts/ci_quality.sh`. For a validated
snapshot, build the disposable lineage index with
`uv run riopa lineage build --manifest PATH --database PATH`. Preserve the
manifest and its digest alongside any derived index; never replace an
authoritative capture with a projection.

## Contributor guide

Use Python 3.14 only, add tests for every contract change, and run the quality
harness before opening a pull request. Do not commit credentials, live source
payloads, caches, databases or generated release bundles. Map material changes
to a Conductor task and regenerate `project/issues.yaml` with the roadmap
command.

## Maintainer guide

Review the track index, metadata and evidence register together. Re-query
protected-main hosted checks before merge. A green check does not establish
rights, preservation acceptance, external reproduction, elapsed-time soak, or
release-authority approval.

## Migration guide

Read the relevant versioned migration artifact before changing a contract:
[canonical migrations](ontology/migrations/), the [compatibility support
policy](compatibility-support-policy.md), and [conformance and release
verification](conformance-and-release-verification.md). Keep old evidence
addressable and record each transformation as a new digest-bound projection.

## Scope and disabled claims

This repository currently supports only bounded regional, public-dataset,
non-operational technical-preview work. Network, timetable, facility,
national, clinical and dispatch claims remain disabled until separately
evidenced. Agent-panel assessment cannot substitute for factual external-user
or operator participation or an accountable release-authority decision.
