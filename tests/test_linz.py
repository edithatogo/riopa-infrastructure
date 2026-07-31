from __future__ import annotations

import json
from pathlib import Path

import pytest

from riopa_provenance.linz import (
    LinzStateError,
    LinzStateStore,
    _validate_revision_interval,
    linz_service_url,
)


def state(*, sequence: int, parent: str | None = None) -> dict[str, object]:
    return {
        "record_type": "linz_layer_state",
        "layer_kind": "layer",
        "layer_id": 42,
        "sequence": sequence,
        "parent_state_sha256": parent,
    }


def test_revision_intervals_require_utc_order_and_matching_precision() -> None:
    _validate_revision_interval("2026-01-01T00:00:00Z", "2026-01-01T00:00:01Z")
    _validate_revision_interval("2026-01-01T00:00:00.000Z", "2026-01-01T00:00:01.000Z")
    with pytest.raises(LinzStateError, match="full UTC RFC 3339"):
        _validate_revision_interval("2026-01-01T00:00:00+00:00", "2026-01-01T00:00:01Z")
    with pytest.raises(LinzStateError, match="identical timestamp precision"):
        _validate_revision_interval("2026-01-01T00:00:00Z", "2026-01-01T00:00:01.0Z")
    with pytest.raises(LinzStateError, match="later"):
        _validate_revision_interval("2026-01-01T00:00:01Z", "2026-01-01T00:00:01Z")


@pytest.mark.parametrize("api_key", ["", "bad/key", "bad?query", "bad#fragment", "bad\nkey"])
def test_service_url_rejects_unsafe_path_credentials(api_key: str) -> None:
    with pytest.raises(LinzStateError, match="unsafe for a path credential"):
        linz_service_url(api_key)
    assert linz_service_url("safe-key") == "https://data.linz.govt.nz/services;key=safe-key/wfs"


def test_state_store_enforces_immutable_sequence_and_parent_chain(tmp_path: Path) -> None:
    store = LinzStateStore(tmp_path, layer_kind="layer", layer_id=42)
    with pytest.raises(LinzStateError, match="no current pointer"):
        store.load_current()
    first = store.write_state(state(sequence=0))
    assert store.load_current() == first.state
    first_hash = str(first.state["state_sha256"])
    second = store.write_state(state(sequence=1, parent=first_hash))
    assert store.load_current() == second.state
    second_hash = str(second.state["state_sha256"])
    with pytest.raises(LinzStateError, match="increment by one"):
        store.write_state(state(sequence=3, parent=second_hash))
    with pytest.raises(LinzStateError, match="parent does not match"):
        store.write_state(state(sequence=2, parent=first_hash))

    pointer = json.loads(store.pointer_path.read_text(encoding="utf-8"))
    pointer["state_sha256"] = "0" * 64
    store.pointer_path.write_text(json.dumps(pointer), encoding="utf-8")
    with pytest.raises(LinzStateError, match="pointer hash"):
        store.load_current()


def test_state_store_rejects_wrong_identity_and_invalid_constructor(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="layer_kind"):
        LinzStateStore(tmp_path, layer_kind="feature", layer_id=1)
    with pytest.raises(ValueError, match="positive"):
        LinzStateStore(tmp_path, layer_kind="layer", layer_id=0)
    with pytest.raises(LinzStateError, match="identity"):
        LinzStateStore(tmp_path, layer_kind="table", layer_id=42).write_state(state(sequence=0))
