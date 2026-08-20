# Foundation, provenance, connector and ontology closeout plan

Status: repository-owned implementation slice (2026-08-01)

This plan converts four foundational Conductor tracks into executable,
fail-closed work packages. It does not promote a release or waive higher-tier
evidence requirements.

| Track | Implemented baseline | Next repository-owned work | Gate / contingency |
|---|---|---|---|
| `foundation_architecture_20260718` | M1 architecture and ADR baseline | Keep ownership, compatibility and migration fixtures synchronized | Missing owner or incompatible migration blocks promotion |
| `provenance_profile_v1_20260718` | Content-addressed capture, lineage and publication validators | Add correction, withdrawal and supersession fixtures | Missing revision or digest fails closed; create successor packet |
| `connector_runtime_capture_20260719` | HTTPS allowlist, DNS pinning, redaction, retries and circuit breaker | Exercise transport, redirect, size and malformed-response paths | Redirect, policy or size failures are never silently retried |
| `canonical_domain_schemas_ontology_20260719` | Canonical URNs, crosswalk semantics and corpus checks | Complete migration fixtures and run all language adapters | Ambiguous mapping or disagreement fails the affected field |

## Panel validation

Use three isolated subagents: clean-room reproducer, adversarial safety
analyst and evidence auditor. Retain each report, environment, command log,
revision and SHA-256 digest. A disagreement is a failed gate, not a majority
vote. Panel results qualify the bounded preview only; beta, RC and stable-v1
gates remain subject to their declared policy.

## Exit evidence

Each track needs a linked test or fixture, a content-bound report and a current
blocker entry. Soak, operational ownership and release-authority decisions
remain open until evidenced.
