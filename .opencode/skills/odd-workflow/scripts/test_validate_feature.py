"""Tests for the ODD feature-document validator."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from validate_feature import main, validate_feature  # noqa: E402

VALID = """# Sample feature

> **Status:** active
> **Owner:** Cipher (Lead Orchestrator)
> **Created:** 2026-10-23

## Specs

- S1 — A requirement.

## Tasks

- T1 | S1 | route | open | commit: pending

## Log

- L1 — original request
"""

CLOSED = (
    VALID.replace(
        "> **Status:** active",
        "> **Status:** closed\n> **Closed:** 2026-10-23",
    )
    .replace(
        "- T1 | S1 | route | open | commit: pending",
        "- T1 | S1 | route | done | commit: pending",
    )
    .replace(
        "- L1 — original request",
        "- L1 — original request\n- L2 — Close: done",
    )
)


def test_valid_document() -> None:
    assert validate_feature(VALID) == []


def test_closed_document() -> None:
    assert validate_feature(CLOSED) == []


def test_closed_without_date() -> None:
    findings = validate_feature(CLOSED.replace("> **Closed:** 2026-10-23\n", ""))
    assert any("Closed date" in finding for finding in findings)


def test_closed_without_close_entry() -> None:
    findings = validate_feature(CLOSED.replace("- L2 — Close: done", "- L2 — later"))
    assert any("Close:" in finding for finding in findings)


def test_closed_with_open_task() -> None:
    findings = validate_feature(CLOSED.replace("| done |", "| open |"))
    assert any("open task" in finding for finding in findings)


def test_closed_with_in_progress_task() -> None:
    findings = validate_feature(CLOSED.replace("| done |", "| in progress |"))
    assert any("in progress task" in finding for finding in findings)


def test_active_with_close_entry() -> None:
    findings = validate_feature(
        VALID.replace("- L1 — original request", "- L1 — original request\n- L2 — Close: done")
    )
    assert any("active feature" in finding for finding in findings)


def test_invalid_status() -> None:
    findings = validate_feature(VALID.replace("> **Status:** active", "> **Status:** blocked"))
    assert any("active or closed" in finding for finding in findings)


def test_missing_specs_section() -> None:
    findings = validate_feature(VALID.replace("## Specs", "## Not specs"))
    assert any("## Specs" in finding for finding in findings)


def test_missing_tasks_section() -> None:
    findings = validate_feature(VALID.replace("## Tasks", "## Not tasks"))
    assert any("## Tasks" in finding for finding in findings)


def test_missing_log_section() -> None:
    findings = validate_feature(VALID.replace("## Log", "## Not log"))
    assert any("## Log" in finding for finding in findings)


def test_missing_l1() -> None:
    findings = validate_feature(VALID.replace("- L1 — original request", "- L2 — later"))
    assert any("L1" in finding for finding in findings)


def test_missing_spec() -> None:
    findings = validate_feature(VALID.replace("- S1 — A requirement.", "- a requirement"))
    assert any("S#" in finding for finding in findings)


def test_task_without_status() -> None:
    findings = validate_feature(
        VALID.replace(
            "- T1 | S1 | route | open | commit: pending",
            "- T1 | S1 | route | commit: pending",
        )
    )
    assert any("Tasks entry" in finding for finding in findings)


def test_placeholder_title() -> None:
    findings = validate_feature(VALID.replace("# Sample feature", "# Feature name"))
    assert any("title" in finding for finding in findings)


def test_placeholder_date() -> None:
    findings = validate_feature(VALID.replace("> **Created:** 2026-10-23", "> **Created:** date"))
    assert any("Created" in finding for finding in findings)


def test_placeholder_outside_code_is_flagged() -> None:
    findings = validate_feature(VALID.replace("A requirement.", "A <placeholder> requirement."))
    assert any("placeholder" in finding for finding in findings)


def test_placeholder_inside_code_is_ignored() -> None:
    findings = validate_feature(
        VALID.replace("A requirement.", "A `odd/tasks/<feature-name>.md` path.")
    )
    assert findings == []


def test_multiple_specs_in_task() -> None:
    findings = validate_feature(
        VALID.replace("- T1 | S1 | route | open | commit: pending", "- T1 | S1, S2 | route | open | commit: pending")
    )
    assert findings == []


def test_one_bad_task_among_valid() -> None:
    findings = validate_feature(
        VALID.replace(
            "- T1 | S1 | route | open | commit: pending",
            "- T1 | S1 | route | open | commit: pending\n- T2 | S2 | route | commit: pending",
        )
    )
    assert any("Tasks entry" in finding for finding in findings)


def test_rejected_status_vocabulary() -> None:
    findings = validate_feature(
        VALID.replace(
            "- T1 | S1 | route | open | commit: pending",
            "- T1 | S1 | route | blocked | commit: pending",
        )
    )
    assert any("open|in progress|done" in finding for finding in findings)


def test_fenced_placeholder_ignored() -> None:
    findings = validate_feature(
        VALID.replace(
            "- S1 — A requirement.",
            "- S1 — A requirement.\n\n```\n<placeholder>\n```",
        )
    )
    assert findings == []


def test_directory_skips_template(tmp_path: Path, capsys) -> None:
    (tmp_path / "_template.md").write_text("not a feature", encoding="utf-8")
    (tmp_path / "feature.md").write_text(VALID, encoding="utf-8")

    assert main(["validate_feature.py", str(tmp_path)]) == 0
    output = capsys.readouterr().out
    assert "feature.md" in output
    assert "_template.md" not in output


def test_main_invalid_returns_one(tmp_path: Path) -> None:
    (tmp_path / "feature.md").write_text("not a feature", encoding="utf-8")
    assert main(["validate_feature.py", str(tmp_path)]) == 1


def test_main_usage_returns_two() -> None:
    assert main(["validate_feature.py"]) == 2


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
