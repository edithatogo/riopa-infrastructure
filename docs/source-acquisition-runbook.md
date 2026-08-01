# Source-authority and acquisition runbook

This runbook is the repository-owned control for any future source acquisition.
It does not authorise acquisition and must not be used to bypass a custodian's
written decision.

## Before requesting authority

1. Define the intended purpose, geography, time range, fields/geometries and
   transformations.
2. List explicit exclusions and prohibited uses (including operational,
   clinical, legal or national-completeness claims where not authorised).
3. Prepare a metadata-only request using
   `docs/source-authority-request-packet.md`.
4. Do not create credentials, scrape endpoints, download payloads or contact a
   custodian without the applicable approval.

## Required approval evidence

An approval record must validate against
`schemas/source-acquisition-approval.schema.json` and
`validate_source_acquisition_approval`. For `allow` and
`allow-with-conditions`, the record must contain real (non-placeholder)
recipient, source revision, rights reference and approving authority values.
The record must also be unexpired at the moment of acquisition.

The written custodian response must identify:

- the authoritative source and exact revision;
- coverage, exclusions and update/freshness behaviour;
- licence, attribution, redistribution, derivative-use and retention terms;
- privacy, safety and sensitive-location restrictions;
- correction, withdrawal and successor-notification procedure; and
- the authority and expiry of the decision.

## Acquisition and preservation

Only the named recipient may acquire the explicitly approved scope. Record a
source receipt (URL or transfer reference, retrieval timestamp, revision and
SHA-256) before transformation. Preserve the approval and receipt together;
never embed credentials or secrets in records, logs or fixtures.

If any term, revision, scope or recipient differs, stop and request a successor
approval. A non-response, ambiguous terms or an expired decision yields
`review-required` and is not permission.

## Fallback posture

Until authority is complete, retain only metadata already available under clear
public terms, use synthetic fixtures, and keep the project regional,
non-operational and non-authoritative. Do not infer national completeness from
an inventory or from a custodian's source-level authority.
