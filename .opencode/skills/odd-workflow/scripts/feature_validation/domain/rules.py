"""Validate feature-document anatomy through pure rules with ordered findings."""

from __future__ import annotations

import re
from pathlib import PurePath

REQUIRED_HEADINGS = ("## Specs", "## Tasks", "## Log")
SPEC_RE = re.compile(r"^- S\d+ — .+$")
TASK_RE = re.compile(
    r"^- T\d+ \| S\d+(?:, S\d+)* \| .+ \| "
    r"(?P<status>open|in progress|done) \| commit: (?P<commit>.*)$"
)
COMMIT_RE = re.compile(r"^[0-9a-fA-F]{7,64}$")
LOG_RE = re.compile(r"^- L1 — .+$")
HEADER_RE = re.compile(r"^> \*\*(Status|Owner|Created):\*\* .+$")
STATUS_RE = re.compile(r"^> \*\*Status:\*\* (active|closed)$")
STATUS_CLOSED_RE = re.compile(r"^> \*\*Status:\*\* closed$")
CLOSED_RE = re.compile(r"^> \*\*Closed:\*\* \S+")
CLOSE_LOG_RE = re.compile(r"^- L\d+ — Close: .+$")
PLACEHOLDER_RE = re.compile(r"<[^>]+>")
CODE_SPAN_RE = re.compile(r"`[^`]*`")
FENCED_BLOCK_RE = re.compile(r"```.*?```", re.DOTALL)


def is_template_reference(reference: str) -> bool:
    """Identify template filenames using host-specific lexical path semantics."""
    return PurePath(reference).name == "_template.md"


def sort_feature_references(references: tuple[str, ...]) -> tuple[str, ...]:
    """Sort references stably using host-specific lexical path semantics."""
    return tuple(sorted(references, key=PurePath))


def _section(lines: list[str], heading: str) -> list[str]:
    """Return the body lines of the first matching level-2 section."""
    start: int | None = None
    for index, line in enumerate(lines):
        if line.strip() == heading:
            start = index + 1
            break
    if start is None:
        return []
    end = len(lines)
    for index in range(start, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    return lines[start:end]


def _strip_code(line: str) -> str:
    """Remove inline code spans so path notation is not a placeholder."""
    return CODE_SPAN_RE.sub("", line)


def validate_feature(text: str) -> list[str]:
    """Return every finding for a feature-document body; empty means valid."""
    findings: list[str] = []
    lines = text.splitlines()

    headings = [line.strip() for line in lines if line.startswith("## ")]
    for heading in REQUIRED_HEADINGS:
        count = headings.count(heading)
        if count != 1:
            findings.append(f"heading {heading!r} must appear exactly once; found {count}")

    if not any(line.startswith("# ") and line.strip() != "# Feature name" for line in lines):
        findings.append("title must not be the template placeholder")

    header_fields = {match.group(1) for line in lines if (match := HEADER_RE.match(line))}
    for field in ("Status", "Owner", "Created"):
        if field not in header_fields:
            findings.append(f"header must include {field}")
    if "> **Created:** date" in text:
        findings.append("Created must be a real date, not the template placeholder")

    specs = _section(lines, "## Specs")
    tasks = _section(lines, "## Tasks")
    log = _section(lines, "## Log")

    status_lines = [
        line.strip() for line in lines if line.strip().startswith("> **Status:**")
    ]
    if len(status_lines) != 1:
        findings.append("header must include exactly one Status line")
    elif not STATUS_RE.match(status_lines[0]):
        findings.append("Status must be active or closed")

    is_closed = any(STATUS_CLOSED_RE.match(line) for line in lines)
    if is_closed and not any(CLOSED_RE.match(line.strip()) for line in lines):
        findings.append("closed feature needs a Closed date")

    has_close_entry = any(CLOSE_LOG_RE.match(line) for line in log)
    if is_closed and not has_close_entry:
        findings.append("closed feature needs a Log 'Close:' entry")
    if not is_closed and has_close_entry:
        findings.append("active feature has a Log 'Close:' entry; set Status: closed")

    spec_entries = [line for line in specs if line.strip().startswith("- ")]
    task_entries = [line for line in tasks if line.strip().startswith("- ")]

    if not spec_entries:
        findings.append("Specs needs at least one '- S# — ...' entry")
    for line in spec_entries:
        if not SPEC_RE.match(line):
            findings.append(f"Specs entry must match '- S# — ...': {line.strip()}")

    if not task_entries:
        findings.append(
            "Tasks needs at least one '- T# | S# | ... | status | commit: ...' entry"
        )
    for line in task_entries:
        if not TASK_RE.match(line):
            findings.append(
                "Tasks entry must match '- T# | S# | ... | open|in progress|done | "
                f"commit: ...': {line.strip()}"
            )

    for line in task_entries:
        match = TASK_RE.match(line)
        if not match:
            continue
        status = match.group("status")
        commit = match.group("commit").strip()
        has_commit_reference = COMMIT_RE.fullmatch(commit) is not None
        if not commit:
            findings.append(f"task commit must not be blank: {line.strip()}")
        if status == "done" and not has_commit_reference:
            findings.append(
                f"done task must have a 7-64 character hexadecimal commit identifier: {line.strip()}"
            )
        elif commit != "pending" and not has_commit_reference:
            findings.append(
                f"task commit must be 'pending' or a 7-64 character hexadecimal commit identifier: {line.strip()}"
            )
        if is_closed:
            if status != "done":
                findings.append(
                    f"closed feature has a {status} task: {line.strip()}"
                )
            if status != "done" and not has_commit_reference:
                findings.append(
                    f"closed feature task must have a 7-64 character hexadecimal commit identifier: {line.strip()}"
                )

    if not any(LOG_RE.match(line) for line in log):
        findings.append("Log needs an L1 entry")

    unfenced = FENCED_BLOCK_RE.sub("", text)
    for line in unfenced.splitlines():
        if PLACEHOLDER_RE.search(_strip_code(line)):
            findings.append(f"unfilled placeholder: {line.strip()}")

    return findings
