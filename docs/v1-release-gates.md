# Stable v1 release gates

`conductor/releases.json` is the normative release train. `conductor/v1-gate.json` aggregates the non-negotiable stable-v1 conditions. A gate is blocking unless explicitly marked otherwise.

## Evidence rules

- Evidence is immutable, signed or content-addressed where feasible.
- A mutable URL alone is insufficient evidence.
- Evidence identifies the tool/version and execution environment that produced or validated it.
- A waiver records scope, reason, owner, approver, mitigation, public summary, remediation and expiry.
- Expired waivers fail the gate; security-critical, governance-prohibition, integrity-failure and unresolved-P0/P1 categories are non-waivable.
- Track completion cannot waive a programme release gate.
- Absence of evidence is reported as not ready, never inferred as passed.

## Release candidate: 0.9.0 / M5

The candidate is feature complete and contract frozen. Only correctness, security, compatibility, performance, documentation and release-evidence work is accepted. A material new feature returns the affected surface to beta.

Candidate qualification includes:

- frozen normative inventory and conformance corpus;
- security and supply-chain qualification;
- national/reference performance and resilience qualification;
- at least 90 consecutive days and 90 daily hosted observations of representative operational-beta evidence;
- at least 30 days and 30 daily hosted observations on the unchanged release candidate;
- two isolated clean-room reproductions by separately prompted reproducer subagents;
- role-separated agent-operated user and operator journeys plus adversarial, evidence-audit and domain review;
- migration, rollback, restore, correction and withdrawal rehearsals;
- complete publication and preservation objects;
- no prohibited defect or expired waiver.

## General availability: 1.0.0 / M6

General availability is a separate decision by the sole repository owner. It requires all 28 v1-critical tracks, all 14 stable gate families, the global defect/evidence/waiver policy, required subagent-panel advice and the owner's signed approval.

The release authority may publish 1.0.0 only when:

1. `riopa roadmap validate` passes;
2. `riopa roadmap status --release 1.0.0` reports ready;
3. signed artifacts, checksums, attestations, SBOMs and preservation copies verify independently;
4. governance, rights, security, operations, performance, interoperability, science and usability approvals are current;
5. support, maintenance, deprecation, vulnerability response, succession and annual revalidation obligations are active.
