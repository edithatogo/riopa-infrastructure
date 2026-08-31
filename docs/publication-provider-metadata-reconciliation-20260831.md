# Public provider metadata reconciliation

WP-003 / publication validation issue #129 gains an anonymous Hugging Face
adapter for an exact metadata object. This is not a generic upload client.

`scripts/reconcile_publication_provider_metadata.py` accepts a strict request
with provider, repository, immutable revision, relative JSON path, expected
SHA-256 and a maximum byte count capped at 2 MiB. It checks public visibility,
the resolved commit, remote path/size and fresh downloaded bytes before emitting
a content-bound observation. Invalid bindings, missing objects, conflicts and
transport failures cannot produce a successful observation. At most three
adapter attempts apply only to transient reads, never to a provider write.
The provider SDK can retry internally; this is not a three-HTTP-request limit.
The hosted job has a five-minute timeout.
Each adapter attempt is retained in a bounded, digest-bound history with a
sanitized outcome; successful recovery does not erase earlier failures.

All provider calls explicitly disable tokens. Live execution is restricted to
GitHub Actions; tests inject a transport and use synthetic metadata. Neither
credentials nor downloaded metadata content are emitted in the report. The
read-only workflow retains both successful and failed observations as artifacts.

The checked-in request selects the already-public v0.4.0 release metadata at the
revision and checksum in `docs/v0.4.0-release-mirror-20260829.json`. It does not
retroactively bind that historical release to a newly generated publication
plan. No source datasets are acquired or uploaded by this workflow.

`matching-metadata-observed` means only that the named public metadata object
matches the expectation at the observed revision. It is not a completed target
receipt, proof of every release asset, current rights clearance, authorization
to write, DOI acceptance, a signature or stable-release qualification. Authenticated
GitHub/Hugging Face/Zenodo publication reconciliation remains separate work.

## Hosted observation

`docs/publication-provider-metadata-acceptance-20260831.json` records successful
Actions run 33385363775 at merged revision
`703b7ccdeb612056bde49306502f036ccebfb1ce`. One anonymous adapter attempt
verified the expected 1,178-byte metadata object. The 1,130-byte observation is
content-bound and retained with the completed job and artifact identifiers.
This is a successful read, not hosted transient-failure/recovery evidence or
authorization to perform a provider write.
