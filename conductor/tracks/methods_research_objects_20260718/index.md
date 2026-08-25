# Evidence index: Research objects, methods supplements and citation automation

- **Track ID:** `methods_research_objects_20260718`
- **Status:** `active`
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
| `RO-CONTRACT-20260822` | Repository-owned research-object, methods and integrity contract | `src/riopa_provenance/crate.py`, `src/riopa_provenance/methods.py`, `src/riopa_provenance/validation.py`, `docs/methods-output-contract.md`, `tests/test_crate.py`, `tests/test_methods.py`, `tests/test_validation_failures.py` | Tasks 1.1–1.3, 2.1–2.3 and 3.3 pass locally; publication, signatures/attestations, external validators, real-data release and external reproduction remain open |
| `RO-ATTESTATION-CONTRACT-20260825` | Release workflow binds SBOM, checksums, research-object subjects and independent GitHub attestation verification | `docs/research-object-attestation-contract-20260825.json`, `.github/workflows/release.yml`, `tests/test_security_controls.py` | Workflow contract passes; protected-tag execution, preservation acceptance and accountable release authority remain pending |
| `RO-PROFILE-VALIDATION-20260825` | Repository-available JSON Schema and RDF/SHACL profile validators run with exact versions and digest-bound fixtures | `scripts/run_profile_validators.py`, `docs/research-object-profile-validation-20260825.json`, `tests/test_research_object_profile_validation.py` | Bounded tooling validation passes; external/non-Python acceptance, preservation, real-data release and authority remain open |
| `RO-REAL-DATA-CANDIDATE-VALIDATION-20260826` | Digest-verify the bounded real-data publication candidate and its materialized artifacts | `scripts/validate_real_data_release_candidate.py`, `docs/publication-real-data-release-candidate-20260825.json`, `docs/publication-real-data-release-candidate-validation-20260826.json`, `tests/test_real_data_release_candidate_validation.py` | Candidate hashes pass and promotion remains disabled; clean-room/external reproduction, attestation, preservation and authority remain open |

## Blocking defects

- Protected-tag SBOM/signature/attestation execution and independent
  verification remain open.
- External profile-validator results, a complete real-data release candidate,
  clean-room/external reproduction, preservation deposition and publication
  authority remain open.

## Repository-owned closeout slice (2026-08-24)

The research-object, methods, citation, projection, closure and deterministic
build contracts are linked above and pass `bash scripts/ci_quality.sh` at
protected `main` revision `ed69976d815f064843c3492fa2045807381857ca`. This
establishes repository-owned packaging behavior only; it does not claim signed
release evidence, external validation, deposition or publication.

## Decisions, exceptions and limitations

- This is a single-developer repository. Agent panels may assess research
  object packets, but cannot substitute for external reproduction or
  accountable release-authority approval.
- Synthetic reviewer bundles and local clean-build checks are bounded
  evidence, not external participant evidence or preservation receipts.
- Public, bounded, non-operational technical-preview scope remains in force.

## Review and handover

Required agent-panel lenses: Provenance analyst, Security analyst, Research-object analyst, External-user workflow analyst.

This index is deliberately non-assertive while the track remains `active` at
M1. Status may advance only through `conductor/workflow.md`; evidence must be
immutable or version-addressed, agent-panel qualified where required, and
sufficient for the applicable release gates.
