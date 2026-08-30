# Licensed Tasman publication and rebuild

This bounded NZ Spatial Archive increment publishes the captured TRMP zones
layer and its standalone CC-BY-4.0 item rights. Attribution is **Tasman District
Council (TDC)**. Mixed catalogue and website captures remain private; this
decision does not classify every Tasman dataset or establish operative status.

## Hosted execution

The `Publish and rebuild licensed Tasman archive` workflow runs after successful
main-branch council preservation, or manually with a council `source_run` ID.
It checks out trusted main-branch code, not code or artifacts from the triggering
run. A single publication writer prevents overlapping publication attempts;
the three source acquisition jobs remain parallel and independently resumable.

The workflow restores the immutable private Tasman packet, verifies its entire
manifest and tar closure before restoring files, and rebuilds the selected
public candidate using the pinned rights contract. It never reacquires the
live service. Changed rights, incomplete acquisition or corrupted bytes stop
publication. The 512 MB retained raw budget and file-count bounds remain in
force. Four workers verify public downloads in parallel.

Only that candidate is committed to `edithatogo/riopa-public-data-archive`.
Durable publication checkpoints retain the original immutable public revision;
retry verification must not silently replace that revision. Anonymous reads
use explicit unauthenticated access and check exact sizes and digests before
acceptance. Download caches remain outside the clean verified packet.

Two separate builds consume the public snapshot. They must agree on canonical
semantics, GeoParquet bytes and DuckDB semantic readback. DuckDB file bytes are
not asserted deterministic. Original geometry is retained; valid and operative
times remain unknown unless source evidence supplies them. These two builds
are hosted repeatability evidence, not two isolated clean-room agent reviews.

Only metadata receipts are retained as Actions artifacts. Raw source payloads,
canonical bulk records, GeoParquet and DuckDB files are never committed to Git.
Public payload acceptance, research-object release and stable-v1 qualification
remain separate outcomes. The whole-package CI coverage threshold stays 90%.

## Recovery

Rerun the workflow with the same source run to restore from private preservation
and reverify the recorded public revision. Do not delete a failing checkpoint,
rewrite historical receipts or republish different bytes under the same path.
Source acquisition failures remain visible in the council receipts even when
preserving the failed attempt succeeds. A successful preservation job alone
does not prove full ePlan acquisition or completion of an alpha operating cycle.

Post-upload verification failures must retain a bounded metadata receipt in the
Actions artifact and a separate durable private attempt record. These records
identify the failed stage and exception class, not raw exception messages,
credentials or payloads. They do not replace the original public revision or
turn a failed verification into acceptance. If private evidence storage itself
fails, the local artifact still records that limitation and the primary failure
remains a failed run.
