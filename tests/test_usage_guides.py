from pathlib import Path


def test_usage_guide_covers_all_bounded_audiences_and_disabled_claims() -> None:
    root = Path(__file__).resolve().parents[1]
    guide = (root / "docs/usage-guides-20260825.md").read_text(encoding="utf-8")
    for heading in (
        "## User guide",
        "## Operator guide",
        "## Contributor guide",
        "## Maintainer guide",
        "## Migration guide",
    ):
        assert heading in guide
    for claim in ("network", "timetable", "facility", "national", "clinical", "dispatch"):
        assert claim in guide.lower()
