# Normative contract ownership and migration matrix

Every normative JSON Schema in `schemas/` has an explicit owner and the same
fail-closed compatibility path. The matrix is intentionally boring: it makes
the boundary auditable and prevents a schema from silently acquiring a new
owner or compatibility policy.

| Contract | Version owner | Compatibility policy | Migration path / executable check |
|---|---|---|---|
| `artifact.schema.json` | Provenance maintainer | additive fields only within a minor; breaking changes require a major profile | `scripts/ci_quality.sh`; `tests/test_validation_integrity.py` |
| `linz-archive-plan.schema.json` | Archive maintainer | additive disposition fields; preserve catalogue identity | `scripts/ci_quality.sh`; `tests/test_linz_catalog.py` |
| `materialization.schema.json` | Materialisation maintainer | projections may add optional fields, never redefine meaning | `scripts/ci_quality.sh`; `tests/test_crate.py` |
| `maturity-model.schema.json` | Programme owner | release-level changes require roadmap migration | `scripts/ci_quality.sh`; `tests/test_roadmap.py` |
| `methods-facts.schema.json` | Publication maintainer | additive facts with stable identifiers | `scripts/ci_quality.sh`; `tests/test_methods.py` |
| `provenance-event.schema.json` | Provenance maintainer | event fields are append-only; hash semantics require a major profile | `scripts/ci_quality.sh`; `tests/test_lineage.py` |
| `quality-report.schema.json` | Quality maintainer | metrics retain identifier and uncertainty semantics | `scripts/ci_quality.sh`; `tests/test_validation_integrity.py` |
| `release-evidence.schema.json` | Release authority | gate IDs and evidence references are migration-bound | `scripts/ci_quality.sh`; `tests/test_roadmap_hardening.py` |
| `release-roadmap.schema.json` | Programme owner | release train migrations preserve monotonic maturity | `scripts/ci_quality.sh`; `tests/test_roadmap_hardening.py` |
| `rights-inventory.schema.json` | Governance analyst | rights decisions are fail-closed and append-only | `scripts/ci_quality.sh`; `tests/test_publication.py` |
| `snapshot-manifest.schema.json` | Archive maintainer | released manifests are immutable; corrections are successors | `scripts/ci_quality.sh`; `tests/test_crate.py` |
| `source-record.schema.json` | Source-registry maintainer | source identity is stable across retrieval/version changes | `scripts/ci_quality.sh`; `tests/test_registry.py` |
| `source-registry.schema.json` | Source-registry maintainer | registry additions are compatible; identity changes require migration | `scripts/ci_quality.sh`; `tests/test_linz_catalog.py` |
| `spatial-feature-link.schema.json` | Spatial maintainer | preserve source identity, geometry digest and temporal assertions | `scripts/ci_quality.sh`; `tests/test_spatial.py` |
| `track-metadata.schema.json` | Programme owner | lifecycle transitions are explicit and timestamped | `scripts/ci_quality.sh`; `tests/test_roadmap_hardening.py` |
| `transformation-run.schema.json` | Provenance maintainer | input/output references remain immutable and hash-addressed | `scripts/ci_quality.sh`; `tests/test_lineage.py` |
| `v1-gate.schema.json` | Release authority | gate identifiers require explicit migration and review | `scripts/ci_quality.sh`; `tests/test_roadmap_hardening.py` |

The compatibility policy is governed by `docs/v1-release-policy.md`. A change
must update the schema, its fixtures/tests, this matrix and a migration note in
the same reviewable change; no compatibility claim is made until the relevant
test command passes.
