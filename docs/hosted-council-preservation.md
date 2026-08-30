# Hosted council preservation

Track: `nz_spatial_archive_mvp_20260718`, issue #49.

`.github/workflows/council-archive.yml` runs three independent source jobs
(Tasman, NPDC and QLDC) concurrently on GitHub Actions. Each source retains its
registered one-request-per-second, single-connection load policy. `fail-fast:
false` lets other sources finish when one source fails. Dispatch manually or use
the daily schedule; a new run is a new observation, not an atomic source snapshot.

## Storage and rights

- Full retained source bytes, including valid incomplete/denied observations,
  go to the **private** Hugging Face dataset `edithatogo/riopa-nz-spatial-raw`.
- Non-reconstructive file manifests and verification receipts go to the public
  dataset `edithatogo/riopa-public-data-archive`.
- This first hosted pipeline does not publish raw payloads publicly. It does
  not exclude future public archival: the licensed Tasman layer can be split
  from mixed-rights website/catalogue material in a subsequent public packet.
  NPDC and QLDC still require exact public-payload disposition. The governing
  decision is `source-rights-archive-default-20260829.json`.
- Never upload `packet/`, `store/` or raw bytes as GitHub Actions artifacts.
  The workflow uploads only `public/preservation.json`.

The existing authenticated owner's credential is stored as the GitHub repository
secret `HF_TOKEN`. It is supplied only to checkpoint/publication steps, never to
the source capture step or a pull-request workflow. The workflow is main-only;
checkout credentials are disabled, Actions are SHA-pinned, and dependencies are
locked in the optional `preservation` extra.

## Failure and recovery contract

1. Before source contact, look for this run/source's HF checkpoint. Missing
   checkpoints start a new capture; credential, integrity and service failures
   fail closed rather than silently discarding a checkpoint.
2. Reuse only a complete checkpoint matching the exact source, GitHub run and
   code revision. Re-download and verify its immutable raw packet and every tar
   member first. The durable checkpoint binds the original public revision and
   both evidence file sizes/digests; recheck those exact bytes anonymously without
   republishing a replacement. Lost public evidence fails checkpoint replay.
3. New acquisition has a 600-second subprocess limit. Source failures/timeouts
   are packaged as incomplete. Retain all well-formed captured responses and
   their original receipt identities; never promote partial responses.
4. Verify local capture hashes and byte counts. Reject symlinks, unsafe paths,
   non-regular files, corrupt metadata, excess file counts and oversized packets.
   Corrupt stores are rejected, not certified as preserved. There is a 512 MB
   packet-content budget, 10,000-file limit and explicit bounded tar overhead.
5. Commit each attempt under `campaigns/<run>/<source>/<attempt>/`. Raw archive
   and manifest are committed together; commits use optimistic concurrency and
   at most four attempts for conflicts/transient errors. Nothing is deleted.
6. Read back the raw archive from the exact returned HF revision. Check remote
   sizes before downloading; verify the manifest before downloading raw bytes.
   Verify archive size/digest and every member, without extracting tar paths.
7. Publish only the manifest and preservation evidence publicly; verify their
   bytes anonymously at the returned immutable revision. Only then write the
   private source checkpoint. Incomplete captures still fail their job after
   successful preservation; their checkpoints are not reused as complete.

Rerun failed jobs to reacquire incomplete sources while retaining prior attempts.
Rerunning all jobs also demonstrates checkpoint reuse for successful sources.
Resume is currently at the **source boundary**, not per HTTP request or byte
range. An abrupt runner loss before HF commit can require re-downloading that
source. A normal source timeout still proceeds to preservation, but unavailable
HF storage or corrupt local bytes cannot be called a successful preservation.
Do not imply zero data-loss risk or exactly-once distributed execution.

Daily runs and manual dispatches do not by themselves satisfy the three-cycle
change/recovery gate, SLO history or stable-only beta/RC periods. Those require
separately reconciled evidence. Successful QLDC route qualification would still
not establish a complete ePlan archive or operative legal status.

## Commands and validation

```sh
gh workflow run council-archive.yml --ref main
gh run list --workflow council-archive.yml
uv run pytest -q tests/test_hosted_council_archive.py
uv run mypy src scripts/hosted_council_archive.py
```

The tests exercise deterministic packets, corrupt/symlinked inputs, unsafe tar
members, partial/time-limited captures, secret isolation, parallel workflow
structure, optimistic commit retries, visibility enforcement, oversized remote
rejection, anonymous readback failure and exact-code checkpoint reuse.

Implementation references: [GitHub job matrices](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations)
and [Hugging Face upload API](https://huggingface.co/docs/huggingface_hub/guides/upload).
