# Evidence index: New Zealand Spatial Archive real-data vertical slice

- **Track ID:** `nz_spatial_archive_mvp_20260718`
- **Status:** `active`
- **Target release:** `0.5.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Reference`
- **Risk / priority:** `Critical` / `P0`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Spatial data lead
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/49

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-004-sharded-archive-contract-20260731` | Catalogue-to-federation stages are independently resumable and content-bound | `src/riopa_provenance/linz_pipeline.py`, `tests/test_linz_pipeline.py`, `docs/linz-archive-pipeline.md` | Synthetic stage/dependency/replay tests pass; real-data MVP remains open |
| `NZ-SPATIAL-COUNCIL-SELECTION-20260825` | Select four council acquisition mechanisms after national inventory | `docs/nz-spatial-council-selection-20260825.json`, `tests/test_nz_spatial_council_selection.py` | Wellington ArcGIS, Queenstown Lakes ePlan, New Plymouth PDF map series and Tasman open-data/online-plan mechanisms are selected; rights, exact capture, legal status and external validation remain open |
| `WP-007-bounded-real-slice-20260731` | Real LINZ metadata, one WCC planning polygon, official planning PDF and facility CSV are content-addressed and linked to portable spatial materialisations | `evidence/wp007-real-slice/manifest.json`, `scripts/verify_wp007_slice.py`, `reports/wp007-bounded-real-slice.md` | Clean semantic rebuild passes; four-council/two-national-family coverage and external research-object validation remain open |
| `DATASET-ARCHIVE-INCORPORATION-20260802` | Required public national/council inputs are routed through immutable raw archive packets before materialisation or analysis | `docs/public-dataset-archive-incorporation-plan-20260802.json`, `tests/test_public_dataset_archive_plan.py` | Archive order and repository ownership defined; full payloads and four-council/two-national-family coverage remain pending |
| `STATS-NZ-MESHBLOCK-ARCHIVE-20260802` | One exact national supporting-geography edition is completely captured, checksum-bound and revision-addressed | [GitHub Actions run 30750165664](https://github.com/edithatogo/open_social_data/actions/runs/30750165664), [Hugging Face packet revision](https://huggingface.co/datasets/edithatogo/riopa-public-data-archive/tree/3f2dc0a4d95a4fcb495551098d58fc5bce9c9202), `docs/public-dataset-archive-incorporation-plan-20260802.json` | 57,575/57,575 IDs and 231 pages captured; pre/post inventory stable; every stored and expanded object verified |
| `STATS-NZ-MESHBLOCK-PROJECTION-20260803` | Content-addressed RIOPA source/capture records and a complete normalized feature projection are built only from the immutable packet | `evidence/stats-nz-meshblock-2026-projection/records-manifest.json`; projection `urn:riopa:projection:sha256:64a1cbce366794b2b802f04dbe2bf1dc5fbf813e5c5b159bcf0782af9adc511f` | 57,575 features, 236 capture records, page-level lineage, 16 null geometries, one invalid geometry preserved and zero implicit repairs; population, LINZ and council coverage remain open |
| `NATIONAL-WORKLOAD-MANIFEST-20260803` | The exact Meshblock geography and provisional subnational population packets are combined into a bounded national reference workload without an unsupported join | `docs/national-workload-manifest-20260803.json`; manifest SHA-256 `2576fb0f4711b57a1847ba5b0617d352ee80cbd7a6f0c3cafcf7f4abc672eb67` | Both packets are immutable and public; the workload permits readback and alignment checks but prohibits Meshblock population assignment, downscaling and national completeness claims |
| `STATS-NZ-MESHBLOCK-QUALITY-20260825` | Bounded geometry, completeness, fidelity, rights-metadata and lineage report over the immutable Meshblock projection | `docs/stats-nz-meshblock-projection-quality-report-20260825.json`, `tests/test_meshblock_projection_quality_report.py` | Projection checks pass; temporal history, population denominator, council/national source coverage, preservation acceptance and publication remain open |
| `STATS-NZ-MESHBLOCK-MATERIALIZATION-VALIDATION-20260826` | Validate receipt, projection identity and GeoParquet/DuckDB materialization links | `scripts/validate_meshblock_materialization_receipt.py`, `docs/meshblock-materialization-receipt-validation-20260826.json`, `tests/test_meshblock_materialization_receipt_validation.py` | The local 57,575-feature restore passes path, size, digest-chain, schema and cross-tool query checks; independent acceptance, national authority and release gates remain open |
| `STATS-NZ-MESHBLOCK-QUERY-CONTRACT-20260826` | Document packet-bound, read-only query examples for the verified projection | `docs/meshblock-projection-query-examples-20260826.md`, `tests/test_meshblock_projection_query_examples.py` | Interface columns are matched to the emitted schema and locally executed; independent acceptance, national authority and release gates remain open |
| `NZ-ARCHIVE-MVP-CLOSEOUT-20260829` | Link repository-owned implementation, tests, panel, migration and release-candidate evidence for the bounded archive slice | `docs/nz-archive-mvp-closeout-evidence-20260829.json`, `tests/test_nz_archive_mvp_closeout_evidence.py` | Linkage is complete for the bounded packet; full source coverage, restoration, preservation, external validation and release-authority gates remain open |
| `NZ-SPATIAL-ARCHIVE-REVIEW-REMEDIATION-20260825` | Review and remediate receipt binding, digest-chain validation, restored-artifact queries and CI failure coverage | `docs/nz-spatial-archive-review-remediation-20260825.json`, `src/riopa_provenance/archived_spatial.py`, `scripts/validate_meshblock_materialization_receipt.py`, `tests/test_meshblock_materialization_receipt_validation.py` | Repository defects are fixed and commit/digest-bound; external, dependency, release-cycle, preservation and authority gates remain open |
| `GTFS-ARCHIVE-DISPOSITION-20260829` | Preserve exact archived dispositions for candidate public Auckland and Christchurch GTFS sources | `docs/gtfs-archive-disposition-20260829.json`, `tests/test_gtfs_archive_disposition.py`, [Hugging Face archive revision](https://huggingface.co/datasets/edithatogo/riopa-public-data-archive/tree/001137c0df64e9f8a7b0539fd0286a7cd5819ce7) | Both candidate manifests are unavailable (404/401) with no payload; network and timetable claims remain disabled pending an exact-edition payload and terms receipt |
| `WCC-PUBLIC-ARCHIVE-SPATIAL-PROJECTION-20260830` | Consume one public-rights-qualified council packet into canonical/bitemporal, GeoParquet and DuckDB projections without live-source contact | `src/riopa_provenance/public_archive_spatial.py`, `docs/wcc-public-archive-spatial-projection-20260830.json`, `tests/test_public_archive_spatial.py` | Immutable HF revision and all packet bytes pass; one feature rebuilds deterministically with unknown valid time and no implicit geometry repair; broader council/national coverage and scheduled-cycle gates remain open |

The same revision’s Conductor regeneration receipt records the methods hash,
roadmap status, generated issue graph and full quality harness. This closes only
the bookkeeping task; national source, rights, preservation, population and
release gates remain open (`docs/nz-archive-mvp-conductor-regeneration-20260825.json`).

## Blocking defects

### New Plymouth document capture increment (2026-08-30)

`docs/npdc-map-document-capture-20260830.json` records the exact index and all
130 distinct in-content PDF downloads (97,420,678 bytes), with HTTP capture IDs,
retrieval times and SHA-256 digests. Every retained response was independently
checked locally for HTTP 200, absence of Content-Range, byte count and digest.
The typed, bounded capture script and hermetic tests are
`scripts/capture_npdc_map_documents.py` and `tests/test_npdc_map_document_capture.py`;
the source is registered in `config/source-registry/npdc-map-documents.json`.
The byte budget limits retained response bodies, not rejected transfer overhead.
Raw PDF objects and HTTP receipts remain in the ignored local archive store;
only non-reconstructive metadata is committed. This completes the index-defined
document acquisition increment, not a four-council capture-to-release chain,
current operative-status assessment, vector conversion, scheduled operation,
public payload rights qualification or independent preservation acceptance.

### Remaining track blockers

- All four blocking dependency tracks remain incomplete.
- Four heterogeneous council and two national source-family capture-to-release chains remain incomplete.
- External research-object validation and a second clean-environment reproduction remain absent.
- The four `0.5.0` release gates, including three scheduled archive cycles with change and recovery evidence, remain unpassed.
- Durable preservation/publication acceptance and accountable release-authority approval remain absent.
- Any defensible Meshblock-level population denominator remains pending. The workload manifest is a bounded reference input, not population or national analytical evidence.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required agent-panel lenses: Provenance analyst, Data-governance analyst, Operations analyst, Research-object analyst.

This index remains deliberately non-assertive while the track is `active`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.

The track entered `active` for the bounded archived Meshblock incorporation slice.
The qualified immutable packet is a frozen safe-parallel interface; incomplete
dependencies and all broader acceptance criteria remain open.
