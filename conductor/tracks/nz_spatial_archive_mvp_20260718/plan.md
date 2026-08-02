# Plan: nz_spatial_archive_mvp_20260718

## 1. Real source capture

- [ ] 1.1 Select councils after national source inventory and record heterogeneity rationale.
- [ ] 1.2 Archive exact-version national layers, council services and planning documents faithfully before incorporating their named snapshots.
- [ ] 1.3 Preserve rights, capability, legal-status and source-health evidence.
- [x] 1.4 Acquire and verify the complete Stats NZ Meshblock 2026 supporting-geography packet at immutable GitHub and Hugging Face revisions.
- [x] 1.5 Project the immutable Meshblock packet into content-addressed RIOPA source and capture records without contacting its live service (`8f34bfd`).

## 2. Canonical bitemporal model

- [ ] 2.1 Transform source layers into canonical feature/version records.
- [ ] 2.2 Preserve original geometry and produce separately evidenced repairs.
- [ ] 2.3 Link source, document and plan identities without unsupported interpretation.
- [x] 2.4 Build a normalized Meshblock feature projection with page-level capture lineage and no implicit geometry repair (`8f34bfd`; projection `urn:riopa:projection:sha256:64a1cbce366794b2b802f04dbe2bf1dc5fbf813e5c5b159bcf0782af9adc511f`).

## 3. Materialisation and quality

- [ ] 3.1 Generate GeoParquet and DuckDB Spatial outputs and query examples only from content-addressed archived source packets.
- [ ] 3.2 Run geometry, topology, completeness, temporal, rights and lineage checks.
- [ ] 3.3 Produce coverage, fidelity and unresolved-status reports.
- [x] 3.4 Validate the complete offline projection and commit bounded evidence while keeping bulk spatial outputs outside Git (`evidence/stats-nz-meshblock-2026-projection/records-manifest.json`).

## 4. Research-object release

- [ ] 4.1 Generate methods, citation, provenance, SBOM and attestations.
- [ ] 4.2 Run external validation and clean-environment rebuild.
- [ ] 4.3 Publish immutable DOI-ready MVP and correction policy.

## 5. Review fixes

- [x] 5.1 Verify compressed and uncompressed artifact identities, require a retrieval receipt for every projected capture record, safely reuse only a verified local packet, reject redirects outside the archive host boundary and separate stable semantic identity from run-specific DuckDB bytes (`ffeb681`, `6c9c5c8`, `f04693c`, `de8b790`).

## Track closeout

- [ ] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [ ] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.
