# Same-day campaign ledger recovery

Run [34629491783](https://github.com/edithatogo/riopa-infrastructure/actions/runs/34629491783)
completed its bounded lane and receipt validation, then failed while building
the cumulative ledger: `qualifying receipts require distinct UTC observation dates`.
The restored history contained three distinct qualifying observations on August 30.
Identical restored copies were already deduplicated by bytes; distinct attempts
on one day were incorrectly rejected altogether.

## Repair and boundary

Retain and chain every distinct receipt. Sort chronologically by UTC instant,
with deterministic digest tie-breaking and failures last at the same instant.
Count each UTC date once for daily qualification. Failed attempts retain their
segment/reset behavior; RC revision, activation, epoch, cadence, 90-day/three-cycle
beta and 30-day RC requirements are unchanged. Reject timezone-naive timestamps.
No receipt is rewritten or dropped to make an elapsed gate pass.

## Local reproduction

Download the named artifact from the failed run with `gh run download 34629491783
--name evidence-campaign-operational-beta-20260830-26bc0b4-operational-observation
--dir /tmp/campaign-34629491783` (one command). Pass all recursively discovered
`*.receipt.json` files to `scripts.build_campaign_ledger.build_ledger`.
`docs/campaign-same-day-recovery-20260912.json` records input hashes and the
local rebuilt chain. Result: 17 files, 15 distinct observations, two identical
copies deduplicated, 13 UTC dates; elapsed gate remains pending.
Three original same-day receipts are retained under
`tests/fixtures/campaign-same-day/` for a network-free regression.

This is a local replay of actual hosted receipts, not a new hosted run. After
integration, the already-configured workflow must produce a successor ledger
before hosted recovery is claimed. No schedule, campaign activation or live
workflow dispatch is changed or initiated here.

## Foundation follow-up

The foundation M3 inventory remains at M2. Inspection found that the declared
provenance 1.0.0-to-1.1.0 migration file is a bounded fixture, whereas the
normative event schema still requires `schema_version: 1.0.0` and does not
provide a target 1.1 event contract. The canonical-crosswalk fixture likewise
explicitly disclaims cross-runtime execution. Relabelling archived records would
not establish an applicable migration. The contract maintainers must identify or
implement the intended target contract before real-data migration qualification.
The campaign repair advances the separate actionable operations blocker and does
not substitute for that M3 evidence.

## Validation

Focused ledger/campaign tests: 30 passed, including real same-day receipts,
UTC dates, failed attempts, ordering, duplicate bytes, activation and RC binding.
Full suite: 1,977 passed, 1 skipped; 90.64% branch-aware coverage. Quality,
packaging/SBOM and deterministic reproducibility harnesses passed. Final advisory
review found no blocking regression or qualification weakening. Operations remains active/M1;
foundation remains validating/M2, with no publication or release decision.
