# Evidence index: Supermarket access, zoning and health-geography reference study

- **Track ID:** `supermarket_health_pilot_20260718`
- **Status:** `active`
- **Target release:** `0.8.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Reference`
- **Risk / priority:** `High` / `P1`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Research lead
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/109

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-010-non-operational-pilot-envelope-20260731` | Reference pilot outputs explicitly reject clinical, legal, commercial and live-operational suitability | `src/riopa_provenance/analysis.py`, `tests/test_analysis.py`, `reports/wp010-synthetic-methods-core.md` | Non-operational envelope passes on synthetic inputs; no supermarket dataset, reproduction or empirical health finding is claimed |
| `WP-010-public-source-intake-20260801` | Candidate population and supermarket sources retain explicit rights and acquisition state | `config/source-registry/wp010-public-pilot-candidates.yaml`, `tests/test_wp010_benchmark.py` | Population metadata is staged; supermarket acquisition remains rights-blocked and no empirical pilot is claimed |
| `WP-010-osm-regional-observation-20260801` | A bounded OSM sensitivity source is captured locally without being treated as authoritative | `scripts/capture_wp010_public_sources.py`, `tests/test_wp010_public_sources.py`, `reports/wp010-synthetic-methods-core.md` | Nine regional supermarket POIs observed; raw geometry remains local and completeness is not claimed |
| `SUPERMARKET-PREREGISTRATION-20260825` | Reference-only baseline estimands, geography, population, exclusions and discrepancy handling | `docs/supermarket-health-preregistration-20260825.json`, `tests/test_supermarket_preregistration.py` | Synthetic/non-clinical template validates; no supermarket dataset, empirical health finding, causal claim or external reproduction is enabled |
| `SUPERMARKET-DENSITY-REFERENCE-20260825` | Deterministic density and population-normalised reference calculation preserves missing facility and denominator coverage | `src/riopa_provenance/supermarket.py`, `tests/test_supermarket_density.py`, `docs/supermarket-density-reference-contract-20260825.json` | Caller-supplied reference helper passes; real archives, study reproduction, population authority, health linkage and release gates remain open |
| `SUPERMARKET-REFERENCE-COMPARISON-20260825` | Compare declared reference and motivating-study fields while preserving mismatch and missing-field evidence | `src/riopa_provenance/supermarket.py`, `tests/test_supermarket_density.py`, `docs/supermarket-reference-comparison-20260825.json` | Descriptor alignment is reported as not reproduced; no motivating-study payload, external reproduction, empirical health evidence or promotion is enabled |
| `SUPERMARKET-INTEGRATED-REFERENCE-CORE-20260825` | Versioned public facility binding, distinct access/context/ecological-health constructs, sensitivity families, cited planning exclusions and complete Pareto trade-offs | `src/riopa_provenance/supermarket_pilot.py`, `tests/test_supermarket_pilot.py`, `docs/supermarket-integrated-reference-contract-20260825.json`, `tests/test_supermarket_integrated_reference_contract.py` | Repository-owned integration, negative tests and Conductor review fixes pass over fixtures/caller-supplied records; negative measures and exposed suppressed-cell rates fail, planning status is re-derived, and no acquisition, empirical analysis, legal status, preferred site, qualification or promotion is claimed |
| `SUPERMARKET-ARCHIVED-SOURCE-20260829` | Qualify an exact-edition public food-premise archive as a bounded reference input | `docs/supermarket-archived-source-qualification-20260829.json`, `tests/test_supermarket_archived_source_qualification.py`, [Hugging Face archive revision](https://huggingface.co/datasets/edithatogo/riopa-public-data-archive/tree/001137c0df64e9f8a7b0539fd0286a7cd5819ce7) | Hamilton payload is content-addressed with 3,245 features and 241 supermarket-classified records (108 marked active); regional, source-classified and non-authoritative, with no currentness or national claim |
| `WP-010-SINGLE-DEVELOPER-CLOSEOUT-20260829` | Bounded public/reference pilot and agent-operated reproduction satisfy the work-package contract | `docs/wp010-single-developer-closeout-20260829.json`, `docs/v1-agent-operated-journeys-20260825.json` | WP-010 repository scope is complete; empirical health, national completeness, operative planning and promotion claims remain disabled |

The same revision’s Conductor regeneration receipt records the methods hash,
roadmap status, generated issue graph and full quality harness. This closes only
the bookkeeping task; public food-retail acquisition, rights, national,
operational, external and release gates remain open (`docs/supermarket-conductor-regeneration-20260825.json`).

## Blocking defects

- All five dependencies remain incomplete at M1: planning rules, accessibility, facility registry, facility location and causal health methods.
- Rights-cleared versioned supermarket/population inputs and factual motivating-study reproduction remain unavailable.
- Representative multimodal access, facility reconciliation, empirical ecological-health and sensitivity analyses have not been executed.
- Operative planning linkage, authority review and representative solver/robustness alternatives remain unavailable.
- Agent-panel qualification, a complete preserved research object, independent reproduction, publication and release authority remain open.

## Decisions, exceptions and limitations

- Synthetic contract evidence is not a supermarket pilot result.
- Bounded integration accepts only public, non-authoritative facility assertions and caller-supplied aggregate records; it cannot establish completeness, individual or causal health effects, planning permission, consent certainty, commercial viability or a preferred location.

## Review and handover

Required agent-panel lenses: Data-governance analyst, Research-object analyst, Quantitative methods analyst, Scientific-methods analyst.

This index is deliberately non-assertive while the track remains `active` at M1. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
