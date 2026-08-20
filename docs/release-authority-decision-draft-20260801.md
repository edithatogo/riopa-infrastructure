# Release-authority decision record (DRAFT — NOT SIGNED)

**Decision status:** DRAFT — NOT SIGNED; no release or promotion is authorised by this document.

**Current posture:** RIOPA remains a bounded regional, public-datasets-only, non-operational technical preview. Network, timetable, facility, national, clinical, dispatch and authoritative claims remain disabled until separately evidenced. The bounded pilot is limited to the frozen WP-010 packet and its documented scope, exclusions, safety constraints and expiry/review conditions.

## Evidence available to the decision-maker

The existing bounded pilot does not depend on access to a national ambulance
dataset. Custodian approval is required only if the scope expands to
authoritative provider, national, current-service or operational claims.

- Repository head: `2278cc8` (operational-cycle evidence schema, stressed/degraded benchmark scenarios, panel templates and release-readiness projection).
- Successor preservation record: [Zenodo 10.5281/zenodo.21737563](https://doi.org/10.5281/zenodo.21737563).
- Internal panel rehearsal: two clean-room bundle builds were byte-identical; `verify.py` passed; expected SHA-256 was `26bf2281…b6813`. This is rehearsal evidence only and does **not** satisfy the mandatory independent external-operator gate.
- Public-source metadata refresh found no candidate with both confirmed authoritative status and clear redistribution rights. No acquisition or national-completeness claim is authorised.
- Repository-owned preparation now includes a fail-closed operational-cycle/soak schema, deterministic local restore/rollback evidence, structured regional benchmark scenarios, and pending qualification templates for all 28 tracks. These artifacts do not represent elapsed-time, production, national-scale or external-operator evidence.

## Promotion prerequisites

### Beta

Before beta consideration, the accountable authority must receive and accept:

1. An independent external person/operator clean-room reproduction, including adverse findings and remediation disposition.
2. A complete provenance, licence and rights receipt for every source used by the beta scope.
3. Domain-confirmed ontology/conformance evidence for the claims made by that scope.
4. Safety review, bounded monitoring and rollback/withdrawal procedures.
5. A named accountable release authority's signed, scope-limited decision.

### Release candidate

In addition to beta prerequisites:

1. Reproducible candidate artifacts and hosted checks bound to the exact release head.
2. Operational/readiness evidence, including failure handling and soak-period results.
3. Reconciliation of all open issues, conductor-track acceptance criteria and evidence links.
4. Explicit approval of source freshness, correction and withdrawal processes.

### Stable v1

In addition to release-candidate prerequisites:

1. Two clean-room reproductions, including at least one qualifying external operator reproduction.
2. Completed external user/operator workflows and documented adverse-case outcomes.
3. Authoritative custodian confirmation for any data or claim presented as authoritative or national.
4. Signed release-authority approval with scope, exclusions, review date and revocation conditions.

## Explicit open external gates

- Independent external operator reproduction remains required for beta, release candidate and stable v1; internal subagent/panel rehearsal cannot substitute for it.
- Written custodian authority, source status, licence and redistribution terms remain outstanding for national/provider ambulance data.
- Domain owner confirmation of ontology/conformance remains outstanding for any expanded claims.
- A named accountable release authority has not signed a promotion decision.
- The bounded pilot must be reviewed by **2026-08-31**, or sooner if scope, rights, source status or safety changes.

## Decision requested from accountable authority

The repository owner has authorized preparation of the release packet, but this draft remains unsigned and records no promotion authorization. Select one and sign separately:

- **Maintain technical preview (recommended):** keep current regional scope and defer beta/RC/stable promotion until all gates above are evidenced.
- **Approve a narrower beta:** only if every beta prerequisite is attached, with explicit exclusions, expiry and rollback conditions.
- **Decline/withdraw:** pause the pilot and publish a withdrawal/correction notice if rights, safety or source status cannot be established.

**Signature:** ____________________  **Role:** ____________________  **Date:** __________
