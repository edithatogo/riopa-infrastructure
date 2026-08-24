# Evidence index: Repository template and cross-repository adoption

- **Track ID:** `repository_template_adoption_20260718`
- **Status:** `active`
- **Target release:** `0.5.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Platform`
- **Risk / priority:** `High` / `P1`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Core platform maintainer
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/44

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-008-related-repository-adapters-20260731` | Related repositories have isolated issue, branch, tested commit and merged pull-request implementations without modifying dirty checkouts | `reports/wp008-cross-repository-adapters.md`, `conformance/adapters/report.json` | Cross-repository fixture validation passes; `fyi-cli` PR #285 and `fyi-archive` PR #319 merged on 2026-07-31 |
| `TEMPLATE-CONTRACT-20260822` | Additive greenfield/brownfield setup, scaffolding, generated-file boundaries and self-tests | `schemas/repository-template-contract.schema.json`, `docs/repository-template-contract-20260822.json`, `docs/repository-template-contract-20260822.md`, `tests/test_repository_template_contract.py` | Tasks 1.1–1.3 are schema- and negative-test validated; cross-repository adoption, external onboarding and independent reproduction remain open |
| `TEMPLATE-DRIFT-20260825` | Read-only template version detection, scaffold drift report and safe-upgrade boundaries | `scripts/check_template_drift.py`, `tests/test_template_drift.py` | Current repository aligns with required scaffolding; cross-repository upgrade, adoption and independent reproduction remain open |
| `TEMPLATE-ADAPTER-EXAMPLES-20260825` | Connector, archive, transformation and analytics adapter boundaries are demonstrated additively | `examples/template-adapters/adapter-examples.json`, `examples/template-adapters/README.md`, `tests/test_template_adapter_examples.py` | Synthetic contract fixture passes; live source, cross-repository adoption and independent reproduction remain open |
| `TEMPLATE-ROLLBACK-PRESERVATION-20260825` | Drift inspection preserves local customisations and never-overwrite files without mutation | `scripts/check_template_drift.py`, `tests/test_template_drift.py` | Repository-owned preservation test passes; cross-repository upgrade, rollback execution and independent reproduction remain open |
| `TEMPLATE-REPOSITORY-INVENTORY-20260825` | Bounded map of related repositories, roles and adoption evidence status | `docs/repository-adoption-inventory-20260825.json`, `tests/test_repository_adoption_inventory.py` | Inventory is explicit and non-authoritative; fresh revision capture, native conformance, staged adoption, migration cost and independent reproduction remain open |

## Blocking defects

- None recorded for the bounded WP-008 adapter slice.

## Decisions, exceptions and limitations

- This evidence is bounded to the two adapter contracts and does not establish
  template adoption or release conformance for either complete repository.

## Review and handover

Required agent-panel lenses: API/schema analyst, Security analyst, Research-object analyst, External-user workflow analyst.

This index is deliberately non-assertive while the track remains `specified`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
