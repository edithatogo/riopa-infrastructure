import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_real_data_candidate_is_digest_bound_and_fail_closed() -> None:
    candidate = json.loads(
        (ROOT / "docs/publication-real-data-release-candidate-20260825.json").read_text(
            encoding="utf-8"
        )
    )
    assert candidate["status"] == "owner-agent-reproduced-bounded-candidate"
    assert candidate["reproduction"]["result"] == "pass"
    assert candidate["reproduction"]["independent"] is False
    assert candidate["promotion_allowed"] is False
    assert any("preservation" in gate for gate in candidate["open_gates"])
    assert candidate["source_packet"]["manifest_sha256"] == (
        "2b773fc68fd630aec197bb5e266e8332e14c15eb251cdfde94ee01a4ee8f20ba"
    )
    assert len(candidate["artifacts"]) == 3
