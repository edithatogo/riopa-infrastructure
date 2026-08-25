from pathlib import Path


def test_packaging_guidance_preserves_fail_closed_release_boundary() -> None:
    root = Path(__file__).resolve().parents[1]
    text = (root / "docs/research-object-packaging-preservation-migration-20260826.md").read_text()
    assert "Python 3.14" in text
    assert "anonymous restore" in text
    assert "successor/correction record" in text
    assert "does not create signed attestations" in text
    assert "non-operational" in text and "technical" in text and "preview" in text
