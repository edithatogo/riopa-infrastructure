import hashlib
import json
from pathlib import Path


def test_canonical_candidate_freeze_is_digest_bound_and_fail_closed() -> None:
    root = Path(__file__).resolve().parents[1]
    record = json.loads((root / "docs/canonical-v1-candidate-freeze-20260829.json").read_text())
    assert record["status"] == "candidate-frozen-not-published"
    for relative, expected in record["artifacts"].items():
        digest = hashlib.sha256((root / relative).read_bytes()).hexdigest()
        assert digest == expected, relative
    assert record["promotion_allowed"] is False
    assert record["supersedes"] == "docs/canonical-v1-candidate-freeze-20260825.json"
    assert "standards-complete claimed-profile validation" in record["open_gates"]
    assert "persistent stable publication identifier and authority decision" in record["open_gates"]
