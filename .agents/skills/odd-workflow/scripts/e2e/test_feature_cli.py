"""Filesystem and command-line tests for the ODD feature validator."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from feature_testkit import make_feature  # noqa: E402
from validate_feature import main  # noqa: E402


def test_directory_validation_skips_template(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "_template.md").write_text(
        make_feature(title="Feature name", created="date"), encoding="utf-8"
    )
    (tmp_path / "feature.md").write_text(make_feature(), encoding="utf-8")

    assert main(["validate_feature.py", str(tmp_path)]) == 0
    output = capsys.readouterr().out
    assert output == f"ok {tmp_path / 'feature.md'}\n"


def test_directory_validation_reports_invalid_document(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "feature.md").write_text(make_feature(title="Feature name"), encoding="utf-8")
    assert main(["validate_feature.py", str(tmp_path)]) == 1
    assert capsys.readouterr().out == (
        f"FAIL {tmp_path / 'feature.md'}\n"
        "  - title must not be the template placeholder\n"
    )


def test_directory_without_feature_documents_returns_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "_template.md").write_text(
        make_feature(title="Feature name", created="date"), encoding="utf-8"
    )
    assert main(["validate_feature.py", str(tmp_path)]) == 1
    assert capsys.readouterr().out == "no feature documents found\n"


def test_main_without_argument_returns_usage_error(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["validate_feature.py"]) == 2
    assert capsys.readouterr().out == "usage: validate_feature.py <file-or-directory>\n"


def test_later_read_failure_preserves_earlier_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    earlier = tmp_path / "a.md"
    earlier.write_text(make_feature(), encoding="utf-8")
    (tmp_path / "z.md").mkdir()

    with pytest.raises(OSError):
        main(["validate_feature.py", str(tmp_path)])

    assert capsys.readouterr().out == f"ok {earlier}\n"
