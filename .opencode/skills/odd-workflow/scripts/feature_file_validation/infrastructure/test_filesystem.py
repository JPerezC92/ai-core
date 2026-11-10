"""Test the feature-file source mapping against isolated real files."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SCRIPTS))

from feature_file_validation.domain._test_support import make_feature_file  # noqa: E402
from feature_file_validation.infrastructure.filesystem import (  # noqa: E402
    FilesystemFeatureFileSource,
)


@pytest.fixture
def feature_file_directory(tmp_path: Path) -> Path:
    """Build immediate and nested candidates from shared feature-file factory data."""
    for name in ("feature.md", "_template.md", "notes.txt"):
        (tmp_path / name).write_text(make_feature_file(), encoding="utf-8")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "nested.md").write_text(make_feature_file(), encoding="utf-8")
    return tmp_path


def test_directory_discovery_maps_only_immediate_markdown_candidates(
    feature_file_directory: Path,
) -> None:
    source = FilesystemFeatureFileSource()

    references = source.discover(str(feature_file_directory))

    assert isinstance(references, tuple)
    assert set(references) == {
        str(feature_file_directory / "feature.md"),
        str(feature_file_directory / "_template.md"),
    }


def test_single_file_reference_is_normalized_and_reads_utf8(tmp_path: Path) -> None:
    source = FilesystemFeatureFileSource()
    path = tmp_path / "feature.md"
    document = make_feature_file(title="Resumen — validación")
    path.write_text(document, encoding="utf-8")
    target = f"{tmp_path}/./feature.md"

    references = source.discover(target)

    assert references == (str(Path(target)),)
    assert source.read(references[0]) == document


def test_missing_file_read_propagates_filesystem_exception(tmp_path: Path) -> None:
    source = FilesystemFeatureFileSource()
    missing = tmp_path / "missing.md"

    with pytest.raises(FileNotFoundError) as raised:
        source.read(str(missing))

    assert raised.value.filename == str(missing)
