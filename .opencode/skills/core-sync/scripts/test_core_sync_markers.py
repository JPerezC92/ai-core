"""Behavior tests for core-region marker recognition and rejection.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/test_core_sync_markers.py
"""

from __future__ import annotations

from _core_sync_testkit import uc


class MarkerValidationTests:
    def test_missing_markers_returns_none(self) -> None:
        assert uc.find_markers("no markers here\n") is None

    def test_inline_marker_is_ignored(self) -> None:
        assert uc.find_markers("prefix <!-- core:begin --> suffix\n") is None

    def test_fenced_marker_is_ignored(self) -> None:
        content = "```\n<!-- core:begin -->\n<!-- core:end -->\n```\n"
        assert uc.find_markers(content) is None

    def test_backtick_fence_closer_resumes_marker_recognition(self) -> None:
        content = (
            "```\n"
            "<!-- core:begin -->\n"
            "<!-- core:end -->\n"
            "```\n"
            "<!-- core:begin -->\n"
            "<!-- core:end -->\n"
        )
        assert uc.find_markers(content) == (4, 5)

    def test_tilde_fence_closer_resumes_marker_recognition(self) -> None:
        content = (
            "~~~\n"
            "<!-- core:begin -->\n"
            "<!-- core:end -->\n"
            "~~~\n"
            "<!-- core:begin -->\n"
            "<!-- core:end -->\n"
        )
        assert uc.find_markers(content) == (4, 5)

    def test_mismatched_fence_character_does_not_resume_marker_recognition(self) -> None:
        content = (
            "````\n"
            "~~~~\n"
            "<!-- core:begin -->\n"
            "<!-- core:end -->\n"
            "````\n"
            "<!-- core:begin -->\n"
            "<!-- core:end -->\n"
        )
        assert uc.find_markers(content) == (5, 6)

    def test_short_fence_closer_does_not_resume_marker_recognition(self) -> None:
        content = (
            "````\n"
            "```\n"
            "<!-- core:begin -->\n"
            "<!-- core:end -->\n"
            "````\n"
            "<!-- core:begin -->\n"
            "<!-- core:end -->\n"
        )
        assert uc.find_markers(content) == (5, 6)

    def test_four_space_indented_fence_closer_does_not_expose_markers(self) -> None:
        content = (
            "```\n"
            "    ```\n"
            "<!-- core:begin -->\n"
            "<!-- core:end -->\n"
            "```\n"
        )
        assert uc.find_markers(content) is None

    def test_tab_indented_fence_closer_does_not_expose_markers(self) -> None:
        content = (
            "```\n"
            "\t```\n"
            "<!-- core:begin -->\n"
            "<!-- core:end -->\n"
            "```\n"
        )
        assert uc.find_markers(content) is None

    def test_duplicate_begin_returns_none(self) -> None:
        content = (
            "a\n<!-- core:begin -->\nb\n<!-- core:begin -->\nc\n<!-- core:end -->\n"
        )
        assert uc.find_markers(content) is None

    def test_reversed_markers_returns_none(self) -> None:
        assert uc.find_markers("<!-- core:end -->\nbody\n<!-- core:begin -->\n") is None
