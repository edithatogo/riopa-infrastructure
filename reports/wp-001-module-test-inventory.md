# WP-001 module and test inventory

Recorded 2026-07-27 from the imported development snapshot. A test file is
listed only when it directly imports or exercises the module; incidental text
references do not establish coverage. Measured line/branch coverage remains
unavailable until the locked environment can be provisioned.

| Module | Lines | Direct focused test | WP-001 disposition |
|---|---:|---|---|
| `arcgis` | 365 | none | restore positive, pagination, attachment and failure tests |
| `capture` | 368 | `test_capture.py` | retain; expand retry/network failure coverage in WP-002 |
| `cli` | 965 | `test_cli.py` | retain; extend with each restored command surface |
| `crate` | 742 | `test_crate.py` | retain; expand arbitrary-bundle and failure tests |
| `hashing` | 44 | `test_hashing.py` | retained |
| `lineage` | 543 | `test_lineage.py` | third restored slice: graph walks, cycle safety, impact ordering and identity conflicts |
| `linz` | 773 | `test_linz.py` | second restored slice: revision/state-chain negative tests; add database failure injection when dependencies provision |
| `linz_catalog` | 620 | `test_linz_catalog.py` | first restored slice in this increment |
| `linz_enrichment` | 463 | none | restore service queue, receipt and resume tests |
| `linz_export` | 322 | none | restore export, integrity and failure tests |
| `linz_federation` | 978 | none | restore policy, staging, path and reproducibility tests |
| `linz_inventory` | 605 | none | restore planning, batching and disposition tests |
| `methods` | 307 | `test_methods.py` | retain; expand missing-evidence consistency tests |
| `publication` | 425 | none | restore rights, retry, reconciliation and resumability tests |
| `registry` | 196 | `test_registry.py` | retained |
| `roadmap` | 1,528 | `test_roadmap.py`, `test_roadmap_hardening.py` | retained |
| `spatial` | 598 | none | restore conversion, invalid geometry and deterministic output tests |
| `validation` | 706 | `test_validation_failures.py`, `test_validation_integrity.py` | retained |
| `wfs` | 223 | `test_wfs.py` | constructor and request-contract negatives; restore transport/pagination failures next |
| `yaml_tools` | 47 | `test_yaml_tools.py` | retained |

## Baseline blockers

- `uv sync --extra dev --extra spatial --frozen` repeatedly failed while
  downloading locked packages from the configured package mirror, including
  `tzdata==2026.3`, `virtualenv==21.6.1`, `httpcore==1.0.9`, and
  `pygments==2.20.0`.
- The system Python has an incomplete pytest installation (`pluggy` missing).
- The partially created environment can start pytest, but package collection
  fails because the project dependency `rfc8785` is unavailable.
- Consequently no new coverage percentage is claimed. The handoff’s last
  recorded combined branch-aware coverage remains historical evidence only,
  not a current result.

## First restored test slice

`tests/test_linz_catalog.py` adds positive, negative, path-safety,
determinism, classification and pagination-header tests for the pure catalogue
core. Syntax compilation is locally verifiable; execution and measured coverage
remain pending locked-environment provisioning.
