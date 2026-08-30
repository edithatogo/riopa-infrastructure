# Hosted council preservation

Track: `nz_spatial_archive_mvp_20260718`, issue #49.

`.github/workflows/council-archive.yml` runs three independent source jobs
(Tasman, NPDC and QLDC) concurrently on GitHub Actions. Each source retains its
registered one-request-per-second, single-connection load policy. `fail-fast:
false` lets other sources finish when one source fails. Dispatch manually or use
the daily schedule; a new run is a new observation, not an atomic source snapshot.
Per-source job concurrency also serialises overlapping manual/scheduled runs
without cancelling an active capture or upload. Different sources still run in parallel.

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
  The workflow uploads only the non-reconstructive `public/` evidence directory.

After a new successful Tasman capture and private preservation, Actions prepares
a layer-only public candidate using a separately captured item licence. The
builder binds the exact approved licence-text digest, item and layer identities,
attribution and captured response integrity. Mixed catalogue and website bytes
are excluded from this candidate, not deleted from private preservation. The
candidate itself stays outside Git/Actions artifacts; only its preparation
summary is uploaded. A preparation failure does not undo the preceding private
preservation. Completed source checkpoint replay skips preparation as well as
capture; this is not a public-publication retry mechanism. Public upload,
anonymous payload readback and materialisation acceptance are separate next steps.

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
   private source checkpoint. Since PR #748, successful preservation/readback
   returns success even for an incomplete source; `acquisition_complete: false`
   remains explicit and its checkpoint is not reused as complete. A green
   preservation job therefore does not establish complete acquisition.

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

## Observed hosted execution — 2026-08-30

[Run 33298342091](https://github.com/edithatogo/riopa-infrastructure/actions/runs/33298342091)
executed three concurrent sources at `1babdbf333091ff3f65b96ccf03990052ce82589`.
Tasman and NPDC completed bounded acquisition and immutable preservation.
First-attempt raw tar sizes were 24,985,600 bytes (Tasman), 98,273,280 bytes
(NPDC), and 3,082,240 bytes (incomplete QLDC). These are archive sizes, not
source payload totals. All three produced anonymous public evidence.

Attempt 2 verified Tasman/NPDC checkpoints and skipped their capture/publication
steps. QLDC reacquired and preserved another incomplete attempt: hosted authority
and guide routes returned 200, while both application routes returned 404.
Independent private-packet readback confirmed the latter observations; they are
not the earlier local 403 observations. Both workflow attempts correctly ended
in failure because QLDC acquisition was incomplete, not because its packet was
lost. This closes task 1.9's hosted preservation/replay scope, not the wider track.

`hosted-council-preservation-20260830.json` records per-attempt job outcomes,
immutable private/public revisions, archive digests, and independently retrieved
anonymous evidence hashes. The isolated reviewer separately checked Tasman and
QLDC public manifests; private verification is explicitly distinguished.

PR #746 briefly serialized the entire matrix to avoid shared HF branch races.
That also serialized downloads, contrary to the approved requirement. The
evidence closeout restores three parallel sources, retaining bounded optimistic
commit retries and same-source cross-run serialization. The cited execution
already exercised this parallel configuration, including immutable readback.

## Reproduction commands

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

Initial hosted registration at `3ae6875` failed before jobs started because
`runner.temp` is not available in job-level environment expressions. The
successor uses a literal ignored work directory with a matching public-only
artifact path; a regression assertion covers both bindings. This was a workflow
validation failure, not a completed capture or a source-service failure.

Implementation references: [GitHub job matrices](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations)
and [Hugging Face upload API](https://huggingface.co/docs/huggingface_hub/guides/upload).

## Observed hosted execution — run 33301038921

[Run 33301038921](https://github.com/edithatogo/riopa-infrastructure/actions/runs/33301038921)
completed successfully on `df52ca881ce6f7937046095e1112b4da2bc1da07`. The
Tasman, QLDC and NPDC jobs succeeded (job IDs `99229124204`, `99229124249` and
`99229124273`). Their evidence artifacts were respectively `9728945563`
(1,008 bytes), `9728942869` (482 bytes) and `9728959528` (480 bytes). The
machine-readable record is
`docs/hosted-council-preservation-run-33301038921.json`.

The Tasman job successfully prepared, but did not publish, the isolated
CC-BY-4.0 candidate for 3,655 features across 12 captured files (24,378,239
bytes), with TDC attribution. QLDC remains a route-qualification-only,
incomplete acquisition. This run provides preservation and preparation
evidence only: it does not establish public-payload upload or anonymous
payload acceptance, canonical/materialised rebuild, operative legal status,
beta/RC/stable-v1 promotion, or any national/operational claim.
