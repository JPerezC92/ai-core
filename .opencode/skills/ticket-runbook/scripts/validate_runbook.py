"""
Validate a ticket working-analysis directory and its closed-out ticket set.

The ``ticket-runbook`` skill writes a working ``analysis/`` set — ``state.md`` plus
``01-identify.md``, ``02-investigate.md``, and ``03-synthesize.md`` — and collapses
it to one ``ticket_<id>.md`` record plus evidence at close.

Usage (from project root):
    python3 .opencode/skills/ticket-runbook/scripts/validate_runbook.py --help
    python3 .opencode/skills/ticket-runbook/scripts/validate_runbook.py <analysis_dir> --scaffold
    python3 .opencode/skills/ticket-runbook/scripts/validate_runbook.py <analysis_dir> --step identify
    python3 .opencode/skills/ticket-runbook/scripts/validate_runbook.py <analysis_dir>
    python3 .opencode/skills/ticket-runbook/scripts/validate_runbook.py <ticket_dir> --close-out

Modes:
    - default     : validate the ``state.md`` header and every present step file's
                    structure; scan completed steps for unfilled fill tokens.
    - --scaffold  : require all four analysis files and their structure, but
                    intentionally ignore step-body fill tokens.
    - --step NAME : validate only the named step file (identify | investigate |
                    synthesize) plus the state header.
    - --close-out : validate the durable ticket set after the working set is
                    removed; every cited Imagen ``path:`` value must resolve.

Exit codes:
    0 — all checks pass (warnings do not affect the exit code)
    1 — one or more violations found
    2 — close-out check skipped (ticket record not found)
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, TypedDict

import yaml

# ---------------------------------------------------------------------------
# Kill-switch pilot values (tunable per project)
# Source: the project's kill-switch configuration
# ---------------------------------------------------------------------------
KILL_MAX_HYPOTHESES: int = 3
KILL_MAX_QUERIES: int = 6
KILL_MAX_RERUNS: int = 2
SLA_WARN_PCT: float = 0.25  # warn when < 25% SLA remaining (= 75% consumed)

# Working-analysis file names. ``state.md`` is the header; the other three are
# the ordered steps.
STATE_FILE: str = "state.md"
STEP_FILES: list[str] = [
    "01-identify.md",
    "02-investigate.md",
    "03-synthesize.md",
]
REQUIRED_ANALYSIS_FILES: list[str] = [STATE_FILE] + STEP_FILES

STEP_NAMES: list[str] = ["identify", "investigate", "synthesize"]
STEP_FILE_BY_NAME: dict[str, str] = {
    "identify": "01-identify.md",
    "investigate": "02-investigate.md",
    "synthesize": "03-synthesize.md",
}

# Required ## headings in every step file.
REQUIRED_STEP_SECTIONS: list[str] = [
    "Steps",
    "Output",
    "Gate",
    "Abort conditions",
]

# Owner/Pre/Reads/Writes appear as blockquote lines, not ## headings.
REQUIRED_BLOCKQUOTE_LABELS: list[str] = [
    "Owner",
    "Pre",
    "Reads",
    "Writes",
]

# Allowed values for the state.md Phase header field.
ALLOWED_PHASES: frozenset[str] = frozenset(STEP_NAMES)

# Allowed values for the state.md identification_verdict header field.
# - "pending"    : initial value set at scaffold time
# - "exact"      : exactly one active incident P-NNN, every discriminator evidenced
# - "structural" : exactly one candidate or active incident P-NNN
# - "no_match"   : no eligible incident P-NNN (an empty register always yields this)
ALLOWED_IDENTIFICATION_VERDICTS: frozenset[str] = frozenset(
    {"pending", "exact", "structural", "no_match"}
)

# Problem-register schema (knowledge/problems.md).
REGISTER_COLUMNS: tuple[str, ...] = (
    "id",
    "date",
    "team",
    "symptom",
    "system",
    "module",
    "problem",
    "discriminators",
    "exclusions",
    "evidence",
    "root_cause",
    "lifecycle",
    "allow_exact",
    "status",
)
ALLOWED_TEAMS: frozenset[str] = frozenset({"incident", "dev"})
ALLOWED_LIFECYCLES: frozenset[str] = frozenset(
    {"candidate", "active", "mitigated", "resolved", "retired"}
)
ALLOWED_ALLOW_EXACT: frozenset[str] = frozenset({"yes", "no"})
ALLOWED_STATUSES: frozenset[str] = frozenset({"open", "closed"})

# Angle-bracket tokens that legitimately persist in fully-filled step files
# (boilerplate references, not data placeholders).  Every other <...> token is
# treated as an unfilled fill-marker.
EXCLUDE_FILL_TOKENS: frozenset[str] = frozenset(
    {"<now>", "<calculated>", "<ID>", "<SYSTEM>", "<timestamp>"}
)

_DATETIME_FMT = "%Y-%m-%dT%H:%M"
_FRACTION_RE = re.compile(r"^(\d+)/(\d+)$")
_FILL_TOKEN_RE = re.compile(r"<[^>]+>")
_PROBLEM_ID_RE = re.compile(r"^P-\d+$")
_SYMPTOM_ID_RE = re.compile(r"S-\d{2}")
_CITED_PATH_RE = re.compile(r"\bpath:\s*\**\s*([^\n]+)")


class AnalysisHeader(TypedDict):
    """The seven required YAML frontmatter fields for ``analysis/state.md``."""

    Phase: str
    SLA_due: str
    Updated: str
    Hypotheses_outstanding: str
    Query_budget: str
    Identification_verdict: str
    Same_query_reruns: str


class ProblemRow(TypedDict):
    """One parsed row of the ``knowledge/problems.md`` register."""

    id: str
    date: str
    team: str
    symptom: str
    system: str
    module: str
    problem: str
    discriminators: str
    exclusions: str
    evidence: str
    root_cause: str
    lifecycle: str
    allow_exact: str
    status: str


class TicketIdentification(TypedDict):
    """The identification fields parsed from a ``ticket_<id>.md`` record."""

    symptom_ids: list[str]
    known_problem_ids: list[str]
    identification_verdict: str


class CloseOutSnapshot(TypedDict):
    """Filesystem values required to evaluate the close-out durable set."""

    ticket_file_name: Optional[str]
    ticket_content: Optional[str]
    working_analysis_files: list[str]
    response_draft_present: bool
    screenshots_dir_present: bool
    validations_dir_present: bool
    missing_image_paths: list[str]


# ── Pure-logic helpers ───────────────────────────────────────────────────────


def load_text(path: Path) -> str:
    """Load UTF-8 text from ``path`` at the validator's IO boundary."""
    return path.read_text(encoding="utf-8")


def _parse_fraction(value: str) -> tuple[int, int]:
    """Parse a ``'N/M'`` fraction string into ``(N, M)``.

    Raises ``ValueError`` when the string does not match the pattern.
    """
    m = _FRACTION_RE.match(str(value).strip())
    if not m:
        raise ValueError(f"Expected N/M fraction, got: {value!r}")
    return int(m.group(1)), int(m.group(2))


def _parse_iso_datetime(value: str) -> Optional[datetime]:
    """Parse an ISO datetime string ``'YYYY-MM-DDTHH:MM'``.

    Returns ``None`` when the value is a placeholder (contains ``<`` or ``Y``
    characters indicating an unfilled template value).
    """
    s = str(value).strip()
    if "<" in s or "Y" in s:
        return None
    try:
        return datetime.strptime(s, _DATETIME_FMT)
    except ValueError:
        return None


def _load_front_matter(content: str, source: str) -> dict[str, object]:
    """Parse the YAML frontmatter block of ``content``.

    Raises ``ValueError`` when the block is absent, unclosed, not a mapping, or
    invalid YAML.
    """
    lines = content.splitlines(keepends=True)

    if not lines or lines[0].rstrip("\r\n") != "---":
        raise ValueError(f"No YAML frontmatter block found in {source}")

    closing: Optional[int] = None
    for i, line in enumerate(lines[1:], start=1):
        if line.rstrip("\r\n") == "---":
            closing = i
            break

    if closing is None:
        raise ValueError(f"Unclosed frontmatter in {source}")

    frontmatter_text = "".join(lines[1:closing])
    try:
        data = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML frontmatter in {source}: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"Frontmatter is not a YAML mapping in {source}")

    return data


def _split_table_row(line: str) -> list[str]:
    """Split a Markdown table row into stripped cells.

    Returns an empty list when the line is not a table row.
    """
    stripped = line.strip()
    if not stripped.startswith("|"):
        return []
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def _coerce_str_list(value: object) -> list[str]:
    """Normalize a YAML scalar or list value into a list of strings."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text or text == "[]":
        return []
    return [part.strip() for part in text.split(",") if part.strip()]


# ── State-header parsing and checks ──────────────────────────────────────────


def parse_state_header(content: str, source: str) -> AnalysisHeader:
    """Extract the seven YAML frontmatter fields from ``analysis/state.md``.

    Raises ``ValueError`` when the file cannot be parsed or is missing fields.
    """
    data = _load_front_matter(content, source)

    required_keys = {
        "Phase",
        "SLA-due",
        "Updated",
        "Hypotheses-outstanding",
        "Query-budget",
        "identification_verdict",
        "Same-query-reruns",
    }
    missing = required_keys - data.keys()
    if missing:
        raise ValueError(f"Missing header fields in {source}: {sorted(missing)}")

    return {
        "Phase": str(data["Phase"]),
        "SLA_due": str(data["SLA-due"]),
        "Updated": str(data["Updated"]),
        "Hypotheses_outstanding": str(data["Hypotheses-outstanding"]),
        "Query_budget": str(data["Query-budget"]),
        "Identification_verdict": str(data["identification_verdict"]),
        "Same_query_reruns": str(data["Same-query-reruns"]),
    }


def load_state_header(path: Path) -> AnalysisHeader:
    """Load and parse ``analysis/state.md`` at the validator's IO boundary."""
    return parse_state_header(load_text(path), str(path))


def _step_rank(fname: str) -> int:
    """Return the 1-based rank of a step filename.

    Returns ``99`` for filenames that do not match a known step (treated as
    always-required).
    """
    if fname in STEP_FILES:
        return STEP_FILES.index(fname) + 1
    return 99


def _current_step_rank(header: AnalysisHeader) -> Optional[int]:
    """Map the ``Phase`` header value to a 1-based step rank.

    Returns ``None`` when ``Phase`` is not a known step name.
    """
    phase = header["Phase"].strip()
    if phase in STEP_FILE_BY_NAME:
        return STEP_FILES.index(STEP_FILE_BY_NAME[phase]) + 1
    return None


def check_phase(header: AnalysisHeader) -> list[str]:
    """Check that ``Phase`` is a known step name.

    Violations:
        PHASE-ERROR: value not in ALLOWED_PHASES
    """
    value = header["Phase"].strip()
    if value not in ALLOWED_PHASES:
        allowed = ", ".join(STEP_NAMES)
        return [
            f"PHASE-ERROR: Phase value {value!r} not in allowed set ({allowed})"
        ]
    return []


def check_identification_verdict(header: AnalysisHeader) -> list[str]:
    """Check that ``identification_verdict`` is an allowed enum value.

    Violations:
        VERDICT-1: value not in ALLOWED_IDENTIFICATION_VERDICTS
    """
    value = header["Identification_verdict"].strip()
    if value not in ALLOWED_IDENTIFICATION_VERDICTS:
        allowed = ", ".join(sorted(ALLOWED_IDENTIFICATION_VERDICTS))
        return [
            f"VERDICT-1: identification_verdict value {value!r} not in "
            f"allowed set ({allowed})"
        ]
    return []


def check_kill_switches(header: AnalysisHeader) -> list[str]:
    """Check kill-switch counters in the parsed header dict.

    Returns a list of violation strings.  Empty list means no kill-switch is
    tripped.

    Violations:
        KILL-1: Hypotheses-outstanding numerator > KILL_MAX_HYPOTHESES
        KILL-2: Query-budget numerator > KILL_MAX_QUERIES
        KILL-3: Same-query-reruns numerator > KILL_MAX_RERUNS
    """
    violations: list[str] = []

    try:
        hyp_consumed, _ = _parse_fraction(header["Hypotheses_outstanding"])
        if hyp_consumed > KILL_MAX_HYPOTHESES:
            violations.append(
                f"KILL-1: hypothesis cap exceeded "
                f"({hyp_consumed} > {KILL_MAX_HYPOTHESES})"
            )
    except ValueError as exc:
        violations.append(f"KILL-1: cannot parse Hypotheses-outstanding — {exc}")

    try:
        q_consumed, _ = _parse_fraction(header["Query_budget"])
        if q_consumed > KILL_MAX_QUERIES:
            violations.append(
                f"KILL-2: query budget exhausted "
                f"({q_consumed} > {KILL_MAX_QUERIES})"
            )
    except ValueError as exc:
        violations.append(f"KILL-2: cannot parse Query-budget — {exc}")

    try:
        rerun_consumed, _ = _parse_fraction(header["Same_query_reruns"])
        if rerun_consumed > KILL_MAX_RERUNS:
            violations.append(
                f"KILL-3: re-run cap exceeded "
                f"({rerun_consumed} > {KILL_MAX_RERUNS})"
            )
    except ValueError as exc:
        violations.append(f"KILL-3: cannot parse Same-query-reruns — {exc}")

    return violations


def check_sla_clock(header: AnalysisHeader) -> Optional[str]:
    """Warn when the SLA time remaining is below ``SLA_WARN_PCT`` of the window.

    Returns a warning string when the threshold is breached, ``None`` otherwise.
    Skips the check silently when SLA-due or Updated are placeholder values.
    """
    sla_due = _parse_iso_datetime(header["SLA_due"])
    updated = _parse_iso_datetime(header["Updated"])

    if sla_due is None or updated is None:
        return None  # placeholder values — template not yet filled

    now = datetime.now()
    total_window = (sla_due - updated).total_seconds()
    if total_window <= 0:
        return None  # degenerate window — cannot compute ratio

    remaining = (sla_due - now).total_seconds()
    remaining_pct = remaining / total_window

    if remaining_pct < SLA_WARN_PCT:
        hours_remaining = max(remaining / 3600, 0.0)
        return (
            f"SLA-WARN: {hours_remaining:.1f} hours remaining "
            f"({remaining_pct * 100:.0f}% of window left)"
        )
    return None


def check_concurrent_session(header: AnalysisHeader) -> Optional[str]:
    """Warn when ``Updated`` was written less than 10 minutes ago.

    This is a non-blocking safety warning: another agent session may still be
    active on the same analysis.  Returns a warning string when the condition is
    met, ``None`` otherwise.  Skips silently when ``Updated`` is a placeholder.
    """
    updated = _parse_iso_datetime(header["Updated"])
    if updated is None:
        return None  # placeholder — template not yet filled

    now = datetime.now()
    delta_seconds = (now - updated).total_seconds()

    if delta_seconds < 600:  # 10 minutes = 600 seconds
        minutes_ago = int(delta_seconds // 60)
        return (
            f"CONCURRENT: another session updated {minutes_ago} minutes ago "
            f"(Updated: {header['Updated']})"
        )
    return None


# ── Step-file structure checks ───────────────────────────────────────────────


def check_step_files_exist(
    step_contents: dict[str, str],
    analysis_dir: str,
    current_rank: Optional[int] = None,
) -> tuple[list[str], list[str]]:
    """Verify that required step files exist in ``analysis_dir``.

    When ``current_rank`` is supplied, step files through that rank are
    violations when absent; later step files are warnings when absent.  Without
    ``current_rank``, absent steps at or below the highest present rank are
    violations and later absences are warnings.

    Returns:
        (violations, warnings) — two separate lists of strings.
    """
    presence = {fname: fname in step_contents for fname in STEP_FILES}

    violations: list[str] = []
    warnings: list[str] = []

    for fname in STEP_FILES:
        rank = _step_rank(fname)
        if presence[fname]:
            continue
        if current_rank is not None and rank <= current_rank:
            violations.append(
                f"MISSING-STEP: {fname} not found in {analysis_dir}"
            )
        elif current_rank is not None:
            warnings.append(
                f"INCOMPLETE-ANALYSIS: {fname} not yet written "
                f"(current step rank: {current_rank:02d})"
            )
        else:
            highest_present = max(
                (r for f, r in ((f, _step_rank(f)) for f in STEP_FILES)
                 if presence[f]),
                default=0,
            )
            if rank <= highest_present:
                violations.append(
                    f"MISSING-STEP: {fname} not found in {analysis_dir}"
                )
            else:
                warnings.append(
                    f"INCOMPLETE-ANALYSIS: {fname} not yet written "
                    f"(highest written rank: {highest_present:02d})"
                )

    return violations, warnings


def check_single_step_file_exists(
    step_contents: dict[str, str], step_name: str
) -> Optional[str]:
    """Return the filename for ``step_name`` when it is present, else ``None``."""
    fname = STEP_FILE_BY_NAME.get(step_name)
    if fname is None:
        return None
    return fname if fname in step_contents else None


def _check_step_body_fill_markers(
    content: str, fname: str
) -> list[tuple[str, str]]:
    """Scan step-file content for unfilled ``<...>`` placeholder tokens.

    Any ``<token>`` NOT in ``EXCLUDE_FILL_TOKENS`` is treated as an unfilled data
    placeholder left over from the scaffold template.  Accepts already-read
    content (no IO performed here).
    """
    findings: list[tuple[str, str]] = []
    for line in content.splitlines():
        for tok in _FILL_TOKEN_RE.findall(line):
            if tok not in EXCLUDE_FILL_TOKENS:
                findings.append((fname, f"UNFILLED-TOKEN: {tok}"))
    return findings


def _check_step_file_sections(
    content: str,
    fname: str,
    include_fill_tokens: bool = True,
) -> list[tuple[str, str]]:
    """Check one step file for required headings, blockquote labels, and tokens.

    Returns a list of ``(filename, missing_item)`` tuples.  Empty list means the
    file is structurally complete.  The caller supplies already-loaded content.
    """
    findings: list[tuple[str, str]] = []
    h2_re = re.compile(r"^##\s+(.+)$")
    blockquote_label_re = re.compile(r"^>\s+\*\*(\w[\w\s-]*):\*\*")

    h2_present: set[str] = set()
    labels_present: set[str] = set()

    for line in content.splitlines():
        h2_match = h2_re.match(line)
        if h2_match:
            h2_present.add(h2_match.group(1).strip())

        bq_match = blockquote_label_re.match(line)
        if bq_match:
            labels_present.add(bq_match.group(1).strip())

    for section in REQUIRED_STEP_SECTIONS:
        if section not in h2_present:
            findings.append((fname, f"## {section}"))

    for label in REQUIRED_BLOCKQUOTE_LABELS:
        if label not in labels_present:
            findings.append((fname, f"**{label}:**"))

    if include_fill_tokens:
        findings.extend(_check_step_body_fill_markers(content, fname))

    return findings


def check_step_files_have_required_sections(
    step_contents: dict[str, str],
    fill_token_rank_limit: Optional[int] = None,
) -> list[tuple[str, str]]:
    """Validate required structure in every present step file.

    Fill-token checks apply to every present step by default.  When
    ``fill_token_rank_limit`` is supplied, they apply only through that rank;
    all later present step files still receive structural checks.
    """
    findings: list[tuple[str, str]] = []

    for fname in STEP_FILES:
        content = step_contents.get(fname)
        if content is None:
            continue  # missing-file check handled by check_step_files_exist
        include_fill_tokens = (
            fill_token_rank_limit is None
            or _step_rank(fname) <= fill_token_rank_limit
        )
        findings.extend(
            _check_step_file_sections(content, fname, include_fill_tokens)
        )

    return findings


def check_single_step_sections(
    step_contents: dict[str, str], step_name: str
) -> list[tuple[str, str]]:
    """Check the required sections for the single step file matching ``step_name``."""
    findings: list[tuple[str, str]] = []
    fname = STEP_FILE_BY_NAME.get(step_name)
    if fname is None:
        return findings
    content = step_contents.get(fname)
    if content is not None:
        findings.extend(_check_step_file_sections(content, fname))
    return findings


def load_step_file_contents(analysis_dir: Path) -> dict[str, str]:
    """Load every present step file at the validator's IO boundary."""
    return {
        fname: load_text(analysis_dir / fname)
        for fname in STEP_FILES
        if (analysis_dir / fname).is_file()
    }


# ── Register-first identification checks ─────────────────────────────────────


def parse_problem_register(content: str) -> list[ProblemRow]:
    """Parse the data rows of a ``knowledge/problems.md`` register.

    Returns one ``ProblemRow`` per well-formed ``P-NNN`` row.  An empty register
    (or a register with only header/separator/no-entry rows) returns ``[]``.
    """
    rows: list[ProblemRow] = []
    for line in content.splitlines():
        cells = _split_table_row(line)
        if not cells or not _PROBLEM_ID_RE.match(cells[0]):
            continue
        if len(cells) != len(REGISTER_COLUMNS):
            continue
        rows.append(
            ProblemRow(
                id=cells[0],
                date=cells[1],
                team=cells[2],
                symptom=cells[3],
                system=cells[4],
                module=cells[5],
                problem=cells[6],
                discriminators=cells[7],
                exclusions=cells[8],
                evidence=cells[9],
                root_cause=cells[10],
                lifecycle=cells[11],
                allow_exact=cells[12],
                status=cells[13],
            )
        )
    return rows


def check_register_rows(content: str) -> list[str]:
    """Validate the schema of every ``P-NNN`` row in a register.

    Violations:
        REGISTER-1: row does not have exactly len(REGISTER_COLUMNS) cells
        REGISTER-2: Team is not `incident` | `dev`
        REGISTER-3: Lifecycle is not an allowed value
        REGISTER-4: Allow_exact is not `yes` | `no`
        REGISTER-5: Status is not `open` | `closed`
        REGISTER-6: Symptom does not reference >=1 S-xx class
    """
    violations: list[str] = []
    for lineno, line in enumerate(content.splitlines(), start=1):
        cells = _split_table_row(line)
        if not cells or not _PROBLEM_ID_RE.match(cells[0]):
            continue
        pi = cells[0]
        if len(cells) != len(REGISTER_COLUMNS):
            violations.append(
                f"REGISTER-1: {pi} (line {lineno}) has {len(cells)} columns, "
                f"expected {len(REGISTER_COLUMNS)}"
            )
            continue
        row = dict(zip(REGISTER_COLUMNS, cells))
        if row["team"] not in ALLOWED_TEAMS:
            violations.append(
                f"REGISTER-2: {pi} Team {row['team']!r} not in "
                f"({', '.join(sorted(ALLOWED_TEAMS))})"
            )
        if row["lifecycle"] not in ALLOWED_LIFECYCLES:
            violations.append(
                f"REGISTER-3: {pi} Lifecycle {row['lifecycle']!r} not in "
                f"({', '.join(sorted(ALLOWED_LIFECYCLES))})"
            )
        if row["allow_exact"] not in ALLOWED_ALLOW_EXACT:
            violations.append(
                f"REGISTER-4: {pi} Allow_exact {row['allow_exact']!r} not in "
                f"({', '.join(sorted(ALLOWED_ALLOW_EXACT))})"
            )
        if row["status"] not in ALLOWED_STATUSES:
            violations.append(
                f"REGISTER-5: {pi} Status {row['status']!r} not in "
                f"({', '.join(sorted(ALLOWED_STATUSES))})"
            )
        if not _SYMPTOM_ID_RE.search(row["symptom"]):
            violations.append(
                f"REGISTER-6: {pi} Symptom {row['symptom']!r} references no S-xx"
            )
    return violations


def check_identification_consistency(
    verdict: str,
    cited_problem_ids: list[str],
    register_rows: list[ProblemRow],
) -> list[str]:
    """Check a verdict against the incident rows it cites.

    Rules:
        - ``no_match`` cites no P-NNN.
        - ``pending`` is scaffold-only.
        - ``exact``/``structural`` cite at least one incident P-NNN.
        - ``exact`` cites exactly one ``active`` row with ``allow_exact: yes``.
        - ``structural`` cites only ``candidate``/``active`` rows.
        - An empty register can only yield ``no_match``.

    Violations:
        VERDICT-2: no_match cites a P-NNN
        VERDICT-3: exact/structural cite no P-NNN
        VERDICT-4: cited ID is not an incident row in the register
        VERDICT-5: exact cites more than one P-NNN
        VERDICT-6: exact cites a non-active row
        VERDICT-7: exact cites a row with allow_exact != yes
        VERDICT-8: structural cites a row outside candidate|active
    """
    violations: list[str] = []
    incident_rows = [row for row in register_rows if row["team"] == "incident"]
    cited = list(dict.fromkeys(cited_problem_ids))

    if verdict == "pending":
        return violations

    if verdict == "no_match":
        if cited:
            violations.append(
                f"VERDICT-2: no_match must not cite a P-NNN (cited: {cited})"
            )
        return violations

    if verdict not in ("exact", "structural"):
        return violations

    if not cited:
        violations.append(
            f"VERDICT-3: {verdict} requires a cited incident P-NNN"
        )
        return violations

    matched = [row for row in incident_rows if row["id"] in set(cited)]
    for cid in cited:
        if not any(row["id"] == cid for row in incident_rows):
            violations.append(
                f"VERDICT-4: cited {cid} is not an incident P-NNN row"
            )

    if verdict == "exact":
        if len(cited) != 1:
            violations.append(
                f"VERDICT-5: exact requires exactly one cited P-NNN "
                f"(cited: {cited})"
            )
        for row in matched:
            if row["lifecycle"] != "active":
                violations.append(
                    f"VERDICT-6: exact requires an active P-NNN "
                    f"({row['id']} is {row['lifecycle']})"
                )
            if row["allow_exact"] != "yes":
                violations.append(
                    f"VERDICT-7: exact requires allow_exact=yes "
                    f"({row['id']} is {row['allow_exact']})"
                )

    if verdict == "structural":
        for row in matched:
            if row["lifecycle"] not in ("candidate", "active"):
                violations.append(
                    f"VERDICT-8: structural requires candidate|active "
                    f"({row['id']} is {row['lifecycle']})"
                )

    return violations


def parse_ticket_record(content: str, source: str) -> TicketIdentification:
    """Extract identification fields from a ``ticket_<id>.md`` frontmatter.

    Missing fields default to an empty list / ``pending`` so a template record
    validates without inventing data.
    """
    data = _load_front_matter(content, source)
    return {
        "symptom_ids": _coerce_str_list(data.get("symptom_ids")),
        "known_problem_ids": _coerce_str_list(data.get("known_problem_ids")),
        "identification_verdict": str(
            data.get("identification_verdict", "pending")
        ).strip(),
    }


# ── Close-out checks ─────────────────────────────────────────────────────────


def _cited_image_paths(content: str) -> list[str]:
    """Return every ``path:`` value found in Imagen-style blocks."""
    paths: list[str] = []
    for match in _CITED_PATH_RE.finditer(content):
        value = match.group(1).strip().strip("`").strip()
        if value:
            paths.append(value)
    return paths


def _resolve_cited_path(
    value: str, ticket_dir: Path, repo_root: Path
) -> Path:
    """Resolve a cited ``path:`` against the ticket dir and the repo root."""
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    for base in (ticket_dir, repo_root):
        resolved = base / candidate
        if resolved.exists():
            return resolved
    return ticket_dir / candidate


def load_close_out_snapshot(
    ticket_dir: Path, repo_root: Path
) -> CloseOutSnapshot:
    """Load the close-out filesystem values at the validator's IO boundary."""
    analysis_dir = ticket_dir / "analysis"
    working_files = (
        sorted(p.name for p in analysis_dir.glob("*.md"))
        if analysis_dir.is_dir()
        else []
    )

    ticket_files = sorted(ticket_dir.glob("ticket_*.md"))
    ticket_name: Optional[str] = None
    ticket_content: Optional[str] = None
    missing_paths: list[str] = []

    if ticket_files:
        ticket_name = ticket_files[0].name
        ticket_content = load_text(ticket_files[0])
        missing_paths = [
            value
            for value in _cited_image_paths(ticket_content)
            if not _resolve_cited_path(value, ticket_dir, repo_root).exists()
        ]

    return {
        "ticket_file_name": ticket_name,
        "ticket_content": ticket_content,
        "working_analysis_files": working_files,
        "response_draft_present": (ticket_dir / "response-draft.md").is_file(),
        "screenshots_dir_present": (ticket_dir / "screenshots").is_dir(),
        "validations_dir_present": (ticket_dir / "validations").is_dir(),
        "missing_image_paths": missing_paths,
    }


def evaluate_close_out(snapshot: CloseOutSnapshot) -> list[str]:
    """Evaluate a loaded close-out snapshot without performing IO.

    Violations:
        CLOSE-0: ticket_<id>.md missing
        CLOSE-1: a working analysis file remains
        CLOSE-2: response-draft.md remains
        CLOSE-3: screenshots/ missing from the durable set
        CLOSE-4: validations/ missing from the durable set
        CLOSE-5: a cited image path does not resolve
    """
    violations: list[str] = []

    if snapshot["ticket_file_name"] is None:
        violations.append("CLOSE-0: ticket_<id>.md not found")

    for name in snapshot["working_analysis_files"]:
        violations.append(
            f"CLOSE-1: working analysis file remains after close: {name}"
        )

    if snapshot["response_draft_present"]:
        violations.append("CLOSE-2: response-draft.md remains after close")

    if not snapshot["screenshots_dir_present"]:
        violations.append("CLOSE-3: screenshots/ missing from the durable set")

    if not snapshot["validations_dir_present"]:
        violations.append("CLOSE-4: validations/ missing from the durable set")

    for value in snapshot["missing_image_paths"]:
        violations.append(f"CLOSE-5: cited image path does not exist: {value}")

    return violations


def load_register_rows(repo_root: Path) -> list[ProblemRow]:
    """Load ``knowledge/problems.md`` incident rows at the IO boundary."""
    register_path = repo_root / "knowledge" / "problems.md"
    if not register_path.is_file():
        return []
    return parse_problem_register(load_text(register_path))


# ── Mode entry points ────────────────────────────────────────────────────────


def validate(analysis_dir: str) -> int:
    """Run all checks on a working ``analysis/`` directory (default mode).

    Returns 0 when all checks pass, 1 when violations are found.  Warnings
    (incomplete analysis, SLA, concurrent session) do not affect the exit code.
    """
    violations: list[str] = []
    warnings: list[str] = []

    try:
        header = load_state_header(Path(analysis_dir) / STATE_FILE)
    except (OSError, ValueError) as exc:
        print(f"HEADER-ERROR: {exc}", file=sys.stderr)
        return 1

    violations.extend(check_phase(header))
    violations.extend(check_identification_verdict(header))

    current_rank = _current_step_rank(header)
    step_contents = load_step_file_contents(Path(analysis_dir))

    if current_rank is not None:
        step_violations, step_warnings = check_step_files_exist(
            step_contents, analysis_dir, current_rank
        )
        violations.extend(step_violations)
        warnings.extend(step_warnings)

    for fname, item in check_step_files_have_required_sections(
        step_contents,
        fill_token_rank_limit=current_rank if current_rank is not None else 0,
    ):
        if item.startswith("UNFILLED-TOKEN:"):
            violations.append(f"{item} in {fname}")
        else:
            violations.append(f"MISSING-SECTION: {fname} is missing {item}")

    violations.extend(check_kill_switches(header))

    sla_warn = check_sla_clock(header)
    if sla_warn:
        warnings.append(sla_warn)
    concurrent_warn = check_concurrent_session(header)
    if concurrent_warn:
        warnings.append(concurrent_warn)

    for warning in warnings:
        print(f"WARN: {warning}", file=sys.stderr)

    if violations:
        for violation in violations:
            print(violation, file=sys.stderr)
        return 1

    base = Path(analysis_dir)
    print(f"\nAnalysis: {analysis_dir}  Phase: {header['Phase']}\n")
    print(f"{'Analysis file':<35} {'Status'}")
    print("-" * 45)
    for fname in REQUIRED_ANALYSIS_FILES:
        status = "ok" if (base / fname).is_file() else "absent (not yet written)"
        print(f"  {fname:<33} {status}")
    print()

    return 0


def validate_scaffold(analysis_dir: str) -> int:
    """Validate a freshly copied ``analysis/`` scaffold without fill tokens."""
    violations: list[str] = []
    warnings: list[str] = []

    try:
        header = load_state_header(Path(analysis_dir) / STATE_FILE)
    except (OSError, ValueError) as exc:
        print(f"HEADER-ERROR: {exc}", file=sys.stderr)
        return 1

    violations.extend(check_phase(header))
    violations.extend(check_identification_verdict(header))

    step_contents = load_step_file_contents(Path(analysis_dir))
    step_violations, step_warnings = check_step_files_exist(
        step_contents, analysis_dir, len(STEP_FILES)
    )
    violations.extend(step_violations)
    warnings.extend(step_warnings)

    for fname, item in check_step_files_have_required_sections(
        step_contents, fill_token_rank_limit=0
    ):
        violations.append(f"MISSING-SECTION: {fname} is missing {item}")

    violations.extend(check_kill_switches(header))

    sla_warn = check_sla_clock(header)
    if sla_warn:
        warnings.append(sla_warn)
    concurrent_warn = check_concurrent_session(header)
    if concurrent_warn:
        warnings.append(concurrent_warn)

    for warning in warnings:
        print(f"WARN: {warning}", file=sys.stderr)
    if violations:
        for violation in violations:
            print(violation, file=sys.stderr)
        return 1

    print(f"ok  scaffold: {analysis_dir}")
    return 0


def validate_step(analysis_dir: str, step_name: str) -> int:
    """Validate a single step file plus the ``state.md`` header.

    Returns 0 when all checks pass, 1 when violations are found.  Exits 1 with a
    clear "step not yet written" message when the named step file is absent.
    """
    violations: list[str] = []
    warnings: list[str] = []

    try:
        header = load_state_header(Path(analysis_dir) / STATE_FILE)
    except (OSError, ValueError) as exc:
        print(f"HEADER-ERROR: {exc}", file=sys.stderr)
        return 1

    violations.extend(check_phase(header))
    violations.extend(check_identification_verdict(header))

    step_contents = load_step_file_contents(Path(analysis_dir))
    fname = check_single_step_file_exists(step_contents, step_name)
    if fname is None:
        expected = STEP_FILE_BY_NAME.get(step_name, f"{step_name}.md")
        print(
            f"STEP-NOT-WRITTEN: step {step_name} ({expected}) "
            f"not yet written in {analysis_dir}",
            file=sys.stderr,
        )
        return 1

    for _fname, item in check_single_step_sections(step_contents, step_name):
        if item.startswith("UNFILLED-TOKEN:"):
            violations.append(f"{item} in {_fname}")
        else:
            violations.append(f"MISSING-SECTION: {_fname} is missing {item}")

    violations.extend(check_kill_switches(header))

    sla_warn = check_sla_clock(header)
    if sla_warn:
        warnings.append(sla_warn)
    concurrent_warn = check_concurrent_session(header)
    if concurrent_warn:
        warnings.append(concurrent_warn)

    for warning in warnings:
        print(f"WARN: {warning}", file=sys.stderr)

    if violations:
        for violation in violations:
            print(violation, file=sys.stderr)
        return 1

    print(f"ok  step {step_name} ({fname})  [analysis: {analysis_dir}]")
    return 0


def validate_close_out(ticket_dir: str, repo_root: str) -> int:
    """Validate the collapsed durable ticket set.

    Returns 0 when the close-out set is complete, 1 when violations are found,
    and 2 when no ``ticket_<id>.md`` record exists (nothing to check).
    """
    snapshot = load_close_out_snapshot(Path(ticket_dir), Path(repo_root))

    if snapshot["ticket_file_name"] is None:
        print(
            "CLOSE-SKIPPED: ticket_<id>.md not found at "
            f"{ticket_dir}",
            file=sys.stderr,
        )
        return 2

    violations = evaluate_close_out(snapshot)

    if snapshot["ticket_content"] is not None:
        record = parse_ticket_record(
            snapshot["ticket_content"], str(snapshot["ticket_file_name"])
        )
        violations.extend(
            check_identification_consistency(
                record["identification_verdict"],
                record["known_problem_ids"],
                load_register_rows(Path(repo_root)),
            )
        )

    if violations:
        for violation in violations:
            print(violation, file=sys.stderr)
        return 1

    print(f"ok  close-out: {ticket_dir}  ({snapshot['ticket_file_name']})")
    return 0


# ── CLI entry point ──────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a ticket working-analysis directory (state.md + steps) "
            "and its closed-out ticket set.\n\n"
            "Default: validate completed steps through the header Phase value.\n"
            "With --scaffold: structural-only validation of all copied steps.\n"
            "With --step NAME: strict validation of only that step + header.\n"
            "With --close-out: validate the collapsed ticket durable set."
        ),
        epilog="Exit code 0 = pass, 1 = fail, 2 = close-out skipped. "
               "Warnings do not affect the exit code.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "analysis_dir",
        help="Path to the analysis directory (or the ticket directory for --close-out)",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--step",
        choices=STEP_NAMES,
        default=None,
        help=(
            "Validate only the named step file (identify | investigate | "
            "synthesize) plus the state.md header."
        ),
    )
    mode.add_argument(
        "--scaffold",
        action="store_true",
        default=False,
        help=(
            "Validate a freshly copied scaffold: require all four analysis "
            "files and their structure, but ignore step-body fill tokens."
        ),
    )
    mode.add_argument(
        "--close-out",
        action="store_true",
        default=False,
        dest="close_out",
        help=(
            "Validate the collapsed durable ticket set: ticket_<id>.md, "
            "screenshots/, validations/, and every cited image path."
        ),
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        dest="repo_root",
        help="Repo root used to resolve cited image paths and the register.",
    )
    return parser


if __name__ == "__main__":
    args = _build_parser().parse_args()
    if args.close_out:
        sys.exit(validate_close_out(args.analysis_dir, args.repo_root))
    if args.step is not None:
        sys.exit(validate_step(args.analysis_dir, args.step))
    if args.scaffold:
        sys.exit(validate_scaffold(args.analysis_dir))
    sys.exit(validate(args.analysis_dir))
