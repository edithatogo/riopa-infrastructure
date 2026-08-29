#!/usr/bin/env bash
set -euo pipefail
output=${1:-dist/riopa-provenance.cdx.json}
mkdir -p "$(dirname "$output")"
uv run cyclonedx-py environment \
  --pyproject pyproject.toml \
  --mc-type library \
  --spec-version 1.6 \
  --output-reproducible \
  --output-format JSON \
  --output-file "$output" \
  "$(uv run python -c 'import sys; print(sys.executable)')"
uv run python scripts/validate_cyclonedx_sbom.py "$output"
