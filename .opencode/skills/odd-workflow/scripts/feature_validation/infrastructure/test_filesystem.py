"""Test feature-source filesystem mapping against isolated real files."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SCRIPTS))

from feature_testkit import make_feature  # noqa: E402
from feature_validation.infrastructure.filesystem import FilesystemFeatureSource  # noqa: E402


@pytest.fixture
def feature_directory(tmp_path: Path) -> Path:
    """Build immediate and nested candidates from shared document-factory data."""
    for name in ("feature.md", "_template.md", "notes.txt"):
        (tmp_path / name).write_text(make_feature(), encoding="utf-8")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "nested.md").write_text(make_feature(), encoding="utf-8")
    return tmp_path


def test_directory_discovery_maps_only_immediate_markdown_candidates(
    feature_directory: Path,
) -> None:
    source = FilesystemFeatureSource()

    references = source.discover(str(feature_directory))

    assert isinstance(references, tuple)
    assert set(references) == {
        str(feature_directory / "feature.md"),
        str(feature_directory / "_template.md"),
    }


def test_single_file_reference_is_normalized_and_reads_utf8(tmp_path: Path) -> None:
    source = FilesystemFeatureSource()
    path = tmp_path / "feature.md"
    document = make_feature(title="Résumé — validación")
    path.write_text(document, encoding="utf-8")
    target = f"{tmp_path}/./feature.md"

    references = source.discover(target)

    assert references == (str(Path(target)),)
    assert source.read(references[0]) == document


def test_missing_file_read_propagates_filesystem_exception(tmp_path: Path) -> None:
    source = FilesystemFeatureSource()
    missing = tmp_path / "missing.md"

    with pytest.raises(FileNotFoundError) as raised:
        source.read(str(missing))

    assert raised.value.filename == str(missing)
