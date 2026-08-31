from __future__ import annotations

import re
import runpy
from pathlib import Path
from unittest.mock import patch

import pytest

from riopa_provenance import tasman_public_packet


@pytest.fixture
def query_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple:
    root = Path(__file__).resolve().parents[1]
    previous = runpy.run_path(str(root / "tests/test_tasman_publication.py"))
    previous["test_real_restore_prepare_public_packet_and_two_rebuilds"](tmp_path, monkeypatch)
    producer = runpy.run_path(str(root / "scripts/publish_tasman_derivatives.py"))
    with patch.dict(
        producer["prepare"].__globals__, {"LICENCE_SHA256": tasman_public_packet.LICENCE_SHA256}
    ):
        packet, manifest = producer["prepare"](tmp_path / "work")
    text = (root / "docs/tasman-verified-query-examples-20260831.md").read_text()
    snippets = re.findall(r"```python\n(.*?)\n```", text, flags=re.DOTALL)
    assert len(snippets) == 1
    # Execute only the repository-owned documented example, never downloaded content.
    namespace: dict = {}
    exec(compile(snippets[0], "tasman-query-example", "exec"), namespace)  # noqa: S102
    return packet, manifest["files"], namespace["query_verified_projection"]


def test_documented_queries_execute_against_real_fixture_producer(query_fixture: tuple) -> None:
    packet, files, query = query_fixture
    assert query(packet, files) == {"feature_count": 1, "non_null_geometry_count": 1}


@pytest.mark.parametrize("damage", ["bytes", "digest", "symlink", "missing"])
def test_documented_queries_reject_unverified_bytes(query_fixture: tuple, damage: str) -> None:
    packet, files, query = query_fixture
    path = packet / "features.parquet"
    if damage == "bytes":
        path.write_bytes(b"corrupt")
    elif damage == "digest":
        files["features.parquet"]["sha256"] = "0" * 64
    elif damage == "symlink":
        replacement = packet / "saved.parquet"
        path.rename(replacement)
        path.symlink_to(replacement)
    else:
        path.unlink()
    with pytest.raises(ValueError):
        query(packet, files)
