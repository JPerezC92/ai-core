"""Build durable feature-file documents for validator tests without filesystem IO."""

from __future__ import annotations

DEFAULT_TITLE = "Sample feature"
DEFAULT_DESCRIPTION = "The feature states what it is in one paragraph."
DEFAULT_WORDING = "the requirement's own wording."
REQUIREMENTS_HEADING = "## Requirements"

# The documented requirement-mark vocabulary, transcribed once for the tests.
# It is deliberately not imported from the rules module: a test that read the
# production constant would parametrise over whatever that constant contains,
# and would stop reporting a narrowed vocabulary.
MARKS = (
    "upstream",
    "upstream · local detail",
    "upstream · narrowed",
    "local",
    "local · conflicts",
)


def make_requirement(
    number: int | str,
    *,
    ticked: bool = True,
    mark: str | None = None,
    wording: str = DEFAULT_WORDING,
    tail: str = "",
) -> str:
    """Build one requirement line in the durable feature file's line shape."""
    tick = "x" if ticked else " "
    marked = f"`{mark}` " if mark is not None else ""
    return f"- [{tick}] R{number} {marked}— {wording}{tail}"


def make_malformed_requirement() -> str:
    """Build a requirement line that misses the dash separator before its text."""
    return f"- [x] R1 {DEFAULT_WORDING}"


def make_requirement_without_number() -> str:
    """Build a requirement line that carries no requirement number."""
    return f"- [x] {DEFAULT_WORDING}"


def make_requirement_with_uppercase_tick() -> str:
    """Build a requirement line whose tick is an uppercase X."""
    return f"- [X] R1 — {DEFAULT_WORDING}"


def make_indented_sublist() -> str:
    """Build an indented sublist line that is not a requirement entry."""
    return "    - [x] R1 — a nested detail, not a requirement line."


def make_bullet_line(text: str) -> str:
    """Build a top-level list entry that is not a requirement line."""
    return f"- {text}"


def make_fenced_block(body: str) -> str:
    """Build a fenced block whose contents are the given body."""
    return f"```\n{body}\n```"


def make_status_line(status: str) -> str:
    """Build one declared status line in the durable feature file's line shape."""
    return f"**Status:** {status}"


def make_requirements_section(*entries: str) -> str:
    """Build a requirements section holding the requirement lines it is given."""
    return "\n\n".join((REQUIREMENTS_HEADING, *entries))


def make_completion_section(
    entry: str = "- [x] **1** `upstream` — the superseded obligation line.",
) -> str:
    """Build the superseded completion-sheet section a feature file must not carry."""
    return f"## Completion\n\n{entry}"


def make_guidance_section(
    entry: str = "- Copy this template to `.aicore/core/odd/features/<feature-name>.md`.",
) -> str:
    """Build the template-only guidance section a real feature file must not carry."""
    return f"## Guidance\n\n{entry}"


def make_prose_section(text: str) -> str:
    """Build a prose document section: plain text, no heading or field syntax."""
    return text


def make_feature_file(
    *,
    title: str = DEFAULT_TITLE,
    description: str = DEFAULT_DESCRIPTION,
    include_title: bool = True,
    status: str = "partial",
    include_status: bool = True,
    requirements_heading: str = REQUIREMENTS_HEADING,
    requirement_entries: tuple[str, ...] | None = None,
    extra_sections: tuple[str, ...] = (),
) -> str:
    """Build a complete durable feature file with targeted field overrides."""
    if requirement_entries is None:
        requirement_entries = (make_requirement(1), make_requirement(2, ticked=False))
    blocks: list[str] = []
    if include_title:
        blocks.extend((f"# {title}", ""))
    if description:
        blocks.extend((description, ""))
    if include_status:
        blocks.extend((make_status_line(status), ""))
    blocks.extend((requirements_heading, ""))
    blocks.extend(requirement_entries)
    for section in extra_sections:
        blocks.extend(("", section))
    return "\n".join(blocks) + "\n"
