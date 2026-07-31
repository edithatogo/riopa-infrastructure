# WP-008 cross-repository adapter evidence

Date: 2026-07-31

## Bounded result

Two isolated clean clones produced additive RIOPA mapping adapters. The existing
dirty checkouts at `/Volumes/PortableSSD/GitHub/fyi-cli` and
`/Volumes/PortableSSD/GitHub/fyi-archive` were not modified.

| Repository | Native revision mapped | Adapter commit | Issue | Pull request | Local verification |
|---|---|---|---|---|---|
| `edithatogo/fyi-cli` | `2db4813da80d8c61f145c24b22ff4392830bcad5` | `75f83ecc6bc0add773ed281ce24a807f2bd1823f` | [#284](https://github.com/edithatogo/fyi-cli/issues/284) | [#285](https://github.com/edithatogo/fyi-cli/pull/285), merged as `d30a124beea0a30b2b59e2382b1853c448cc3b12` | 282 workspace tests and one doc-test passed at the initial adapter head; the schema correction passed nine focused tests, formatting, Clippy and exact central-schema validation |
| `edithatogo/fyi-archive` | `cea43a097f8928d7eaa4295d284f0b8d3999637b` | `a76eaeb5984da348c4aeb5ff0bc29b46feadcce5` | [#318](https://github.com/edithatogo/fyi-archive/issues/318) | [#319](https://github.com/edithatogo/fyi-archive/pull/319), merged as `4af7da5c95c2448f1a3a667779ca2f943999e67b` | 458 tests passed, one skipped, 91.76% repository branch coverage; the focused adapter suite passes 23 tests with 100% statement/branch coverage plus changed-file Ruff and ty checks |

The source revision identifies the pre-adapter native contract being mapped.
The separate adapter commit identifies the proposed implementation and prevents
the mapping from being misread as evidence about a later native contract.

## Cross-repository conformance

`schemas/adapter-mapping.schema.json` preserves four distinct classifications:
exact, approximate, extension-only and unmapped. Extension-only fields may name
an explicitly namespaced extension; unmapped fields must remain null. Exact and
approximate mappings must name a RIOPA target.

The committed profiles and deterministic aggregate are:

- `conformance/adapters/fyi-cli.json`
- `conformance/adapters/fyi-archive.json`
- `conformance/adapters/report.json`
- `tests/test_adapters.py`

The central test reloads both profiles through the schema and semantic checks,
requires unique repository identities, recomputes classification counts and
hashes, and compares the result byte-semantically with the committed report.

## Limitations

Both pull requests were merged on 2026-07-31. The mapping profiles demonstrate
explicit semantic correspondence; they do not claim full repository
conformance, publication, or lossless equivalence for approximate,
extension-only or unmapped fields.
