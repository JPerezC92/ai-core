"""Source-version contract for AICore agent runtime specs."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core_sync_pkg.domain.regions import split_frontmatter  # noqa: E402


EXPECTED_SOURCE_VERSIONS: dict[str, str] = {
    "atrium.md": "1.7.0",
    "augur.md": "1.5.0",
    "bastion.md": "1.10.0",
    "crucible.md": "1.12.0",
    "forge.md": "1.8.0",
    "herald.md": "1.9.0",
    "inquisitor.md": "1.10.0",
    "investigator.md": "1.4.0",
    "ledger.md": "1.6.0",
    "lumen.md": "1.3.0",
    "marshal.md": "1.5.0",
    "quill.md": "1.5.0",
    "scribe.md": "1.3.0",
    "sentinel.md": "1.17.0",
    "vault.md": "1.7.0",
    "warden.md": "1.8.0",
}


def test_agent_spec_source_versions_match_declared_frontmatter() -> None:
    specs_dir = Path(__file__).resolve().parents[6] / ".opencode" / "agents"
    spec_names = {path.name for path in specs_dir.glob("*.md")}

    assert spec_names == set(EXPECTED_SOURCE_VERSIONS)
    for spec_name, expected_version in EXPECTED_SOURCE_VERSIONS.items():
        content = (specs_dir / spec_name).read_text(encoding="utf-8")
        frontmatter, _ = split_frontmatter(content)
        assert f"version: {expected_version}" in frontmatter.splitlines(), spec_name
