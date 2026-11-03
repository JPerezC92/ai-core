"""Contract that separate per-agent profile files stay retired."""

from __future__ import annotations

from pathlib import Path


def test_agent_profiles_are_retired() -> None:
    repo_root = Path(__file__).resolve().parents[6]
    profiles = sorted((repo_root / "agents").glob("*/profile.md"))
    assert profiles == [], profiles
