import json
from pathlib import Path


def test_panel_batch_manifest_is_pending_and_non_assertive() -> None:
    root = Path(__file__).parents[1]
    manifest = json.loads(
        (root / "docs" / "panel-qualification-batch-20260802.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["schema"] == "riopa.panel-qualification-batch.v1"
    assert manifest["status"] == "template-ready"
    assert manifest["non_assertive"] is True
    assert manifest["source_revision"] is None
    assert manifest["bundle_sha256"] is None
    assert manifest["required_roles"] == [
        "adversarial-reviewer",
        "evidence-auditor",
        "reproducer",
    ]
    assert manifest["tracks"]
    for track in manifest["tracks"]:
        assert track["status"] == "pending"
        assert track["reports"] == []
        assert track["track_id"]


def test_panel_batch_manifest_links_release_decision() -> None:
    root = Path(__file__).parents[1]
    manifest = json.loads(
        (root / "docs" / "panel-qualification-batch-20260802.json").read_text(
            encoding="utf-8"
        )
    )
    decision = root / manifest["release_decision_ref"]
    assert decision.exists()
