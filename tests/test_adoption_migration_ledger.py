from pathlib import Path

from scripts.build_adoption_migration_ledger import build_migration_ledger


def test_migration_ledger_preserves_losses_and_unknown_costs() -> None:
    root = Path(__file__).resolve().parents[1]
    ledger = build_migration_ledger(root)
    assert ledger["record_type"] == "riopa_adoption_migration_ledger"
    assert ledger["adapter_repositories"]
    assert ledger["contributor_feedback"]["status"] == "not-collected"
    assert ledger["migration_costs"]["status"] == "not-measured"
    assert ledger["promotion_allowed"] is False
