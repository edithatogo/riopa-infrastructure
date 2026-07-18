# Minimal Example

This directory is a **synthetic metadata-only example**. It demonstrates valid contracts, a three-event hash chain, manifest closure, methods generation and deterministic RO-Crate packaging. It does not contain a genuine LINZ layer, council plan, facility list or legal interpretation.

Run:

```bash
uv run riopa validate --root ../..
uv run riopa methods --manifest snapshot-manifest.json --output METHODS.generated.md
uv run riopa research-object --manifest snapshot-manifest.json --output-dir ../../dist/example-research-object
(cd ../../dist/example-research-object && sha256sum -c checksums.sha256)
```

The placeholder payload hashes and commit identifier are deliberately obvious and are labelled `synthetic-placeholder`. A stable production release profile will reject unresolved placeholders.
