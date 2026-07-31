# Preservation deposit plan

No deposit, DOI, release or preservation qualification is claimed by this plan.

## Recommended failure domains

1. Preserve the public Git source revision through Software Heritage.
2. Deposit the exact release assets, checksums, SBOM, attestations, research
   object and independent-review evidence in Zenodo or an approved
   institutional repository.

The release manifest must bind both deposits by persistent identifier and
content digest. GitHub alone is the build and distribution system, not the
independent preservation failure domain.

## Deposit sequence

1. Build an unpublished candidate and freeze every asset digest.
2. Complete clean-room reproduction against those bytes.
3. Resolve findings by creating a successor candidate; never overwrite reviewed
   evidence.
4. Create the protected release tag only after review succeeds.
5. Verify GitHub artifact attestations and `SHA256SUMS`.
6. Submit source to Software Heritage and capture the resulting persistent
   identifier.
7. Deposit the verified release package and evidence in Zenodo or the selected
   institutional repository, initially as a draft when supported.
8. Compare deposited downloads against the release manifest before finalising
   publication.
9. Record custodian, retention policy, access status, fixity-check schedule and
   recovery-test result.

## External requirements

Repository preparation can be automated, but final deposit requires an
authorised account owner. DOI publication, protected-tag creation, release
environment approval and any preservation-provider terms remain explicit
external actions.
