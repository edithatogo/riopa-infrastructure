# Reviewed Repository Inventory

This is the baseline evidence inventory for the architecture bundle. It should be regenerated periodically from repository manifests rather than maintained indefinitely by hand.

| Repository | Role observed | Relevant native evidence | Initial RIOPA adapter |
|---|---|---|---|
| `edithatogo/conductor-next` | context, plans, tracks and repository workflow | canonical Conductor documents and track directories | repository/track metadata projection |
| `edithatogo/fyi-cli` | source access and faithful capture | payload hash chain, provider contracts, source-specific capture logic | capture/artifact/provenance events |
| `edithatogo/fyi-archive` | orchestration, preservation and multi-mirror publication | WARC/WACZ, manifests, DuckDB, hashes, SBOM, attestations and DOI workflows | snapshot/materialisation/research-object release |
| `edithatogo/corpus-legislation-nz` | official-source legislation corpus | raw XML/HTML, normalised JSONL, Parquet, content hashes, coverage, HF/Zenodo | legal-source and corpus snapshot mapping |
| `edithatogo/nlp-policy-nz` | derived legislative/policy NLP | model/ontology pipeline, Parquet/LanceDB and publication protocol | transformation/model/source-span lineage |
| `edithatogo/rulespec-nz` | source-grounded rules-as-code | corpus citation paths, pinned SHAs, parity references and ratcheted gaps | provision/rule assertion and validation lineage |
| `edithatogo/open_social_data` | multi-provider social-data catalogue/fetch engine | provider URLs, ETags, Last-Modified, quality reports, Parquet and local catalogue | source/change/quality/catalogue mapping |
| `edithatogo/healthpoint-rs` | typed facility/service connector | FHIR identity, retrieval/source/tool provenance and explicit redistribution policy | rights-aware facility assertions |
| `edithatogo/digitalnz` | DigitalNZ notebooks/forked workbench surface | API exploration and harvest examples | evaluate whether to adapt, replace with typed connector, or retain as reference only |
| `edithatogo/ecosystem-docs` | ecosystem documentation hub | public map of interoperable research tools | programme/adoption/status publication |

## Review limitations

- The review is architectural and representative, not an exhaustive line-by-line audit of every repository.
- A repository may have stronger evidence than its README exposes.
- Adoption status must be measured by conformance fixtures and release artifacts, not this table.
- Forked or upstream-derived repositories require a separate ownership and divergence review before assigning implementation work.
