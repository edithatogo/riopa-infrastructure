# Normative contract ownership and migration matrix

Every normative JSON Schema in `schemas/` has an explicit owner and the same
fail-closed compatibility path. The matrix is intentionally boring: it makes
the boundary auditable and prevents a schema from silently acquiring a new
owner or compatibility policy.

| Contract | Version owner | Compatibility policy | Migration path / executable check |
|---|---|---|---|
| `accessibility-matrix.schema.json` | Accessibility maintainer | preserve units, unreachable semantics and network identity; semantic changes require migration | `scripts/ci_quality.sh`; `tests/test_accessibility.py` |
| `accessibility-measure.schema.json` | Accessibility maintainer | preserve measure identifiers, denominators and uncertainty semantics | `scripts/ci_quality.sh`; `tests/test_accessibility.py` |
| `accessibility-scenario.schema.json` | Accessibility maintainer | version mode, impedance and scenario assumptions independently | `scripts/ci_quality.sh`; `tests/test_accessibility.py` |
| `adapter-mapping.schema.json` | API/schema analyst | retain source and target versions; breaking mappings require explicit replacement | `scripts/ci_quality.sh`; `tests/test_adapters.py` |
| `analysis-preregistration.schema.json` | Scientific-method maintainer | registered designs are immutable; amendments retain original identity and rationale | `scripts/ci_quality.sh`; `tests/test_analysis_preregistration.py` |
| `analysis-protocol.schema.json` | Scientific-method maintainer | version estimands and analysis assumptions; preserve protocol identity | `scripts/ci_quality.sh`; `tests/test_analysis.py` |
| `archived-capture-view.schema.json` | Provenance maintainer | experimental opt-in projection; native 1.0 records and hashes remain immutable | `tests/test_capture_migration.py`; `docs/archived-capture-view-migration.md` |
| `artifact.schema.json` | Provenance maintainer | additive fields only within a minor; breaking changes require a major profile | `scripts/ci_quality.sh`; `tests/test_validation_integrity.py` |
| `canonical-crosswalk.schema.json` | Spatial maintainer | preserve source/target identities and temporal validity; changed mappings require successors | `scripts/ci_quality.sh`; `tests/test_spatial_crosswalk.py` |
| `governance-decision.schema.json` | Governance analyst | decisions remain scope-bound and attributable; changed permissions require new evidence | `scripts/ci_quality.sh`; `tests/test_governance.py` |
| `gtfs-archive-disposition.schema.json` | Archive maintainer | preserve feed hashes and exact rights scope; disposition changes require new evidence | `scripts/ci_quality.sh`; `tests/test_gtfs_archive_disposition.py` |
| `health-analysis-design.schema.json` | Scientific-method maintainer | version causal assumptions, estimands and missing-data rules with migration evidence | `scripts/ci_quality.sh`; `tests/test_health_analysis_design.py` |
| `hosted-evidence.schema.json` | Release authority | retain exact revision, run and artifact identity; changed evidence requires new records | `scripts/ci_quality.sh`; `tests/test_hosted_evidence.py` |
| `interoperability-conformance-contract.schema.json` | Interoperability maintainer | version profile claims and validator expectations; breaking changes require conformance migration | `scripts/ci_quality.sh`; `tests/test_interoperability_conformance_contract.py` |
| `linz-archive-plan.schema.json` | Archive maintainer | additive disposition fields; preserve catalogue identity | `scripts/ci_quality.sh`; `tests/test_linz_catalog.py` |
| `materialization.schema.json` | Materialisation maintainer | projections may add optional fields, never redefine meaning | `scripts/ci_quality.sh`; `tests/test_crate.py` |
| `maturity-model.schema.json` | Programme owner | release-level changes require roadmap migration | `scripts/ci_quality.sh`; `tests/test_roadmap.py` |
| `methods-facts.schema.json` | Publication maintainer | additive facts with stable identifiers | `scripts/ci_quality.sh`; `tests/test_methods.py` |
| `nz-spatial-archive-rights-capability-health.schema.json` | Archive maintainer | preserve exact rights scope, capability state and health evidence; no implicit permission upgrade | `scripts/ci_quality.sh`; `tests/test_nz_spatial_archive_rights_capability_health.py` |
| `operations-control.schema.json` | Operations maintainer | version SLO, recovery and retention requirements; preserve campaign evidence | `scripts/ci_quality.sh`; `tests/test_operations_control_contract.py` |
| `planning-transition.schema.json` | Planning maintainer | preserve operative version identity and temporal transitions; corrections require successors | `scripts/ci_quality.sh`; `tests/test_transitions.py` |
| `provenance-event.schema.json` | Provenance maintainer | event fields are append-only; hash semantics require a major profile | `scripts/ci_quality.sh`; `tests/test_lineage.py` |
| `publication-plan.schema.json` | Publication maintainer | preserve exact targets, representation and rights decisions; changed plans require revalidation | `scripts/ci_quality.sh`; `tests/test_publication.py` |
| `quality-report.schema.json` | Quality maintainer | metrics retain identifier and uncertainty semantics | `scripts/ci_quality.sh`; `tests/test_validation_integrity.py` |
| `release-evidence.schema.json` | Release authority | gate IDs and evidence references are migration-bound | `scripts/ci_quality.sh`; `tests/test_roadmap_hardening.py` |
| `release-roadmap.schema.json` | Programme owner | release train migrations preserve monotonic maturity | `scripts/ci_quality.sh`; `tests/test_roadmap_hardening.py` |
| `repository-template-contract.schema.json` | API/schema analyst | version producer/consumer interfaces; breaking template changes require adoption migration | `scripts/ci_quality.sh`; `tests/test_repository_template_contract.py` |
| `rights-inventory.schema.json` | Governance analyst | rights decisions are fail-closed and append-only | `scripts/ci_quality.sh`; `tests/test_publication.py` |
| `snapshot-manifest.schema.json` | Archive maintainer | released manifests are immutable; corrections are successors | `scripts/ci_quality.sh`; `tests/test_crate.py` |
| `source-acquisition-approval.schema.json` | Governance analyst | approvals remain exact-source and scope-bound; changed scope requires fresh approval evidence | `scripts/ci_quality.sh`; `tests/test_source_acquisition_approval.py` |
| `source-health-observation.schema.json` | Source-registry maintainer | observations are append-only; preserve observation time, source identity and failure semantics | `scripts/ci_quality.sh`; `tests/test_validation_failures.py` |
| `source-record.schema.json` | Source-registry maintainer | source identity is stable across retrieval/version changes | `scripts/ci_quality.sh`; `tests/test_registry.py` |
| `source-registry.schema.json` | Source-registry maintainer | registry additions are compatible; identity changes require migration | `scripts/ci_quality.sh`; `tests/test_linz_catalog.py` |
| `spatial-feature-link.schema.json` | Spatial maintainer | preserve source identity, geometry digest and temporal assertions | `scripts/ci_quality.sh`; `tests/test_spatial.py` |
| `supermarket-archive-qualification.schema.json` | Archive maintainer | retain source hashes, rights and qualification limits; corrections require versioned evidence | `scripts/ci_quality.sh`; `tests/test_supermarket_archived_source_qualification.py` |
| `track-metadata.schema.json` | Programme owner | lifecycle transitions are explicit and timestamped | `scripts/ci_quality.sh`; `tests/test_roadmap_hardening.py` |
| `transformation-run.schema.json` | Provenance maintainer | input/output references remain immutable and hash-addressed | `scripts/ci_quality.sh`; `tests/test_lineage.py` |
| `v1-gate.schema.json` | Release authority | gate identifiers require explicit migration and review | `scripts/ci_quality.sh`; `tests/test_roadmap_hardening.py` |

The compatibility policy is governed by `docs/v1-release-policy.md`. A change
must update the schema, its fixtures/tests, this matrix and a migration note in
the same reviewable change; no compatibility claim is made until the relevant
test command passes.

The executable architecture fitness check requires exactly one complete row for
each current `schemas/*.schema.json` contract. This is the JSON Schema inventory;
API, CLI, model and research-object version axes remain governed separately by
`docs/v1-release-policy.md` and their owning track evidence. Listed checks are
migration validation entry points, not claims that a migration or stable
compatibility has already been qualified.
