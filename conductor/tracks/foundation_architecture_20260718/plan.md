# Plan: foundation_architecture_20260718

## 1. V1 boundary and decisions

- [x] 1.1 Reconcile all v0.1 ADRs with the revised v1 maturity and release model. (docs/adr/README.md; 42adef0)
- [x] 1.2 Define platform, dataset, analytics and application release boundaries and non-claims. (docs/v1-scope-and-boundaries.md; 43805ba)
- [x] 1.3 Record responsibility, ownership and version axes for every component. (docs/v1-scope-and-boundaries.md; docs/architecture.md; 43805ba)

## 2. Programme governance

- [x] 2.1 Define maintainers, approvers, reviewers, release authority and exception expiry. (docs/governance-and-sustainability.md; f95b827)
- [x] 2.2 Define issue, Conductor, ADR and release-evidence sources of truth. (docs/governance-and-sustainability.md; f95b827)
- [x] 2.3 Establish sustainability, succession and contribution expectations. (docs/governance-and-sustainability.md; f95b827)

## 3. Architecture conformance

- [x] 3.1 Implement machine validation for tracks, dependencies, maturity and release gates. (src/riopa_provenance/roadmap.py; existing baseline)
- [x] 3.2 Generate the GitHub issue graph from Conductor artifacts and reject drift. (scripts/create_issues.py; project/issues.yaml; existing baseline)
- [x] 3.3 Add architecture fitness checks for source-of-truth and version-boundary violations. (src/riopa_provenance/roadmap.py; tests/test_roadmap_hardening.py; c5f66bc)

## 4. Ratification and handover

- [ ] 4.1 Conduct maintainer and external architecture review.
- [ ] 4.2 Resolve or explicitly accept findings with time-limited exceptions.
- [ ] 4.3 Publish the accepted architecture and v1 programme baseline.

## 5. Review fixes

- [x] 5.1 Record task SHAs, evidence identifiers and active blockers in the track metadata and plan. (7448786; review fix)

## Track closeout

- [ ] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [ ] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.
