import json
from pathlib import Path

from scripts.generate_canonical_bindings import render_binding


def test_typescript_binding_matches_normative_schema() -> None:
    schema = json.loads(Path("schemas/canonical-crosswalk.schema.json").read_text())
    generated = Path("bindings/typescript/canonical-crosswalk-v1.d.ts").read_text()
    assert generated == render_binding(schema)
    assert "readonly confidence: CanonicalCrosswalkConfidence" in generated
    assert "readonly to: string | null" in generated
    assert '"inapplicable";' in generated


def test_binding_documentation_keeps_runtime_validation_boundary() -> None:
    documentation = Path("bindings/typescript/README.md").read_text()
    assert "does not perform runtime validation" in documentation
    assert "not a complete JSON Schema implementation" in documentation
