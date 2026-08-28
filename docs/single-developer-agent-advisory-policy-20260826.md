# Single-developer and agent-advisory policy

RIOPA Infrastructure is a single-developer repository. One human is the
developer, maintainer and accountable repository owner. No second human
reviewer, consultant, user, operator, clinician, community representative or
release authority is assumed or claimed unless a future content-bound evidence
record explicitly identifies that participation.

## Structured agent panels

The developer uses structured advice from separately prompted AI subagents assigned named lenses
such as security, governance, quantitative methods, operations or
reproducibility. These agents are advisory tools. Separately prompted agents can
provide useful challenge and process separation, but they are not independent
humans, external stakeholders or accountable decision-makers.

Repository-defined review, user-journey, operator-journey and clean-room
reproduction gates are satisfied by a role-separated subagent panel. A panel
must include, as applicable, a clean-room reproducer, adversarial reviewer,
evidence auditor, domain reviewer and synthesizer. Its content-bound manifest
records each role, session and model identity, exact revision and artifact
digests, environment, commands, results, findings, dissent, remediation and
rerun outcome. A synthesizer cannot silently override dissent.

The developer decides how to disposition agent findings and remains accountable
for repository changes and release decisions. An agent may prepare or review a
decision packet, but cannot approve it on the developer's behalf.

## Evidence boundaries

Agent-panel evidence may satisfy the repository's prospective review,
agent-operated workflow and isolated clean-room reproduction requirements. It
does not claim another human participated. Agents cannot establish:

- human peer, clinical, legal, cultural or community review;
- source ownership, licence scope, redistribution permission or legal authority;
- third-party conformance or preservation acceptance;
- elapsed operational evidence; or
- accountable human approval.

No active or future track requires a second human, external person, external
user or external operator. References to independent reproduction in historical
evidence describe the contract in force at that time; prospectively,
independence means isolation of agent role, prompt, environment, checkout,
cache and uncommitted implementation state. The absence of other human advice
is never concealed by relabelling agent output as human evidence.

Where a proposed scope would genuinely require clinical, legal, cultural or
community authority, the sole owner must either obtain content-bound factual
evidence of that participation or exclude the affected scope with a signed
non-applicability rationale. An agent panel cannot convert such a scope-triggered
fact into repository-owned evidence.

External facts remain external facts. GitHub Actions execution, upstream source
responses and terms, package or dataset publication, OIDC attestations,
persistent identifiers, preservation-provider acceptance and elapsed calendar
observations require evidence from those systems. A subagent panel validates
the evidence but does not manufacture it.

## Applicability

This policy applies to every active RIOPA Conductor track and to future track
work. Historical evidence remains interpreted according to its exact wording,
with agent panels treated as repository-owned advisory review unless an
evidence record proves a different status.
