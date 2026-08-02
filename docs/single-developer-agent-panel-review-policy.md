# Single-developer agent-panel review policy

RIOPA is maintained as a single-developer repository. Repository review is
therefore performed by a multi-agent panel coordinated by an orchestrating
agent. No acceptance criterion requires a second person as reviewer.

## Panel contract

For each review, the orchestrator assigns at least two distinct agent analysts
different lenses, records their identities, revision, scope, method, findings
and limitations, and synthesises one content-bound recommendation. A panel
member must not silently resolve its own finding. Findings are fixed, accepted
with an explicit limitation, or kept open.

The `review_roles` metadata field is retained for schema compatibility. Its
values are agent-panel lenses, not staffing requirements. A scientific-methods
analyst evaluates claims and methods; it does not represent human peer review.

## Boundaries

Agent-panel review can qualify repository-owned code, documentation, methods,
benchmarks and evidence packets. It does not create elapsed time, execute a
workflow in a hosted failure domain, attest to an external user's experience,
or make an accountable release decision. Those facts remain distinct campaign
gates until their actual evidence exists or the applicable release scope is
formally changed.

An external operator or user may supply execution or usability evidence, but is
not a reviewer and is not required to review the repository. The accountable
release authority approves promotion; it is not a code or scientific-methods assessor.

## Minimum evidence

- immutable repository revision and input-artifact digests;
- at least two named agent analyses with distinct lenses;
- orchestrator synthesis, options, recommendation and contingency;
- disposition of every material finding;
- explicit non-claims for hosted, elapsed, external-user and authority gates.
