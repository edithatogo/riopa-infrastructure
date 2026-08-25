from pathlib import Path

from scripts.run_template_journey import run_template_journey


def test_template_journey_rehearsal_is_pass_and_non_mutating() -> None:
    root = Path(__file__).resolve().parents[1]
    result = run_template_journey(root)
    assert result["status"] == "pass"
    assert result["journey_class"] == "local-read-only-rehearsal"
    assert result["mutations_performed"] == []
    assert result["promotion_allowed"] is False


def test_template_journey_fails_closed_for_missing_contract(tmp_path: Path) -> None:
    try:
        run_template_journey(tmp_path)
    except ValueError as error:
        assert "contract" in str(error)
    else:
        raise AssertionError("missing contract should fail closed")
