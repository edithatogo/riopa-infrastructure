# Evidence index: Research objects, methods supplements and citation automation

- **Track ID:** `methods_research_objects_20260718`
- **Status:** `validating`
- **Target release:** `0.4.0`
- **Current maturity:** `M2`
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
| `WP-006-attested-release-verification-20260731` | Release workflow attests and independently verifies package, research-object, SBOM and checksum subjects before publication | `.github/workflows/release.yml`, `docs/conformance-and-release-verification.md` | Historical contract state was policy-only; successor `v0.4.0` evidence now proves protected-tag execution, GitHub OIDC verification and public-preview preservation, while the stable candidate remains open |
| `WP-007-preserved-real-inputs-20260731` | Bounded real-source bytes, receipts, rights references and canonical materialisations are hash-bound and clean-rebuild verified | `evidence/wp007-real-slice/manifest.json`, `scripts/verify_wp007_slice.py` | Repository evidence package passes; full RO-Crate, external validation and preservation deposit remain open |
| `WP-010-deterministic-reviewer-handoff-20260801` | A synthetic analytical benchmark can be transferred as byte-identical reviewer bundles and verified without project dependencies | `examples/wp010-synthetic-benchmark/`, `scripts/build_wp010_reviewer_bundle.py`, `tests/test_wp010_benchmark.py` | Deterministic handoff passes locally; it is not a deposited research object or isolated role-separated clean-room agent reproduction |
| `RO-CONTRACT-20260822` | Repository-owned research-object, methods and integrity contract | `src/riopa_provenance/crate.py`, `src/riopa_provenance/methods.py`, `src/riopa_provenance/validation.py`, `docs/methods-output-contract.md`, `tests/test_crate.py`, `tests/test_methods.py`, `tests/test_validation_failures.py` | Tasks 1.1–1.3, 2.1–2.3 and 3.3 pass locally; publication, signatures/attestations, external validators, real-data release and isolated role-separated clean-room agent reproduction remain open |
| `PUBLICATION-CITATION-READINESS-20260826` | Validate that preview citation guidance is digest-bound, packet-first and explicitly promotion-disabled | `scripts/validate_publication_citation_readiness.py`, `docs/publication-citation-readiness-validation-20260826.json`, `tests/test_publication_citation_readiness.py` | Bounded citation contract passes; isolated role-separated clean-room agent reproduction, attestation, preservation, elapsed qualification and accountable publication remain open |
| `RO-ATTESTATION-CONTRACT-20260825` | Release workflow binds SBOM, checksums, research-object subjects and independent GitHub attestation verification | `docs/research-object-attestation-contract-20260825.json`, `.github/workflows/release.yml`, `tests/test_security_controls.py`, `docs/v0.4.0-preservation-wp006-reconciliation-20260829.json` | Contract and `v0.4.0` protected-tag/attestation/preservation execution pass; trusted stable-candidate signing, preservation and accountable release authority remain pending |
| `RO-PROFILE-VALIDATION-20260825` | Repository-available JSON Schema and RDF/SHACL profile validators run with exact versions and digest-bound fixtures | `scripts/run_profile_validators.py`, `docs/research-object-profile-validation-20260825.json`, `tests/test_research_object_profile_validation.py` | Bounded tooling validation passes; external/non-Python acceptance, preservation, real-data release and authority remain open |
| `RO-REAL-DATA-CANDIDATE-VALIDATION-20260826` | Digest-verify the bounded real-data publication candidate and its materialized artifacts | `scripts/validate_real_data_release_candidate.py`, `docs/publication-real-data-release-candidate-20260825.json`, `docs/publication-real-data-release-candidate-validation-20260826.json`, `tests/test_real_data_release_candidate_validation.py` | Candidate hashes pass and promotion remains disabled; isolated role-separated clean-room agent reproduction, attestation, preservation and authority remain open |
| `RO-PACKAGING-GUIDANCE-20260826` | Publish reproducible packaging, preservation, restore and append-only migration guidance for the bounded preview | `docs/research-object-packaging-preservation-migration-20260826.md`, `tests/test_research_object_packaging_guidance.py` | Guidance is repository-owned and fail-closed; provider acceptance, signed attestation, isolated role-separated clean-room agent reproduction, elapsed qualification and authority remain open |
| `RO-M2-PROMOTION-20260827` | Qualify the experimental executable-proof boundary against an exact source tree | `docs/methods-research-objects-m2-promotion-20260827.json`, `tests/test_methods_research_objects_m2_promotion.py` | Repository-owned positive, negative, deterministic, profile, integrity and hosted-release evidence passes; M3-M6 gates remain open |

## Blocking maturity gates

- M3 requires a complete representative real-data research object and clean
  environment reproduction with failure handling.
- M4 requires repeated external use, preservation operation and SLO evidence.
- M5 requires release-candidate security, recovery, panel and soak qualification.
- M6 requires a stable signed and preserved publication, isolated
  role-separated clean-room agent reproduction and accountable stable-release
  authority.

The generic validation, deterministic packaging, negative tests, bounded
real-data candidate, repository-available profile validation, protected-tag
attestation execution and independent GitHub verification satisfy the
experimental M2 boundary only. The published v0.3.0 example research object is
release evidence for these mechanics; it is not the complete v0.4 real-source
vertical slice.

## Repository-owned closeout slice (2026-08-24)

The research-object, methods, citation, projection, closure and deterministic
build contracts are linked above and pass `bash scripts/ci_quality.sh` at
protected `main` revision `ed69976d815f064843c3492fa2045807381857ca`. This
establishes repository-owned packaging behavior only; it does not claim signed
release evidence, external validation, deposition or publication.

## Decisions, exceptions and limitations

- This is a single-developer repository. Role-separated subagent panels supply
  the repository clean-room reproduction evidence but cannot substitute for
  provider, elapsed-operation or accountable release-authority facts.
- Synthetic reviewer bundles and local clean-build checks are bounded
  evidence, not exact-candidate role-separated agent-panel evidence or preservation receipts.
- Public, bounded, non-operational technical-preview scope remains in force.

## Review and handover

Required agent-panel lenses: Provenance analyst, Security analyst, Research-object analyst, User-workflow analyst.

This index is deliberately non-assertive while the track remains `validating`
at experimental M2. Status may advance only through `conductor/workflow.md`; evidence must be
immutable or version-addressed, agent-panel qualified where required, and
sufficient for the applicable release gates.

## Review record

- Review scope: exact-tree experimental M2 promotion only.
- Boundary: no normative research-object interface or package bytes change.
- Non-claim: this does not pass any v0.4 release gate or establish human/external evidence.
- Validation: focused promotion tests, full test suite, quality and reproducibility pass locally; all five hosted required checks passed on implementation commit `dec7ac4` in PR #624.

The track remains `validating` at M2 and is not complete or archive-eligible.
