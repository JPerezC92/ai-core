"""Explicit snapshot selection tests.

An explicit index or commit snapshot must ignore unstaged worktree edits and
leave unrelated staged and dirty work intact.
"""

from __future__ import annotations

from adoption_test_repos import EngineTestCase


class SnapshotExplicitnessTests(EngineTestCase):
    def test_index_ignores_unstaged_worktree_edit(self) -> None:
        fixture = self.build_greeting()
        worktree = fixture["adopter"] / "content/greeting.txt"
        worktree.write_text("DIRTY WORKTREE\n", encoding="utf-8")
        args = ["check", *self.base_check_args(fixture), "--adopter-index"]
        self.assert_exit(self.run_cli(*args), 0)
        assert worktree.read_text(encoding="utf-8") == "DIRTY WORKTREE\n"

    def test_commit_revision_ignores_unstaged_worktree_edit(self) -> None:
        fixture = self.build_greeting()
        worktree = fixture["adopter"] / "content/greeting.txt"
        worktree.write_text("DIRTY WORKTREE\n", encoding="utf-8")
        args = [
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision",
            fixture["adopter_rev"],
        ]
        self.assert_exit(self.run_cli(*args), 0)

    def test_index_check_leaves_unrelated_staged_and_dirty_work_intact(self) -> None:
        fixture = self.build_greeting()
        adopter = fixture["adopter"]
        self.write(adopter, "OWNER-NOTES.md", "owner note v1\n")
        self.commit(adopter, "owner notes")
        self.write(adopter, "OWNER-STAGED.md", "staged owner\n")
        self.stage(adopter, "OWNER-STAGED.md")
        self.write(adopter, "OWNER-NOTES.md", "dirty owner\n")

        index_before = self.index_state(adopter)
        worktree_before = self.worktree_bytes(adopter)
        proc = self.run_cli(
            "check", *self.base_check_args(fixture), "--adopter-index"
        )
        self.assert_exit(proc, 0)
        assert self.index_state(adopter) == index_before
        assert self.worktree_bytes(adopter) == worktree_before
