# RIOPA development handoff status

**Handoff date:** 20 July 2026  
**Base roadmap release:** 0.2.0 / M1  
**Status:** unreleased development handoff; not a tagged release and not stable v1

This tree combines the verified 0.2.0 roadmap/Conductor bundle with subsequent development implementations for faithful HTTP capture, ArcGIS and WFS archival, LINZ baseline/changeset processing, complete LINZ catalogue planning and export, spatial materialisation, lineage projection, rights-aware publication staging, hardened validation and CI/CD scaffolding.

## Verified for this handoff

- Locked installation succeeds with `uv sync --extra dev --extra spatial --frozen`.
- The command-line package imports and `riopa --help` succeeds.
- The existing automated suite passes: **84 tests**.
- `scripts/ci_quality.sh` passes, including Ruff, strict MyPy, Bandit, action-pin checks, workflow-policy checks, schema and example validation, source-registry validation, roadmap/evidence validation, deterministic issue generation, package build, Twine checks and CycloneDX SBOM validation.
- `scripts/ci_reproducibility.sh` passes and produces byte-identical verified research objects.
- The GitHub/Conductor bootstrap completes in non-writing dry-run mode.
- The local-clone discovery tool correctly identifies the primary repository by normalised remote URL and reports missing required related clones without modifying them.
- Historical 0.2.0 evidence is preserved byte-for-byte under `conductor/release-evidence/artifacts/0.2.0/`; newer development files do not masquerade as old release evidence.

## Known qualification gap

The newer archive and LINZ modules were recovered from development outputs without their complete focused test suite. The available tests cover the merged package at approximately **38.2% combined branch-aware coverage** (40.0% statement and 33.5% branch coverage); therefore the repository's 90% full-package coverage gate is expected to fail until those tests are restored or rebuilt. This is a visible development blocker, not a reason to lower or bypass the stable quality target.

The bootstrap prompt requires the agent to record this accurately, open a tracking issue, and avoid tagging or publishing a release. The next implementation branch should restore comprehensive unit, property, integration, failure-injection and deterministic-fixture tests for the new modules before the release workflow is enabled.

## Remote and data state

This handoff has **not** independently created or verified:

- `https://github.com/edithatogo/riopa-infrastructure`;
- a repository Project, issue graph or ruleset;
- a live LINZ or council capture;
- a Hugging Face dataset repository;
- a Zenodo deposition or DOI;
- secrets, scheduled archival jobs or operational history;
- an external clean-room reproduction.

The included `BOOTSTRAP_AGENT_PROMPT.md` and guarded scripts establish the local Git repository, discover related clones, create or reconcile the GitHub remote, wire `origin`, push without force, configure conservative repository settings, and create/reconcile the Conductor Project and issue graph when run under an authenticated GitHub CLI session.

## Files to start with

1. `BOOTSTRAP_AGENT_PROMPT.md` — paste-ready execution prompt.
2. `config/workspace/repositories.json` — expected related repositories and write policies.
3. `scripts/discover_workspace_repositories.py` — read-only clone discovery; optionally clones explicitly permitted missing repositories.
4. `scripts/bootstrap_local_handoff.sh` — guarded local and GitHub bootstrap wrapper.
5. `scripts/bootstrap_github.sh` — idempotent repository, Project, label and issue orchestration.
