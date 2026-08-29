import json
import re
from pathlib import Path


def test_latest_beta_rc_observations_are_exact_and_fail_closed() -> None:
    record = json.loads(
        Path("docs/hosted-beta-rc-observations-20260829.json").read_text(encoding="utf-8")
    )
    assert re.fullmatch(r"[0-9a-f]{40}", record["candidate_revision"])
    assert record["beta"]["status"] == "success"
    assert record["rc"]["status"] == "success"
    assert record["beta"]["campaign_id"].startswith("operational-beta-")
    assert record["rc"]["campaign_id"].startswith("operational-rc-")
    assert record["promotion_allowed"] is False
    assert record["nonclaims"]
