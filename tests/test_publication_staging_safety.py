from __future__ import annotations

from pathlib import Path

import pytest

import riopa_provenance.publication as publication
from riopa_provenance.crate import build_research_object
from riopa_provenance.hashing import sha256_file


@pytest.fixture
def staging_inputs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    root = Path(__file__).resolve().parents[1]
    source = build_research_object(
        root / "examples/minimal/snapshot-manifest.json", tmp_path / "source"
    )
    plan = publication.build_publication_plan(source, tmp_path / "plan.json")

    def forbid_recursive_delete(*args: object, **kwargs: object) -> None:
        raise AssertionError("Staging must never recursively delete a directory")

    # Regression probes must remain harmless even against the old implementation.
    monkeypatch.setattr(publication.shutil, "rmtree", forbid_recursive_delete)
    return source, plan


def inventory(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): sha256_file(path)
        for path in root.rglob("*")
        if path.is_file() and not path.is_symlink()
    }


@pytest.mark.parametrize("scenario", ["source", "ancestor", "inside-source", "existing", "plan"])
def test_unsafe_stage_paths_preserve_inputs(
    staging_inputs: tuple[Path, Path], tmp_path: Path, scenario: str
) -> None:
    source, plan = staging_inputs
    if scenario == "source":
        output = source
    elif scenario == "ancestor":
        output = tmp_path
    elif scenario == "inside-source":
        output = source / "new-stage"
    else:
        output = tmp_path / "existing"
        output.mkdir()
        (output / "sentinel.txt").write_text("user-owned data")
        if scenario == "plan":
            copied = output / "publication-plan.json"
            copied.write_bytes(plan.read_bytes())
            plan = copied
    before = inventory(tmp_path)
    with pytest.raises(publication.PublicationError):
        publication.stage_publication(plan, source, output)
    assert inventory(tmp_path) == before
    if scenario == "inside-source":
        assert not output.exists()


@pytest.mark.parametrize("scenario", ["output", "parent", "dangling"])
def test_symlink_stage_paths_are_rejected_without_touching_targets(
    staging_inputs: tuple[Path, Path], tmp_path: Path, scenario: str
) -> None:
    source, plan = staging_inputs
    target = tmp_path / "target"
    target.mkdir()
    (target / "sentinel.txt").write_text("preserve")
    link = tmp_path / "stage-link"
    link.symlink_to(target if scenario != "dangling" else tmp_path / "missing-target")
    output = link / "child" if scenario == "parent" else link
    before = inventory(target)
    with pytest.raises(publication.PublicationError):
        publication.stage_publication(plan, source, output)
    assert link.is_symlink()
    assert inventory(target) == before
    assert not (tmp_path / "missing-target").exists()


def test_fresh_sibling_stage_succeeds_and_replay_preserves_original(
    staging_inputs: tuple[Path, Path], tmp_path: Path
) -> None:
    source, plan = staging_inputs
    before_source = inventory(source)
    output = publication.stage_publication(plan, source, tmp_path / "fresh-stage")
    assert (output / "github/artifact-raw.json").is_file()
    assert (output / "publication-crosswalk.json").is_file()
    before_stage = inventory(output)
    with pytest.raises(publication.PublicationError):
        publication.stage_publication(plan, source, output)
    assert inventory(output) == before_stage
    assert inventory(source) == before_source
