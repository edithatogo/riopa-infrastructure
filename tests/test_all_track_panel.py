import json
from pathlib import Path

from scripts.validate_all_track_panel import ROLES, validate

ROOT = Path(__file__).resolve().parents[1]
REPORT_ROOT = ROOT / "docs/panel-reports/20260802"


def test_all_track_panel_reports_are_content_bound_and_complete() -> None:
    reports = [REPORT_ROOT / f"{role}.json" for role in sorted(ROLES)]
    assert (
        validate(
            reports,
            ROOT / "conductor/tracks",
            REPORT_ROOT / "orchestrator-synthesis.json",
        )
        == []
    )


def test_all_track_panel_does_not_overclaim_qualification() -> None:
    reports = [json.loads((REPORT_ROOT / f"{role}.json").read_text()) for role in sorted(ROLES)]
    by_track: dict[str, list[str]] = {}
    for report in reports:
        for track in report["tracks"]:
            by_track.setdefault(track["track_id"], []).append(track["disposition"])
    assert len(by_track) == 28
    assert any("fail" in dispositions for dispositions in by_track.values())
    assert all("pass" not in dispositions for dispositions in by_track.values())


def test_orchestrator_keeps_every_m6_disposition_not_qualified() -> None:
    synthesis = json.loads((REPORT_ROOT / "orchestrator-synthesis.json").read_text())
    assert synthesis["programme_disposition"] == "not-qualified-for-m6-or-release-promotion"
    assert {track["final_disposition"] for track in synthesis["tracks"]} == {"not-qualified"}


def test_panel_manifest_records_complete_but_not_qualified() -> None:
    manifest = json.loads((REPORT_ROOT / "manifest.json").read_text())
    assert manifest["status"] == "complete-not-qualified"
    assert manifest["track_count"] == 28
    assert manifest["final_track_dispositions"] == {"not-qualified": 28}
    assert manifest["post_panel_remediation"]["qualification_effect"] == (
        "none-until-a-content-bound-rerun"
    )
