"""Tests for user-story index discovery and status mirroring."""

from __future__ import annotations

import contextlib
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import validate_plan as vp  # noqa: E402
from _validate_plan_testkit import (  # noqa: E402
    VALID_PHASE,
    VALID_PLAN,
    build_single_file_plan,
    write_fixture,
)


class ValidatePlanStoryIndexTests:
    def test_index_missing_slug_flagged(self, tmp_path: Path) -> None:
        write_fixture(
            tmp_path,
            "index.md",
            "# Index\n\n| Title | Status |\n|---|---|\n| other | active |\n",
        )
        write_fixture(
            tmp_path,
            "my-feature.md",
            "# User story — my-feature\n\n> **Status:** active\n",
        )
        assert vp.check_story_index(str(tmp_path)) == [
            "INDEX-MISSING: story slug `my-feature` not listed in index.md"
        ]

    def test_status_matches_own_row_not_another_row(self, tmp_path: Path) -> None:
        write_fixture(
            tmp_path,
            "index.md",
            "# User stories\n\n| Slug | Title | Status |\n|---|---|---|\n"
            "| other | Other feature | active |\n"
            "| my-feature | My feature | completed |\n",
        )
        write_fixture(
            tmp_path,
            "my-feature.md",
            "# User story — my-feature\n\n> **Status:** active\n",
        )
        assert vp.check_story_index(str(tmp_path)) == [
            "INDEX-MISMATCH: story `my-feature` Status 'active' not mirrored "
            "in index.md"
        ]

    def test_status_matching_own_row_passes_despite_other_rows(
        self, tmp_path: Path
    ) -> None:
        write_fixture(
            tmp_path,
            "index.md",
            "# User stories\n\n| Slug | Title | Status |\n|---|---|---|\n"
            "| other | Other feature | completed |\n"
            "| my-feature | My feature | active |\n",
        )
        write_fixture(
            tmp_path,
            "my-feature.md",
            "# User story — my-feature\n\n> **Status:** active\n",
        )
        assert vp.check_story_index(str(tmp_path)) == []

    def test_fenced_status_in_body_does_not_override_header_status(
        self, tmp_path: Path
    ) -> None:
        write_fixture(
            tmp_path,
            "index.md",
            "# User stories\n\n| Slug | Status |\n|---|---|\n| my-feature | active |\n",
        )
        write_fixture(
            tmp_path,
            "my-feature.md",
            "# User story — my-feature\n\n"
            "> **Status:** active\n\n"
            "## Evidence\n\n"
            "```markdown\n"
            "> **Status:** completed\n"
            "```\n",
        )
        assert vp.check_story_index(str(tmp_path)) == []

    def test_validate_plan_dir_missing_story_index_outputs_exact_diagnostic(
        self, tmp_path: Path
    ) -> None:
        write_fixture(tmp_path, "plan.md", VALID_PLAN)
        write_fixture(tmp_path, "phase-01-owner.md", VALID_PHASE)
        stories_dir = tmp_path / "user-stories"
        stories_dir.mkdir()
        write_fixture(
            stories_dir,
            "my-feature.md",
            "# User story — my-feature\n\n> **Status:** active\n",
        )
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            result = vp.validate_plan_dir(str(tmp_path), stories_dir=str(stories_dir))
        assert result == 1
        assert stderr.getvalue() == (
            f"MISSING-INDEX: {stories_dir / 'index.md'} not found "
            "but story files exist\n"
        )

    def test_validate_plan_dir_story_status_mismatch_outputs_exact_diagnostic(
        self, tmp_path: Path
    ) -> None:
        write_fixture(tmp_path, "plan.md", VALID_PLAN)
        write_fixture(tmp_path, "phase-01-owner.md", VALID_PHASE)
        stories_dir = tmp_path / "user-stories"
        stories_dir.mkdir()
        write_fixture(
            stories_dir,
            "index.md",
            "# User stories\n\n| Slug | Status |\n|---|---|\n| my-feature | completed |\n",
        )
        write_fixture(
            stories_dir,
            "my-feature.md",
            "# User story — my-feature\n\n> **Status:** active\n",
        )
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            result = vp.validate_plan_dir(str(tmp_path), stories_dir=str(stories_dir))
        assert result == 1
        assert stderr.getvalue() == (
            "INDEX-MISMATCH: story `my-feature` Status 'active' not mirrored "
            "in index.md\n"
        )

    def test_validate_single_file_story_status_mismatch_outputs_exact_diagnostic(
        self, tmp_path: Path
    ) -> None:
        plan_file = write_fixture(tmp_path, "plan.md", build_single_file_plan())
        stories_dir = tmp_path / "user-stories"
        stories_dir.mkdir()
        write_fixture(
            stories_dir,
            "index.md",
            "# User stories\n\n| Slug | Status |\n|---|---|\n| my-feature | completed |\n",
        )
        write_fixture(
            stories_dir,
            "my-feature.md",
            "# User story — my-feature\n\n> **Status:** active\n",
        )
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = vp.run(
                ["--single-file", str(plan_file), "--stories", str(stories_dir)]
            )
        assert result == 1
        assert stdout.getvalue() == ""
        assert stderr.getvalue() == (
            "INDEX-MISMATCH: story `my-feature` Status 'active' not mirrored "
            "in index.md\n"
        )

    def test_validate_single_file_matching_index_outputs_success_line(
        self, tmp_path: Path
    ) -> None:
        plan_file = write_fixture(tmp_path, "plan.md", build_single_file_plan())
        stories_dir = tmp_path / "user-stories"
        stories_dir.mkdir()
        write_fixture(
            stories_dir,
            "index.md",
            "# User stories\n\n| Slug | Status |\n|---|---|\n| my-feature | active |\n",
        )
        write_fixture(
            stories_dir,
            "my-feature.md",
            "# User story — my-feature\n\n> **Status:** active\n",
        )
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = vp.run(
                ["--single-file", str(plan_file), "--stories", str(stories_dir)]
            )
        assert result == 0
        assert stdout.getvalue() == f"ok  single-file plan: {plan_file}\n"
        assert stderr.getvalue() == ""
