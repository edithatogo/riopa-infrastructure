import importlib.util
import io
import tarfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "hf_hosted_recovery", ROOT / "scripts/hf_hosted_recovery.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _member(name: str, *, link: str | None = None) -> tarfile.TarInfo:
    member = tarfile.TarInfo(name)
    if link is not None:
        member.type = tarfile.SYMTYPE
        member.linkname = link
    return member


def test_archive_members_must_remain_beneath_destination(tmp_path: Path) -> None:
    MODULE.validate_archive_members([_member("repo/pyproject.toml")], tmp_path)
    with pytest.raises(ValueError, match="unsafe archive member"):
        MODULE.validate_archive_members([_member("../outside")], tmp_path)


def test_archive_links_are_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="archive links"):
        MODULE.validate_archive_members([_member("repo/link", link="../outside")], tmp_path)


def test_fixture_archive_has_one_safe_root(tmp_path: Path) -> None:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
        tar.addfile(_member("repo/pyproject.toml"), io.BytesIO())
    buffer.seek(0)
    with tarfile.open(fileobj=buffer, mode="r:gz") as tar:
        MODULE.validate_archive_members(tar.getmembers(), tmp_path)
