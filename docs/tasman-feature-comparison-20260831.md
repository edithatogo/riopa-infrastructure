# Tasman archived feature comparison

The publication workflow compares each verified Tasman canonical projection to
the immutable initial accepted derived packet recorded in
`tasman-derived-acceptance-20260831.json`. This is a fixed baseline comparison,
not a comparison to the immediately preceding scheduled cycle.

## Identity and evidence

Comparison uses source object identifiers, not capture-specific feature IDs.
Source attributes and original geometry are compared separately. New capture
IDs or archive-recorded times alone must not report a data change. Source IDs
are identifiers within this selected layer, not evidence that upstream IDs can
never be reassigned. Changed geometry is not automatically repaired or treated
as an operative planning change.

Both canonical inputs are byte-bound. The baseline is anonymously read at its
recorded immutable Hugging Face revision; the current projection comes from the
already verified publication workflow. Downloading occurs only on GitHub Actions.
The comparison step receives no publication credential and cannot publish data.
Only the metadata report is retained in the existing Actions evidence artifact.

## Failure and recovery boundaries

Invalid digests, duplicate identities, malformed canonical records and unsafe
paths fail closed. Hermetic corruption-and-retry tests demonstrate that a failed
comparison cannot become success evidence and that retrying with verified bytes
can complete. Such tests are not elapsed hosted operational evidence or a
scheduled source failure/recovery cycle.

The report does not qualify the three-cycle alpha gate, the stable beta/RC
periods, legal validity, clean-room reproduction or whole-track completion.
It also cannot establish whether a difference originated upstream or in a
changed transformation. Run-attempt provenance and producer evidence remain
necessary when interpreting a reported difference.

## Next qualification work

Observe actual scheduled captures and their automatic publication follow-ups.
Bind each comparison to its source-run provenance; deduplicate retries by
source-run identity. A rolling predecessor ledger and a representative hosted
failure/recovery observation remain separate work, as do wider council and
national-source coverage. Do not promote the alpha gate merely because repeated
manual baseline comparisons pass.
