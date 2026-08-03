# WP-010 external operator reproduction request

This package is ready to send to an independent operator. It is a request,
not evidence that reproduction has occurred and not an authorization for beta,
release-candidate or stable-v1 promotion.

## Frozen target

- Follow [`wp010-external-reproduction-handoff.md`](wp010-external-reproduction-handoff.md).
- Use the exact frozen revision and reviewer-bundle digest stated there.
- Verify the published packet at [Zenodo DOI 10.5281/zenodo.21737563](https://doi.org/10.5281/zenodo.21737563).
- Do not substitute a local or modified packet; record the observed SHA-256.

## Independence and approval requirements

The operator must be a person outside the implementation run, disclose their
identity or accountable organisation, and state any relationship or conflict
with the project. The project owner must approve the operator before the run;
that approval is recorded with the report and does not waive any release gate.

## Requested report

Complete [`wp010-external-reproduction-report-template.md`](wp010-external-reproduction-report-template.md)
and return it as a content-bound report containing:

1. operator identity, independence statement and approval reference;
2. operating system, runtime and dependency versions;
3. exact revision, Zenodo DOI and packet/bundle digests;
4. commands run and complete stdout/stderr or linked immutable logs;
5. pass/fail results, deviations, safety or rights observations;
6. report digest, date and recommendation limited to the bounded pilot.

Until this report is accepted, the pilot remains regional, non-operational and
non-authoritative, and issue #149 remains open.
