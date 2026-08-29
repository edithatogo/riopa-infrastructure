# Release-authority decision record (DRAFT — NOT SIGNED)

**Decision status:** DRAFT — NOT SIGNED; no release or promotion is authorised by this document.

**Current posture:** RIOPA remains a bounded regional, public-datasets-only, non-operational technical preview. Network, timetable, facility, national, clinical, dispatch and authoritative claims remain disabled until separately evidenced. The bounded pilot is limited to the frozen WP-010 packet and its documented scope, exclusions, safety constraints and expiry/review conditions.

## Evidence available to the decision-maker

The existing bounded pilot does not depend on access to a national ambulance
dataset. Custodian approval is required only if the scope expands to
authoritative provider, national, current-service or operational claims.

- Repository head: `d66fb07` (Tier-A ArcGIS archive publication, bounded test-acceleration profiles, operational-cycle evidence schema, benchmark scenarios, panel templates and release-readiness projection).
- Successor preservation record: [Zenodo 10.5281/zenodo.21737563](https://doi.org/10.5281/zenodo.21737563).
- Public Tier-A archive revision: `001137c0df64e9f8a7b0539fd0286a7cd5819ce7` on [Hugging Face](https://huggingface.co/datasets/edithatogo/riopa-public-data-archive). It contains three rights-qualified regional packets (230 features total) with fixity and publication receipts; it does not establish national or operational authority.
- Role-separated agent evidence: two clean-room bundle builds were byte-identical; `verify.py` passed; expected SHA-256 was `26bf2281…b6813`; hosted clean-room and two distinct agent journeys are recorded. This satisfies the bounded repository reproduction gate but not elapsed operation, external-system acceptance or promotion authority.
- Public-source metadata refresh found no candidate with both confirmed authoritative status and clear redistribution rights. No acquisition or national-completeness claim is authorised.
- Repository-owned preparation now includes a fail-closed operational-cycle/soak schema, deterministic local restore/rollback evidence, structured regional benchmark scenarios, bounded test-feedback profiles, and pending qualification templates for all 28 tracks. These artifacts do not represent elapsed-time, production or national-scale evidence.

## Promotion prerequisites

### Beta

Before beta consideration, the accountable authority must receive and accept:

1. A role-separated agent-panel clean-room reproduction, including adverse findings, dissent and remediation disposition.
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

1. Two isolated role-separated agent clean-room reproductions.
2. Two distinct agent-operated user/operator journeys with documented adverse-case outcomes.
3. Authoritative custodian confirmation for any data or claim presented as authoritative or national.
4. Signed release-authority approval with scope, exclusions, review date and revocation conditions.

## Explicit open factual gates

- Candidate-specific role-separated agent reproduction and workflow evidence must be rerun for beta, release candidate and stable v1; no second human or external operator is required.
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
