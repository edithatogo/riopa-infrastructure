import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_archive_default_maximises_capture_without_treating_silence_as_permission() -> None:
    decision = json.loads((ROOT / "docs/source-rights-archive-default-20260829.json").read_text())
    defaults = decision["defaults"]

    assert defaults["lawful_acquisition"].startswith("capture when a public download")
    assert defaults["private_full_preservation"].startswith(
        "preserve every complete lawfully acquired"
    )
    assert defaults["public_evidence"].startswith("publish metadata")
    assert "affirmatively authorised" in defaults["public_full_payload"]
    assert len(decision["public_payload_bases"]) == 5
    assert "A takedown contingency" in " ".join(decision["clarifications"])


def test_archive_default_records_narrow_exclusions_and_contingencies() -> None:
    decision = json.loads((ROOT / "docs/source-rights-archive-default-20260829.json").read_text())

    assert any("explicit prohibition" in item for item in decision["full_archive_exclusions"])
    assert set(decision["operational_contingencies"]) == {
        "missing_publication_basis",
        "terms_change",
        "rights_challenge",
        "mixed_rights",
    }
    assert decision["legal_baseline"]["jurisdiction"] == "New Zealand"
