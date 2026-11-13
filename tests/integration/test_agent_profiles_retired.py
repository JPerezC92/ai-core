"""Contract that separate per-agent profile files stay retired."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from support.agent_spec_documents import REPO_ROOT  # noqa: E402


def test_agent_profiles_are_retired() -> None:
    profiles = sorted((REPO_ROOT / "agents").glob("*/profile.md"))
    assert profiles == [], profiles
