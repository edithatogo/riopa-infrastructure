# Quality baseline inventory

**Recorded:** 2026-07-30  
**Work package:** WP-001  
**Scope:** imported `riopa_provenance` modules and repository tests

This is an inventory, not a coverage result. The runtime dependency environment
is currently incomplete (`pytest` cannot import `pluggy`, and the frozen `uv`
environment cannot be provisioned), so no coverage percentage is asserted.

| Module | Test coverage entry | Functions/methods counted by source scan | Verification state |
|---|---|---:|---|
| `arcgis` | `tests/test_arcgis.py` | 6 | focused tests present |
| `capture` | `tests/test_capture.py` | 18 | focused tests present |
| `cli` | `tests/test_cli.py` | 34 | focused tests present |
| `crate` | `tests/test_crate.py` | 19 | focused tests present |
| `governance` | `tests/test_governance.py` | 5 | focused tests present |
| `hashing` | `tests/test_hashing.py` | 4 | focused tests present |
| `lineage` | `tests/test_lineage.py` | 15 | focused tests present |
| `linz` | `tests/test_linz.py` | 27 | focused tests present |
| `linz_catalog` | `tests/test_linz_catalog.py` | 19 | focused tests present |
| `linz_enrichment` | `tests/test_linz_enrichment.py` | 9 | focused tests present |
| `linz_export` | `tests/test_linz_export.py` | 8 | focused tests present |
| `linz_federation` | `tests/test_linz_federation.py` | 13 | focused tests present |
| `linz_inventory` | `tests/test_linz_inventory.py` | 17 | focused tests present |
| `methods` | `tests/test_methods.py` | 6 | focused tests present |
| `publication` | `tests/test_publication.py` | 8 | focused tests present |
| `registry` | `tests/test_registry.py` | 8 | focused tests present |
| `roadmap` | `tests/test_roadmap.py`, `tests/test_roadmap_hardening.py` | 27 | focused tests present |
| `spatial` | `tests/test_spatial.py` | 15 | focused tests present |
| `validation` | `tests/test_validation_failures.py`, `tests/test_validation_integrity.py` | 21 | split focused tests present |
| `wfs` | `tests/test_wfs.py` | 2 | focused tests present |
| `yaml_tools` | `tests/test_yaml_tools.py` | 1 | focused tests present |

## Reproducible verification record

- `python -m compileall -q src tests`: passed.
- JSON schema parsing with the standard library: passed.
- `python -m pytest --collect-only -q`: blocked by missing `pluggy` in the
  available interpreter.
- `uv sync --extra dev --extra spatial --frozen`: remains blocked by unavailable
  internal package artifacts; no stable coverage gate was weakened.

The next verification step is to provision the declared frozen environment and
run collection, focused tests, the full quality harness and coverage. Until
then, this inventory must not be treated as evidence of the 90% release target.
