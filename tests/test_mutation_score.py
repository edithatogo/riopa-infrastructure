from pathlib import Path

from scripts.check_mutation_score import mutation_counts


def test_mutation_counts_parse_result_statuses() -> None:
    counts = mutation_counts("x.one: killed\nx.two: survived\nx.three: timeout\nx.four: no tests\n")
    assert counts == {
        "killed": 1,
        "survived": 1,
        "timeout": 1,
        "no tests": 1,
        "suspicious": 0,
    }


def test_mutation_receipt_script_is_tracked() -> None:
    assert Path("scripts/check_mutation_score.py").is_file()
