# Plan: methods_research_objects_20260718

## 1. Validation and package contract

- [x] 1.1 Replace filename-specific validation with schema-declared arbitrary-bundle validation. Evidence: `src/riopa_provenance/validation.py::validate_manifest_closure`, `src/riopa_provenance/crate.py::verify_research_object`, `tests/test_crate.py`.
- [x] 1.2 Define non-circular package manifest, checksum and RO-Crate finalisation rules. Evidence: `src/riopa_provenance/crate.py::build_research_object`, `docs/methods-output-contract.md`, `tests/test_crate.py::test_research_object_build_is_content_deterministic`.
- [x] 1.3 Add payload, rights, quality, software, environment and preservation closure checks. Evidence: `src/riopa_provenance/validation.py::validate_manifest_closure`, `tests/test_validation_failures.py`, `tests/test_crate.py`.

## 2. Methods and metadata generators

- [x] 2.1 Generate concise methods, full supplement, methods facts and limitations. Evidence: `src/riopa_provenance/methods.py::generate_methods_markdown`, `docs/methods-output-contract.md`, `tests/test_methods.py`.
- [x] 2.2 Generate CFF, DataCite, PROV, OpenLineage and workflow/run crate projections. Evidence: `src/riopa_provenance/crate.py::build_research_object`, `tests/test_crate.py`.
- [x] 2.3 Add consistency and missing-evidence diagnostics. Evidence: `src/riopa_provenance/methods.py`, `src/riopa_provenance/validation.py`, `tests/test_validation_failures.py`.

## 3. Integrity and external validation

- [x] 3.1 Define and test the SBOM, checksum and attestation workflow contract. The protected-tag workflow generates and independently verifies release subjects; hosted tag execution, preservation acceptance and release authority remain pending. (`docs/research-object-attestation-contract-20260825.json`, `.github/workflows/release.yml`, `tests/test_security_controls.py`)
- [x] 3.2 Run the repository-available JSON Schema and RDF/SHACL profile validators and record exact versions/results (`scripts/run_profile_validators.py`, `docs/research-object-profile-validation-20260825.json`, `tests/test_research_object_profile_validation.py`). External/non-Python acceptance, preservation and publication gates remain open.
- [x] 3.3 Test deterministic and tolerance-equivalent clean builds. Evidence: `tests/test_crate.py::test_research_object_build_is_content_deterministic`.

## 4. Publication workflow

- [~] 4.1 Validate one bounded real-data release candidate. The archived Wellington slice, source manifest and three materialized artifacts are now digest-verified as a promotion-disabled candidate; clean-room/external reproduction, attestation, preservation and accountable publication gates remain open (`scripts/validate_real_data_release_candidate.py`, `docs/publication-real-data-release-candidate-validation-20260826.json`, `tests/test_real_data_release_candidate_validation.py`).
- [ ] 4.2 Conduct clean-room verification and citation usability review.
- [ ] 4.3 Publish stable packaging, preservation and migration guidance.

## Track closeout

- [x] C.1 Link implementation, test, review, migration and release evidence in `index.md` for the repository-owned package slice; signing, external validation and publication gates remain explicitly pending.
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [x] C.4 Update metadata status and target-release evidence through the Conductor workflow; status remains `active`/M1 because the documented gates are unresolved.
