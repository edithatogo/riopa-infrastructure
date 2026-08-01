from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DOI = "10.5281/zenodo.21735818"
DIGEST = "bf22b88342d577ca84ce554b77cba90cf38c6df3e617a125c1801eb5d7291d9b"

def test_wp010_decision_and_reproduction_handoff_bind_deposit_identity() -> None:
    decision = (ROOT / "docs/wp010-bounded-pilot-decision.md").read_text()
    handoff = (ROOT / "docs/wp010-external-reproduction-handoff.md").read_text()
    for text in (decision, handoff):
        assert DOI in text
        assert DIGEST in text
    assert re.search(r"zenodo\.org/records/21735818", decision)

def test_wp010_deposit_is_not_mistaken_for_external_reproduction() -> None:
    decision = (ROOT / "docs/wp010-bounded-pilot-decision.md").read_text()
    handoff = (ROOT / "docs/wp010-external-reproduction-handoff.md").read_text()
    assert "external reproduction remains required" in decision
    assert "external person/operator" in handoff

def test_wp010_request_requires_approval_and_content_bound_report() -> None:
    request = (ROOT / "docs/wp010-external-reproduction-request.md").read_text()
    assert "person outside the implementation run" in request
    assert "approve the operator" in request
    assert "report digest" in request
    assert "issue #149 remains open" in request
