"""Extract creation bodies and check completed PASS body structure, not truth."""

from __future__ import annotations

import re

from .records import Finding, ReviewDecisions, ReviewMetadata, ReviewPreparationError


def extract_body(draft: str) -> str | ReviewPreparationError:
    """Remove the creation-only title wrapper without normalizing body bytes."""
    match = re.match(r"\ATitle: [^\r\n]+\r?\n\r?\n---\r?\n\r?\n", draft)
    if match is None or not draft[match.end():].startswith("## Summary"):
        return ReviewPreparationError("DRAFT_INVALID", "creation draft title wrapper and Summary required")
    return draft[match.end():]


def _cells(line: str) -> list[str]:
    return [cell.strip().replace(r"\|", "|") for cell in re.split(r"(?<!\\)\|", line.strip())[1:-1]]


def parse_sections(body: str) -> dict[str, str] | ReviewPreparationError:
    """Split unique canonical headings while retaining section content verbatim."""
    error = ReviewPreparationError("BODY_INVALID", "unique canonical sections with content required")
    if not isinstance(body, str):
        return error
    matches = list(re.finditer(r"^## ([^\r\n]+)(?:\r?\n|$)", body, re.MULTILINE))
    names = [match[1] for match in matches]
    order = ["Summary", "Breaking changes", "Test plan", "Findings / blockers", "Test evidence", "Open debt"]
    if not matches or matches[0].start() != 0 or len(set(names)) != len(names):
        return error
    if any(name not in order for name in names) or names != sorted(names, key=order.index):
        return error
    if any(name not in names for name in ("Summary", "Test plan", "Findings / blockers")):
        return error
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        content = body[match.end():end]
        if not content.strip():
            return error
        sections[match[1]] = content
    return sections


def parse_findings(content: str) -> list[Finding] | ReviewPreparationError:
    """Parse the canonical finding schema without judging resolution evidence."""
    error = ReviewPreparationError("BODY_INVALID", "canonical finding table required")
    if content.strip() in ("No findings.", "No review findings yet."):
        return []
    lines = [line for line in content.splitlines() if line.strip()]
    if len(lines) < 3 or lines[0] != "| ID | Severity | Status | Evidence | Owner / resolution |":
        return error
    if re.fullmatch(r"\|(?:\s*:?-+:?\s*\|){5}", lines[1]) is None:
        return error
    rows = [_cells(line) for line in lines[2:]]
    if any(not line.strip().startswith("|") or not line.strip().endswith("|") for line in lines[2:]):
        return error
    for row in rows:
        if len(row) != 5 or not all(row) or re.fullmatch(r"F[1-9][0-9]*", row[0]) is None:
            return error
        if row[1].strip("`") not in ("BLOCK", "ADVISORY") or row[2].strip("`") not in ("OPEN", "IN PROGRESS", "FIXED", "DEFERRED", "REJECTED"):
            return error
    ids = [row[0] for row in rows]
    if len(set(ids)) != len(ids) or ids != [f"F{index}" for index in range(1, len(ids) + 1)]:
        return error
    return [
        Finding(id=row[0], severity=row[1].strip("`"), status=row[2].strip("`"),
                evidence=row[3], resolution=row[4])
        for row in rows
    ]


def validate_body(body: str, metadata: ReviewMetadata, decisions: ReviewDecisions = ReviewDecisions()) -> ReviewPreparationError | None:
    """Check structural correspondence only; owners establish actual evidence truth.

    PASS and accepted ADVISORY use explicit supplied N/A and debt provenance.
    No structural check establishes the truth or authority of these claims.
    """
    error = ReviewPreparationError("BODY_INVALID", "completed canonical review body required")
    if not isinstance(body, str):
        return error
    lines = body.rstrip().splitlines()
    verdict = re.fullmatch(r"\[(PASS|ADVISORY)\] — (.+)", lines[-1]) if lines else None
    if verdict is None:
        return error
    content = body[:body.rfind(lines[-1])]
    if re.search(r"^\[(?:PASS|ADVISORY|BLOCK)\] —", content, re.MULTILINE):
        return error
    sections = parse_sections(content)
    if isinstance(sections, ReviewPreparationError):
        return sections
    if re.search(r"^Title:", body, re.MULTILINE):
        return error
    findings = parse_findings(sections["Findings / blockers"])
    if isinstance(findings, ReviewPreparationError):
        return findings
    if sections["Findings / blockers"].strip() == "No review findings yet.":
        return error
    unresolved = [finding for finding in findings if finding.status not in ("FIXED", "REJECTED")]
    if verdict[1] == "PASS" and unresolved:
        return error
    accepted = {entry.target: entry for entry in decisions.acceptance}
    debts = {entry.target: entry for entry in decisions.debt}
    if set(accepted) != {finding.id for finding in unresolved}:
        return error
    if verdict[1] == "ADVISORY" and (not unresolved or any(finding.severity != "ADVISORY" for finding in unresolved)):
        return error
    for entry in accepted.values():
        if entry.actor not in verdict[2] or entry.date not in verdict[2]:
            return error
    deferred = {finding.id for finding in findings if finding.status == "DEFERRED"}
    # Every deferred finding requires debt authority; additional records may
    # authorize independent follow-ups without creating artificial findings.
    if not deferred.issubset(debts):
        return error
    if debts:
        expected_debt = [f"- {entry.target} — {entry.destination}, authorized by {entry.actor} on {entry.date}" for entry in decisions.debt]
        if sections.get("Open debt", "").strip().splitlines() != expected_debt:
            return error
        if any(
            debts[finding.id].destination != finding.resolution.partition(" — ")[0]
            for finding in findings if finding.id in deferred
        ):
            return error
    elif "Open debt" in sections:
        return error
    plan = sections["Test plan"].strip().splitlines()
    if len(plan) < 2 or any(not re.fullmatch(r"- \[[ x]\] .+", line) for line in plan):
        return error
    items = [line[6:] for line in plan]
    if len(set(items)) != len(items):
        return error
    excluded = {entry.target for entry in decisions.not_applicable}
    unchecked = {line[6:] for line in plan if line.startswith("- [ ]")}
    if unchecked != excluded:
        return error
    items = [item for item in items if item not in excluded]
    if not items:
        return None if "Test evidence" not in sections else error
    if "Test evidence" not in sections:
        return error
    evidence = sections["Test evidence"].strip().splitlines()
    base_match = re.fullmatch(r"- Base: `([^`]+)`", evidence[2]) if len(evidence) > 2 else None
    if base_match is None:
        return error
    base = base_match[1]
    if "$" in base or base.rsplit("/", 1)[-1] != metadata["baseRefName"]:
        return error
    header = [
        f"- PR: `#{metadata['number']}`",
        f"- Immutable head SHA: `{metadata['headRefOid']}`",
        f"- Base: `{base}`",
        f'- Scope command: `git diff "{base}"...{metadata["headRefOid"]}`',
    ]
    if evidence[:4] != header:
        return error
    tail = [line for line in evidence[4:] if line.strip()]
    if len(tail) != len(items) + 2:
        return error
    if tail[0] != "| Test-plan item | Literal action/input | Observed result | Executor |" or tail[1] != "|---|---|---|---|":
        return error
    rows = [_cells(line) for line in tail[2:]]
    if any(len(row) != 4 or not all(row) for row in rows):
        return error
    if len(set(row[0] for row in rows)) != len(rows) or set(row[0] for row in rows) != set(items):
        return error
    return None
