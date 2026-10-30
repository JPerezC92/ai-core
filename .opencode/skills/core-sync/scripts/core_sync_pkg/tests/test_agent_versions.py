"""Source-version contract for AICore agent runtime specs."""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core_sync_pkg.domain.regions import split_frontmatter  # noqa: E402


EXPECTED_SPEC_FILES: frozenset[str] = frozenset(
    {
        "atrium.md",
        "augur.md",
        "bastion.md",
        "crucible.md",
        "forge.md",
        "herald.md",
        "inquisitor.md",
        "investigator.md",
        "ledger.md",
        "lumen.md",
        "marshal.md",
        "quill.md",
        "scribe.md",
        "sentinel.md",
        "vault.md",
        "warden.md",
    }
)

SEMVER = re.compile(r"\d+\.\d+\.\d+")


def _declared_version(frontmatter: str, spec_name: str) -> str:
    versions = [
        line.split(":", 1)[1].strip()
        for line in frontmatter.splitlines()
        if line.startswith("version:")
    ]
    assert len(versions) == 1, (
        f"{spec_name}: expected exactly one version line, found {versions}"
    )
    return versions[0]


def test_agent_specs_declare_a_valid_version() -> None:
    specs_dir = Path(__file__).resolve().parents[6] / ".opencode" / "agents"
    assert specs_dir.is_dir(), f"missing agents directory: {specs_dir}"
    assert {path.name for path in specs_dir.glob("*.md")} == set(EXPECTED_SPEC_FILES)
    for spec_name in sorted(EXPECTED_SPEC_FILES):
        content = (specs_dir / spec_name).read_text(encoding="utf-8")
        frontmatter, _ = split_frontmatter(content)
        assert frontmatter, f"{spec_name}: no frontmatter block"
        declared = _declared_version(frontmatter, spec_name)
        assert SEMVER.fullmatch(declared), f"{spec_name}: invalid version {declared!r}"
