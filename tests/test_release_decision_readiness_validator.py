import json
from pathlib import Path

from scripts.validate_release_decision_readiness import validate_readiness

ROOT = Path(__file__).resolve().parents[1]


def _projection() -> dict[str, object]:
    return json.loads((ROOT / "docs/release-decision-readiness-20260801.json").read_text())


def test_release_decision_readiness_is_non_authorising() -> None:
    assert validate_readiness(_projection()) == ()


def test_release_decision_readiness_rejects_authority() -> None:
    projection = _projection()
    projection["release_authority"] = "approved"
    assert any("release_authority" in error for error in validate_readiness(projection))


def test_release_decision_readiness_rejects_duplicate_tracks() -> None:
    projection = _projection()
    tracks = projection["tracks"]
    tracks[1]["track_id"] = tracks[0]["track_id"]
    assert any("must be unique" in error for error in validate_readiness(projection))
