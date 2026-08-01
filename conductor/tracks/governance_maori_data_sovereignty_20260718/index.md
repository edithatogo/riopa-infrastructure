# Evidence index: Rights, privacy and scope-triggered data governance framework

- **Track ID:** `governance_maori_data_sovereignty_20260718`
- **Status:** `validating`
- **Target release:** `0.3.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Governance`
- **Risk / priority:** `Critical` / `P0`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Programme owner
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/19

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-003-hierarchical-rights-20260731` | Rights propagate to artifact and target-specific publication decisions without widening inherited permission | `src/riopa_provenance/publication.py`, `schemas/publication-plan.schema.json`, `tests/test_publication.py` | Narrowing-only inheritance and fail-closed conflict tests pass |
| R01, R02, R04, R05 | Versioned governance decision framework and schema | `docs/governance-decision-framework.md`, `schemas/governance-decision.schema.json` | Implemented; complete schema and quality suites pass locally |
| R01 | Governance decision references on source, artifact, transformation, snapshot and release records | `schemas/source-record.schema.json`, `schemas/artifact.schema.json`, `schemas/transformation-run.schema.json`, `schemas/snapshot-manifest.schema.json`, `schemas/release-evidence.schema.json` | Implemented; complete schema and quality suites pass locally |
| R02, R03 | Fail-closed public/controlled decision core and tests | `src/riopa_provenance/governance.py`, `tests/test_governance.py` | Implemented; complete runtime suite passes locally |
| R01, R03 | Withdrawal and supersession record helpers | `src/riopa_provenance/governance.py`, `tests/test_governance.py` | Implemented; operational exercise pending |
| R04, R05 | Optional scope-triggered cultural or community governance guidance | `docs/governance-engagement-pathway.md` | Implemented as optional guidance; no live co-design/review claimed |
| R05 | Applied benefit/harm/equity review instrument | `docs/applied-governance-review-template.md` | Template only; pilot decisions pending |
| R02, R03 | Synthetic withdrawal and public/controlled pathway drill | `reports/governance-withdrawal-drill.md` | Passed; live takedown/reconciliation not claimed |
| R04, R05 | Release and pilot governance audit | `reports/governance-release-pilot-audit.md` | No live pilots/releases approved; future scope explicitly bounded |
| R04 | Review fix for expiry and conflict handling | `src/riopa_provenance/governance.py`, `tests/test_governance.py` | Implemented; complete runtime suite passes locally |
| R04, R05 | Explicit scope-triggered review activation and non-inference boundary | `src/riopa_provenance/governance.py`, `tests/test_governance.py`, `reports/governance-scope-trigger-audit.md` | 14 tests pass; no identity/geography inference or mandatory Māori co-design gate |
| R01, R02, R04 | Unknown classification and unresolved conflict fail closed | `tests/test_governance.py` | Negative tests pass; no permission widening from incomplete review |
| R01, R02, R04 | Metadata-only custodian and authority request boundary | `docs/source-authority-request-packet.md`, `docs/external-dependency-register.md` | Prepared, unsent; no acquisition, credentials or authority inferred |
| R01, R02, R03, R04 | Acquisition approval record boundary | `docs/source-acquisition-approval-template.md` | Requires recipient, source, rights, scope and expiry before acquisition |
| R05 | Planned facility, health, deprivation and culturally sensitive geography review | `reports/governance-use-case-review.md` | All remain `review-required`; no publication approval inferred |

## Blocking defects

- None recorded for the implemented bounded framework.

## Decisions, exceptions and limitations

- Public visibility is not permission to redistribute or infer; all unresolved decisions remain `review-required`.
- No live co-design or Māori governance approval is claimed or required by the
  repository baseline; the pathway is optional guidance activated only by
  declared scope or another applicable obligation.
- Local target reconciliation is tested; no live distribution/takedown system
  is claimed by the bounded synthetic drill.

## Review and handover

Required reviewer roles: Governance reviewer, Security reviewer, Data steward, Scientific reviewer.

Implementation is validating. Evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.
