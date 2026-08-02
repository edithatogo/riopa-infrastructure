# Evidence index: Research objects, methods supplements and citation automation

- **Track ID:** `methods_research_objects_20260718`
- **Status:** `specified`
- **Target release:** `0.4.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Platform`
- **Risk / priority:** `Critical` / `P0`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Core platform maintainer
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/34

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-003-publication-binding-20260731` | Research-object bytes bind deterministic, target-specific publication plans | `src/riopa_provenance/publication.py`, `schemas/publication-plan.schema.json`, `tests/test_publication.py` | Content binding, target staging and negative rights tests pass |
| `WP-006-attested-release-verification-20260731` | Release workflow attests and independently verifies package, research-object, SBOM and checksum subjects before publication | `.github/workflows/release.yml`, `docs/conformance-and-release-verification.md` | Workflow policy passes locally; no protected tag, external profile validation or preservation deposit is claimed |
| `WP-007-preserved-real-inputs-20260731` | Bounded real-source bytes, receipts, rights references and canonical materialisations are hash-bound and clean-rebuild verified | `evidence/wp007-real-slice/manifest.json`, `scripts/verify_wp007_slice.py` | Repository evidence package passes; full RO-Crate, external validation and preservation deposit remain open |
| `WP-010-deterministic-reviewer-handoff-20260801` | A synthetic analytical benchmark can be transferred as byte-identical reviewer bundles and verified without project dependencies | `examples/wp010-synthetic-benchmark/`, `scripts/build_wp010_reviewer_bundle.py`, `tests/test_wp010_benchmark.py` | Deterministic handoff passes locally; it is not a deposited research object or external reproduction |

## Blocking defects

- None recorded.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required agent-panel lenses: Provenance analyst, Security analyst, Research-object analyst, External-user workflow analyst.

This index is deliberately non-assertive while the track remains `specified`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.
