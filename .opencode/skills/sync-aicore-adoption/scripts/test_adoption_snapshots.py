"""Explicit snapshot selection, read-only contracts, and live-state review."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest
import yaml

from adoption_content import _destination_unit_digest, _unit_upstream_digest
from adoption_contracts import SyncError
from adoption_digests import _sha256
from adoption_git import (
    _GitRepo,
    _RevisionSnapshot,
    _resolve_git_path,
    _run_controlled_read,
)
from adoption_loaders import _control_document_from_bytes, _raw_file_digest
from adoption_schema import _validate_lock_document
from adoption_test_data import (
    EMPTY_REVIEW,
    TWO_UNIT_DECISION_REVIEW,
    review_with_transition,
)
from adoption_test_repos import (
    ENGINE_PATH,
    AdopterFixture,
    EngineTestCase,
    git_environment,
)


def _run_cli_with_environment(
    environment: dict[str, str], working_directory: Path, *args: str
) -> subprocess.CompletedProcess[str]:
    """Run the engine CLI under one explicit isolated environment."""
    return subprocess.run(
        [sys.executable, "-B", str(ENGINE_PATH), *args],
        capture_output=True,
        text=True,
        cwd=working_directory,
        env=environment,
    )


def _global_config_state(environment: dict[str, str]) -> tuple[int, str]:
    """Capture the resolved global Git configuration through one environment."""
    proc = subprocess.run(
        ["git", "config", "--global", "--list"],
        capture_output=True,
        text=True,
        env=environment,
    )
    return proc.returncode, proc.stdout


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


class ReadOnlyTests(EngineTestCase):
    def test_check_writes_nothing_to_adopter(self) -> None:
        fixture = self.build_greeting()
        before_files = self.worktree_bytes(fixture["adopter"])
        before_git = self.git_state(fixture["adopter"])
        proc = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision",
            fixture["adopter_rev"],
        )
        self.assert_exit(proc, 0)
        assert before_files == self.worktree_bytes(fixture["adopter"])
        assert before_git == self.git_state(fixture["adopter"])

    def test_tampered_candidate_check_leaves_accepted_lock_unchanged(self) -> None:
        """A failed candidate check is read-only and does not replace the accepted lock."""
        fixture = self.build_greeting()
        old_lock = fixture["lock"].read_bytes()
        before_files = self.worktree_bytes(fixture["adopter"])
        before_git = self.git_state(fixture["adopter"])
        bad_candidate = fixture["lock"].read_text(encoding="utf-8").replace(
            "accepted_source_commit", "tampered_source_commit"
        )
        candidate_path = self.write(self.root, "bad-candidate.lock.yaml", bad_candidate)
        check = self.run_cli(
            "check",
            *self.base_check_args(fixture, lock=candidate_path),
            "--adopter-revision",
            fixture["adopter_rev"],
        )
        assert check.returncode != 0
        assert fixture["lock"].read_bytes() == old_lock
        assert self.worktree_bytes(fixture["adopter"]) == before_files
        assert self.git_state(fixture["adopter"]) == before_git

    def test_declaration_byte_change_rejects_without_mutation(self) -> None:
        """Changing declaration bytes invalidates the accepted review and writes nothing."""
        fixture = self.build_greeting()
        lock_before = fixture["lock"].read_bytes()
        fixture["declaration"].write_text(
            fixture["declaration"].read_text(encoding="utf-8") + "\n# tampered\n",
            encoding="utf-8",
        )
        before_files = self.worktree_bytes(fixture["adopter"])
        before_git = self.git_state(fixture["adopter"])
        check = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision",
            fixture["adopter_rev"],
            "--format",
            "json",
        )
        assert check.returncode == 2
        assert "declaration_changed" in check.stderr
        assert fixture["lock"].read_bytes() == lock_before
        assert self.worktree_bytes(fixture["adopter"]) == before_files
        assert self.git_state(fixture["adopter"]) == before_git

    def test_propose_lock_writes_stdout_only(self) -> None:
        fixture = self.build_greeting()
        fixture["review"].write_text(
            review_with_transition(
                EMPTY_REVIEW,
                self.rev(fixture["upstream"]),
                fixture["declaration"].read_text(encoding="utf-8"),
                _raw_file_digest(str(fixture["lock"])),
            ),
            encoding="utf-8",
        )
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "fresh transition")
        adopter_before = self.worktree_bytes(fixture["adopter"])
        upstream_before = self.worktree_bytes(fixture["upstream"])
        adopter_git = self.git_state(fixture["adopter"])
        upstream_git = self.git_state(fixture["upstream"])
        proc = self.run_cli(
            "propose-lock",
            "--upstream-repo",
            str(fixture["upstream"]),
            "--catalog",
            str(fixture["catalog"]),
            "--declaration",
            str(fixture["declaration"]),
            "--review",
            str(fixture["review"]),
            "--lock",
            str(fixture["lock"]),
            "--adopter-revision",
            fixture["adopter_rev"],
        )
        self.assert_exit(proc, 0)
        assert "schema_version: 2" in proc.stdout
        assert proc.stderr == ""
        assert adopter_before == self.worktree_bytes(fixture["adopter"])
        assert upstream_before == self.worktree_bytes(fixture["upstream"])
        assert adopter_git == self.git_state(fixture["adopter"])
        assert upstream_git == self.git_state(fixture["upstream"])

    def test_verify_all_writes_nothing_to_checkouts(self) -> None:
        fixture = self.build_verify()
        adopters = [fixture["checkouts"] / "good", fixture["checkouts"] / "stale"]
        before = {str(path): self.worktree_bytes(path) for path in adopters}
        before_git = {str(path): self.git_state(path) for path in adopters}
        proc = self.run_cli(
            "verify-all",
            "--upstream-repo",
            str(fixture["upstream"]),
            "--catalog",
            str(fixture["catalog"]),
            "--registry",
            str(fixture["current_registry"]),
            "--checkouts-root",
            str(fixture["checkouts"]),
        )
        self.assert_exit(proc, 0)
        for path in adopters:
            assert before[str(path)] == self.worktree_bytes(path)
            assert before_git[str(path)] == self.git_state(path)

    def test_removed_apply_is_rejected_without_snapshot_writes(self) -> None:
        fixture = self.build_greeting(advance="content")
        adopter, upstream = fixture["adopter"], fixture["upstream"]
        before = (self.worktree_bytes(adopter), self.git_state(adopter))
        upstream_before = (self.worktree_bytes(upstream), self.git_state(upstream))
        proc = self.run_cli(
            "apply", *self.base_check_args(fixture), "--adopter-revision", fixture["adopter_rev"]
        )
        self.assert_exit(proc, 2, "invalid choice")
        assert (self.worktree_bytes(adopter), self.git_state(adopter)) == before
        assert (self.worktree_bytes(upstream), self.git_state(upstream)) == upstream_before

    def test_commands_leave_global_git_configuration_unchanged(self) -> None:
        """Guards the Phase 3 gate bullet "global Git configuration survives".

        The fixture's isolated Git environment pins ``GIT_CONFIG_GLOBAL``; this
        test points that isolated path at a seeded temp file, runs ``check``,
        ``propose-lock``, and the rejected ``apply`` probe under the exact same
        environment, then asserts the global configuration bytes and
        ``git config --global --list`` output are unchanged. Only temporary
        repositories and a temporary config file are used.
        """
        fixture = self.build_greeting()
        global_config = self.root / "isolated-global-gitconfig"
        global_config.write_text(
            "[user]\n\tname = Isolated Global\n", encoding="utf-8"
        )
        environment = git_environment()
        environment["GIT_CONFIG_GLOBAL"] = str(global_config)

        before_bytes = global_config.read_bytes()
        before_state = _global_config_state(environment)
        assert before_state == (0, "user.name=Isolated Global\n")

        check = _run_cli_with_environment(
            environment,
            self.root,
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision",
            fixture["adopter_rev"],
        )
        self.assert_exit(check, 0)
        fixture["review"].write_text(
            review_with_transition(
                EMPTY_REVIEW,
                self.rev(fixture["upstream"]),
                fixture["declaration"].read_text(encoding="utf-8"),
                _raw_file_digest(str(fixture["lock"])),
            ),
            encoding="utf-8",
        )
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "fresh transition")
        proposal = _run_cli_with_environment(
            environment,
            self.root,
            "propose-lock",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--lock", str(fixture["lock"]),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(proposal, 0)
        self.write(fixture["adopter"], ".aicore/adoption.lock.yaml", proposal.stdout)
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "install candidate")
        installed = _run_cli_with_environment(
            environment,
            self.root,
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision", fixture["adopter_rev"],
            "--format", "json",
        )
        self.assert_exit(installed, 0)
        rejected = _run_cli_with_environment(
            environment,
            self.root,
            "apply",
            *self.base_check_args(fixture),
            "--adopter-revision",
            fixture["adopter_rev"],
        )
        self.assert_exit(rejected, 2, "invalid choice")

        assert global_config.read_bytes() == before_bytes
        assert _global_config_state(environment) == before_state


class LiveStateReviewTests(EngineTestCase):
    """Snapshot verification is distinct from unchecked live worktree state."""

    def _prepare_and_review(self, fixture: AdopterFixture) -> str:
        self.write(
            fixture["adopter"],
            "content/note-local.txt",
            "note v2 reconciled\nLOCAL_BUSINESS_RULE: keep\n",
        )
        prepared_rev = self.commit(fixture["adopter"], "prepared note adaptation")
        fixture["adopter_rev"] = prepared_rev
        catalog = yaml.safe_load(fixture["catalog"].read_text(encoding="utf-8"))
        declaration = yaml.safe_load(
            fixture["declaration"].read_text(encoding="utf-8")
        )
        unit = next(item for item in catalog["units"] if item["id"] == "note")
        declaration_unit = next(
            item for item in declaration["units"] if item["id"] == "note"
        )
        target = self.rev(fixture["upstream"])
        source = _unit_upstream_digest(
            _GitRepo(str(fixture["upstream"])), target, unit
        )
        result = _destination_unit_digest(
            unit,
            declaration_unit,
            _RevisionSnapshot(_GitRepo(str(fixture["adopter"])), prepared_rev),
        )
        fixture["review"].write_text(
            review_with_transition(
                TWO_UNIT_DECISION_REVIEW,
                target,
                fixture["declaration"].read_text(encoding="utf-8"),
                _raw_file_digest(str(fixture["lock"])),
                decision_digests={"note": (source, result)},
            ),
            encoding="utf-8",
        )
        return prepared_rev

    def _propose_index(self, fixture: AdopterFixture) -> subprocess.CompletedProcess[str]:
        return self.run_cli(
            "propose-lock",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--lock", str(fixture["lock"]),
            "--adopter-index",
        )

    def test_altered_staged_snapshot_after_review_rejects_candidate(self) -> None:
        fixture = self.build_two_unit(EMPTY_REVIEW)
        self._prepare_and_review(fixture)
        first = self._propose_index(fixture)
        self.assert_exit(first, 0)

        # Changing the staged snapshot after approval no longer matches the
        # reviewed destination digest, so candidate generation must fail.
        self.write(fixture["adopter"], "content/note-local.txt", "tampered after review\n")
        self.git(fixture["adopter"], "add", "content/note-local.txt")
        rejected = self._propose_index(fixture)
        self.assert_exit(rejected, 2, "review_changed")
        assert rejected.stdout == ""

    def test_worktree_edit_after_verified_snapshot_survives_for_re_review(self) -> None:
        fixture = self.build_two_unit(EMPTY_REVIEW)
        self._prepare_and_review(fixture)
        proposal = self._propose_index(fixture)
        self.assert_exit(proposal, 0)
        candidate = self.write(self.root, "reviewed-candidate.lock.yaml", proposal.stdout)
        self.assert_exit(
            self.run_cli(
                "check", *self.base_check_args(fixture, lock=candidate),
                "--adopter-index", "--format", "json",
            ),
            0,
        )

        # A newer unstaged local edit is not part of the verified snapshot and
        # is never replaced by it; the owner must re-review before acceptance.
        note = fixture["adopter"] / "content/note-local.txt"
        note.write_text("newer local edit\n", encoding="utf-8")
        self.assert_exit(
            self.run_cli(
                "check", *self.base_check_args(fixture, lock=candidate),
                "--adopter-index", "--format", "json",
            ),
            0,
        )
        assert note.read_text(encoding="utf-8") == "newer local edit\n"
        staged = self.git(
            fixture["adopter"], "show", ":content/note-local.txt"
        ).stdout
        assert staged == "note v2 reconciled\nLOCAL_BUSINESS_RULE: keep\n"


class BaselineSingleReadTests(EngineTestCase):
    """The baseline digest and the parsed rows derive from exactly one buffer."""

    def test_baseline_digest_is_derived_from_the_parsed_bytes(self) -> None:
        """The shared loader seam never re-reads ``path``.

        Check and propose both parse and hash through this captured buffer.

        The supplied buffer deliberately differs from the file on disk: if
        the seam parsed or hashed the path instead of the buffer, both
        outputs would reflect the on-disk bytes and this test would fail.
        """
        fixture = self.build_greeting()
        on_disk = fixture["lock"].read_bytes()
        alternate = on_disk.replace(b"example/upstream", b"example/alternate")
        assert alternate != on_disk
        document, digest = _control_document_from_bytes(
            str(fixture["lock"]), "invalid_lock", alternate, _validate_lock_document
        )
        assert digest == _sha256(alternate)
        assert digest != _raw_file_digest(str(fixture["lock"]))
        assert document["upstream_repository"] == "example/alternate"


def _write_executable(path: Path, body: str) -> None:
    """Write one local sentinel script. It must not be invoked by a controlled read."""
    path.write_text(body, encoding="utf-8")
    path.chmod(0o755)


def _index_bytes(repo: Path) -> bytes:
    """Read the selected repository's real index, not an ambient index file."""
    resolved = _resolve_git_path(str(repo), "index")
    assert resolved is not None
    return Path(resolved).read_bytes()


class ControlledReadSafetyTests(EngineTestCase):
    """T1 and T2: selected-repository reads do not follow ambient redirects or fetch."""

    def test_t1_selected_snapshot_ignores_ambient_redirects(self) -> None:
        fixture = self.build_greeting()
        selected = fixture["adopter"]
        decoy = self.root / "decoy"
        self.init_repo(decoy)
        self.write(decoy, "content/greeting.txt", "DECOY\n")
        self.commit(decoy, "decoy")
        sentinel = self.root / "alias-hook-sentinel"
        script = self.root / "alias-hook.sh"
        _write_executable(
            script,
            "#!/bin/sh\ntouch " + str(sentinel) + "\nexit 0\n",
        )
        global_config = self.root / "poison-global.gitconfig"
        global_config.write_text(
            "[core]\n"
            f"\tfsmonitor = {script}\n"
            "[alias]\n"
            f"\tshow = !{script}\n",
            encoding="utf-8",
        )
        trace = self.root / "injected.trace"
        trace2 = self.root / "injected.trace2"
        poison = {
            "GIT_DIR": str(decoy / ".git"),
            "GIT_WORK_TREE": str(decoy),
            "GIT_INDEX_FILE": str(decoy / ".git" / "index"),
            "GIT_OBJECT_DIRECTORY": str(decoy / ".git" / "objects"),
            "GIT_TRACE": str(trace),
            "GIT_TRACE2": str(trace2),
            "GIT_CONFIG_GLOBAL": str(global_config),
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "core.fsmonitor",
            "GIT_CONFIG_VALUE_0": str(script),
        }
        index_before = _index_bytes(selected)
        refs_before = self.git(selected, "for-each-ref").stdout
        files_before = self.worktree_bytes(selected)
        with mock.patch.dict(os.environ, poison, clear=False):
            blob = _GitRepo(str(selected)).show_blob(
                fixture["adopter_rev"], "content/greeting.txt"
            )
            environment = dict(os.environ)
            environment.update(poison)
            checked = _run_cli_with_environment(
                environment,
                self.root,
                "check",
                *self.base_check_args(fixture),
                "--adopter-revision",
                fixture["adopter_rev"],
            )
        assert blob == b"hello\n"
        self.assert_exit(checked, 0)
        assert not sentinel.exists()
        assert not trace.exists()
        assert not trace2.exists()
        assert _index_bytes(selected) == index_before
        assert self.git(selected, "for-each-ref").stdout == refs_before
        assert self.worktree_bytes(selected) == files_before
        assert (decoy / "content/greeting.txt").read_text(encoding="utf-8") == "DECOY\n"

    def test_t2_promisor_missing_object_refuses_without_fetch(self) -> None:
        fixture = self.build_greeting()
        repo = fixture["adopter"]
        sentinel = self.root / "fetch-sentinel"
        script = self.root / "fetch-helper.sh"
        _write_executable(
            script,
            "#!/bin/sh\ntouch " + str(sentinel) + "\nexit 1\n",
        )
        resolved_index = _resolve_git_path(str(repo), "index")
        assert resolved_index is not None
        index_path = Path(resolved_index)
        index_before = index_path.read_bytes()
        refs_before = self.git(repo, "for-each-ref").stdout
        self.git(repo, "config", "core.repositoryformatversion", "1")
        config = repo / ".git" / "config"
        config.write_text(
            config.read_text(encoding="utf-8")
            + "[extensions]\n\tpartialclone = origin\n"
            + '[remote "origin"]\n\tpromisor = true\n'
            + f"\turl = ext::{script}\n",
            encoding="utf-8",
        )
        missing = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        proc = _run_controlled_read(str(repo), ("cat-file", "-p", missing))
        assert proc.returncode != 0
        assert b"partial or promisor read refused" in proc.stderr
        with pytest.raises(SyncError) as caught:
            _GitRepo(str(repo)).blob(missing, "adopter_snapshot_unavailable")
        assert caught.value.code == "adopter_snapshot_unavailable"
        assert not sentinel.exists()
        assert index_path.read_bytes() == index_before
        assert self.git(repo, "for-each-ref").stdout == refs_before

    def test_t2_false_promisor_is_not_enabled(self) -> None:
        fixture = self.build_greeting()
        repo = fixture["adopter"]
        sentinel = self.root / "false-promisor-sentinel"
        script = self.root / "false-promisor.sh"
        _write_executable(
            script,
            "#!/bin/sh\ntouch " + str(sentinel) + "\nexit 1\n",
        )
        self.git(repo, "config", "remote.origin.promisor", "false")
        self.git(repo, "config", "remote.origin.url", f"ext::{script}")
        blob = _GitRepo(str(repo)).show_blob(
            fixture["adopter_rev"], "content/greeting.txt"
        )
        assert blob == b"hello\n"
        with pytest.raises(SyncError) as caught:
            _GitRepo(str(repo)).blob(
                "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                "adopter_snapshot_unavailable",
            )
        assert caught.value.code == "adopter_snapshot_unavailable"
        assert not sentinel.exists()

    def test_t2_status_does_not_run_fsmonitor_or_rewrite_index(self) -> None:
        fixture = self.build_greeting()
        repo = fixture["adopter"]
        sentinel = self.root / "fsmonitor-sentinel"
        script = self.root / "fsmonitor.sh"
        _write_executable(
            script,
            "#!/bin/sh\ntouch " + str(sentinel) + "\nexit 0\n",
        )
        note = repo / "OWNER-NOTES.md"
        note.write_text("owner note\n", encoding="utf-8")
        self.commit(repo, "note")
        os.utime(note, None)
        self.git(repo, "config", "core.fsmonitor", str(script))
        assert not sentinel.exists()
        index_before = _index_bytes(repo)
        refs_before = self.git(repo, "for-each-ref").stdout
        status = _run_controlled_read(
            str(repo),
            (
                "status",
                "--porcelain=v2",
                "-z",
                "--untracked-files=all",
                "--ignore-submodules=none",
            ),
        )
        assert status.returncode == 0
        assert not sentinel.exists()
        assert _index_bytes(repo) == index_before
        assert self.git(repo, "for-each-ref").stdout == refs_before
