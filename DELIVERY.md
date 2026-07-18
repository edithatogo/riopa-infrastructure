# Delivery record

This repository is the executable architecture and implementation bundle for **RIOPA Infrastructure v0.1.0**, created on 18 July 2026.

## Included

- 7 architecture decision records;
- 13 dependency-linked Conductor tracks with specification, plan, metadata and index files;
- 10 JSON Schemas covering sources, artifacts, provenance events, transformations, materialisations, snapshots, quality, rights, methods facts and spatial rule links;
- a reference Python package and CLI for validation, publication-ready methods generation and RO-Crate research-object construction;
- a three-event, hash-linked synthetic example with internal and manifest integrity verification;
- GitHub repository, Project, issue graph, dependency, cross-repository adoption and RIOPA umbrella-mirroring automation;
- a staged New Zealand Spatial Archive source and implementation plan;
- facility-location, supermarket/health and ambulance/hospital pilot tracks;
- governance, licensing, privacy and Māori data sovereignty gates.

## Verified delivery state

- 24 schema and closed-bundle integrity checks pass.
- 23 automated tests pass.
- Branch-aware test coverage is 91.28% with a 90% CI floor.
- Methods regeneration is byte-for-byte stable against the checked-in example.
- The example research object rebuilds and all internal SHA-256 checks pass.
- GitHub issue and full bootstrap dry runs resolve the complete hierarchy without network writes.

This source archive does not claim that the remote GitHub repository, Project or issues exist until an applied bootstrap writes `project/bootstrap-summary.md` and `project/bootstrap-report.json`.

## Verification commands

```bash
uv sync --extra dev --frozen
uv run ruff check .
uv run ruff format --check .
uv run riopa validate --root .
uv run pytest --cov=riopa_provenance --cov-branch --cov-fail-under=90
make verify-bundle
bash -n scripts/bootstrap_github.sh
make bootstrap-dry-run
```

## Remote activation

```bash
gh auth refresh -s repo -s project
bash scripts/bootstrap_github.sh \
  --owner edithatogo \
  --repo riopa-infrastructure \
  --visibility public \
  --create-project \
  --create-issues \
  --cross-repo \
  --mirror-umbrella \
  --apply
```

GitHub saved project views are configured manually from `project/project.yaml`; all other declared bootstrap operations are automated and idempotent.
