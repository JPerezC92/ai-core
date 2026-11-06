"""End-to-end behavior test: merge-mode `apply` registers the destination index.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_merge_qmd_index.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest  # noqa: E402

from _core_sync_testkit import (  # noqa: E402
    QMD_CORE_INDEX,
    QMD_DESTINATION,
    QMD_DESTINATION_FOLDER,
    QMD_SOURCE,
    REV_A,
    _apply_args,
    _check_args,
    _merge_setup,
    _qmd_index,
)
from core_sync_pkg.infrastructure.composition import main  # noqa: E402


class MergeQmdIndexEndToEndTests:
    """Register the destination folder's name as the qmd index end to end."""

    def test_apply_retargets_the_index_and_check_reports_current(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        source, destination, bindings_path = _merge_setup(
            tmp_path,
            source_content=QMD_SOURCE,
            destination_content=QMD_DESTINATION,
            destination_name=QMD_DESTINATION_FOLDER,
        )
        destination_path = destination / "opencode.jsonc"

        assert main(_apply_args(source, destination, bindings_path, REV_A)) == 0

        written = destination_path.read_text(encoding="utf-8")
        assert _qmd_index(written) == QMD_DESTINATION_FOLDER
        assert json.dumps(QMD_CORE_INDEX) not in written

        capsys.readouterr()
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 0
        assert capsys.readouterr().out == "current\n"
