"""Filesystem and command-line tests for the ODD durable feature-file validator."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from feature_file_validation.domain._test_support import (  # noqa: E402
    make_feature_file,
    make_malformed_requirement,
)
from validate_feature_file import main  # noqa: E402


def test_directory_validation_skips_template(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "_template.md").write_text(make_feature_file(), encoding="utf-8")
    (tmp_path / "feature.md").write_text(make_feature_file(), encoding="utf-8")

    assert main(["validate_feature_file.py", str(tmp_path)]) == 0
    output = capsys.readouterr().out
    assert output == f"ok {tmp_path / 'feature.md'} — status: partial\n"


def test_single_file_validation_reports_the_derived_status(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    feature_file = tmp_path / "feature.md"
    feature_file.write_text(make_feature_file(), encoding="utf-8")

    assert main(["validate_feature_file.py", str(feature_file)]) == 0
    output = capsys.readouterr().out
    assert output == f"ok {feature_file} — status: partial\n"


def test_directory_validation_reports_invalid_feature_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    feature_file = tmp_path / "feature.md"
    feature_file.write_text(
        make_feature_file(requirement_entries=(make_malformed_requirement(),)),
        encoding="utf-8",
    )

    assert main(["validate_feature_file.py", str(tmp_path)]) == 1
    output = capsys.readouterr().out
    assert output.startswith(f"FAIL {feature_file}\n")
    assert "  - feature-file-requirement-entry:" in output


def test_directory_without_feature_files_returns_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "_template.md").write_text(make_feature_file(), encoding="utf-8")

    assert main(["validate_feature_file.py", str(tmp_path)]) == 1
    assert capsys.readouterr().out == "no feature files found\n"


def test_main_without_argument_returns_usage_error(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["validate_feature_file.py"]) == 2
    assert capsys.readouterr().out == "usage: validate_feature_file.py <file-or-directory>\n"


def test_later_read_failure_preserves_earlier_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    earlier = tmp_path / "a.md"
    earlier.write_text(make_feature_file(), encoding="utf-8")
    (tmp_path / "z.md").mkdir()

    with pytest.raises(OSError):
        main(["validate_feature_file.py", str(tmp_path)])

    assert capsys.readouterr().out == f"ok {earlier} — status: partial\n"
