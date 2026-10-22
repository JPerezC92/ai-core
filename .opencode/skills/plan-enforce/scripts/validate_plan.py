"""
Validate a plan directory (or single-file plan) against the plan/phase/story
consistency checklist.

Usage (from project root):
    <python> .opencode/skills/plan-enforce/scripts/validate_plan.py <plan_dir>
    <python> .opencode/skills/plan-enforce/scripts/validate_plan.py <plan.md> --single-file
    <python> .opencode/skills/plan-enforce/scripts/validate_plan.py <plan_dir> --stories <dir>
    <python> .opencode/skills/plan-enforce/scripts/validate_plan.py <plan.md> --single-file --stories <dir>

Mechanical/repetitive subset only: Status enum, Completed line, required
sections, unfilled <...>/TBD/date placeholders, the completed-plan audit gate
(auditor/verdict/date), and user-stories index mirroring (`--stories` applies
to both layouts; with `--single-file`, the entry composes it at the CLI edge).
Single-file layout runs
content-only checks and never looks for phase files; subfolder layout
adds phase sections + blockquote labels, the canonical phase executor-command
table shape, goal trace, manifest equality, and verification parity. Semantic
correctness (values match evidence, verdict/naming consistency, executor
authority) is the skill loop's analysis job — this script is a helper, not the
authority.

Exit codes:
    0 — all checks pass (warnings do not affect exit code)
    1 — one or more violations found
"""

from __future__ import annotations

import sys

from plan_validate_pkg import (
    ALLOWED_AUDIT_VERDICTS,
    ALLOWED_MANIFEST_ACTIONS,
    ALLOWED_STATUS,
    BASE_REQUIRED_SECTIONS,
    BODY_ALTERNATIVES,
    OUT_OF_SCOPE_PREFIX,
    PHASE_REQUIRED_LABELS,
    PHASE_REQUIRED_SECTIONS,
    VERIFY_TABLE_HEADER,
    PhaseSnapshot,
    PlanMetadata,
    PlanSnapshot,
    StoryIndexSnapshot,
    StoryMetadata,
    StorySnapshot,
    check_audit_gate,
    check_completed_line,
    check_goal_trace,
    check_manifest_equality,
    check_phase_file,
    check_phase_snapshot,
    check_phase_verify_table,
    check_placeholders,
    check_plan_file,
    check_plan_snapshot,
    check_required_sections,
    check_status,
    check_story_index,
    check_story_index_snapshot,
    check_verification_parity,
    load_phase_snapshot,
    load_phase_snapshots,
    load_plan_snapshot,
    load_story_index_snapshot,
    load_story_snapshot,
    load_text,
    parse_plan_metadata,
    parse_story_metadata,
    validate_plan_dir,
    validate_plan_snapshot,
    validate_single_file,
)
from plan_validate_pkg.entry import run

__all__ = [
    "ALLOWED_AUDIT_VERDICTS",
    "ALLOWED_MANIFEST_ACTIONS",
    "ALLOWED_STATUS",
    "BASE_REQUIRED_SECTIONS",
    "BODY_ALTERNATIVES",
    "OUT_OF_SCOPE_PREFIX",
    "PHASE_REQUIRED_LABELS",
    "PHASE_REQUIRED_SECTIONS",
    "VERIFY_TABLE_HEADER",
    "PhaseSnapshot",
    "PlanMetadata",
    "PlanSnapshot",
    "StoryIndexSnapshot",
    "StoryMetadata",
    "StorySnapshot",
    "check_audit_gate",
    "check_completed_line",
    "check_goal_trace",
    "check_manifest_equality",
    "check_phase_file",
    "check_phase_snapshot",
    "check_phase_verify_table",
    "check_placeholders",
    "check_plan_file",
    "check_plan_snapshot",
    "check_required_sections",
    "check_status",
    "check_story_index",
    "check_story_index_snapshot",
    "check_verification_parity",
    "load_phase_snapshot",
    "load_phase_snapshots",
    "load_plan_snapshot",
    "load_story_index_snapshot",
    "load_story_snapshot",
    "load_text",
    "parse_plan_metadata",
    "parse_story_metadata",
    "validate_plan_dir",
    "validate_plan_snapshot",
    "validate_single_file",
]


if __name__ == "__main__":
    sys.exit(run())
