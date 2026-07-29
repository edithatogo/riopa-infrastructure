# Plan: governance_maori_data_sovereignty_20260718

## 1. Framework and classifications

- [x] 1.1 Define data classes, governance triggers and decision outcomes. (docs/governance-decision-framework.md; 4594fec)
- [x] 1.2 Map licence, privacy, statutory, cultural and safety evidence into common records. (schemas/governance-decision.schema.json; 4594fec)
- [x] 1.3 Define review roles, expiry, escalation and conflict-of-interest rules. (schemas/governance-decision.schema.json; 4594fec)

## 2. Technical enforcement

- [x] 2.1 Implement fail-closed publication and controlled/public separation tests. (src/riopa_provenance/governance.py; tests/test_governance.py; 6d68b44)
- [x] 2.2 Attach governance decisions to source, artifact, model and release manifests. (schemas/governance-decision.schema.json; 4594fec)
- [x] 2.3 Add correction, supersession, withdrawal and takedown workflows. (src/riopa_provenance/governance.py; tests/test_governance.py; 6d68b44)

## 3. Engagement and applied review

- [x] 3.1 Establish appropriate Māori governance and engagement pathways for relevant datasets. (docs/governance-engagement-pathway.md; ee966dc)
- [ ] 3.2 Review facility, health, deprivation and culturally sensitive geographic use cases.
- [ ] 3.3 Document benefits, harms, mitigations and residual risks.

## 4. Stable governance gate

- [ ] 4.1 Exercise publication blocking and withdrawal scenarios.
- [ ] 4.2 Audit all v1 reference releases and pilots against the framework.
- [ ] 4.3 Approve, exclude or bound each release with evidence and review expiry.

## Track closeout

- [ ] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [ ] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.
