"""Containment of pytest temporary directories inside the project root."""

from __future__ import annotations

from pathlib import Path

import pytest


class PytestTempRootTests:
    """Prove every filesystem case lives under the project, not the host temp."""

    def test_tmp_path_resolves_inside_the_project(
        self, tmp_path: Path, tmp_path_factory: pytest.TempPathFactory
    ) -> None:
        project_root = Path(__file__).resolve().parents[1]
        assert tmp_path.resolve().is_relative_to(project_root)
        assert tmp_path_factory.getbasetemp().resolve().is_relative_to(project_root)
