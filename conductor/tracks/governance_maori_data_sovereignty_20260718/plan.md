# Plan: governance_maori_data_sovereignty_20260718

## 1. Framework and classifications

- [x] 1.1 Define data classes, governance triggers and decision outcomes. (docs/governance-decision-framework.md; 4594fec)
- [x] 1.2 Map licence, privacy, statutory, cultural and safety evidence into common records. (schemas/governance-decision.schema.json; 4594fec)
- [x] 1.3 Define review roles, expiry, escalation and conflict-of-interest rules. (schemas/governance-decision.schema.json; 4594fec)

## 2. Technical enforcement

- [x] 2.1 Implement fail-closed publication and controlled/public separation tests. (src/riopa_provenance/governance.py; tests/test_governance.py; 6d68b44)
- [x] 2.2 Attach governance decisions to source, artifact, model and release manifests. (schemas/governance-decision.schema.json; schemas/{source-record,artifact,transformation-run,snapshot-manifest,release-evidence}.schema.json; 0095dc0)
- [x] 2.3 Add correction, supersession, withdrawal and takedown workflows. (src/riopa_provenance/governance.py; tests/test_governance.py; 6d68b44)

## 3. Engagement and applied review

- [x] 3.1 Document optional scope-triggered cultural or community governance and engagement guidance where it is requested or applicable. (docs/governance-engagement-pathway.md; ee966dc)
- [x] 3.2 Review facility, health, deprivation and culturally sensitive geographic use cases. (reports/governance-use-case-review.md; 2026-07-29)
- [x] 3.3 Document benefits, harms, mitigations and residual risks. (reports/governance-use-case-review.md; 2026-07-29)

## 4. Stable governance gate

- [x] 4.1 Exercise publication blocking and withdrawal scenarios. (reports/governance-withdrawal-drill.md; standalone drill passed 2026-07-29)
- [x] 4.2 Audit all v1 reference releases and pilots against the framework. (reports/governance-release-pilot-audit.md; 2026-07-29)
- [x] 4.3 Approve, exclude or bound each release with evidence and review expiry. (reports/governance-release-pilot-audit.md; 2026-07-29)

## 5. Review fixes

- [x] 5.1 Validate review expiry, conflict-of-interest handling and predecessor preservation fail closed. (src/riopa_provenance/governance.py; tests/test_governance.py; c3579bd)

## Track closeout

- [x] C.1 Link implementation, test, review, migration and release evidence in `index.md`. (0b062d5)
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected. (476ff5a)
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains; the foundation dependency and live evidence gates remain open.
- [x] C.4 Update metadata status and target-release evidence through the Conductor workflow; status remains `validating`/M1 because the documented gates are unresolved.
