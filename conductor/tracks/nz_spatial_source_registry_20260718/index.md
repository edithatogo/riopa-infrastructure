# Evidence index: New Zealand spatial source and authority registry

- **Track ID:** `nz_spatial_source_registry_20260718`
- **Status:** `active`
- **Target release:** `0.4.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Operational`
- **Risk / priority:** `High` / `P0`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Spatial data lead
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/39

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-004-catalogue-disposition-pipeline-20260731` | Plan-bound catalogue scope flows through content-bound detail, service and planning stages | `src/riopa_provenance/linz_catalog.py`, `src/riopa_provenance/linz_enrichment.py`, `src/riopa_provenance/linz_inventory.py`, `src/riopa_provenance/linz_pipeline.py`, `tests/test_linz_pipeline.py` | Deterministic synthetic orchestration tests pass; no live catalogue claim |
| `DATASET-ARCHIVE-ROUTING-20260802` | Missing public national, council, network, timetable and facility sources have an archive-first ownership and incorporation plan | `docs/public-dataset-archive-incorporation-plan-20260802.json`, `docs/public-dataset-archive-incorporation-plan-20260802.md`, `tests/test_public_dataset_archive_plan.py` | Cross-repository issues routed; source payload capture, completeness and continuing freshness remain pending |
| `STATS-NZ-MESHBLOCK-ARCHIVE-20260802` | The Stats NZ Meshblock 2026 source identity, edition, rights, service schema and complete raw capture are revision-bound | [Hugging Face packet revision](https://huggingface.co/datasets/edithatogo/riopa-public-data-archive/tree/3f2dc0a4d95a4fcb495551098d58fc5bce9c9202), `docs/public-dataset-archive-incorporation-plan-20260802.json` | Complete geography archive verified; population tables, registry projections, continuing freshness and broader authority coverage remain open |
| `NZ-REGISTRY-BASELINE-20260822` | Bounded authority/source-family baseline with explicit disabled national families | `docs/nz-spatial-registry-baseline-20260822.json`, `config/source-registry/nz-spatial-pilot.yaml`, `tests/test_nz_spatial_registry_baseline.py` | Tasks 1.1–1.3 pass bounded validation; complete authority inventory, live discovery, archive coverage and continuing freshness remain open |
| `NZ-CONNECTOR-READINESS-20260824` | Declared pilot endpoint mechanisms are classified for metadata rehearsal versus credential/operator-gated execution | `src/riopa_provenance/registry.py:classify_connector_readiness`, `tests/test_source_registry_readiness.py`, `docs/nz-spatial-connector-readiness-contract-20260824.json` | Projection is fail-closed and non-contacting; live discovery, health, rights, completeness and authority remain open |
| `NZ-SOURCE-CHANGE-EVENTS-20260825` | Stable source/service/version identity and digest-only change events | `src/riopa_provenance/registry.py:SourceIdentity`, `src/riopa_provenance/registry.py:build_source_change_event`, `tests/test_source_registry_readiness.py` | Pure contract tests pass; endpoint health, rights, authority and completeness remain open |

The same revision’s Conductor regeneration receipt records the methods hash,
roadmap status, generated issue graph and full quality harness. This closes only
the bookkeeping task; source authority, rights, preservation and release gates
remain open (`docs/source-registry-conductor-regeneration-20260825.json`).

| `NZ-SOURCE-HEALTH-QUARANTINE-20260825` | Fail-closed health, disappearance and terms-change evaluation over declared archived observations | `src/riopa_provenance/registry.py:evaluate_declared_source_health`, `docs/nz-source-health-quarantine-contract-20260825.json`, `tests/test_source_registry_readiness.py` | Missing, degraded, terms-changed and not-observed records quarantine; no live health, authority, completeness or national claim is made |
| `NZ-SOURCE-METADATA-SNAPSHOT-20260825` | Content-addressed declared metadata, capability, terms and rights snapshot | `src/riopa_provenance/registry.py:build_declared_source_snapshot`, `docs/nz-source-metadata-snapshot-contract-20260825.json`, `tests/test_source_registry_readiness.py` | Non-contacting snapshot contract passes; payload capture, preservation acceptance and authority coverage remain open |
| `NZ-DECLARED-PLAN-DISCOVERY-20260825` | Non-contacting queue for declared planning-document endpoints and explicit not-observed fields | `src/riopa_provenance/registry.py::build_declared_plan_discovery`, `docs/nz-declared-plan-discovery-contract-20260825.json`, `tests/test_registry.py` | Discovery metadata is preserved and promotion-disabled; document capture, provision extraction, legal status, authority and preservation remain open |
| `NZ-SOURCE-REGISTRY-RELEASE-CANDIDATE-20260825` | Deterministic content-addressed registry and coverage release candidate | `src/riopa_provenance/registry.py::build_registry_release_candidate`, `docs/nz-source-registry-release-candidate-contract-20260825.json`, `tests/test_registry.py` | Candidate is unpublished and promotion-disabled; current-authority completeness, payload preservation, rights, publication and accountable release decision remain open |
| `NZ-SOURCE-REGISTRY-CLOSEOUT-20260826` | Link implementation, tests, agent-panel, migration and release-candidate evidence for the bounded registry slice | `docs/nz-source-registry-closeout-evidence-20260826.json`, `tests/test_nz_source_registry_closeout_evidence.py` | Repository-owned closeout links pass; current-authority completeness, payload preservation, external participation and accountable release remain open |

## Blocking defects

- Live national catalogue/authority coverage and all other archive packets listed in the public-dataset plan remain pending; the Meshblock 2026 geography slice is complete.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required agent-panel lenses: Governance analyst, API/schema analyst, Data-governance analyst, Operations analyst.

This index is deliberately bounded while the track remains `active`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
