#!/usr/bin/env bash
set -euo pipefail
uv run ruff check .
# Historical release evidence is digest-bound and intentionally retains the
# formatter version used when that release was attested.
uv run ruff format --check . --exclude conductor/release-evidence/artifacts
uv run mypy src/riopa_provenance
uv run bandit -q -c pyproject.toml -r src/riopa_provenance
uv run python scripts/check_action_pins.py --root .
uv run python scripts/check_workflow_lint.py --root .
uv run python scripts/check_workflow_policy.py --root .
uv run python scripts/check_tracked_secrets.py --root .
uv run riopa validate --root .
uv run riopa registry validate --registry config/source-registry/nz-spatial-pilot.yaml --schema schemas/source-registry.schema.json
uv run riopa roadmap validate --root .
uv run python scripts/validate_all_track_panel.py \
  docs/panel-reports/20260802/adversarial-analyst.json \
  docs/panel-reports/20260802/evidence-auditor.json \
  docs/panel-reports/20260802/reproducer.json \
  --tracks-root conductor/tracks \
  --synthesis docs/panel-reports/20260802/orchestrator-synthesis.json
cp project/issues.yaml "${TMPDIR:-/tmp}/riopa-issues-before.json"
uv run riopa roadmap generate-issues --root .
diff -u "${TMPDIR:-/tmp}/riopa-issues-before.json" project/issues.yaml
uv run riopa methods --manifest examples/minimal/snapshot-manifest.json --output "${TMPDIR:-/tmp}/RIOPA-METHODS.md"
diff -u examples/minimal/METHODS.md "${TMPDIR:-/tmp}/RIOPA-METHODS.md"
rm -rf dist/package
uv build --out-dir dist/package
uv run twine check dist/package/*
scripts/build_sbom.sh dist/package/riopa-provenance.cdx.json
