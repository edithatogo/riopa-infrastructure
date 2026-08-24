import json
from pathlib import Path

from riopa_provenance.validation import validate_instance


def test_supermarket_preregistration_is_valid_reference_template() -> None:
    root = Path(__file__).resolve().parents[1]
    packet = json.loads((root / "docs/supermarket-health-preregistration-20260825.json").read_text())
    schema = json.loads((root / "schemas/analysis-preregistration.schema.json").read_text())
    assert validate_instance(packet, schema) == ()
    assert packet["domain"] == "synthetic-non-clinical"
    assert len(packet["analyses"]) == 3
    assert any("causal" in limitation for limitation in packet["limitations"])
