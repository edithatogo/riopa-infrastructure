from pathlib import Path

from scripts.validate_repo_context import context_errors


def test_canonical_repository_context_is_present() -> None:
    assert context_errors(Path(__file__).resolve().parents[1]) == []
