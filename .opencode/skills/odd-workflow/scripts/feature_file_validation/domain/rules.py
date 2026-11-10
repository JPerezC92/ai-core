"""Validate durable feature-file anatomy through pure rules with ordered findings."""

from __future__ import annotations

import re
from pathlib import PurePath

from feature_file_validation.domain.records import (
    FeatureFileAssessment,
    FeatureRequirement,
    FeatureStatus,
)

TEMPLATE_NAME = "_template.md"
REQUIREMENTS_HEADING = "## Requirements"
GUIDANCE_HEADING = "## Guidance"
COMPLETION_HEADING = "## Completion"
ACHIEVED: FeatureStatus = "achieved"
PARTIAL: FeatureStatus = "partial"
NOT_STARTED: FeatureStatus = "not started"
STATUSES = (ACHIEVED, PARTIAL, NOT_STARTED)
MARKS = (
    "upstream",
    "upstream · local detail",
    "upstream · narrowed",
    "local",
    "local · conflicts",
)

TITLE_RE = re.compile(r"^# (?P<title>\S.*)$")
STATUS_RE = re.compile(r"^\*\*Status:\*\*[ \t]*(?P<value>.*)$")
REQUIREMENT_RE = re.compile(
    r"^- \[(?P<tick>[x ])\] R(?P<number>\d+) (?:`(?P<mark>[^`]*)` )?— (?P<wording>.+)$"
)
STATE_FIELD_RE = re.compile(r"(?:\*\*|__)?[ \t]*State[ \t]*(?:\*\*|__)?[ \t]*:")
PLACEHOLDER_RE = re.compile(r"<[^>]+>")
CODE_SPAN_RE = re.compile(r"`[^`]*`")
FENCED_BLOCK_RE = re.compile(r"```.*?```", re.DOTALL)


def is_template_reference(reference: str) -> bool:
    """Identify template filenames using host-specific lexical path semantics."""
    return PurePath(reference).name == TEMPLATE_NAME


def sort_feature_file_references(references: tuple[str, ...]) -> tuple[str, ...]:
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


def _title_index(lines: list[str]) -> int | None:
    """Return the line number of the first H1 title line, or None when absent."""
    for index, line in enumerate(lines):
        if TITLE_RE.match(line) is not None:
            return index
    return None


def _title_findings(lines: list[str]) -> list[str]:
    """Return findings for a missing H1 title line."""
    if _title_index(lines) is None:
        return [
            "feature-file-title: the file must open with an H1 title line "
            "'# <feature name>'"
        ]
    return []


def _description_findings(lines: list[str]) -> list[str]:
    """Return findings for a title with no paragraph saying what the feature is."""
    title = _title_index(lines)
    if title is None:
        return []
    paragraph: list[str] = []
    for line in lines[title + 1 :]:
        if line.startswith("#"):
            break
        if STATUS_RE.match(line) is not None:
            break
        if line.strip():
            paragraph.append(line)
    if paragraph:
        return []
    return [
        "feature-file-description: the title needs one paragraph saying what "
        "the feature is"
    ]


def _status_values(lines: list[str]) -> list[str]:
    """Return the declared status values in file order."""
    return [
        match.group("value").strip()
        for line in lines
        if (match := STATUS_RE.match(line)) is not None
    ]


def _status_findings(lines: list[str]) -> list[str]:
    """Return findings for a missing, repeated or unrecognised status line."""
    values = _status_values(lines)
    if not values:
        return [
            "feature-file-status: the file must carry exactly one "
            "'**Status:** achieved|partial|not started' line; found none"
        ]
    if len(values) > 1:
        return [
            "feature-file-status: the file must carry exactly one status line; "
            f"found {len(values)}"
        ]
    value = values[0]
    if value not in STATUSES:
        return [
            "feature-file-status: status must be one of 'achieved', 'partial' "
            f"or 'not started'; found {value!r}"
        ]
    return []


def _requirement_candidates(lines: list[str]) -> list[str]:
    """Return the requirement-shaped lines written in the requirements section."""
    return [
        line
        for line in _section(lines, REQUIREMENTS_HEADING)
        if line.startswith("- [")
    ]


def _requirement_lines(lines: list[str]) -> list[str]:
    """Return the requirement lines that match the file's line shape."""
    return [
        line
        for line in _requirement_candidates(lines)
        if REQUIREMENT_RE.match(line) is not None
    ]


def _requirements_findings(lines: list[str]) -> list[str]:
    """Return findings for the requirements section and its requirement lines."""
    count = sum(1 for line in lines if line.strip() == REQUIREMENTS_HEADING)
    if count != 1:
        return [
            f"feature-file-requirements: heading '{REQUIREMENTS_HEADING}' must "
            f"appear exactly once; found {count}"
        ]
    if not _requirement_lines(lines):
        return [
            "feature-file-requirements: '## Requirements' needs at least one "
            "'- [ ] R<n> — <requirement>' line"
        ]
    return []


def _entry_findings(lines: list[str]) -> list[str]:
    """Return findings for requirement-shaped lines that miss the line shape."""
    return [
        "feature-file-requirement-entry: requirement line must match "
        "'- [x] R<n> — <requirement>' or '- [x] R<n> `<mark>` — <requirement>': "
        f"{line.strip()}"
        for line in _requirement_candidates(lines)
        if REQUIREMENT_RE.match(line) is None
    ]


def _requirement_numbers(lines: list[str]) -> list[int]:
    """Return the requirement numbers in file order."""
    return [
        int(match.group("number"))
        for line in _requirement_lines(lines)
        if (match := REQUIREMENT_RE.match(line)) is not None
    ]


def _numbering_findings(lines: list[str]) -> list[str]:
    """Return findings when requirement numbers are not consecutive from one."""
    numbers = _requirement_numbers(lines)
    expected = 1
    for number in numbers:
        if number != expected:
            return [
                "feature-file-requirement-numbering: requirement numbers must be "
                f"consecutive from 1 with no gaps or duplicates; found {numbers}"
            ]
        expected += 1
    return []


def read_requirements(text: str) -> tuple[FeatureRequirement, ...]:
    """Return the requirement lines with their ticks, marks and wording."""
    requirements: list[FeatureRequirement] = []
    for line in _requirement_lines(text.splitlines()):
        match = REQUIREMENT_RE.match(line)
        if match is None:
            continue
        requirements.append(
            FeatureRequirement(
                number=match.group("number"),
                mark=match.group("mark") or "",
                wording=match.group("wording"),
                ticked=match.group("tick") == "x",
            )
        )
    return tuple(requirements)


def _mark_findings(text: str) -> list[str]:
    """Return findings for requirement marks outside the closed vocabulary."""
    return [
        "feature-file-requirement-mark: requirement "
        f"{requirement.number} carries an unknown mark {requirement.mark!r}; "
        "marks are 'upstream', 'upstream · local detail', 'upstream · narrowed', "
        "'local' or 'local · conflicts'"
        for requirement in read_requirements(text)
        if requirement.mark and requirement.mark not in MARKS
    ]


def _superseded_findings(lines: list[str]) -> list[str]:
    """Return findings for the superseded completion-sheet artifacts."""
    findings: list[str] = []
    if any(line.strip() == COMPLETION_HEADING for line in lines):
        findings.append(
            f"feature-file-superseded-section: '{COMPLETION_HEADING}' is a "
            "superseded completion-sheet section; the feature file records its "
            "requirements instead"
        )
    findings.extend(
        "feature-file-superseded-state: requirement line carries the superseded "
        f"'State:' field: {line.strip()}"
        for line in _requirement_candidates(lines)
        if STATE_FIELD_RE.search(line) is not None
    )
    return findings


def _placeholder_findings(text: str) -> list[str]:
    """Return findings for unfilled placeholder text outside code."""
    unfenced = FENCED_BLOCK_RE.sub("", text)
    return [
        f"feature-file-unfilled-placeholder: unfilled placeholder: {line.strip()}"
        for line in unfenced.splitlines()
        if PLACEHOLDER_RE.search(_strip_code(line)) is not None
    ]


def _guidance_findings(lines: list[str]) -> list[str]:
    """Return findings for the template-only guidance section."""
    if any(line.strip() == GUIDANCE_HEADING for line in lines):
        return [
            f"feature-file-template-guidance: '{GUIDANCE_HEADING}' is "
            "template-only; a real feature file carries no Guidance section"
        ]
    return []


def _findings(text: str) -> list[str]:
    """Return every finding for a durable feature-file body in a stable order."""
    lines = text.splitlines()
    findings: list[str] = []
    findings.extend(_title_findings(lines))
    findings.extend(_description_findings(lines))
    findings.extend(_status_findings(lines))
    findings.extend(_requirements_findings(lines))
    findings.extend(_entry_findings(lines))
    findings.extend(_numbering_findings(lines))
    findings.extend(_mark_findings(text))
    findings.extend(_derivation_findings(text))
    findings.extend(_superseded_findings(lines))
    findings.extend(_placeholder_findings(text))
    findings.extend(_guidance_findings(lines))
    return findings


def derive_feature_status(
    requirements: tuple[FeatureRequirement, ...],
) -> FeatureStatus | None:
    """Return the status derived from the ticks.

    Every requirement ticked is achieved, some ticked is partial, none ticked is
    not started. A file without requirement lines derives no status and is
    reported by the requirements-section rule instead.
    """
    if not requirements:
        return None
    ticked = sum(1 for requirement in requirements if requirement.ticked)
    if ticked == len(requirements):
        return ACHIEVED
    if ticked:
        return PARTIAL
    return NOT_STARTED


def _derivation_findings(text: str) -> list[str]:
    """Return findings when the declared status disagrees with the ticks."""
    values = _status_values(text.splitlines())
    if len(values) != 1 or values[0] not in STATUSES:
        return []
    derived = derive_feature_status(read_requirements(text))
    if derived is None or derived == values[0]:
        return []
    return [
        f"feature-file-status-derivation: declared status {values[0]!r} does not "
        f"match the status derived from the ticks {derived!r}"
    ]


def assess_feature_file(text: str) -> FeatureFileAssessment:
    """Return the ordered findings and the status derived from the ticks."""
    return FeatureFileAssessment(
        findings=tuple(_findings(text)),
        status=derive_feature_status(read_requirements(text)),
    )


def validate_feature_file(text: str) -> list[str]:
    """Return every finding for a durable feature-file body; empty means valid."""
    return _findings(text)
