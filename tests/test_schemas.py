from pathlib import Path

from riopa_provenance.validation import validate_bundle


def test_all_schemas_and_examples_validate() -> None:
    root = Path(__file__).resolve().parents[1]
    results = validate_bundle(root)
    failures = [result for result in results if not result.valid]
    assert not failures, "\n".join(
        f"{result.path}: {'; '.join(result.errors)}" for result in failures
    )
