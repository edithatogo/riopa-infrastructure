from __future__ import annotations

import json
from pathlib import Path

PACKET = Path("docs/publication-package-preparation-20260825.json")


def test_publication_package_matrix_covers_required_package_classes() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    assert packet["status"] == "candidate-preparation-only"
    assert packet["publication_ready"] is False
    assert {item["package_id"] for item in packet["packages"]} == {
        "infrastructure",
        "methods",
        "data-descriptor",
        "applied-benchmark",
    }
    assert all(item["references"] and item["required_checks"] for item in packet["packages"])


def test_publication_package_matrix_preserves_external_gates() -> None:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    pending = " ".join(packet["pending_gates"])
    assert "external operator/user reproduction" in pending
    assert "elapsed beta/RC qualification" in pending
    assert "accountable release-authority decision" in pending
