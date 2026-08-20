# Stable-v1 blocker audit — 2026-08-01

This is a repository-owned status snapshot for planning work. It does not waive
the normative gates in `conductor/v1-gate.json` or promote any track.

## Current inventory

The Conductor registry contains 28 v1-critical tracks. All 28 currently target
M6 but remain at M1; 26 are `specified`, one is `active`, and one is
`validating`. Consequently, the stable-v1 gate cannot pass yet even though the
roadmap and local validators are healthy.

## Top repository-owned blockers

### 1. Track implementation and evidence progression

The critical tracks are still mostly specifications. Each track needs an
implementation slice, executable tests, an immutable/version-addressed
evidence record, and a status transition through the Conductor workflow. The
highest-leverage starting points are the dependency roots:

- `foundation_architecture_20260718` (currently active)
- `facility_location_engine_20260718`
- `canonical_domain_schemas_ontology_20260719`
- `provenance_profile_v1_20260718`

**Contingency:** if a track cannot be implemented safely without external
data, keep it specified and add a bounded fixture/evidence plan rather than
claiming completion.

### 2. Cross-track contracts and conformance evidence

The stable gate requires frozen schemas, ontology, APIs and at least two
conforming implementations. The repository should next produce a versioned
positive/negative conformance corpus and machine-readable results before any
track is advanced to beta or higher.

**Contingency:** fail closed on unmapped fields and publish only the bounded
regional technical-preview scope until the corpus is complete.

### 3. Operational, security and performance qualification

The release plan requires security/supply-chain qualification, representative
operational cycles, 90 days of beta evidence and a 30-day release-candidate
soak. These are repository-owned evidence programmes but cannot be fabricated
from local unit-test results.

**Contingency:** maintain the current technical-preview label and create
version-addressed test plans, fixtures and report templates while soak data is
accumulated.

## External gates deliberately unchanged

The bounded WP-010 panel path is approved for the public-datasets-only,
regional, non-operational preview. Higher-tier release requirements and the
2026-08-31 review remain governed by their existing decisions. This audit does
not reinterpret panel output as operational or national evidence.

## Next repository-owned actions

1. Implement and evidence the dependency-root tracks in topological order.
2. Add the shared conformance corpus and machine-readable result artifact.
3. Add repeatable operational/security/performance test harnesses and begin
   collecting time-based evidence.
4. Regenerate the release-evidence index whenever a track advances.
5. Re-run `uv run riopa roadmap validate` and the complete test suite at every
   status transition.
