"""Hermetic project-wide pytest discovery proof in a temporary project."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path


class TestpathsDiscoveryTests:
    """Prove discovery settings against temporary project files only."""

    def test_testpaths_discovers_project_locations_and_excludes_configured_junk(
        self, tmp_path: Path
    ) -> None:
        source_config = Path(__file__).resolve().parents[4] / "pyproject.toml"
        parsed = tomllib.loads(source_config.read_text(encoding="utf-8"))
        settings = parsed["tool"]["pytest"]["ini_options"]
        option_names = ("testpaths", "norecursedirs", "python_files", "python_classes")
        options = {name: settings[name] for name in option_names}
        project = tmp_path / "project"
        project.mkdir()
        config_lines = ["[tool.pytest.ini_options]"]
        config_lines.extend(f"{name} = {json.dumps(options[name])}" for name in option_names)
        (project / "pyproject.toml").write_text("\n".join(config_lines) + "\n", encoding="utf-8")

        cases = {
            "tests/test_discovery_tests.py": (
                "class TestsAreaTests:\n    def test_collected(self) -> None:\n        pass\n"
            ),
            "src/test_discovery_src.py": (
                "class SrcAreaTests:\n    def test_collected(self) -> None:\n        pass\n"
            ),
            "package/test_discovery_package.py": (
                "from package.support import MARKER\n\n"
                "class PackageAreaTests:\n"
                "    def test_imported_package_fixture(self) -> None:\n"
                "        assert MARKER == 'package-imported'\n"
            ),
            ".hidden/test_discovery_hidden.py": (
                "class DotDirectoryTests:\n    def test_collected(self) -> None:\n        pass\n"
            ),
            ".venv/test_discovery_excluded.py": (
                "class ExcludedEnvironmentTests:\n    def test_not_collected(self) -> None:\n        pass\n"
            ),
            "node_modules/test_discovery_excluded.py": (
                "class ExcludedNodeModulesTests:\n    def test_not_collected(self) -> None:\n        pass\n"
            ),
            "output/test_discovery_excluded.py": (
                "class ExcludedOutputTests:\n    def test_not_collected(self) -> None:\n        pass\n"
            ),
            "plans/.completed/test_discovery_excluded.py": (
                "class ExcludedCompletedPlansTests:\n    def test_not_collected(self) -> None:\n        pass\n"
            ),
            "build/test_discovery_excluded.py": (
                "class ExcludedBuildTests:\n    def test_not_collected(self) -> None:\n        pass\n"
            ),
            "dist/test_discovery_excluded.py": (
                "class ExcludedDistTests:\n    def test_not_collected(self) -> None:\n        pass\n"
            ),
            "__pycache__/test_discovery_excluded.py": (
                "class ExcludedBytecodeTests:\n    def test_not_collected(self) -> None:\n        pass\n"
            ),
            ".git/test_discovery_excluded.py": (
                "class ExcludedGitMetadataTests:\n    def test_not_collected(self) -> None:\n        pass\n"
            ),
        }
        for relative, content in cases.items():
            target = project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        (project / "package/__init__.py").write_text("", encoding="utf-8")
        (project / "package/support.py").write_text("MARKER = 'package-imported'\n", encoding="utf-8")

        cache_dir = tmp_path / "pytest-cache"
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "--collect-only",
                "-o",
                f"cache_dir={cache_dir}",
            ],
            cwd=project,
            capture_output=True,
            text=True,
            env=env,
            timeout=60,
        )
        assert proc.returncode == 0, (
            "temporary project collection must succeed: "
            f"exit {proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}"
        )
        node_ids = [line.strip() for line in proc.stdout.splitlines() if "::" in line]
        expected = {
            "tests/test_discovery_tests.py::TestsAreaTests::test_collected",
            "src/test_discovery_src.py::SrcAreaTests::test_collected",
            "package/test_discovery_package.py::PackageAreaTests::test_imported_package_fixture",
            ".hidden/test_discovery_hidden.py::DotDirectoryTests::test_collected",
        }
        assert set(node_ids) == expected, f"unexpected collected node identities: {node_ids}"
        assert not any("Excluded" in node_id for node_id in node_ids)
