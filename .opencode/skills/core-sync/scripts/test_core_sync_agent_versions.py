"""Source-version contract for AICore agent runtime specs."""

from __future__ import annotations

from pathlib import Path

from _core_sync_testkit import uc


EXPECTED_SOURCE_VERSIONS = {
    "atrium.md": "1.2.2",
    "augur.md": "1.2.2",
    "bastion.md": "1.5.2",
    "crucible.md": "1.6.3",
    "forge.md": "1.3.2",
    "herald.md": "1.4.3",
    "inquisitor.md": "1.4.2",
    "investigator.md": "1.3.2",
    "ledger.md": "1.4.2",
    "lumen.md": "1.2.1",
    "marshal.md": "1.3.0",
    "quill.md": "1.3.2",
    "scribe.md": "1.2.2",
    "sentinel.md": "1.10.0",
    "vault.md": "1.4.3",
    "warden.md": "1.5.2",
}


def test_agent_spec_source_versions_match_declared_frontmatter() -> None:
    specs_dir = Path(__file__).resolve().parents[4] / ".opencode" / "agents"
    spec_names = {path.name for path in specs_dir.glob("*.md")}

    assert spec_names == set(EXPECTED_SOURCE_VERSIONS)
    for spec_name, expected_version in EXPECTED_SOURCE_VERSIONS.items():
        content = (specs_dir / spec_name).read_text(encoding="utf-8")
        frontmatter, _ = uc.split_frontmatter(content)
        assert f"version: {expected_version}" in frontmatter.splitlines(), spec_name
