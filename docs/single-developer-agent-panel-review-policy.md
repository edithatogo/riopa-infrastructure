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
benchmarks and evidence packets. Owner-authorized agents may also execute the
operator and user workflows for this single-person repository. Agent execution
does not create elapsed time or make an accountable release decision. Those
facts remain distinct campaign gates until their actual evidence exists.

The repository owner is the accountable release authority. An agent may prepare
the decision packet and report, but may not approve promotion on the owner's
behalf.

## Minimum evidence

- immutable repository revision and input-artifact digests;
- at least two named agent analyses with distinct lenses;
- orchestrator synthesis, options, recommendation and contingency;
- disposition of every material finding;
- explicit non-claims for hosted, elapsed and authority gates.
