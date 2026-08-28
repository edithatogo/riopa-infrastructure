# Plan: nz_spatial_archive_operations_20260719

## 1. Rollout planning

- [x] 1.1 Prioritise sources by public value, rights, technical readiness and risk in the bounded rollout contract. (`docs/nz-spatial-archive-rollout-plan-20260825.json`; `4b4da7e`)
- [x] 1.2 Define per-source schedules, backfill bounds, load limits and owners without contacting live endpoints. (`docs/nz-spatial-archive-rollout-plan-20260825.json`; `4b4da7e`)
- [x] 1.3 Establish exception, manual-review and retirement workflows with fail-closed status transitions. (`docs/nz-spatial-archive-rollout-plan-20260825.json`, `tests/test_nz_spatial_rollout_plan.py`; `4b4da7e`)

## 2. National automation

- [ ] 2.1 Deploy permitted machine-readable connectors in controlled waves.
- [x] 2.2 Implement the repository-owned delta decision, schema/capability drift and fail-closed quarantine core. (`src/riopa_provenance/archive_operations.py`, `tests/test_archive_operations.py`; `be70b30`) Live connector execution and incident resolution remain under 2.1, 3.2 and 3.3.
- [ ] 2.3 Build national snapshot assembly and partial-release handling.
  - [x] Implement digest-verified partial-release assembly that retains explicit exclusions and cannot authorize promotion. (`src/riopa_provenance/archive_operations.py`, `tests/test_archive_operations.py`; `be70b30`)

## 3. Coverage and operations evidence

- [ ] 3.1 Publish multidimensional coverage, freshness, quality, rights and status reports.
  - [x] Implement a bounded report generator that keeps authority, layer type, time depth, legal status, rights, quality, disposition and availability separate and never infers a national percentage. (`src/riopa_provenance/archive_operations.py`, `tests/test_archive_operations.py`; `be70b30`)
- [ ] 3.2 Operate for the required beta SLO evidence period.
- [ ] 3.3 Resolve or formally accept operational exceptions.

## 4. Stable national service gate

- [ ] 4.1 Conduct national restore, correction and source-retirement exercises.
- [ ] 4.2 Validate capacity, preservation and cost controls.
- [ ] 4.3 Approve and publish the stable operating model and coverage limitations.

## Track closeout

- [x] C.1 Link the current implementation and test evidence in `index.md`; review, migration and release evidence remain explicitly unavailable.
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected. The locked methods generation, roadmap status, issue graph and full quality harness passed; the methods output was temporary and not a release artifact (`docs/nz-archive-operations-conductor-regeneration-20260825.json`).
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [x] C.4 Update metadata status and target-release evidence through the Conductor workflow; metadata remains `active`/M1 for target release `0.8.0`, with hosted recovery, preservation, beta SLO duration, national restore/cost evidence, external operation and accountable-authority gates unresolved.
