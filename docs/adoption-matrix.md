# Cross-Repository Adoption Matrix

The goal is additive standardisation. Existing evidence is retained and mapped; repositories are not forced into one language or storage engine.

| Repository | Existing strength | Gap addressed by RIOPA | First adoption issue |
|---|---|---|---|
| `fyi-cli` | faithful capture, content hashes and tamper-evident hash chain | semantic activity/input/output events, source rights facet, stable cross-repo IDs | emit RIOPA capture events alongside current chain |
| `fyi-archive` | orchestration, WARC/WACZ truth, Parquet/DuckDB, mirrors, SBOM and release provenance | shared snapshot manifest, RO-Crate 1.3, structured transformations/quality and methods generator | build a RIOPA-compatible release bundle without changing capture ownership |
| `nlp-policy-nz` | modular pipeline, Parquet/LanceDB, ontology and publication tooling | model/ontology/chunk lineage, source-span derivation, shared research-object package | emit transformation runs and derived-layer lineage |
| `healthpoint-rs` | FHIR-first typed connector, explicit rights status and provenance | shared source/capture events and facility assertions for spatial reconciliation | map export manifest and records to RIOPA profile, preserving licence restrictions |
| `open_social_data` | typed multi-provider catalogue/fetch engine, ETag/Last-Modified and quality reports | shared source/change/run/materialisation events | emit RIOPA events beside current Rust outputs |
| `digitalnz` | forked/upstream notebook workbench relevant to Gazette discovery | ownership/divergence decision before adapter work | use as reference unless a maintained typed connector is justified |
| `corpus-legislation-nz` | versioned NZ legislation corpus | legal-source version, transformation and provision identity linkage | publish a RIOPA snapshot/research-object mapping |
| `rulespec-nz` | corpus citation paths, pinned comparison SHAs and ratcheted validation gaps | explicit provision-to-rule and manual-interpretation lineage | map one source-grounded RuleSpec slice |
| `ecosystem-docs` | central documentation hub | programme architecture and adoption status | publish RIOPA programme page and links |
| future `nz-spatial-archive` | reference archive | full implementation | instantiate all mandatory profile components |

## Adoption levels

- **A0 documented:** repository identifies source, output and existing provenance mechanisms.
- **A1 event producer:** emits valid capture/transformation events.
- **A2 snapshot producer:** emits snapshot manifest, materialisation and quality records.
- **A3 research-object producer:** emits RO-Crate, methods, citation and attestations.
- **A4 independently reproduced:** a clean environment rebuild is recorded and compared.

## Compatibility rule

A repository may adopt only the relevant level. For example, a connector should not fabricate a dataset snapshot; an analytics repository need not own source credentials.

## Migration sequence

1. Inventory current fields and evidence.
2. Create a mapping document with exact/approximate/unmapped classifications.
3. Add optional RIOPA output behind a stable command or library feature.
4. Add schema and golden-fixture tests.
5. Run dual output through at least one release.
6. Promote the RIOPA contract to supported after downstream validation.
