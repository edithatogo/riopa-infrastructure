# Stats NZ Meshblock 2026 normalized projection evidence

This bounded record set was built only from the immutable Hugging Face packet
revision `3f2dc0a4d95a4fcb495551098d58fc5bce9c9202`. The build did not contact the
ArcGIS endpoint recorded in the source manifest.

The content-addressed projection
`urn:riopa:projection:sha256:64a1cbce366794b2b802f04dbe2bf1dc5fbf813e5c5b159bcf0782af9adc511f`
contains 57,575 features in EPSG:2193 and binds 236 independently addressed
capture records. Its normalized semantic SHA-256 is
`1b0a0e6a9ffde6b065dcbee5f65e8bd31d141c927895edb34b98d9499b0ea69f`.

The complete object-ID inventory matched the archived pages. Sixteen source
features have null geometry. One translated source geometry is invalid and is
preserved as invalid; the normalizer performed zero implicit geometry repairs.
Each row identifies its page-level capture and the SHA-256 of its translated
source WKB geometry.

Bulk products are intentionally excluded from Git. The verified local build
produced:

- GeoParquet SHA-256
  `713868f5f63c56c8ce7ff179e84ba6aec67608a3af2a4761f4bcbae796e2d649`
  (230,509,833 bytes).
- DuckDB SHA-256
  `cf0cae2f64fda05969bb4dc29adaab82b8ad181381fdc092fc46e6e4a8f50804`
  (297,021,440 bytes; deterministic semantics).
- Quality-report SHA-256
  `a7810eb59e5fef8e0660f09f666c58d7bbcfc60b0054a5316dc449a9a1e73a64`.

These physical file hashes belong to this build's materialization receipt.
DuckDB promises deterministic semantics rather than byte-identical database
files; its physical hash is therefore excluded from the stable projection URN.

Rebuild with:

```console
uv run --extra spatial python scripts/build_archived_spatial_projection.py \
  config/archive-sources/stats-nz-meshblock-2026.json \
  --packet-root .riopa-local/archive-packets/stats-nz-meshblock-2026 \
  --records-dir evidence/stats-nz-meshblock-2026-projection \
  --output-dir .riopa-local/spatial-projections/stats-nz-meshblock-2026 \
  --download
```

This is supporting-geography evidence only. It is not a population denominator,
accessibility result, national performance measurement, or legal interpretation.
