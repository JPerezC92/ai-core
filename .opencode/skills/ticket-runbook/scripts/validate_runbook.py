"""
Validate a runbook directory: header fields, phase files, kill-switch budgets,
SLA clock, and concurrent-session safety.

Usage (from project root):
    uv run --locked python .opencode/skills/ticket-runbook/scripts/validate_runbook.py --help
    uv run --locked python .opencode/skills/ticket-runbook/scripts/validate_runbook.py <runbook_dir> --scaffold
    uv run --locked python .opencode/skills/ticket-runbook/scripts/validate_runbook.py <runbook_dir> --phase 03
    uv run --locked python .opencode/skills/ticket-runbook/scripts/validate_runbook.py <runbook_dir> --require-ledger-sync

Full validation:
    - Validates the runbook.md header (all 7 required fields).
    - Requires phase files through the current ``Phase`` header value and
      scans those completed phases for required sections and fill tokens.
      Present future phase files are structurally validated, but their template
      fill tokens are ignored.  Missing future phase files are warnings.
    - Checks kill-switch budgets, SLA clock, and concurrent-session safety.
    - Emits a phase-by-phase status table to stdout on success.

Single-phase validation (``--phase NN``):
    - Validates the runbook.md header as above.
    - Checks ONLY the specified phase file (``phase-NN-*.md``) for required
      sections.  If the phase file does not yet exist, exits non-zero with a
       clear "phase NN not yet written" message (not a schema error).

Scaffold validation (``--scaffold``):
    - Requires all six copied phase files and validates their required sections
      and blockquote labels.
    - Validates the runbook header, Replay-candidate enum, and kill-switch
      budgets, but intentionally ignores phase-body fill tokens.

Ledger sync check (``--require-ledger-sync``):
    - For each completed phase (status ✅ in ## Phase index table of runbook.md),
      compares the phase file mtime against the sibling ticket_<ID>.md mtime.
    - Failure: any completed phase file was modified more than 5 minutes after
      ticket_<ID>.md → per-phase Ledger sync was skipped (AGENTS.md violation).
    - Success: all completed phase files are within 5 minutes of ticket_<ID>.md.
    - Edge case: ticket_<ID>.md not found → exit 2 (LEDGER-CHECK-SKIPPED).

Exit codes:
    0 — all checks pass (warnings do not affect exit code)
    1 — one or more violations found
    2 — ledger sync check skipped (ticket file not found)
"""

import argparse
import os
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

# Phase file names required in every runbook directory
REQUIRED_PHASE_FILES: list[str] = [
    "phase-01-triage.md",
    "phase-02-priorart.md",
    "phase-03-hypothesis.md",
    "phase-04-validate.md",
    "phase-05-synthesis.md",
    "phase-06-respond.md",
]

# Required ## headings in every phase file
REQUIRED_PHASE_SECTIONS: list[str] = [
    "Steps",
    "Output",
    "Gate",
    "Abort conditions",
]

# Owner/Pre/Reads/Writes appear as blockquote lines, not ## headings
REQUIRED_BLOCKQUOTE_LABELS: list[str] = [
    "Owner",
    "Pre",
    "Reads",
    "Writes",
]

_DATETIME_FMT = "%Y-%m-%dT%H:%M"
_FRACTION_RE = re.compile(r"^(\d+)/(\d+)$")


class RunbookHeader(TypedDict):
    """The seven required YAML frontmatter fields for a runbook."""

    Phase: str
    SLA_due: str
    Updated: str
    Hypotheses_outstanding: str
    Query_budget: str
    Replay_candidate: str
    Same_query_reruns: str


class LedgerSyncSnapshot(TypedDict):
    """Filesystem values required to evaluate the ledger-sync time window."""

    ticket_file_name: str
    ticket_mtime: float
    phase_mtimes: dict[str, float]

# Allowed values for the Replay-candidate header field.
# - "pending"    : initial value set at scaffold time (before phase-02 runs)
# - "yes"        : exact match — skip phases 03/04/05
# - "structural" : pattern match — skip phase 03, run phase 04 with adapted queries
# - "no"         : no match — full investigation
ALLOWED_REPLAY_CANDIDATE_VALUES: frozenset[str] = frozenset(
    {"pending", "yes", "structural", "no"}
)

# Angle-bracket tokens that legitimately persist in fully-filled runbook phase
# files (boilerplate references, not data placeholders).  Every other <...>
# token is treated as an unfilled fill-marker.
# Source: grep -roE "<[^>]+>" over the runbook template + verified against
# a filled runbook (zero false positives at these 5 tokens).
EXCLUDE_FILL_TOKENS: frozenset[str] = frozenset(
    {"<now>", "<calculated>", "<ID>", "<SYSTEM>", "<timestamp>"}
)


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


# ── Core validation functions ────────────────────────────────────────────────


def parse_runbook_header(content: str, source: str) -> RunbookHeader:
    """Extract the seven YAML frontmatter header fields from loaded text.

    Returns a dict with keys:
        Phase, SLA-due, Updated, Hypotheses-outstanding,
        Query-budget, Replay-candidate, Same-query-reruns

    Raises ``ValueError`` when the file cannot be parsed or is missing fields.
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
    data = yaml.safe_load(frontmatter_text)

    if not isinstance(data, dict):
        raise ValueError(f"Frontmatter is not a YAML mapping in {source}")

    required_keys = {
        "Phase",
        "SLA-due",
        "Updated",
        "Hypotheses-outstanding",
        "Query-budget",
        "Replay-candidate",
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
        "Replay_candidate": str(data["Replay-candidate"]),
        "Same_query_reruns": str(data["Same-query-reruns"]),
    }


def load_runbook_header(path: Path) -> RunbookHeader:
    """Load and parse a runbook header at the validator's IO boundary."""
    return parse_runbook_header(load_text(path), str(path))


def _phase_number(fname: str) -> int:
    """Extract the zero-padded phase number from a phase filename.

    E.g. ``"phase-03-hypothesis.md"`` → ``3``.  Returns ``99`` for filenames
    that do not match the expected pattern (treated as always-required).
    """
    m = re.match(r"phase-(\d+)-", fname)
    return int(m.group(1)) if m else 99


def check_phase_files_exist(
    phase_contents: dict[str, str],
    runbook_dir: str,
    current_phase: Optional[int] = None,
) -> tuple[list[str], list[str]]:
    """Verify that required phase files exist in ``runbook_dir``.

    When ``current_phase`` is supplied, phase files through that number are
    violations when absent; later phase files are warnings when absent. This
    is the phase-aware behavior used by full and scaffold validation.

    Without ``current_phase``, preserves the legacy file-presence behavior:

    - Determine the **highest phase number** that is present on disk.
    - Absent phases with number ≤ highest_present are **violations** (holes
      in the sequence; something was unexpectedly removed).
    - Absent phases with number > highest_present are **warnings** (the
      runbook is in progress; those phases have not been written yet).

    When NO phase files are present at all, all 6 are treated as violations
    (nothing has been written; runbook is probably not initialised).

    Returns:
        (violations, warnings) — two separate lists of strings.
    """
    presence = {
        _phase_number(fname): fname in phase_contents for fname in REQUIRED_PHASE_FILES
    }

    violations: list[str] = []
    warnings: list[str] = []

    for fname in REQUIRED_PHASE_FILES:
        phase_num = _phase_number(fname)
        if presence[phase_num]:
            continue  # file is present — no issue
        if current_phase is not None and phase_num <= current_phase:
            violations.append(
                f"MISSING-PHASE: {fname} not found in {runbook_dir}"
            )
        elif current_phase is not None:
            warnings.append(
                f"INCOMPLETE-RUNBOOK: {fname} not yet written "
                f"(current phase: {current_phase:02d})"
            )
        else:
            highest_present = max(
                (n for n, exists in presence.items() if exists), default=0
            )
            if phase_num <= highest_present:
                violations.append(
                    f"MISSING-PHASE: {fname} not found in {runbook_dir}"
                )
            else:
                warnings.append(
                    f"INCOMPLETE-RUNBOOK: {fname} not yet written "
                    f"(highest written phase: {highest_present:02d})"
                )

    return violations, warnings


def check_single_phase_file_exists(
    phase_contents: dict[str, str], phase_num: int
) -> Optional[str]:
    """Return the filename for phase ``phase_num`` in ``runbook_dir``.

    Returns the matched filename string when the file is found, or ``None``
    when no matching phase file exists (the file has not been written yet).
    """
    for fname in REQUIRED_PHASE_FILES:
        if _phase_number(fname) == phase_num and fname in phase_contents:
            return fname
    return None


_FILL_TOKEN_RE = re.compile(r"<[^>]+>")


def _check_phase_body_fill_markers(
    content: str, fname: str
) -> list[tuple[str, str]]:
    """Scan phase file content for unfilled ``<...>`` placeholder tokens.

    Any ``<token>`` NOT in ``EXCLUDE_FILL_TOKENS`` is treated as an unfilled
    data placeholder left over from the scaffold template.

    Accepts already-read file content (no IO performed here).
    Returns a list of ``(filename, "UNFILLED-TOKEN: <tok>")`` tuples.
    """
    findings: list[tuple[str, str]] = []
    for line in content.splitlines():
        for tok in _FILL_TOKEN_RE.findall(line):
            if tok not in EXCLUDE_FILL_TOKENS:
                findings.append((fname, f"UNFILLED-TOKEN: {tok}"))
    return findings


def _check_phase_file_sections(
    content: str,
    fname: str,
    include_fill_tokens: bool = True,
) -> list[tuple[str, str]]:
    """Check a single phase file for required headings, blockquote labels,
    and, when requested, unfilled scaffold placeholder tokens.

    Returns a list of ``(filename, missing_item)`` tuples for each missing
    item.  Empty list means the file is structurally complete.

    The caller supplies already-loaded content. The in-memory content is passed
    to ``_check_phase_body_fill_markers`` so no second read is performed.
    """
    findings: list[tuple[str, str]] = []
    h2_re = re.compile(r"^##\s+(.+)$")
    blockquote_label_re = re.compile(r"^>\s+\*\*(\w[\w\s-]*):\*\*")

    lines = content.splitlines()

    h2_present: set[str] = set()
    labels_present: set[str] = set()

    for line in lines:
        h2_match = h2_re.match(line)
        if h2_match:
            h2_present.add(h2_match.group(1).strip())

        bq_match = blockquote_label_re.match(line)
        if bq_match:
            labels_present.add(bq_match.group(1).strip())

    for section in REQUIRED_PHASE_SECTIONS:
        if section not in h2_present:
            findings.append((fname, f"## {section}"))

    for label in REQUIRED_BLOCKQUOTE_LABELS:
        if label not in labels_present:
            findings.append((fname, f"**{label}:**"))

    if include_fill_tokens:
        findings.extend(_check_phase_body_fill_markers(content, fname))

    return findings


def check_phase_files_have_required_sections(
    phase_contents: dict[str, str],
    fill_token_phase_limit: Optional[int] = None,
) -> list[tuple[str, str]]:
    """Validate required structure in every present phase file.

    Fill-token checks apply to every present phase by default. When
    ``fill_token_phase_limit`` is supplied, they apply only through that phase;
    all later present phase files still receive structural checks.

    Phase files that do not yet exist are silently skipped — absence is
    handled by ``check_phase_files_exist``.
    """
    findings: list[tuple[str, str]] = []

    for fname in REQUIRED_PHASE_FILES:
        content = phase_contents.get(fname)
        if content is None:
            continue  # missing-file check handled by check_phase_files_exist
        include_fill_tokens = (
            fill_token_phase_limit is None
            or _phase_number(fname) <= fill_token_phase_limit
        )
        findings.extend(
            _check_phase_file_sections(content, fname, include_fill_tokens)
        )

    return findings


def check_single_phase_sections(
    phase_contents: dict[str, str], phase_num: int
) -> list[tuple[str, str]]:
    """Check the required sections for the single phase file matching ``phase_num``.

    Returns a list of ``(filename, missing_item)`` tuples.  Empty list means
    the phase file is structurally complete.  The caller must confirm the
    file exists before calling (see ``check_single_phase_file_exists``).
    """
    findings: list[tuple[str, str]] = []
    for fname in REQUIRED_PHASE_FILES:
        if _phase_number(fname) == phase_num:
            content = phase_contents.get(fname)
            if content is not None:
                findings.extend(_check_phase_file_sections(content, fname))
    return findings


def load_phase_file_contents(runbook_dir: Path) -> dict[str, str]:
    """Load every present required phase file at the validator's IO boundary."""
    return {
        fname: load_text(runbook_dir / fname)
        for fname in REQUIRED_PHASE_FILES
        if (runbook_dir / fname).is_file()
    }


def check_replay_candidate(header: RunbookHeader) -> list[str]:
    """Check that ``Replay-candidate`` is one of the allowed enum values.

    Returns a list of violation strings.  Empty list means the value is valid.

    Violations:
        REPLAY-1: value not in ALLOWED_REPLAY_CANDIDATE_VALUES
    """
    value = header["Replay_candidate"].strip()
    if value not in ALLOWED_REPLAY_CANDIDATE_VALUES:
        allowed = ", ".join(sorted(ALLOWED_REPLAY_CANDIDATE_VALUES))
        return [
            f"REPLAY-1: Replay-candidate value {value!r} not in allowed set "
            f"({allowed})"
        ]
    return []


def check_kill_switches(header: RunbookHeader) -> list[str]:
    """Check kill-switch counters in the parsed header dict.

    Returns a list of violation strings.  Empty list means no kill-switch
    is tripped.

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


def check_sla_clock(header: RunbookHeader) -> Optional[str]:
    """Warn when the SLA time remaining is below ``SLA_WARN_PCT`` of the window.

    Returns a warning string when the threshold is breached, ``None`` otherwise.
    Skips the check silently when SLA-due or Updated are placeholder values.
    """
    sla_due = _parse_iso_datetime(header["SLA_due"])
    updated = _parse_iso_datetime(header["Updated"])

    if sla_due is None or updated is None:
        return None  # placeholder values — template not yet filled

    now = datetime.now()
    # Make naive datetimes comparable
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


def check_concurrent_session(header: RunbookHeader) -> Optional[str]:
    """Warn when ``Updated`` was written less than 10 minutes ago.

    This is a non-blocking safety warning: another agent session may
    still be active on the same runbook.  Returns a warning string when the
    condition is met, ``None`` otherwise.

    Skips silently when ``Updated`` is a placeholder value.
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


def _parse_current_phase(header: RunbookHeader) -> Optional[int]:
    """Parse the ``Phase`` field from the runbook header into an integer.

    Returns ``None`` when the value is a placeholder (e.g. ``"<fill>"``).
    """
    raw = header["Phase"].strip().lstrip("0") or "0"
    try:
        return int(raw)
    except ValueError:
        return None


def _validate_header_phase(current_phase: Optional[int]) -> Optional[str]:
    """Return a violation when ``Phase`` is not one of the six runbook phases."""
    if current_phase is None or not 1 <= current_phase <= len(REQUIRED_PHASE_FILES):
        return "PHASE-ERROR: Phase must be an integer from 01 through 06"
    return None


def validate(runbook_dir: str) -> int:
    """Run all checks on ``runbook_dir`` (full-runbook mode).

    Prints violations to stderr and warnings to stderr with ``WARN:`` prefix.
    Emits a phase-by-phase status table to stdout on success.
    Returns 0 if all checks pass, 1 if violations found.
    Warnings (e.g. incomplete runbook, SLA, concurrent session) do NOT affect
    the exit code.
    """
    violations: list[str] = []
    warnings: list[str] = []

    runbook_path = Path(runbook_dir) / "runbook.md"

    # -- Parse header ---------------------------------------------------------
    try:
        header = load_runbook_header(runbook_path)
    except (OSError, ValueError) as exc:
        print(f"HEADER-ERROR: {exc}", file=sys.stderr)
        return 1

    current_phase = _parse_current_phase(header)
    phase_error = _validate_header_phase(current_phase)
    if phase_error:
        violations.append(phase_error)

    # -- Phase files exist and phase-aware body checks ------------------------
    phase_contents = load_phase_file_contents(Path(runbook_dir))
    if phase_error is None:
        phase_violations, phase_warnings = check_phase_files_exist(
            phase_contents, runbook_dir, current_phase
        )
        violations.extend(phase_violations)
        warnings.extend(phase_warnings)

    for fname, item in check_phase_files_have_required_sections(
        phase_contents,
        fill_token_phase_limit=current_phase if phase_error is None else 0,
    ):
        if item.startswith("UNFILLED-TOKEN:"):
            violations.append(f"{item} in {fname}")
        else:
            violations.append(f"MISSING-SECTION: {fname} is missing {item}")

    # -- Replay-candidate enum ------------------------------------------------
    violations.extend(check_replay_candidate(header))

    # -- Kill switches --------------------------------------------------------
    violations.extend(check_kill_switches(header))

    # -- SLA clock ------------------------------------------------------------
    sla_warn = check_sla_clock(header)
    if sla_warn:
        warnings.append(sla_warn)

    # -- Concurrent session ---------------------------------------------------
    concurrent_warn = check_concurrent_session(header)
    if concurrent_warn:
        warnings.append(concurrent_warn)

    # -- Report ---------------------------------------------------------------
    for w in warnings:
        print(f"WARN: {w}", file=sys.stderr)

    if violations:
        for v in violations:
            print(v, file=sys.stderr)
        return 1

    # -- Phase status table (on success) --------------------------------------
    base = Path(runbook_dir)
    print(f"\nRunbook: {runbook_dir}  Phase: {header['Phase']}\n")
    print(f"{'Phase file':<35} {'Status'}")
    print("-" * 45)
    for fname in REQUIRED_PHASE_FILES:
        status = "ok" if fname in phase_contents else "absent (not yet written)"
        print(f"  {fname:<33} {status}")
    print()

    return 0


def validate_scaffold(runbook_dir: str) -> int:
    """Validate a freshly copied six-phase scaffold without body fill tokens."""
    violations: list[str] = []
    warnings: list[str] = []
    runbook_path = Path(runbook_dir) / "runbook.md"

    try:
        header = load_runbook_header(runbook_path)
    except (OSError, ValueError) as exc:
        print(f"HEADER-ERROR: {exc}", file=sys.stderr)
        return 1

    current_phase = _parse_current_phase(header)
    phase_error = _validate_header_phase(current_phase)
    if phase_error:
        violations.append(phase_error)

    phase_violations, phase_warnings = check_phase_files_exist(
        load_phase_file_contents(Path(runbook_dir)),
        runbook_dir,
        len(REQUIRED_PHASE_FILES),
    )
    violations.extend(phase_violations)
    warnings.extend(phase_warnings)

    for fname, item in check_phase_files_have_required_sections(
        load_phase_file_contents(Path(runbook_dir)), fill_token_phase_limit=0
    ):
        violations.append(f"MISSING-SECTION: {fname} is missing {item}")

    violations.extend(check_replay_candidate(header))
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

    print(f"ok  scaffold: {runbook_dir}")
    return 0


def validate_phase(runbook_dir: str, phase_num: int) -> int:
    """Validate a single phase file in ``runbook_dir``.

    Checks:
    - ``runbook.md`` header can be parsed (required).
    - The phase file for ``phase_num`` exists; if absent, exits 1 with a clear
      "phase NN not yet written" message (not a schema error).
    - The phase file has all required sections and blockquote labels.
    - Kill-switch budgets pass.

    Returns 0 if all checks pass, 1 if violations found.
    """
    violations: list[str] = []
    warnings: list[str] = []

    runbook_path = Path(runbook_dir) / "runbook.md"

    # -- Parse header ---------------------------------------------------------
    try:
        header = load_runbook_header(runbook_path)
    except (OSError, ValueError) as exc:
        print(f"HEADER-ERROR: {exc}", file=sys.stderr)
        return 1

    phase_error = _validate_header_phase(_parse_current_phase(header))
    if phase_error:
        violations.append(phase_error)

    # -- Single phase file exists? --------------------------------------------
    phase_contents = load_phase_file_contents(Path(runbook_dir))
    fname = check_single_phase_file_exists(phase_contents, phase_num)
    if fname is None:
        # Find the expected filename for a clearer message
        expected = next(
            (f for f in REQUIRED_PHASE_FILES if _phase_number(f) == phase_num),
            f"phase-{phase_num:02d}-*.md",
        )
        print(
            f"PHASE-NOT-WRITTEN: phase {phase_num:02d} ({expected}) "
            f"not yet written in {runbook_dir}",
            file=sys.stderr,
        )
        return 1

    # -- Phase file sections and fill-marker scan ----------------------------
    for _fname, item in check_single_phase_sections(phase_contents, phase_num):
        if item.startswith("UNFILLED-TOKEN:"):
            violations.append(f"{item} in {_fname}")
        else:
            violations.append(f"MISSING-SECTION: {_fname} is missing {item}")

    # -- Replay-candidate enum ------------------------------------------------
    violations.extend(check_replay_candidate(header))

    # -- Kill switches --------------------------------------------------------
    violations.extend(check_kill_switches(header))

    # -- SLA clock (warning only) ---------------------------------------------
    sla_warn = check_sla_clock(header)
    if sla_warn:
        warnings.append(sla_warn)

    # -- Concurrent session (warning only) ------------------------------------
    concurrent_warn = check_concurrent_session(header)
    if concurrent_warn:
        warnings.append(concurrent_warn)

    # -- Report ---------------------------------------------------------------
    for w in warnings:
        print(f"WARN: {w}", file=sys.stderr)

    if violations:
        for v in violations:
            print(v, file=sys.stderr)
        return 1

    print(
        f"ok  phase {phase_num:02d} ({fname})  [runbook: {runbook_dir}]"
    )
    return 0


# ── Ledger-sync helpers ──────────────────────────────────────────────────────

_LEDGER_SYNC_WINDOW_SECONDS: int = 300  # 5 minutes


def parse_completed_phases(content: str) -> list[str]:
    """Return filenames of phases marked ✅ in the ## Phase index table.

    Scans the ``## Phase index`` table rows in ``runbook.md`` for the ✅ status
    character.  Returns a list of phase filenames (e.g. ``["phase-01-triage.md",
    "phase-02-priorart.md"]``).  Returns an empty list when no phases are
    marked completed or the table is absent.

    Receives already-loaded ``runbook.md`` text and performs no file IO.
    """
    lines = content.splitlines()

    in_phase_index: bool = False
    completed: list[str] = []

    for line in lines:
        if re.match(r"^##\s+Phase index", line):
            in_phase_index = True
            continue
        if in_phase_index:
            # Stop at next ## heading
            if re.match(r"^##", line):
                break
            # Table row containing ✅ and a backtick-quoted phase filename
            if "✅" in line:
                fname_match = re.search(r"`(phase-\d{2}-[^`]+\.md)`", line)
                if fname_match:
                    completed.append(fname_match.group(1))

    return completed


def load_ledger_sync_snapshot(
    runbook_dir: Path, runbook_md_path: Path
) -> Optional[LedgerSyncSnapshot]:
    """Load ticket and completed-phase mtimes for a ledger-sync comparison."""
    ticket_files = list(runbook_dir.parent.glob("ticket_*.md"))
    if not ticket_files:
        return None

    ticket_file = ticket_files[0]
    phase_mtimes: dict[str, float] = {}
    for fname in parse_completed_phases(load_text(runbook_md_path)):
        phase_path = runbook_dir / fname
        if phase_path.is_file():
            phase_mtimes[fname] = os.path.getmtime(phase_path)

    return {
        "ticket_file_name": ticket_file.name,
        "ticket_mtime": os.path.getmtime(ticket_file),
        "phase_mtimes": phase_mtimes,
    }


def evaluate_ledger_sync(snapshot: LedgerSyncSnapshot) -> tuple[int, str]:
    """Evaluate loaded ledger-sync filesystem values without performing IO.

    Returns a ``(exit_code, message)`` tuple:

    - ``(0, "Ledger sync OK: ...")`` — all completed phase files within window.
    - ``(1, "LEDGER-DRIFT: ...")``   — at least one phase file mtime exceeds
      ticket mtime by more than ``_LEDGER_SYNC_WINDOW_SECONDS``.
    - ``(2, "LEDGER-CHECK-SKIPPED: ...")`` — ``ticket_<ID>.md`` not found at
      expected path (cannot perform comparison).

    The snapshot is loaded by ``load_ledger_sync_snapshot`` before this pure
    comparison function runs.
    """
    if not snapshot["phase_mtimes"]:
        return (
            0,
            "Ledger sync OK: no completed phases (✅) found in Phase index — nothing to check.",
        )

    ticket_mtime = snapshot["ticket_mtime"]
    ticket_ts: str = datetime.fromtimestamp(ticket_mtime).strftime("%Y-%m-%dT%H:%M")

    drift_lines: list[str] = []
    for fname, phase_mtime in snapshot["phase_mtimes"].items():
        delta: float = phase_mtime - ticket_mtime
        if delta > _LEDGER_SYNC_WINDOW_SECONDS:
            phase_ts: str = datetime.fromtimestamp(phase_mtime).strftime(
                "%Y-%m-%dT%H:%M"
            )
            drift_lines.append(
                f"LEDGER-DRIFT: {fname} modified {phase_ts} but "
                f"{snapshot['ticket_file_name']} last sync {ticket_ts}\n"
                f"  -> Cipher dispatched Ledger only at close-out; "
                f"per-phase rule violated. See AGENTS.md, Cipher Hard Rules."
            )

    if drift_lines:
        return (1, "\n".join(drift_lines))

    return (
        0,
        "Ledger sync OK: all phase files sync'd within 5 min of "
        f"{snapshot['ticket_file_name']}.",
    )


def check_ledger_sync(runbook_dir: str, runbook_md_path: str) -> tuple[int, str]:
    """Load and check ledger synchronization without changing exit meanings."""
    snapshot = load_ledger_sync_snapshot(Path(runbook_dir), Path(runbook_md_path))
    if snapshot is None:
        return (
            2,
            "LEDGER-CHECK-SKIPPED: ticket_<ID>.md not found at "
            f"{Path(runbook_dir).parent}",
        )
    return evaluate_ledger_sync(snapshot)


# ── CLI entry point ──────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a runbook directory against the 7-field schema "
            "and phase-file structure.\n\n"
            "Default: validate completed phases through the header Phase value.\n"
            "With --scaffold: structural-only validation of all six copied phases.\n"
            "With --phase NN: strict validation of only that phase file + header."
        ),
        epilog="Exit code 0 = pass, 1 = fail.  Warnings do not affect exit code.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "runbook_dir",
        help="Path to the runbook directory (contains runbook.md + phase-NN-*.md files)",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--phase",
        metavar="NN",
        type=int,
        default=None,
        help=(
            "Validate only the specified phase file (e.g. --phase 03 checks "
            "phase-03-hypothesis.md + runbook.md header).  If the phase file "
            "does not yet exist, exits 1 with a clear message."
        ),
    )
    mode.add_argument(
        "--scaffold",
        action="store_true",
        default=False,
        help=(
            "Validate a freshly copied scaffold: require all six phase files and "
            "their structure, but ignore phase-body fill tokens."
        ),
    )
    mode.add_argument(
        "--require-ledger-sync",
        action="store_true",
        default=False,
        help=(
            "Check that each completed phase (✅ in Phase index) was synced within "
            "5 minutes of ticket_<ID>.md mtime. Exit 1 on drift, 2 if ticket file "
            "not found. Default behavior is unchanged when this flag is absent."
        ),
    )
    return parser


if __name__ == "__main__":
    args = _build_parser().parse_args()
    if args.require_ledger_sync:
        runbook_md = str(Path(args.runbook_dir) / "runbook.md")
        exit_code, message = check_ledger_sync(args.runbook_dir, runbook_md)
        if exit_code == 0:
            print(message)
        else:
            print(message)
        sys.exit(exit_code)
    elif args.phase is not None:
        sys.exit(validate_phase(args.runbook_dir, args.phase))
    elif args.scaffold:
        sys.exit(validate_scaffold(args.runbook_dir))
    else:
        sys.exit(validate(args.runbook_dir))
