# Evidence index: New Zealand spatial source and authority registry

- **Track ID:** `nz_spatial_source_registry_20260718`
- **Status:** `validating`
- **Target release:** `0.4.0`
- **Current maturity:** `M2`
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
| `NZ-SOURCE-REGISTRY-M2-PROMOTION-20260829` | Qualify the experimental registry executable-proof boundary against an exact source tree | `docs/nz-source-registry-m2-promotion-20260829.json`, `tests/test_nz_source_registry_m2_promotion.py` | Repository-owned registry, negative-path, snapshot, health and candidate evidence passes; M3-M6 gates remain open |
| `SOURCE-RIGHTS-PUBLICATION-DECISION-20260829` | Group missing and existing licences into maximum-lawful public archive tiers | `docs/source-rights-publication-decision-matrix-20260829.json`, `docs/source-rights-publication-decision-matrix-20260829.md`, `tests/test_source_rights_publication_decision_matrix.py` | Exact open terms permit Tier A publication for WCC Churton, the ambulance prototype and Greater Wellington GIS; authority, freshness, completeness and operational claims remain separate |
| `SOURCE-RIGHTS-ARCHIVE-DEFAULT-20260829` | Default to complete lawful capture and private preservation unless explicitly restricted | `docs/source-rights-archive-default-20260829.json`, `docs/source-rights-archive-default-20260829.md`, `tests/test_source_rights_archive_default.py` | Missing licences no longer block lawful capture or private preservation; full public payloads still require an affirmative legal basis |
| `PUBLIC-TIER-A-ARCHIVE-PUBLICATION-20260829` | Capture and publicly preserve the newly qualified Tier-A ArcGIS sources | `config/source-registry/public-archive-tier-a-20260829.yaml`, `docs/public-tier-a-archive-publication-20260829.json`, [public archive revision](https://huggingface.co/datasets/edithatogo/riopa-public-data-archive/tree/001137c0df64e9f8a7b0539fd0286a7cd5819ce7), `tests/test_public_tier_a_archive_publication.py` | Three content-addressed packets and 230 total features are public after hosted PR checksum verification; source-specific authority and operational non-claims remain attached |
| `EXISTING-PUBLIC-ARCHIVE-RIGHTS-20260829` | Qualify existing Hamilton, Marlborough and Stats NZ public archive packets | `docs/existing-public-archive-rights-qualification-20260829.json`, four `config/archive-sources/*.json` descriptors, `tests/test_existing_public_archive_rights.py` | Four immutable packet revisions are bound to applicable CC BY terms and attribution; completeness, currency, legal authority and fitness remain unclaimed |

## Blocking maturity gates

- M3 requires current-authority completeness, live source-rights and health
  validation, migration and representative failure handling.
- M4 requires repeated hosted health monitoring, SLO evidence and role-separated
  agent-operated workflows.
- M5 requires release-candidate security, recovery, panel and soak qualification.
- M6 requires a stable signed and preserved registry release, isolated
  multi-agent clean-room reproduction and the sole owner's signed decision.

The Meshblock 2026 geography slice is complete, but the remaining national
catalogue/authority coverage and archive packets remain pending.

## Decisions, exceptions and limitations

- Public payloads are preferred whenever exact-item or applicable
  publisher-wide open terms permit them. Unresolved payload rights default to
  public metadata, terms, receipts and digests rather than suppressing the
  source record.
- Exact-item exceptions, privacy, safety and restricted LINZ product terms
  override general open-data terms.
- Complete lawful capture and private preservation are the default unless an
  explicit restriction or applicable law, privacy, safety or technical limit
  requires narrower handling. Copyright silence alone is not public-copying
  permission.

## Review and handover

Required agent-panel lenses: Governance analyst, API/schema analyst, Data-governance analyst, Operations analyst.

This index is deliberately bounded while the track remains `validating` at
experimental M2. Status may advance only through `conductor/workflow.md`;
evidence must be immutable or version-addressed, agent-panel qualified where
required, and sufficient for the applicable release gates. The track is not
complete or archive-eligible, and this promotion passes no v0.4 release gate.
