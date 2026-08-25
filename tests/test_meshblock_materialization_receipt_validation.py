from pathlib import Path

from scripts.validate_meshblock_materialization_receipt import build_report


def test_meshblock_materialization_receipt_links_are_fail_closed() -> None:
    root = Path(__file__).resolve().parents[1]
    report = build_report(root)
    assert report["status"] == "receipt-and-projection-links-validated"
    assert report["promotion_allowed"] is False
    assert len(report["receipt_sha256"]) == 64
    assert any("bulk artifact" in gate for gate in report["open_gates"])
