import hashlib
import json
from pathlib import Path


def test_provenance_profile_candidate_freeze_is_unsigned_and_digest_bound() -> None:
    root = Path(__file__).resolve().parents[1]
    record = json.loads(
        (root / "docs/provenance-profile-v1-candidate-freeze-20260825.json").read_text()
    )
    assert record["status"] == "candidate-frozen-unsigned"
    for relative, expected in record["artifacts"].items():
        assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == expected
    assert record["signature"]["status"] == "not-signed"
    assert record["promotion_allowed"] is False
