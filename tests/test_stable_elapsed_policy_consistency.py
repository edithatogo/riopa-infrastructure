from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_normative_stable_elapsed_thresholds_are_consistent() -> None:
    operations = (ROOT / "docs/operations-slo.md").read_text(encoding="utf-8")
    definition = (ROOT / "docs/v1-definition-of-done.md").read_text(encoding="utf-8")
    gates = (ROOT / "docs/v1-release-gates.md").read_text(encoding="utf-8")

    normalized_operations = " ".join(operations.replace("**", "").split())
    assert "90 consecutive calendar days" in normalized_operations
    assert "90 daily hosted observations" in normalized_operations
    assert "30 consecutive calendar days" in normalized_operations
    assert "30 daily hosted observations" in normalized_operations
    assert "90 consecutive days with 90 daily hosted observations" in definition
    assert "30-day unchanged-candidate soak with 30 daily hosted observations" in definition
    assert "90" in gates and "30" in gates

    obsolete = (
        "14 consecutive days",
        "seven-day unchanged-candidate",
        "7 consecutive calendar days",
        "7 daily hosted observations",
    )
    for phrase in obsolete:
        assert phrase not in operations
        assert phrase not in definition
