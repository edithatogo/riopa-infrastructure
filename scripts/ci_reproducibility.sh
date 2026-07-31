#!/usr/bin/env bash
set -euo pipefail
root=${TMPDIR:-/tmp}/riopa-reproducibility
rm -rf "$root"
mkdir -p "$root/one" "$root/two"
uv run riopa research-object --manifest examples/minimal/snapshot-manifest.json --output-dir "$root/one"
uv run riopa research-object --manifest examples/minimal/snapshot-manifest.json --output-dir "$root/two"
uv run riopa research-object-verify --root "$root/one"
uv run riopa research-object-verify --root "$root/two"
diff -qr "$root/one" "$root/two"
uv run python scripts/verify_wp007_slice.py
(
  cd "$root/one"
  sha256sum --check checksums.sha256
)
