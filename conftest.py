"""Project-wide pytest configuration.

Contains every filesystem case inside the project root by setting pytest's
base temporary directory under ``output/.pytest-tmp/<pid>/`` when the caller
did not supply ``--basetemp``. Parallel workers get distinct directories so
they never delete one another's trees. ``output/`` remains excluded from
collection by the existing ``norecursedirs`` setting.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Place the default temp root inside the project when ``--basetemp`` is unset."""
    if getattr(config.option, "basetemp", None) is not None:
        return
    project_root = Path(__file__).resolve().parent
    basetemp = project_root / "output" / ".pytest-tmp" / f"p{os.getpid()}"
    basetemp.parent.mkdir(parents=True, exist_ok=True)
    config.option.basetemp = basetemp
