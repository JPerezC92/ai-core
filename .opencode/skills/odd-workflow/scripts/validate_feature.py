"""Validate ODD feature documents under odd/tasks.

Mechanical anatomy only: headings, header fields, S#/T#/L1, task status, and
unfilled placeholders. Allowed task status: open, in progress, done. Semantic
correctness — whether a spec is meaningful, whether a task is complete, whether
evidence is true — is Cipher's review, not this script. File IO stays in main().

Usage:
    uv run --frozen python3 .opencode/skills/odd-workflow/scripts/validate_feature.py odd/tasks
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_HEADINGS = ("## Specs", "## Tasks", "## Log")
SPEC_RE = re.compile(r"^- S\d+ — .+$")
TASK_RE = re.compile(
    r"^- T\d+ \| S\d+(?:, S\d+)* \| .+ \| (?:open|in progress|done) \| commit: .+$"
)
LOG_RE = re.compile(r"^- L1 — .+$")
HEADER_RE = re.compile(r"^> \*\*(Status|Owner|Created):\*\* .+$")
PLACEHOLDER_RE = re.compile(r"<[^>]+>")
CODE_SPAN_RE = re.compile(r"`[^`]*`")
FENCED_BLOCK_RE = re.compile(r"```.*?```", re.DOTALL)


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

    if not any(LOG_RE.match(line) for line in log):
        findings.append("Log needs an L1 entry")

    unfenced = FENCED_BLOCK_RE.sub("", text)
    for line in unfenced.splitlines():
        if PLACEHOLDER_RE.search(_strip_code(line)):
            findings.append(f"unfilled placeholder: {line.strip()}")

    return findings


def main(argv: list[str]) -> int:
    """Validate one feature file or every feature file in a directory."""
    if len(argv) != 2:
        print("usage: validate_feature.py <file-or-directory>")
        return 2

    target = Path(argv[1])
    files = sorted(target.glob("*.md")) if target.is_dir() else [target]
    files = [path for path in files if path.name != "_template.md"]
    if not files:
        print("no feature documents found")
        return 1

    failed = False
    for path in files:
        findings = validate_feature(path.read_text(encoding="utf-8"))
        if findings:
            failed = True
            print(f"FAIL {path}")
            for finding in findings:
                print(f"  - {finding}")
        else:
            print(f"ok {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
