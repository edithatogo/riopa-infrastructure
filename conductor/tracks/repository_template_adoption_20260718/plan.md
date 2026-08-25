# Plan: repository_template_adoption_20260718

## 1. Template hardening

- [x] 1.1 Define greenfield and brownfield setup contracts and generated-file boundaries. Evidence: `schemas/repository-template-contract.schema.json`, `docs/repository-template-contract-20260822.json`, `docs/repository-template-contract-20260822.md`. (a400d49)
- [x] 1.2 Include Conductor, CI, security, release, citation and support scaffolding. Evidence: `docs/repository-template-contract-20260822.json`, `conductor/workflow.md`, `.github/workflows/validate.yml`, `.github/workflows/security.yml`, `.github/workflows/release.yml`, `docs/operations-and-support.md`. (a400d49)
- [x] 1.3 Add template self-tests and documentation tests. Evidence: `tests/test_repository_template_contract.py`, `scripts/ci_quality.sh`, `scripts/ci_reproducibility.sh`. (a400d49)

## 2. Adapters and upgrades

- [x] 2.1 Provide connector, archive, transformation and analytics adapter examples. (`examples/template-adapters/adapter-examples.json`, `examples/template-adapters/README.md`, `tests/test_template_adapter_examples.py`; synthetic additive contract only)
- [x] 2.2 Implement read-only template version detection, drift reporting and safe-upgrade recommendations. The report detects missing scaffolding and records mutation-free boundaries; cross-repository upgrade execution remains open (`scripts/check_template_drift.py`, `tests/test_template_drift.py`).
- [x] 2.3 Add rollback and local-customisation preservation tests. (`tests/test_template_drift.py`; read-only drift report proves never-overwrite files and local bytes are unchanged)

## 3. Cross-repository adoption

- [~] 3.1 Inventory and map the related fyi, archive, corpus, policy, health and social-data repositories. The bounded inventory records roles and evidence status without claiming current adoption; fresh revision capture and native conformance remain open (`docs/repository-adoption-inventory-20260825.json`, `tests/test_repository_adoption_inventory.py`).
- [~] 3.2 Implement read-only additive profile and research-object readiness emission in staged waves. The emitter detects local scaffolding and research-object entrypoints without mutation; cross-repository execution and adoption remain open (`scripts/build_adoption_profile.py`, `tests/test_adoption_profile.py`, `docs/repository-adoption-profile-contract-20260825.json`).
- [~] 3.3 Record semantic losses, contributor feedback and migration costs. Adapter semantic-loss classifications are summarized; contributor feedback and migration costs remain explicitly `not-collected`/`not-measured` until factual evidence exists (`scripts/build_adoption_migration_ledger.py`, `tests/test_adoption_migration_ledger.py`, `docs/repository-adoption-migration-ledger-contract-20260825.json`).

## 4. Stable developer experience

- [ ] 4.1 Conduct clean onboarding and release journeys on supported environments.
- [ ] 4.2 Reach the required adoption and independent reproduction levels.
- [ ] 4.3 Publish template support, compatibility and upgrade policy.

## Track closeout

- [ ] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [ ] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.
