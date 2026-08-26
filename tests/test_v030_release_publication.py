import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "docs/v0.3.0-release-publication-20260827.json"


def test_v030_publication_receipt_records_failure_and_recovery_exactly() -> None:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))

    assert receipt["release"] == "0.3.0"
    assert receipt["channel"] == "experimental-prerelease"
    assert receipt["tag"] == {
        "name": "v0.3.0",
        "object": "a0cd5fdbecff586beddd598b584d6cfbbcc384e1",
        "target_commit": "8fccbf7bc3af88c347b00a6ce39b8b48a4dce39c",
        "kind": "annotated-unsigned",
    }
    assert receipt["preparation"]["status"] == "passed"
    assert receipt["preparation"]["required_checks"] == 5
    assert receipt["release_workflow"]["conclusion"] == "failure"
    assert receipt["release_workflow"]["automated_publication"] == "failed"
    assert receipt["release_workflow"]["github_oidc_attestation"] == "passed"
    assert receipt["release_workflow"]["independent_attestation_verification"] == "passed"
    assert receipt["recovery"]["status"] == "passed"
    assert receipt["recovery"]["checksums_reverified_before_publication"] is True
    assert receipt["post_publication_verification"] == {
        "all_assets_downloaded": True,
        "sha256sums_passed": True,
        "release_is_draft": False,
        "release_is_prerelease": True,
    }

    assets = receipt["assets"]
    assert len(assets) == 5
    assert len({asset["name"] for asset in assets}) == len(assets)
    assert all(len(asset["sha256"]) == 64 for asset in assets)
    assert all(asset["size"] > 0 for asset in assets)
    assert any("did not pass overall" in item for item in receipt["non_claims"])
    assert any("No DOI" in item for item in receipt["non_claims"])
