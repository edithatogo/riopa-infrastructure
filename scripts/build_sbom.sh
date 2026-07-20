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
uv run python - "$output" <<'PY'
import json
import sys
from pathlib import Path
path = Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
assert data["bomFormat"] == "CycloneDX"
assert data["specVersion"] == "1.6"
assert data.get("components")
print(f"Validated CycloneDX SBOM with {len(data['components'])} components: {path}")
PY
