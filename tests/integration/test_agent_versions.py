"""Source-version contract for AICore agent runtime specs."""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from support.agent_spec_documents import AGENT_SPECS_DIR, split_frontmatter  # noqa: E402


EXPECTED_SPEC_FILES: frozenset[str] = frozenset(
    {
        "atrium.md",
        "bastion.md",
        "crucible.md",
        "forge.md",
        "herald.md",
        "inquisitor.md",
        "investigator.md",
        "ledger.md",
        "lumen.md",
        "quill.md",
        "scribe.md",
        "sentinel.md",
        "vault.md",
        "warden.md",
    }
)

EXPECTED_SPEC_VERSIONS: dict[str, str] = {
    "atrium.md": "1.14.1",
    "bastion.md": "1.18.1",
    "crucible.md": "1.18.1",
    "forge.md": "3.3.0",
    "herald.md": "1.14.1",
    "inquisitor.md": "1.16.2",
    "investigator.md": "1.5.0",
    "ledger.md": "2.3.0",
    "lumen.md": "1.4.1",
    "quill.md": "1.6.0",
    "scribe.md": "1.4.0",
    "sentinel.md": "1.21.1",
    "vault.md": "1.8.0",
    "warden.md": "1.10.0",
}

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
    assert AGENT_SPECS_DIR.is_dir(), f"missing agents directory: {AGENT_SPECS_DIR}"
    assert {path.name for path in AGENT_SPECS_DIR.glob("*.md")} == set(
        EXPECTED_SPEC_FILES
    )
    for spec_name in sorted(EXPECTED_SPEC_FILES):
        content = (AGENT_SPECS_DIR / spec_name).read_text(encoding="utf-8")
        frontmatter, _ = split_frontmatter(content)
        assert frontmatter, f"{spec_name}: no frontmatter block"
        declared = _declared_version(frontmatter, spec_name)
        assert SEMVER.fullmatch(declared), f"{spec_name}: invalid version {declared!r}"


def test_agent_specs_declare_the_expected_version() -> None:
    assert set(EXPECTED_SPEC_VERSIONS) == set(EXPECTED_SPEC_FILES), (
        "the pinned version map must cover exactly the pinned agent specs"
    )
    for spec_name, expected in sorted(EXPECTED_SPEC_VERSIONS.items()):
        content = (AGENT_SPECS_DIR / spec_name).read_text(encoding="utf-8")
        frontmatter, _ = split_frontmatter(content)
        assert frontmatter, f"{spec_name}: no frontmatter block"
        declared = _declared_version(frontmatter, spec_name)
        assert declared == expected, (
            f"{spec_name}: expected version {expected!r}, found {declared!r}"
        )
