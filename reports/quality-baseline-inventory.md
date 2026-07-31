# Quality baseline inventory

**Recorded:** 2026-07-30  
**Work package:** WP-001  
**Scope:** imported `riopa_provenance` modules and repository tests

The dependency environment is now reproducibly provisioned from the portable
public-PyPI lockfile. The complete functional suite passes, but branch-aware
package coverage is **56%**, below the unchanged **90%** stable-release gate.
WP-001 therefore remains blocked on comprehensive test restoration rather than
dependency provisioning.

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
| `retry` | `tests/test_retry.py` | 4 | focused policy tests added in WP-002 |
| `roadmap` | `tests/test_roadmap.py`, `tests/test_roadmap_hardening.py` | 27 | focused tests present |
| `spatial` | `tests/test_spatial.py` | 15 | focused tests present |
| `validation` | `tests/test_validation_failures.py`, `tests/test_validation_integrity.py` | 21 | split focused tests present |
| `wfs` | `tests/test_wfs.py` | 2 | focused tests present |
| `yaml_tools` | `tests/test_yaml_tools.py` | 1 | focused tests present |

## Reproducible verification record

- `uv sync --python 3.13 --extra dev --extra spatial --frozen`: passed.
- `.venv/bin/python -m pytest -q`: **178 passed**.
- `uv run --python 3.13 bash scripts/ci_quality.sh`: passed, including Ruff,
  formatting, strict MyPy, Bandit, action-pin and workflow checks, schema and
  example validation, roadmap validation, package build, Twine checks and SBOM
  validation.
- Branch-aware coverage: **56%**, measured with the same `pytest-cov` options as
  GitHub Actions; the `--cov-fail-under=90` gate correctly remains failing.
- Exact-head GitHub Actions on `32bd5d5` proved locked installation and the
  engineering quality job; the Python 3.12/3.13 test jobs first exposed missing
  `scripts` package importability, corrected in `eb623f9`, and then retain the
  honest coverage gate.

The next WP-001 step is focused test restoration for the lowest-coverage
modules, beginning with `linz_enrichment`, `spatial`, `arcgis`, `publication`,
`wfs`, `linz_federation`, `linz_export`, `linz`, `lineage` and `linz_catalog`.
The passing functional suite is not evidence that the 90% release target has
been achieved.
