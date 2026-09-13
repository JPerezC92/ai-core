"""Tests for validate_runbook.py — proves it catches each violation class and
validates well-formed working analyses, register-first identification, and the
close-out collapse.

Run: python3 .opencode/skills/ticket-runbook/scripts/test_validate_runbook.py
"""

import contextlib
import io
import re
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import validate_runbook as vr  # noqa: E402


TEMPLATE_ANALYSIS_DIR = Path(__file__).parents[1] / "references" / "analysis"

STEP_FILES = [
    "01-identify.md",
    "02-investigate.md",
    "03-synthesize.md",
]

_DATETIME_FMT = "%Y-%m-%dT%H:%M"


def _state_md(
    phase: str = "synthesize",
    verdict: str = "pending",
    completed: list[str] | None = None,
) -> str:
    step_rows = [
        ("identify", "01-identify.md", "Cipher"),
        ("investigate", "02-investigate.md", "Investigator"),
        ("synthesize", "03-synthesize.md", "Cipher"),
        ("respond", "response-draft.md", "Quill"),
    ]
    completed = completed or []
    rows = ""
    for name, fname, owner in step_rows:
        status = "✅" if fname in completed else "⬜"
        rows += f"| {name} | `{fname}` | {owner} | {status} |\n"

    return (
        "---\n"
        f'Phase: "{phase}"\n'
        'SLA-due: "2099-01-01T00:00"\n'
        'Updated: "2099-01-01T00:00"\n'
        'Hypotheses-outstanding: "0/3"\n'
        'Query-budget: "0/6"\n'
        f'identification_verdict: "{verdict}"\n'
        'Same-query-reruns: "0/2"\n'
        "---\n\n"
        "# Working analysis — Fixture\n\n"
        "## Step index\n\n"
        "| Step | File | Owner | Status |\n"
        "|---|---|---|---|\n"
        + rows
    )


def _filled_step(fname: str) -> str:
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


def _make_analysis(
    d: str,
    step_files: list[str] | None = None,
    phase: str = "synthesize",
    verdict: str = "pending",
) -> Path:
    analysis_dir = Path(d) / "analysis"
    analysis_dir.mkdir()
    (analysis_dir / "state.md").write_text(
        _state_md(phase=phase, verdict=verdict), encoding="utf-8"
    )
    for fname in (step_files if step_files is not None else STEP_FILES):
        (analysis_dir / fname).write_text(_filled_step(fname), encoding="utf-8")
    return analysis_dir


def _patch_header(analysis_dir: Path, updates: dict[str, str]) -> None:
    """Replace existing quoted frontmatter fields using constrained text edits."""
    state_md = analysis_dir / "state.md"
    content = state_md.read_text(encoding="utf-8")
    for field, value in updates.items():
        pattern = rf'(?m)^{field}: "[^\n]*"$'
        replacement = f'{field}: "{value}"'
        content, replacements = re.subn(pattern, replacement, content, count=1)
        assert replacements == 1, f"state.md has no quoted {field} field"
    state_md.write_text(content, encoding="utf-8")


def _copy_initialized_scaffold(d: str) -> Path:
    analysis_dir = Path(d) / "analysis"
    shutil.copytree(TEMPLATE_ANALYSIS_DIR, analysis_dir)
    updates = {
        "Phase": "identify",
        "SLA-due": "2099-01-01T00:00",
        "Updated": "2000-01-01T00:00",
        "Hypotheses-outstanding": "0/3",
        "Query-budget": "0/6",
        "identification_verdict": "pending",
        "Same-query-reruns": "0/2",
    }
    _patch_header(analysis_dir, updates)
    return analysis_dir


def _fill_template_identify(analysis_dir: Path) -> None:
    identify = analysis_dir / "01-identify.md"
    content = identify.read_text(encoding="utf-8")
    identify.write_text(re.sub(r"<[^>]+>", "fixture", content), encoding="utf-8")


REGISTER_HEADER = (
    "| " + " | ".join(column.upper() for column in vr.REGISTER_COLUMNS) + " |"
)
REGISTER_SEP = "|" + "---|" * len(vr.REGISTER_COLUMNS)


def _row(**fields: str) -> str:
    values = [fields.get(column, "") for column in vr.REGISTER_COLUMNS]
    return "| " + " | ".join(values) + " |"


def _register(*rows: str) -> str:
    return "\n".join(["## Register", "", REGISTER_HEADER, REGISTER_SEP, *rows])


def _ticket_dir(
    d: str,
    with_working: bool = False,
    with_draft: bool = False,
    with_dirs: bool = True,
    image_exists: bool = True,
    verdict: str = "no_match",
    known: str = "[]",
) -> Path:
    ticket_dir = Path(d) / "ticket"
    ticket_dir.mkdir()
    if with_dirs:
        (ticket_dir / "screenshots").mkdir()
        (ticket_dir / "validations").mkdir()
    if with_working:
        analysis_dir = ticket_dir / "analysis"
        analysis_dir.mkdir()
        (analysis_dir / "state.md").write_text("x", encoding="utf-8")
        (analysis_dir / "01-identify.md").write_text("x", encoding="utf-8")
    if with_draft:
        (ticket_dir / "response-draft.md").write_text("x", encoding="utf-8")
    image = "screenshots/01_source_entity.png"
    if image_exists and with_dirs:
        (ticket_dir / image).write_text("x", encoding="utf-8")
    content = (
        "---\n"
        "symptom_ids: []\n"
        f"known_problem_ids: {known}\n"
        f"identification_verdict: {verdict}\n"
        "---\n\n"
        "#### Imagen1\n"
        f"- **path:** {image}\n"
    )
    (ticket_dir / "ticket_999999.md").write_text(content, encoding="utf-8")
    return ticket_dir


class ValidateRunbookTests(unittest.TestCase):
    # ── Scaffold and structure ───────────────────────────────────────────────

    def test_copied_scaffold_passes_scaffold_validation(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            analysis_dir = _copy_initialized_scaffold(d)
            self.assertEqual(vr.validate_scaffold(str(analysis_dir)), 0)

    def test_copied_scaffold_rejects_malformed_phase(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            analysis_dir = _copy_initialized_scaffold(d)
            _patch_header(analysis_dir, {"Phase": "not-a-phase"})
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                result = vr.validate_scaffold(str(analysis_dir))

            self.assertEqual(result, 1)
            self.assertEqual(
                stderr.getvalue(),
                "PHASE-ERROR: Phase value 'not-a-phase' not in allowed set "
                "(identify, investigate, synthesize)\n",
            )

    def test_copied_scaffold_rejects_missing_step(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            analysis_dir = _copy_initialized_scaffold(d)
            (analysis_dir / "02-investigate.md").unlink()
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                result = vr.validate_scaffold(str(analysis_dir))

            self.assertEqual(result, 1)
            self.assertIn(
                "MISSING-STEP: 02-investigate.md", stderr.getvalue()
            )

    def test_default_ignores_future_template_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            analysis_dir = _copy_initialized_scaffold(d)
            _fill_template_identify(analysis_dir)
            self.assertEqual(vr.validate(str(analysis_dir)), 0)

    def test_default_rejects_structural_defect_in_present_future_step(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            analysis_dir = _copy_initialized_scaffold(d)
            _fill_template_identify(analysis_dir)
            investigate = analysis_dir / "02-investigate.md"
            investigate.write_text(
                investigate.read_text(encoding="utf-8").replace(
                    "## Gate", "## Requirements", 1
                ),
                encoding="utf-8",
            )
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                result = vr.validate(str(analysis_dir))

            self.assertEqual(result, 1)
            self.assertEqual(
                stderr.getvalue(),
                "MISSING-SECTION: 02-investigate.md is missing ## Gate\n",
            )

    def test_completed_step_token_fails_default_and_strict_validation(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            analysis_dir = _copy_initialized_scaffold(d)
            _fill_template_identify(analysis_dir)
            identify = analysis_dir / "01-identify.md"
            identify.write_text(
                identify.read_text(encoding="utf-8") + "\n<unfilled-completed>\n",
                encoding="utf-8",
            )
            default_stderr = io.StringIO()
            with contextlib.redirect_stderr(default_stderr):
                default_result = vr.validate(str(analysis_dir))

            self.assertEqual(default_result, 1)
            self.assertEqual(
                default_stderr.getvalue(),
                "UNFILLED-TOKEN: <unfilled-completed> in 01-identify.md\n",
            )
            step_stderr = io.StringIO()
            with contextlib.redirect_stderr(step_stderr):
                step_result = vr.validate_step(str(analysis_dir), "identify")

            self.assertEqual(step_result, 1)
            self.assertEqual(
                step_stderr.getvalue(),
                "UNFILLED-TOKEN: <unfilled-completed> in 01-identify.md\n",
            )

    def test_valid_analysis_passes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            analysis_dir = _make_analysis(d)
            self.assertEqual(vr.validate(str(analysis_dir)), 0)

    def test_missing_step_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            analysis_dir = _make_analysis(d)
            (analysis_dir / "02-investigate.md").unlink()
            violations, warnings = vr.check_step_files_exist(
                vr.load_step_file_contents(analysis_dir), str(analysis_dir)
            )
            self.assertEqual(
                violations,
                [
                    "MISSING-STEP: 02-investigate.md not found in "
                    f"{analysis_dir}"
                ],
            )
            self.assertEqual(warnings, [])

    def test_missing_section_in_step_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            analysis_dir = _make_analysis(d)
            p = analysis_dir / "02-investigate.md"
            p.write_text(
                p.read_text(encoding="utf-8").replace(
                    "## Gate", "## Not Gate"
                ),
                encoding="utf-8",
            )
            findings = vr.check_step_files_have_required_sections(
                vr.load_step_file_contents(analysis_dir)
            )
            self.assertEqual(findings, [("02-investigate.md", "## Gate")])

    def test_unfilled_token_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            analysis_dir = _make_analysis(d)
            p = analysis_dir / "01-identify.md"
            p.write_text(
                p.read_text(encoding="utf-8") + "\n<fill>\n", encoding="utf-8"
            )
            findings = vr.check_step_files_have_required_sections(
                vr.load_step_file_contents(analysis_dir)
            )
            self.assertEqual(
                findings,
                [("01-identify.md", "UNFILLED-TOKEN: <fill>")],
            )

    # ── Header enums and budgets ─────────────────────────────────────────────

    def test_hypothesis_cap_violation(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            analysis_dir = _make_analysis(d)
            _patch_header(
                analysis_dir,
                {
                    "Hypotheses-outstanding": (
                        f"{vr.KILL_MAX_HYPOTHESES + 1}/{vr.KILL_MAX_HYPOTHESES}"
                    )
                },
            )
            header = vr.load_state_header(analysis_dir / "state.md")
            self.assertEqual(
                vr.check_kill_switches(header),
                ["KILL-1: hypothesis cap exceeded (4 > 3)"],
            )

    def test_query_budget_violation(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            analysis_dir = _make_analysis(d)
            _patch_header(
                analysis_dir,
                {
                    "Query-budget": (
                        f"{vr.KILL_MAX_QUERIES + 1}/{vr.KILL_MAX_QUERIES}"
                    )
                },
            )
            header = vr.load_state_header(analysis_dir / "state.md")
            self.assertEqual(
                vr.check_kill_switches(header),
                ["KILL-2: query budget exhausted (7 > 6)"],
            )

    def test_rerun_violation(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            analysis_dir = _make_analysis(d)
            _patch_header(
                analysis_dir,
                {
                    "Same-query-reruns": (
                        f"{vr.KILL_MAX_RERUNS + 1}/{vr.KILL_MAX_RERUNS}"
                    )
                },
            )
            header = vr.load_state_header(analysis_dir / "state.md")
            self.assertEqual(
                vr.check_kill_switches(header),
                ["KILL-3: re-run cap exceeded (3 > 2)"],
            )

    def test_identification_verdict_invalid_enum(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            analysis_dir = _make_analysis(d)
            _patch_header(
                analysis_dir, {"identification_verdict": "bogus"}
            )
            header = vr.load_state_header(analysis_dir / "state.md")
            self.assertEqual(
                vr.check_identification_verdict(header),
                [
                    "VERDICT-1: identification_verdict value 'bogus' not in "
                    "allowed set (exact, no_match, pending, structural)"
                ],
            )

    def test_phase_invalid_enum(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            analysis_dir = _make_analysis(d)
            _patch_header(analysis_dir, {"Phase": "not-a-phase"})
            header = vr.load_state_header(analysis_dir / "state.md")
            self.assertEqual(
                vr.check_phase(header),
                [
                    "PHASE-ERROR: Phase value 'not-a-phase' not in allowed set "
                    "(identify, investigate, synthesize)"
                ],
            )

    def test_concurrent_session_warning(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            analysis_dir = _make_analysis(d)
            five_min_ago = datetime.now() - timedelta(minutes=5)
            _patch_header(
                analysis_dir,
                {"Updated": five_min_ago.strftime(_DATETIME_FMT)},
            )
            header = vr.load_state_header(analysis_dir / "state.md")
            warning = vr.check_concurrent_session(header)
            self.assertIsNotNone(warning)
            self.assertIn("CONCURRENT", warning)

    # ── Step modes ───────────────────────────────────────────────────────────

    def test_step_flag_on_present_step(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            analysis_dir = _make_analysis(d, STEP_FILES)
            self.assertEqual(
                vr.validate_step(str(analysis_dir), "investigate"), 0
            )

    def test_step_flag_on_missing_step(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            analysis_dir = _make_analysis(d, STEP_FILES[:1])
            buf = io.StringIO()
            with contextlib.redirect_stderr(buf):
                result = vr.validate_step(str(analysis_dir), "synthesize")
            self.assertEqual(result, 1)
            self.assertIn("STEP-NOT-WRITTEN", buf.getvalue())

    def test_partial_analysis_default_passes_with_warning(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            analysis_dir = _make_analysis(
                d, STEP_FILES[:2], phase="investigate"
            )
            buf = io.StringIO()
            with contextlib.redirect_stderr(buf):
                result = vr.validate(str(analysis_dir))
            self.assertEqual(result, 0)
            self.assertIn("INCOMPLETE-ANALYSIS", buf.getvalue())

    # ── Register-first identification ────────────────────────────────────────

    def test_parse_problem_register_empty(self) -> None:
        content = (
            "## Register\n\n"
            "| ID | Date | Team | Symptom | System | Module | Problem | "
            "Discriminators | Exclusions | Evidence | Root cause | Lifecycle | "
            "Allow_exact | Status |\n"
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n\n"
            "(no entries yet)"
        )
        self.assertEqual(vr.parse_problem_register(content), [])

    def test_parse_problem_register_rows(self) -> None:
        row = _row(
            id="P-001",
            date="2026-01-01",
            team="incident",
            symptom="S-05, S-07",
            system="sys",
            module="mod",
            problem="slow CDN",
            discriminators="host=cdn-a",
            exclusions="host=cdn-b",
            evidence="log:42",
            root_cause="cache miss",
            lifecycle="candidate",
            allow_exact="no",
            status="open",
        )
        rows = vr.parse_problem_register(_register(row))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id"], "P-001")
        self.assertEqual(rows[0]["team"], "incident")
        self.assertEqual(rows[0]["symptom"], "S-05, S-07")
        self.assertEqual(rows[0]["lifecycle"], "candidate")
        self.assertEqual(rows[0]["allow_exact"], "no")

    def test_register_schema_rejects_bad_lifecycle(self) -> None:
        row = _row(
            id="P-001",
            date="2026-01-01",
            team="incident",
            symptom="S-05",
            lifecycle="bogus",
            allow_exact="no",
            status="open",
        )
        violations = vr.check_register_rows(_register(row))
        self.assertTrue(
            any("REGISTER-3" in item for item in violations), violations
        )

    def test_register_schema_rejects_bad_column_count(self) -> None:
        content = "## Register\n\n| P-001 | 2026-01-01 | incident |\n"
        violations = vr.check_register_rows(content)
        self.assertTrue(
            any("REGISTER-1" in item for item in violations), violations
        )

    def test_empty_register_verdict_no_match_ok(self) -> None:
        self.assertEqual(
            vr.check_identification_consistency("no_match", [], []), []
        )

    def test_empty_register_verdict_exact_rejected(self) -> None:
        violations = vr.check_identification_consistency(
            "exact", ["P-001"], []
        )
        self.assertTrue(
            any("VERDICT-4" in item for item in violations), violations
        )

    def test_exact_requires_cited_p_nnn(self) -> None:
        self.assertEqual(
            vr.check_identification_consistency("exact", [], []),
            ["VERDICT-3: exact requires a cited incident P-NNN"],
        )

    def test_exact_requires_active_and_allow_exact(self) -> None:
        candidate = _row(
            id="P-001",
            date="2026-01-01",
            team="incident",
            symptom="S-05",
            lifecycle="candidate",
            allow_exact="no",
            status="open",
        )
        violations = vr.check_identification_consistency(
            "exact", ["P-001"], vr.parse_problem_register(_register(candidate))
        )
        self.assertTrue(
            any("VERDICT-6" in item for item in violations), violations
        )
        self.assertTrue(
            any("VERDICT-7" in item for item in violations), violations
        )

        active = _row(
            id="P-002",
            date="2026-01-01",
            team="incident",
            symptom="S-05",
            lifecycle="active",
            allow_exact="yes",
            status="open",
        )
        self.assertEqual(
            vr.check_identification_consistency(
                "exact", ["P-002"], vr.parse_problem_register(_register(active))
            ),
            [],
        )

    def test_structural_requires_candidate_or_active(self) -> None:
        mitigated = _row(
            id="P-001",
            date="2026-01-01",
            team="incident",
            symptom="S-05",
            lifecycle="mitigated",
            allow_exact="no",
            status="open",
        )
        violations = vr.check_identification_consistency(
            "structural", ["P-001"], vr.parse_problem_register(_register(mitigated))
        )
        self.assertTrue(
            any("VERDICT-8" in item for item in violations), violations
        )

        candidate = _row(
            id="P-002",
            date="2026-01-01",
            team="incident",
            symptom="S-05",
            lifecycle="candidate",
            allow_exact="no",
            status="open",
        )
        self.assertEqual(
            vr.check_identification_consistency(
                "structural",
                ["P-002"],
                vr.parse_problem_register(_register(candidate)),
            ),
            [],
        )

    def test_no_match_rejects_cited_p_nnn(self) -> None:
        active = _row(
            id="P-001",
            date="2026-01-01",
            team="incident",
            symptom="S-05",
            lifecycle="active",
            allow_exact="yes",
            status="open",
        )
        violations = vr.check_identification_consistency(
            "no_match", ["P-001"], vr.parse_problem_register(_register(active))
        )
        self.assertEqual(
            violations,
            ["VERDICT-2: no_match must not cite a P-NNN (cited: ['P-001'])"],
        )

    def test_parse_ticket_record(self) -> None:
        content = (
            "---\n"
            "symptom_ids: [S-05, S-07]\n"
            "known_problem_ids: [P-001]\n"
            "identification_verdict: structural\n"
            "---\n\n# ticket\n"
        )
        record = vr.parse_ticket_record(content, "ticket_1.md")
        self.assertEqual(record["symptom_ids"], ["S-05", "S-07"])
        self.assertEqual(record["known_problem_ids"], ["P-001"])
        self.assertEqual(record["identification_verdict"], "structural")

    # ── Close-out collapse ───────────────────────────────────────────────────

    def test_close_out_pass(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ticket_dir = _ticket_dir(d)
            snapshot = vr.load_close_out_snapshot(ticket_dir, ticket_dir)
            self.assertEqual(vr.evaluate_close_out(snapshot), [])
            self.assertEqual(
                vr.validate_close_out(str(ticket_dir), str(ticket_dir)), 0
            )

    def test_close_out_working_files_remain(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ticket_dir = _ticket_dir(d, with_working=True)
            snapshot = vr.load_close_out_snapshot(ticket_dir, ticket_dir)
            violations = vr.evaluate_close_out(snapshot)
            self.assertTrue(
                any("CLOSE-1" in item for item in violations), violations
            )
            self.assertEqual(
                vr.validate_close_out(str(ticket_dir), str(ticket_dir)), 1
            )

    def test_close_out_response_draft_remains(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ticket_dir = _ticket_dir(d, with_draft=True)
            snapshot = vr.load_close_out_snapshot(ticket_dir, ticket_dir)
            violations = vr.evaluate_close_out(snapshot)
            self.assertTrue(
                any("CLOSE-2" in item for item in violations), violations
            )

    def test_close_out_missing_durable_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ticket_dir = _ticket_dir(d, with_dirs=False)
            snapshot = vr.load_close_out_snapshot(ticket_dir, ticket_dir)
            violations = vr.evaluate_close_out(snapshot)
            self.assertTrue(
                any("CLOSE-3" in item for item in violations), violations
            )
            self.assertTrue(
                any("CLOSE-4" in item for item in violations), violations
            )

    def test_close_out_missing_ticket(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ticket_dir = Path(d) / "ticket"
            ticket_dir.mkdir()
            snapshot = vr.load_close_out_snapshot(ticket_dir, ticket_dir)
            self.assertTrue(
                any("CLOSE-0" in item for item in vr.evaluate_close_out(snapshot))
            )
            buf = io.StringIO()
            with contextlib.redirect_stderr(buf):
                result = vr.validate_close_out(str(ticket_dir), str(ticket_dir))
            self.assertEqual(result, 2)
            self.assertIn("CLOSE-SKIPPED", buf.getvalue())

    def test_close_out_missing_image_path(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ticket_dir = _ticket_dir(d, image_exists=False)
            snapshot = vr.load_close_out_snapshot(ticket_dir, ticket_dir)
            violations = vr.evaluate_close_out(snapshot)
            self.assertTrue(
                any("CLOSE-5" in item for item in violations), violations
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
