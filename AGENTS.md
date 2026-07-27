# Codex operating instructions for RIOPA Infrastructure

These instructions apply to the whole repository. More specific `AGENTS.md` files may narrow them in subdirectories, but must not weaken safety, provenance, quality, or release gates.

## Mission

Continue implementing the RIOPA programme from the present development snapshot toward a stable, hardened, supported v1.0. Treat the Conductor artefacts, programme contracts, source registries, issue graph, and evidence requirements as the programme source of truth.

Do not stop after analysing, bootstrapping, or writing a plan. Make the safest useful changes that can be completed in the current session, test them, update their evidence and documentation, commit them, push when a verified remote is available, then continue with the next ready work package until genuinely blocked or the execution environment ends.

## Start of every session

1. Read, in order:
   - `CODEX_AUTONOMOUS_IMPLEMENTATION.md`
   - `HANDOFF_STATUS.md`
   - `conductor/product.md`
   - `conductor/workflow.md`
   - `conductor/tracks.md`
   - `ROADMAP_STATUS.md`
   - the specification, plan, metadata and evidence index for every track touched.
2. Run `python scripts/codex_orchestrator.py next --write` to create a machine-local work packet under `.riopa-local/codex/`.
3. Inspect `git status`, remotes, current branch, recent history and `.riopa-local/workspace-repositories.json` before modifying this or any related repository.
4. Run focused baseline tests before editing. Run the broadest affordable harness before committing.

## Conductor and issue discipline

- Every material change must map to a Conductor track and, once GitHub is active, a GitHub issue.
- Do not mark a track complete because code exists. Completion requires the acceptance criteria and evidence in its `spec.md`, `plan.md`, `metadata.json`, and `index.md`.
- Keep generated issue configuration, track metadata, Project state, documentation, tests and code consistent.
- Record blockers as explicit issues and local work-package state; do not silently omit them.
- Preserve historical release evidence. Create new evidence for new code rather than rewriting earlier attestations.

## Git discipline

- Preserve the reconstructed artifact history and all later commits.
- Never force-push, rewrite published history, delete a remote, or use destructive reset on a pre-existing worktree.
- Work on the current branch unless the live repository policy or issue workflow requires an issue-linked feature branch.
- Commit coherent, reviewable units with conventional commit messages.
- Before each commit: inspect the staged diff, run focused tests, scan for credentials and confirm generated/bulk data are excluded.
- Before ending: wait for commands to complete, commit intended changes, and leave the worktree clean unless an unavoidable blocker is documented.

## Related repositories

- Discover clones by normalised remote URL using `scripts/discover_workspace_repositories.py`; never infer identity from a folder name alone.
- Do not modify a dirty related clone.
- Respect each repository's `write_policy` in `config/workspace/repositories.json`.
- Cross-repository work must have a linked issue, a focused branch, its own tests and a separate commit/PR. Never mix unrelated repositories in one commit.
- Reuse the user's own repositories where they provide the required capability; do not create overlapping external abstractions without first checking the adoption matrix.

## Engineering and quality rules

- Python 3.12/3.13, `uv`, strict MyPy, Ruff, Bandit, pytest and branch-aware coverage are mandatory for the current implementation.
- Do not lower, bypass or hide the 90% stable-release coverage target. Improve coverage with meaningful unit, property, contract, integration, failure-injection and reproducibility tests.
- Keep raw evidence immutable and content-addressed. Canonical state and physical formats are versioned projections.
- Use RFC 8785/cross-language canonicalisation for signed or chained JSON.
- Fail closed on integrity, rights, legal-status, provenance and publication ambiguity.
- Never claim feature/row lineage, legal authority, external conformance, causal inference, operational maturity or reproducibility beyond the available evidence.
- Prefer deterministic pure cores around network, storage and external-service adapters.
- Make retries bounded and idempotent; preserve failed-attempt evidence.
- Treat security, rights, Māori data sovereignty, privacy, preservation and accessibility as architectural requirements, not later documentation tasks.

## Data and credential safety

- Never print, persist, commit or expose secrets. Required credentials include but are not limited to `LINZ_API_KEY`, GitHub, Hugging Face and Zenodo tokens.
- Do not commit live GIS payloads, Parquet, GeoParquet, DuckDB, rasters, caches, `.env` files or machine-local maps.
- Do not redistribute a source payload until its rights decision permits the exact target and representation.
- Large or live archival runs require bounded storage, resumability, explicit source registration and an evidence-backed publication plan.

## Autonomous priority order

Unless new evidence changes the critical path, work through `codex/implementation-queue.json` in order. The first priorities are:

1. reconcile the imported development code with Conductor evidence and restore comprehensive tests;
2. harden capture/runtime source health, retry, network and failure semantics;
3. implement hierarchical rights inheritance and resumable publication state;
4. operationalise catalogue-complete LINZ capture through sharded, resumable CI;
5. implement feature-level differences, lineage impact queries and external conformance;
6. execute a bounded real LINZ/council vertical slice when credentials, rights and network access permit;
7. implement cross-repository adapters and then accessibility, optimisation, simulation and applied pilots.

## Required end-of-work report

Report: commits created, tests and checks run, measured coverage, GitHub/Project/issue state, related repositories touched, evidence updated, remaining blockers, and the next work package. Do not claim remote actions, live data capture, publication or release maturity unless verified directly.
