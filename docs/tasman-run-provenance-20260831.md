# Tasman hosted run provenance

Track: `nz_spatial_archive_mvp_20260718`, task 3.8, issue #49.

The source and derived publication receipts prove named packet acceptance, but
do not themselves prove whether capture began on a schedule. A separate
metadata-only receipt binds their byte hashes to GitHub's source and publication
run-attempt records. It runs after both publication verifiers and before the
metadata artifact upload.

The collector validates the repository, workflow path, branch, run and attempt
identities, source success, publication producer revision and triggering event.
An automatic `workflow_run` follow-up must match the upstream event's run and
attempt. Source capture and triggering attempts are recorded separately because
a successful retry may reuse an earlier capture checkpoint. A stable source-run
key supports deduplication: reruns are not additional scheduled captures.

The archived `hosted-run.json` also binds the original Tasman acquisition to its
run, attempt and code revision. Its enclosing matrix run may have failed for
another council; that overall outcome is retained, not relabelled as success.
The triggering attempt must still have succeeded.

Only read-only GitHub Actions access is added. The collector receives no Hugging
Face credential and neither downloads payloads nor publishes data. It retains
allowlisted metadata and receipt hashes, never API responses or exception text.
Failures make the workflow fail and retain a sanitized failure artifact.

## Qualification boundary

A scheduled source trigger is an observation, not release-cycle qualification.
This collector does not evaluate data change, recovery, source completeness,
clean-room reproduction or elapsed beta/RC requirements. Its qualification field
therefore remains false. The publication job is still running when this receipt
is produced; the completed workflow status must be checked separately.

Receipts are retained in the existing 90-day GitHub metadata artifact. They are
not a new durable Hugging Face preservation claim. Exact successful hosted
evidence is committed separately after execution. Existing source and derived
receipts remain unchanged, and the archive track stays active/M1.
