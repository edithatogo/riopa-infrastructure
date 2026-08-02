# Programme governance and sustainability

## Decision rights

| Role | Decision authority | Required evidence |
|---|---|---|
| Programme owner | scope, priorities and track ownership | Conductor metadata and decision record |
| Governance analyst | rights, privacy, Māori data sovereignty and exceptions | signed or attributed review record |
| API/schema analyst | normative contracts, compatibility and migrations | schema diff and compatibility evidence |
| Security analyst | threat, dependency and integrity qualification | security findings and disposition |
| Release authority | release readiness and waivers | signed/attested release decision |
| External-user workflow analyst | agent assessment of workflow semantics and limitations | content-bound panel report; does not substitute for participant evidence |
| Maintainer | implementation, triage and support response | issue history and support record |

No single role can waive a governance prohibition, integrity failure or critical
security defect. A waiver must identify its scope, approver, compensating
control, expiry and remediation issue in machine-readable release evidence.

## Sources of truth

- Conductor `spec.md`, `plan.md`, `metadata.json` and `index.md`: track scope,
  work and evidence.
- `conductor/releases.json` and release-evidence records: release gates and
  gate outcomes.
- `project/issues.yaml`: generated issue graph; never hand edit.
- ADRs and this register: architectural decisions and their status.
- Git history and checksums: immutable implementation and artifact identity.

## Contribution and succession

Contributors work through issues and focused changes with tests and evidence.
Maintainers document ownership transfer before leaving a role, preserve access
and recovery procedures, and keep at least two analysts familiar with every
release-critical contract; agents may contribute one of those analyses while
accountable ownership remains explicit. The project publishes supported environments,
security reporting, response boundaries and deprecation notices for stable 1.x.

## Review cadence

Continuous checks cover validation, security and source health. Monthly review
covers track status, blockers, evidence, waivers, source freshness, adoption
and costs. Every release candidate requires compatibility, security,
performance, governance and preservation agent-panel qualification plus any
distinct independent-reproduction evidence.

## Current approval state

This document defines the operating contract; named signatories and external
agent-panel reports are still required before the foundation track can close.
