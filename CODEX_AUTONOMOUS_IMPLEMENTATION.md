# Autonomous Codex implementation brief

## Outcome

Starting from this handoff, establish the repository locally with its included Git history, restore it from the included Git bundle if necessary, discover relevant local clones, create or reconcile `edithatogo/riopa-infrastructure`, wire and safely push `origin`, activate the configured GitHub Project and issue graph, then continue implementing the stable-v1 programme autonomously.

This is an unreleased development handoff. Do not tag it as v1.0, publish data, mint a DOI or claim operational maturity merely because bootstrap succeeds.

## Execute, do not merely describe

When the repository is first opened, run:

```bash
bash scripts/bootstrap_codex_handoff.sh --apply --clone-missing
```

If GitHub authentication or scopes are unavailable, complete every local phase, record the exact remote blocker under `.riopa-local/bootstrap/`, and continue implementation locally. Do not discard useful local work merely because a remote action is blocked.

After the bootstrap script returns, read the active work packet it creates under `.riopa-local/codex/` and continue immediately. Do not end the session at “bootstrap complete”.

## Bootstrap invariants

- The ZIP normally contains `.git/` with reconstructed artifact history plus `handoff/riopa-infrastructure.bundle` as a recovery copy.
- The history is intentionally transparent: it reconstructs the v0.1.0, v0.2.0 and development artifact snapshots, then adds the Codex handoff harness. It is not represented as the lost original authoring history.
- If `.git/` is absent after extraction, restore it from the bundle and verify that the worktree matches `main` before any remote action.
- Reuse a correctly matching existing remote. Refuse unrelated or divergent history and never force-push.
- Use `config/workspace/repositories.json` and normalised remotes to find related repositories.
- Do not modify dirty related clones or the planned `nz-spatial-archive` repository during initial bootstrap.

## Autonomous implementation loop

Repeat this loop while useful work remains and the environment permits:

1. **Orient**
   - run `python scripts/codex_orchestrator.py status` and `... next --write`;
   - read the mapped Conductor tracks and live issue(s);
   - inspect recent commits, open defects and current test/coverage output.
2. **Choose a bounded increment**
   - select the smallest vertical slice that advances acceptance criteria and can be objectively verified;
   - state the intended evidence before implementation;
   - avoid speculative framework expansion when a real adapter/test can validate the contract.
3. **Implement**
   - use typed, deterministic, testable cores;
   - keep network and storage side effects behind explicit adapters;
   - add migrations, failure semantics, observability and documentation with the feature rather than later.
4. **Verify**
   - run focused tests while iterating;
   - run Ruff, strict MyPy, Bandit and the broadest relevant pytest/coverage suite before commit;
   - run reproducibility, schema, issue-drift, package and workflow-policy checks when affected;
   - do not weaken gates to obtain green output.
5. **Record evidence**
   - update track evidence indexes and metadata only to the level actually demonstrated;
   - update generated issue configuration and live issue comments/labels where available;
   - capture commands, outputs, digests and limitations without credentials.
6. **Commit and synchronise**
   - review the staged diff and secret scan;
   - create a coherent conventional commit;
   - push normally when origin and upstream are verified;
   - update the local work-package state.
7. **Continue**
   - move to the next unblocked package rather than stopping for a general progress summary.

## First implementation campaign

### Campaign A — baseline reconciliation and test restoration

- Inventory every imported module, existing test and uncovered branch.
- Reconcile actual implementation against the corresponding Conductor track and issue configuration.
- Restore focused tests for `arcgis`, `wfs`, `linz`, `linz_catalog`, `linz_enrichment`, `linz_export`, `linz_inventory`, `linz_federation`, `spatial`, `lineage`, `publication`, `capture`, `validation` and `crate`.
- Add property tests for manifests, event graphs, path safety, pagination and state machines.
- Add failure-injection tests for interrupted changeset application and publication retries.
- Raise measured package coverage toward the existing 90% target without exclusion games.

### Campaign B — operational archival hardening

- Implement source-health observations, freshness classification, schema/licence change detection and issue deduplication.
- Implement bounded idempotent retries, `Retry-After`, circuit breaking and attempt evidence.
- Harden DNS resolution and connection pinning against private-address and rebinding attacks while preserving TLS hostname validation.
- Add ArcGIS attachments, related tables, domains, subtypes and service/item metadata.
- Add deterministic snapshot differences for sources without changesets.

### Campaign C — rights, publication and preservation

- Implement hierarchical rights inheritance from source through artifact and publication target.
- Implement a resumable, idempotent GitHub/Hugging Face/Zenodo publication state machine with reconciliation receipts.
- Bind Git commit, signed tag, GitHub release, Hugging Face revision, Zenodo concept/version DOI, snapshot and research-object identifiers.
- Add independent validators for RO-Crate, DataCite, CFF, CycloneDX, GeoParquet, PROV and OpenLineage profiles.
- Add signed checkpoints, attestations, rollback protection and preservation/fixity workflows.

### Campaign D — catalogue-complete LINZ operations

- Convert the catalogue workflow to bounded shards: catalogue, item details, service inventories, enriched catalogue, archive plan, payload batches and federation staging.
- Make jobs resumable and idempotent; record complete/failed/deferred/rights-blocked dispositions for every catalogue identity.
- Add storage/egress estimation, hot/warm/cold tiers and raster-specific validation.
- Periodically reconcile accumulated changesets against a fresh full export.
- Preserve catalogue history, removals, replacements and service migrations.

### Campaign E — real vertical slice and ecosystem adoption

When network, credentials and rights allow, execute one small live slice with one LINZ layer, one council ArcGIS source, one WFS/planning source and one facility source. Keep it bounded, publish nothing without approval, and generate a complete research object and clean-room reconstruction evidence.

Then implement native RIOPA adapters in clean related clones using separate issues/branches, beginning with `fyi-cli` and `fyi-archive`.

### Campaign F — analytics and applications

Implement accessibility as a separate reusable engine, then facility registry/entity resolution, solver cores and verified domain adapters. Progress supermarket, ambulance and hospital pilots only after their data, rights, validation and governance prerequisites are explicit.

## Stop conditions

Stop only when one of these applies:

- the execution environment is ending;
- a required credential/approval is unavailable and no local/mock/contract work remains;
- proceeding would risk data loss, rights breach, security compromise or destructive remote changes;
- every currently unblocked work package is complete and evidenced.

When stopped, leave a clean committed worktree where possible and write a precise continuation packet under `.riopa-local/codex/`.
