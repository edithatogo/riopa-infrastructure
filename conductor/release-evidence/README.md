# Release evidence

Each planned release can have one machine-readable `<version>.json` evidence record.
The record is validated against `schemas/release-evidence.schema.json`; local evidence
paths and declared SHA-256 digests are verified by `riopa roadmap validate`.

A release is reported ready only when every blocking gate has current evidence and all
stage-specific track requirements pass. Stable `1.0.0` additionally requires the global
thresholds, immutable and content-bound evidence, signed role approvals, release
artifacts and defect limits in `conductor/v1-gate.json`. Every local stable-evidence
file requires a verified digest; every external stable-evidence reference requires a
digest or recognised content-addressed persistent identifier.

Evidence is evidence of work completed; it must never be pre-populated merely to make a
roadmap appear green. Waivers are scoped, public, approved and time-limited. The stable
non-waivable categories cannot be bypassed.
