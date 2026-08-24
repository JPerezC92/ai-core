"""Tests for validate_runbook.py — proves it catches each violation class and
validates well-formed, phase-aware runbooks.

Run: uv run --locked --project .opencode/skills/ticket-runbook python .opencode/skills/ticket-runbook/scripts/test_validate_runbook.py
"""

import os
import shutil
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from typing import TypedDict

sys.path.insert(0, str(Path(__file__).parent))
import validate_runbook as vr  # noqa: E402


REQUIRED_PHASE_FILES = [
    "phase-01-triage.md",
    "phase-02-priorart.md",
    "phase-03-hypothesis.md",
    "phase-04-validate.md",
    "phase-05-synthesis.md",
    "phase-06-respond.md",
]

_DATETIME_FMT = "%Y-%m-%dT%H:%M"
TEMPLATE_RUNBOOK_DIR = Path(__file__).parents[1] / "references" / "runbook"

RunbookHeaderUpdates = TypedDict(
    "RunbookHeaderUpdates",
    {
        "Phase": str,
        "SLA-due": str,
        "Updated": str,
        "Hypotheses-outstanding": str,
        "Query-budget": str,
        "Replay-candidate": str,
        "Same-query-reruns": str,
    },
    total=False,
)


def _filled_phase(fname: str) -> str:
    return (
        f"# {fname}\n\n"
        "> **Owner:** Investigator\n"
        "> **Pre:** none\n"
        "> **Reads:** none\n"
        "> **Writes:** none\n\n"
        "## Steps\n\n1. step one\n\n"
        "## Output\n\n- **Artifact:** filled output\n\n"
        "## Gate\n\n- \u2b1c done\n\n"
        "## Abort conditions\n\n- halt if broken\n"
    )


def _runbook_md(phase: str = "02", completed: list[str] | None = None) -> str:
    phase_rows = [
        ("01", "phase-01-triage.md", "Cipher"),
        ("02", "phase-02-priorart.md", "Investigator"),
        ("03", "phase-03-hypothesis.md", "Investigator"),
        ("04", "phase-04-validate.md", "Investigator"),
        ("05", "phase-05-synthesis.md", "Cipher"),
        ("06", "phase-06-respond.md", "Quill"),
    ]
    completed = completed or []
    rows = ""
    for num, fname, owner in phase_rows:
        status = "✅" if fname in completed else "⬜"
        rows += f"| {num} | `{fname}` | {owner} | {status} |\n"

    return (
        "---\n"
        f'Phase: "{phase}"\n'
        'SLA-due: "2099-01-01T00:00"\n'
        'Updated: "2099-01-01T00:00"\n'
        'Hypotheses-outstanding: "0/3"\n'
        'Query-budget: "0/6"\n'
        'Replay-candidate: "pending"\n'
        'Same-query-reruns: "0/2"\n'
        "---\n\n"
        "# Runbook — Fixture\n\n"
        "## Phase index\n\n"
        "| Phase | File | Owner | Status |\n"
        "|---|---|---|---|\n"
        + rows
    )


def _make_runbook(d: str, phase_files: list[str] | None = None) -> Path:
    runbook_dir = Path(d) / "runbook"
    runbook_dir.mkdir()
    (runbook_dir / "runbook.md").write_text(_runbook_md(), encoding="utf-8")
    for fname in (phase_files if phase_files is not None else REQUIRED_PHASE_FILES):
        (runbook_dir / fname).write_text(_filled_phase(fname), encoding="utf-8")
    return runbook_dir


def _patch_header(runbook_dir: Path, updates: RunbookHeaderUpdates) -> None:
    """Replace existing quoted frontmatter fields using constrained text edits."""
    runbook_md = runbook_dir / "runbook.md"
    content = runbook_md.read_text(encoding="utf-8")
    for field, value in updates.items():
        pattern = rf"(?m)^{field}: \"[^\n]*\"$"
        replacement = f'{field}: "{value}"'
        content, replacements = __import__("re").subn(
            pattern, replacement, content, count=1
        )
        assert replacements == 1, f"runbook.md has no quoted {field} field"
    runbook_md.write_text(content, encoding="utf-8")


def _copy_initialized_scaffold(d: str) -> Path:
    runbook_dir = Path(d) / "runbook"
    shutil.copytree(TEMPLATE_RUNBOOK_DIR, runbook_dir)
    updates: RunbookHeaderUpdates = {
        "Phase": "01",
        "SLA-due": "2099-01-01T00:00",
        "Updated": "2000-01-01T00:00",
        "Hypotheses-outstanding": "0/3",
        "Query-budget": "0/6",
        "Replay-candidate": "pending",
        "Same-query-reruns": "0/2",
    }
    _patch_header(runbook_dir, updates)
    phase_one = runbook_dir / "phase-01-triage.md"
    content = phase_one.read_text(encoding="utf-8")
    content = content.replace(
        "> **Pre:** Ticket ID available; ticket-read tool authenticated.",
        "> **Pre:** Ticket 999999 available; ticket-read tool authenticated.",
    )
    phase_one.write_text(content, encoding="utf-8")
    return runbook_dir


def _fill_template_phase_one(runbook_dir: Path) -> None:
    phase_one = runbook_dir / "phase-01-triage.md"
    content = phase_one.read_text(encoding="utf-8")
    for token, value in {
        "<fill>": "fixture value",
        "<class-ref>": "fixture-class",
        "<agent(s)>": "Investigator",
    }.items():
        content = content.replace(token, value)
    phase_one.write_text(content, encoding="utf-8")


class ValidateRunbookTests(unittest.TestCase):
    def test_copied_scaffold_passes_scaffold_validation(self):
        with tempfile.TemporaryDirectory() as d:
            runbook_dir = _copy_initialized_scaffold(d)
            self.assertEqual(vr.validate_scaffold(str(runbook_dir)), 0)

    def test_copied_scaffold_rejects_malformed_phase(self):
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as d:
            runbook_dir = _copy_initialized_scaffold(d)
            _patch_header(runbook_dir, {"Phase": "not-a-phase"})
            scaffold_stderr = io.StringIO()
            with contextlib.redirect_stderr(scaffold_stderr):
                scaffold_result = vr.validate_scaffold(str(runbook_dir))

            self.assertEqual(scaffold_result, 1)
            self.assertEqual(
                scaffold_stderr.getvalue(),
                "PHASE-ERROR: Phase must be an integer from 01 through 06\n",
            )
            _fill_template_phase_one(runbook_dir)
            phase_stderr = io.StringIO()
            with contextlib.redirect_stderr(phase_stderr):
                phase_result = vr.validate_phase(str(runbook_dir), phase_num=1)

            self.assertEqual(phase_result, 1)
            self.assertEqual(
                phase_stderr.getvalue(),
                "PHASE-ERROR: Phase must be an integer from 01 through 06\n",
            )

    def test_copied_scaffold_rejects_out_of_range_phase(self):
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as d:
            runbook_dir = _copy_initialized_scaffold(d)
            _patch_header(runbook_dir, {"Phase": "07"})
            scaffold_stderr = io.StringIO()
            with contextlib.redirect_stderr(scaffold_stderr):
                scaffold_result = vr.validate_scaffold(str(runbook_dir))

            self.assertEqual(scaffold_result, 1)
            self.assertEqual(
                scaffold_stderr.getvalue(),
                "PHASE-ERROR: Phase must be an integer from 01 through 06\n",
            )
            _fill_template_phase_one(runbook_dir)
            phase_stderr = io.StringIO()
            with contextlib.redirect_stderr(phase_stderr):
                phase_result = vr.validate_phase(str(runbook_dir), phase_num=1)

            self.assertEqual(phase_result, 1)
            self.assertEqual(
                phase_stderr.getvalue(),
                "PHASE-ERROR: Phase must be an integer from 01 through 06\n",
            )

    def test_default_ignores_future_template_tokens(self):
        with tempfile.TemporaryDirectory() as d:
            runbook_dir = _copy_initialized_scaffold(d)
            _fill_template_phase_one(runbook_dir)
            self.assertEqual(vr.validate(str(runbook_dir)), 0)

    def test_default_rejects_structural_defect_in_present_future_phase(self):
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as d:
            runbook_dir = _copy_initialized_scaffold(d)
            _fill_template_phase_one(runbook_dir)
            phase_two = runbook_dir / "phase-02-priorart.md"
            phase_two.write_text(
                phase_two.read_text(encoding="utf-8").replace(
                    "## Gate", "## Requirements", 1
                ),
                encoding="utf-8",
            )
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                result = vr.validate(str(runbook_dir))

            self.assertEqual(result, 1)
            self.assertEqual(
                stderr.getvalue(),
                "MISSING-SECTION: phase-02-priorart.md is missing ## Gate\n",
            )

    def test_completed_phase_token_fails_default_and_strict_validation(self):
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as d:
            runbook_dir = _copy_initialized_scaffold(d)
            _fill_template_phase_one(runbook_dir)
            phase_one = runbook_dir / "phase-01-triage.md"
            phase_one.write_text(
                phase_one.read_text(encoding="utf-8") + "\n<unfilled-completed>\n",
                encoding="utf-8",
            )
            default_stderr = io.StringIO()
            with contextlib.redirect_stderr(default_stderr):
                default_result = vr.validate(str(runbook_dir))

            self.assertEqual(default_result, 1)
            self.assertEqual(
                default_stderr.getvalue(),
                "UNFILLED-TOKEN: <unfilled-completed> in phase-01-triage.md\n",
            )
            phase_stderr = io.StringIO()
            with contextlib.redirect_stderr(phase_stderr):
                phase_result = vr.validate_phase(str(runbook_dir), phase_num=1)

            self.assertEqual(phase_result, 1)
            self.assertEqual(
                phase_stderr.getvalue(),
                "UNFILLED-TOKEN: <unfilled-completed> in phase-01-triage.md\n",
            )

    def test_valid_runbook_passes(self):
        with tempfile.TemporaryDirectory() as d:
            runbook_dir = _make_runbook(d)
            self.assertEqual(vr.validate(str(runbook_dir)), 0)

    def test_hypothesis_cap_violation(self):
        with tempfile.TemporaryDirectory() as d:
            runbook_dir = _make_runbook(d)
            _patch_header(runbook_dir, {"Hypotheses-outstanding": f"{vr.KILL_MAX_HYPOTHESES + 1}/{vr.KILL_MAX_HYPOTHESES}"})
            header = vr.load_runbook_header(runbook_dir / "runbook.md")
            self.assertEqual(
                vr.check_kill_switches(header),
                ["KILL-1: hypothesis cap exceeded (4 > 3)"],
            )

    def test_query_budget_violation(self):
        with tempfile.TemporaryDirectory() as d:
            runbook_dir = _make_runbook(d)
            _patch_header(runbook_dir, {"Query-budget": f"{vr.KILL_MAX_QUERIES + 1}/{vr.KILL_MAX_QUERIES}"})
            header = vr.load_runbook_header(runbook_dir / "runbook.md")
            self.assertEqual(
                vr.check_kill_switches(header),
                ["KILL-2: query budget exhausted (7 > 6)"],
            )

    def test_rerun_violation(self):
        with tempfile.TemporaryDirectory() as d:
            runbook_dir = _make_runbook(d)
            _patch_header(runbook_dir, {"Same-query-reruns": f"{vr.KILL_MAX_RERUNS + 1}/{vr.KILL_MAX_RERUNS}"})
            header = vr.load_runbook_header(runbook_dir / "runbook.md")
            self.assertEqual(
                vr.check_kill_switches(header),
                ["KILL-3: re-run cap exceeded (3 > 2)"],
            )

    def test_replay_candidate_invalid_enum(self):
        with tempfile.TemporaryDirectory() as d:
            runbook_dir = _make_runbook(d)
            _patch_header(runbook_dir, {"Replay-candidate": "bogus"})
            header = vr.load_runbook_header(runbook_dir / "runbook.md")
            self.assertEqual(
                vr.check_replay_candidate(header),
                [
                    "REPLAY-1: Replay-candidate value 'bogus' not in allowed set "
                    "(no, pending, structural, yes)"
                ],
            )

    def test_missing_phase_file(self):
        with tempfile.TemporaryDirectory() as d:
            runbook_dir = _make_runbook(d)
            (runbook_dir / "phase-03-hypothesis.md").unlink()
            violations, warnings = vr.check_phase_files_exist(
                vr.load_phase_file_contents(runbook_dir), str(runbook_dir)
            )
            self.assertEqual(
                violations,
                [
                    "MISSING-PHASE: phase-03-hypothesis.md not found in "
                    f"{runbook_dir}"
                ],
            )
            self.assertEqual(warnings, [])

    def test_missing_section_in_phase_file(self):
        with tempfile.TemporaryDirectory() as d:
            runbook_dir = _make_runbook(d)
            p = runbook_dir / "phase-04-validate.md"
            p.write_text(p.read_text(encoding="utf-8").replace("## Gate", "## Not Gate"), encoding="utf-8")
            findings = vr.check_phase_files_have_required_sections(
                vr.load_phase_file_contents(runbook_dir)
            )
            self.assertEqual(findings, [("phase-04-validate.md", "## Gate")])

    def test_unfilled_token_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            runbook_dir = _make_runbook(d)
            p = runbook_dir / "phase-01-triage.md"
            p.write_text(p.read_text(encoding="utf-8") + "\n<fill>\n", encoding="utf-8")
            findings = vr.check_phase_files_have_required_sections(
                vr.load_phase_file_contents(runbook_dir)
            )
            self.assertEqual(
                findings,
                [("phase-01-triage.md", "UNFILLED-TOKEN: <fill>")],
            )

    def test_concurrent_session_warning(self):
        with tempfile.TemporaryDirectory() as d:
            runbook_dir = _make_runbook(d)
            five_min_ago = datetime.now() - timedelta(minutes=5)
            _patch_header(runbook_dir, {"Updated": five_min_ago.strftime(_DATETIME_FMT)})
            header = vr.load_runbook_header(runbook_dir / "runbook.md")
            warning = vr.check_concurrent_session(header)
            self.assertIsNotNone(warning)
            self.assertIn("CONCURRENT", warning)

    def test_phase_flag_on_present_phase(self):
        with tempfile.TemporaryDirectory() as d:
            runbook_dir = _make_runbook(d, REQUIRED_PHASE_FILES[:2])
            self.assertEqual(vr.validate_phase(str(runbook_dir), phase_num=2), 0)

    def test_phase_flag_on_missing_phase(self):
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as d:
            runbook_dir = _make_runbook(d, REQUIRED_PHASE_FILES[:3])
            buf = io.StringIO()
            with contextlib.redirect_stderr(buf):
                result = vr.validate_phase(str(runbook_dir), phase_num=4)
            self.assertEqual(result, 1)
            self.assertIn("PHASE-NOT-WRITTEN", buf.getvalue())

    def test_partial_runbook_default_passes_with_warning(self):
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as d:
            runbook_dir = _make_runbook(d, REQUIRED_PHASE_FILES[:3])
            buf = io.StringIO()
            with contextlib.redirect_stderr(buf):
                result = vr.validate(str(runbook_dir))
            self.assertEqual(result, 0)
            self.assertIn("INCOMPLETE-RUNBOOK", buf.getvalue())

    def test_ledger_sync_pass(self):
        with tempfile.TemporaryDirectory() as d:
            runbook_dir = _make_runbook(d, REQUIRED_PHASE_FILES)
            (runbook_dir / "runbook.md").write_text(_runbook_md(completed=["phase-01-triage.md", "phase-02-priorart.md"]), encoding="utf-8")
            ticket = Path(d) / "ticket_999998.md"
            ticket.write_text("fixture", encoding="utf-8")
            now = time.time()
            for f in ["phase-01-triage.md", "phase-02-priorart.md"]:
                os.utime(runbook_dir / f, (now, now))
            os.utime(ticket, (now, now))
            code, msg = vr.check_ledger_sync(str(runbook_dir), str(runbook_dir / "runbook.md"))
            self.assertEqual(code, 0)
            self.assertIn("Ledger sync OK", msg)

    def test_ledger_sync_drift(self):
        with tempfile.TemporaryDirectory() as d:
            runbook_dir = _make_runbook(d, REQUIRED_PHASE_FILES)
            (runbook_dir / "runbook.md").write_text(_runbook_md(completed=["phase-01-triage.md", "phase-02-priorart.md"]), encoding="utf-8")
            ticket = Path(d) / "ticket_999997.md"
            ticket.write_text("fixture", encoding="utf-8")
            base = time.time()
            os.utime(ticket, (base, base))
            os.utime(runbook_dir / "phase-01-triage.md", (base, base))
            os.utime(runbook_dir / "phase-02-priorart.md", (base + 1800, base + 1800))
            code, msg = vr.check_ledger_sync(str(runbook_dir), str(runbook_dir / "runbook.md"))
            self.assertEqual(code, 1)
            self.assertIn("LEDGER-DRIFT:", msg)
            self.assertIn("phase-02-priorart.md", msg)

    def test_ledger_sync_skipped_when_ticket_missing(self):
        with tempfile.TemporaryDirectory() as d:
            runbook_dir = _make_runbook(d, REQUIRED_PHASE_FILES[:1])
            (runbook_dir / "runbook.md").write_text(_runbook_md(completed=["phase-01-triage.md"]), encoding="utf-8")
            code, msg = vr.check_ledger_sync(str(runbook_dir), str(runbook_dir / "runbook.md"))
            self.assertEqual(code, 2)
            self.assertIn("LEDGER-CHECK-SKIPPED:", msg)


if __name__ == "__main__":
    unittest.main(verbosity=2)
