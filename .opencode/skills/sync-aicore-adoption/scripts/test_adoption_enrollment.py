"""Ordered clean-start and real-catalog enrollment tests.

One fresh and one existing synthetic enrollment freeze approval before writes
and stop without restore on failure. The real-catalog flow drives the same
shared ordered driver against the shipped catalog and complete corpus.
"""

from __future__ import annotations

import json
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import cast

import pytest
import yaml

from adoption_constants import AICORE_SUITE_COMMAND, RULE_LAYOUT_VALUE
from adoption_content import _scan_rule_layout, _unit_upstream_digest
from adoption_contracts import StoryMergeMember
from adoption_digests import _sha256
from adoption_git import _GitRepo, _resolve_git_path
from adoption_loaders import _raw_file_digest
from adoption_mapping import evaluate_applicability
from adoption_stories import merge_story_index
from adoption_test_acceptance_data import (
    BOOTSTRAP_ADOPTED_PATHS,
    BOOTSTRAP_AGENT_EXTENSION,
    BOOTSTRAP_CONFLICT_MANIFEST,
    BOOTSTRAP_DEBT_HEADER,
    BOOTSTRAP_DECLARATION,
    BOOTSTRAP_EXISTING_DEBT,
    BOOTSTRAP_EXISTING_FILES,
    BOOTSTRAP_EXISTING_GITKEEP,
    BOOTSTRAP_EXISTING_MANIFEST,
    BOOTSTRAP_EXISTING_PROBLEMS,
    BOOTSTRAP_EXPECTED_EXISTING_DEPENDENCIES,
    BOOTSTRAP_EXPECTED_FRESH_DEPENDENCIES,
    BOOTSTRAP_FRESH_GITKEEP,
    BOOTSTRAP_FRESH_MANIFEST_BEFORE,
    BOOTSTRAP_PROBLEM_HEADER,
    BOOTSTRAP_RETAINED_PATHS,
    BOOTSTRAP_REVIEW_EVIDENCE,
    BOOTSTRAP_SKILL,
    BOOTSTRAP_SKILL_NO_DEPENDENCIES,
    BOOTSTRAP_SOURCE_FILES,
    BOOTSTRAP_SOURCE_GITKEEP,
    REAL_CATALOG_DEBT_HEADER,
    REAL_CATALOG_PROBLEM_HEADER,
    REAL_CATALOG_SYMPTOMS,
)
from adoption_test_data import CATALOG_REL
from adoption_test_enrollment import (
    _REAL_CATALOG_ADAPTED_UNITS,
    _REAL_CATALOG_ROOT_UNIT,
    _REAL_CATALOG_STORY_KIND,
    OrderedEnrollmentDriverMixin,
    PinConflict,
    FrozenReviewMissing,
    CleanStartAbort,
    PartialWriteStopped,
    _STATUS_ARGS,
    _enroll_member,
    _manifest_dependencies,
    _prepare_agent,
    _prepare_config,
    _prepare_root,
    _prepare_story_index,
    _real_catalog_excluded,
    _real_catalog_gitignore,
    _real_catalog_members,
    _real_catalog_opencode_config,
    _real_catalog_runner_config,
    _skill_dependency_requirements,
    _union_manifest_dependencies,
)
from adoption_test_prepared import _external_destination_digest, _external_unit_digest
from adoption_test_repos import EngineTestCase, repository_root
from adoption_test_runner_data import AICORE_RUNNER, NO_TESTS_RUNNER


def _debt_source_path(catalog: dict[str, object]) -> str:
    """Return the catalog's debt-register source path from its member mapping."""
    unit = next(
        item
        for item in cast(list[dict[str, object]], catalog["units"])
        if str(item["id"]) == "knowledge-debt"
    )
    members = cast(list[dict[str, object]], unit["members"])
    return str(members[0]["source"])


class OrderedBootstrapAcceptanceTests(EngineTestCase, OrderedEnrollmentDriverMixin):
    """One fresh and one existing enrollment. Approval is frozen before writes."""

    def _prepare_all(
        self, before: dict[str, str] | None
    ) -> tuple[dict[str, str], list[str]]:
        """Prepare every adopted result outside the destination."""
        source = BOOTSTRAP_SOURCE_FILES
        root_before = None if before is None else before["AGENTS.md"]
        agent_before = None if before is None else before[".opencode/agents/reviewer.md"]
        manifest_before = (
            BOOTSTRAP_FRESH_MANIFEST_BEFORE
            if before is None
            else before["pyproject.toml"]
        )
        config_before = None if before is None else before["opencode.jsonc"]
        index_before = None if before is None else before["user-stories/index.md"]
        requirements = _skill_dependency_requirements(source[".opencode/skills/enrolled/SKILL.md"])
        manifest = _union_manifest_dependencies(manifest_before, requirements)
        index, collisions = _prepare_story_index(source["user-stories/index.md"], index_before)
        prepared = {
            "AGENTS.md": _prepare_root(source["AGENTS.md"], root_before),
            ".opencode/agents/reviewer.md": _prepare_agent(
                source[".opencode/agents/reviewer.md"], agent_before
            ),
            "agents/reviewer/profile.md": source["agents/reviewer/profile.md"],
            "skills/mirror-note.md": source["skills/mirror-note.md"],
            "knowledge/debt.md": _enroll_member(
                None if before is None else before["knowledge/debt.md"],
                source["knowledge/debt.template.md"],
                BOOTSTRAP_DEBT_HEADER,
            ),
            "knowledge/symptoms.md": source["knowledge/symptoms.md"],
            "knowledge/problems.md": _enroll_member(
                None if before is None else before["knowledge/problems.md"],
                source["knowledge/problems.md"],
                BOOTSTRAP_PROBLEM_HEADER,
            ),
            "plans/.gitkeep": _enroll_member(
                None if before is None else before["plans/.gitkeep"],
                source["plans/.gitkeep"],
                BOOTSTRAP_FRESH_GITKEEP,
            ),
            "pyproject.toml": manifest,
            ".opencode/skills/enrolled/SKILL.md": source[".opencode/skills/enrolled/SKILL.md"],
            "opencode.jsonc": _prepare_config(config_before),
            "user-stories/alpha.md": source["user-stories/alpha.md"],
            "user-stories/index.md": index,
        }
        assert tuple(prepared) == BOOTSTRAP_ADOPTED_PATHS
        return prepared, collisions

    def _review_text(self, prepared: dict[str, str], declaration_text: str) -> str:
        catalog = yaml.safe_load((self.upstream / CATALOG_REL).read_text(encoding="utf-8"))
        declaration = yaml.safe_load(declaration_text)
        assert isinstance(catalog, dict)
        assert isinstance(declaration, dict)
        files = {
            relative: ("100644", text.encode("utf-8"))
            for relative, text in prepared.items()
        }
        upstream = _GitRepo(str(self.upstream))
        target = self.rev(self.upstream)
        decisions: list[dict[str, object]] = []
        for unit in catalog["units"]:
            assert isinstance(unit, dict)
            declaration_unit = next(
                item for item in declaration["units"] if item["id"] == unit["id"]
            )
            protected = bool(unit.get("rule_documents"))
            mode = str(declaration_unit["mode"])
            if not protected and mode not in ("adapted", "replacement", "destination_owned"):
                continue
            document: dict[str, object] = {
                "unit": unit["id"],
                "decision": "applied",
                "reviewer": "reviewer",
                "evidence": BOOTSTRAP_REVIEW_EVIDENCE,
                "reviewed_upstream_digest": _unit_upstream_digest(upstream, target, unit),
                "reviewed_destination_digest": _external_destination_digest(
                    unit, declaration_unit, files
                ),
            }
            if protected:
                document["verified_layout"] = RULE_LAYOUT_VALUE
            decisions.append(document)
        review = {
            "schema_version": 2,
            "upstream_repository": catalog["catalog"]["upstream_repository"],
            "transition": {
                "baseline_lock_digest": None,
                "target_source_commit": target,
                "declaration_digest": _sha256(declaration_text.encode("utf-8")),
            },
            "decisions": decisions,
        }
        return yaml.safe_dump(review, sort_keys=False)

    def _enroll(
        self,
        *,
        editor_confirmed: bool | None,
        before: dict[str, str] | None,
        fail_after_content_writes: int | None = None,
        approval: bool = True,
        after_prepare: Callable[[], None] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return self._ordered_enroll(
            editor_confirmed=editor_confirmed,
            before=before,
            prepare=self._prepare_all,
            declaration_text=BOOTSTRAP_DECLARATION,
            build_review=self._review_text,
            fail_after_content_writes=fail_after_content_writes,
            approval=approval,
            after_prepare=after_prepare,
        )

    def _commit_owner_notes(self) -> None:
        self.write(self.adopter, "OWNER-NOTES.md", "unrelated owner work\n")
        self.commit(self.adopter, "owner notes")

    def _assert_transformations(self, *, fresh: bool) -> None:
        adopter = self.adopter
        upstream = self.upstream
        destination = (adopter / "AGENTS.md").read_text(encoding="utf-8")
        source = (upstream / "AGENTS.md").read_text(encoding="utf-8")
        destination_layout, destination_violation = _scan_rule_layout(destination)
        source_layout, source_violation = _scan_rule_layout(source)
        assert destination_layout is not None, destination_violation
        assert source_layout is not None, source_violation
        assert destination_layout.mandatory == source_layout.mandatory
        assert destination_layout.extensions != source_layout.extensions
        assert b"Destination-local extension rules." in destination_layout.extensions
        assert b"Core-owned environment preferences." not in destination_layout.extensions
        agent = (adopter / ".opencode/agents/reviewer.md").read_text(encoding="utf-8")
        agent_source = (upstream / ".opencode/agents/reviewer.md").read_text(encoding="utf-8")
        agent_layout, agent_violation = _scan_rule_layout(agent)
        agent_source_layout, agent_source_violation = _scan_rule_layout(agent_source)
        assert agent_layout is not None, agent_violation
        assert agent_source_layout is not None, agent_source_violation
        assert agent_layout.mandatory == agent_source_layout.mandatory
        assert BOOTSTRAP_AGENT_EXTENSION.strip() in agent
        assert (adopter / "agents/reviewer/profile.md").read_bytes() == (
            upstream / "agents/reviewer/profile.md"
        ).read_bytes()
        assert (adopter / "skills/mirror-note.md").read_bytes() == (
            upstream / "skills/mirror-note.md"
        ).read_bytes()
        assert (adopter / "knowledge/symptoms.md").read_bytes() == (
            upstream / "knowledge/symptoms.md"
        ).read_bytes()
        assert "DEBT-001" not in (adopter / "knowledge/debt.md").read_text(encoding="utf-8")
        assert "P-001" not in (adopter / "knowledge/problems.md").read_text(encoding="utf-8")
        assert BOOTSTRAP_SOURCE_GITKEEP not in (adopter / "plans/.gitkeep").read_text(
            encoding="utf-8"
        )
        manifest = (adopter / "pyproject.toml").read_text(encoding="utf-8")
        assert "core-upstream" not in manifest
        assert "core-history" not in manifest
        assert 'name = "relay"' in manifest
        assert "[tool.relay]" in manifest
        config = json.loads((adopter / "opencode.jsonc").read_text(encoding="utf-8"))
        assert config["permission"]["bash"]["sudo *"] == "deny"
        assert (adopter / "OWNER-NOTES.md").read_text(encoding="utf-8") == (
            "unrelated owner work\n"
        )
        lock = yaml.safe_load(self.proposal_stdout)
        assert isinstance(lock, dict)
        destinations = [
            member.get("destination")
            for unit in lock["units"]
            for member in unit.get("members") or []
        ]
        assert "user-stories/index.md" not in destinations
        if fresh:
            assert (adopter / "knowledge/debt.md").read_text(encoding="utf-8") == (
                BOOTSTRAP_DEBT_HEADER
            )
            assert (adopter / "knowledge/problems.md").read_text(encoding="utf-8") == (
                BOOTSTRAP_PROBLEM_HEADER
            )
            assert (adopter / "plans/.gitkeep").read_text(encoding="utf-8") == (
                BOOTSTRAP_FRESH_GITKEEP
            )
            assert _manifest_dependencies(manifest) == list(BOOTSTRAP_EXPECTED_FRESH_DEPENDENCIES)
            assert self.collisions == []
            assert config["local"] == "fresh-custom"
        else:
            assert (adopter / "knowledge/debt.md").read_text(encoding="utf-8") == (
                BOOTSTRAP_EXISTING_DEBT
            )
            assert (adopter / "knowledge/problems.md").read_text(encoding="utf-8") == (
                BOOTSTRAP_EXISTING_PROBLEMS
            )
            assert (adopter / "plans/.gitkeep").read_text(encoding="utf-8") == (
                BOOTSTRAP_EXISTING_GITKEEP
            )
            assert 'version = "1.4.2"' in manifest
            assert 'requires-python = ">=3.11"' in manifest
            assert _manifest_dependencies(manifest) == list(
                BOOTSTRAP_EXPECTED_EXISTING_DEPENDENCIES
            )
            assert "relay-own" in (adopter / "user-stories/index.md").read_text(
                encoding="utf-8"
            )
            assert "Local trailing section" in (
                adopter / "user-stories/index.md"
            ).read_text(encoding="utf-8")
            assert self.collisions == [
                "collision: path user-stories/alpha.md; core wins",
                "collision: slug alpha; core wins",
            ]
            assert config["local"] == "existing-custom"

    def test_fresh_enrollment_freezes_approval_before_writes(self) -> None:
        self.init_bootstrap_upstream()
        self.init_repo(self.adopter)
        assert not (self.adopter / "knowledge/debt.md").exists()
        self._commit_owner_notes()
        start = len(self.command_trace)
        self._enroll(editor_confirmed=True, before=None)
        self._assert_driver_trace(start)
        self._assert_transformations(fresh=True)
        assert not (self.adopter / "node_modules").exists()

    def test_existing_enrollment_transforms_predecessor_not_final_bytes(self) -> None:
        self.init_bootstrap_upstream()
        self.init_repo(self.adopter)
        for relative, text in BOOTSTRAP_EXISTING_FILES.items():
            self.write(self.adopter, relative, text)
        self._commit_owner_notes()
        before = {
            relative: (self.adopter / relative).read_bytes()
            for relative in BOOTSTRAP_EXISTING_FILES
        }
        requirements = _skill_dependency_requirements(BOOTSTRAP_SKILL)
        once = _union_manifest_dependencies(BOOTSTRAP_EXISTING_MANIFEST, requirements)
        assert _union_manifest_dependencies(once, requirements) == once
        assert (
            _union_manifest_dependencies(BOOTSTRAP_EXISTING_MANIFEST, ())
            == BOOTSTRAP_EXISTING_MANIFEST
        )
        assert (
            _union_manifest_dependencies(
                BOOTSTRAP_EXISTING_MANIFEST,
                _skill_dependency_requirements(BOOTSTRAP_SKILL_NO_DEPENDENCIES),
            )
            == BOOTSTRAP_EXISTING_MANIFEST
        )
        start = len(self.command_trace)
        self._enroll(editor_confirmed=True, before=dict(BOOTSTRAP_EXISTING_FILES))
        self._assert_driver_trace(start)
        adopter = self.adopter
        assert (adopter / "AGENTS.md").read_bytes() != before["AGENTS.md"]
        assert (adopter / ".opencode/agents/reviewer.md").read_bytes() != before[
            ".opencode/agents/reviewer.md"
        ]
        assert (adopter / "pyproject.toml").read_bytes() != before["pyproject.toml"]
        assert (adopter / "opencode.jsonc").read_bytes() != before["opencode.jsonc"]
        assert (adopter / "user-stories/index.md").read_bytes() != before[
            "user-stories/index.md"
        ]
        for relative in BOOTSTRAP_RETAINED_PATHS:
            assert (adopter / relative).read_bytes() == before[relative]
        self._assert_transformations(fresh=False)

    def test_pin_conflict_stops_before_destination_writes(self) -> None:
        self.init_bootstrap_upstream()
        self.init_repo(self.adopter)
        predecessor = dict(BOOTSTRAP_EXISTING_FILES)
        predecessor["pyproject.toml"] = BOOTSTRAP_CONFLICT_MANIFEST
        for relative, text in predecessor.items():
            self.write(self.adopter, relative, text)
        self._commit_owner_notes()
        before = self.worktree_bytes(self.adopter)
        with pytest.raises(PinConflict):
            self._enroll(editor_confirmed=True, before=predecessor)
        assert self.worktree_bytes(self.adopter) == before
        assert not (self.adopter / ".aicore").exists()

    def test_missing_approval_stops_before_writes(self) -> None:
        self.init_bootstrap_upstream()
        self.init_repo(self.adopter)
        self._commit_owner_notes()
        before = self.worktree_bytes(self.adopter)
        with pytest.raises(FrozenReviewMissing):
            self._enroll(editor_confirmed=True, before=None, approval=False)
        assert self.worktree_bytes(self.adopter) == before
        assert "missing_approval" in self.events
        assert "write_controls" not in self.events

    def test_mid_write_failure_stops_without_restore(self) -> None:
        self.init_bootstrap_upstream()
        self.init_repo(self.adopter)
        self._commit_owner_notes()
        start = len(self.command_trace)
        with pytest.raises(PartialWriteStopped):
            self._enroll(
                editor_confirmed=True, before=None, fail_after_content_writes=1
            )
        adopter = self.adopter
        assert (adopter / ".aicore/adoption.yaml").is_file()
        assert (adopter / ".aicore/adoption-review.yaml").is_file()
        assert (adopter / "AGENTS.md").is_file()
        assert not (adopter / "user-stories/index.md").exists()
        assert not (adopter / ".aicore/adoption.lock.yaml").exists()
        assert "stop_partial" in self.events
        for argv in self.command_trace[start:]:
            assert "restore" not in argv
            assert "reset" not in argv
            assert "stash" not in argv
            assert "clean" not in argv

    @pytest.mark.parametrize(
        "kind",
        (
            "staged",
            "unstaged",
            "untracked",
            "conflict",
            "editor",
            "repository",
            "skip_worktree",
        ),
    )
    def test_dirty_destination_aborts_before_mutation(self, kind: str) -> None:
        editor_confirmed: bool | None = True
        if kind == "repository":
            self.adopter = self.root / "not-a-repo"
            self.adopter.mkdir()
        else:
            self.init_repo(self.adopter)
            self._commit_owner_notes()
            if kind == "staged":
                self.write(self.adopter, "STAGED.md", "staged\n")
                self.stage(self.adopter, "STAGED.md")
            elif kind == "unstaged":
                self.write(self.adopter, "OWNER-NOTES.md", "dirty\n")
            elif kind == "untracked":
                self.write(self.adopter, "UNTRACKED.md", "new\n")
            elif kind == "conflict":
                self.write(self.adopter, "conflict.txt", "base\n")
                self.commit(self.adopter, "base")
                self.git(self.adopter, "checkout", "-b", "other")
                self.write(self.adopter, "conflict.txt", "other\n")
                self.commit(self.adopter, "other side")
                self.git(self.adopter, "checkout", "main")
                self.write(self.adopter, "conflict.txt", "main\n")
                self.commit(self.adopter, "main side")
                self.git(self.adopter, "merge", "other", check=False)
            elif kind == "editor":
                editor_confirmed = None
            elif kind == "skip_worktree":
                self.git(self.adopter, "update-index", "--skip-worktree", "OWNER-NOTES.md")
            else:
                raise AssertionError(kind)
        before = self.worktree_bytes(self.adopter)
        start = len(self.command_trace)
        with pytest.raises(CleanStartAbort):
            self._enroll(editor_confirmed=editor_confirmed, before=None)
        assert self.worktree_bytes(self.adopter) == before
        assert "abort" in self.events
        assert "write_controls" not in self.events
        for argv in self.command_trace[start:]:
            assert "add" not in argv
            assert "commit" not in argv
            assert "stash" not in argv
            assert "reset" not in argv
            assert "clean" not in argv
            assert "restore" not in argv

    @pytest.mark.parametrize(
        "relative",
        (
            ".aicore/adoption.yaml",
            ".aicore/adoption-review.yaml",
            ".aicore/adoption.lock.yaml",
            "plans/.gitkeep",
        ),
    )
    def test_t5_existing_ignored_occupant_aborts_before_write(self, relative: str) -> None:
        self.init_repo(self.adopter)
        self._commit_owner_notes()
        self.write(self.adopter, ".gitignore", relative + "\n")
        self.commit(self.adopter, "ignore planned write")
        occupant = "ignored occupant\n"
        self.write(self.adopter, relative, occupant)
        before = self.worktree_bytes(self.adopter)
        with pytest.raises(CleanStartAbort) as caught:
            self._enroll(editor_confirmed=True, before=None)
        assert str(caught.value) == f"ignored path would be overwritten: {relative}"
        assert self.worktree_bytes(self.adopter) == before
        assert (self.adopter / relative).read_text(encoding="utf-8") == occupant
        assert "write_controls" not in self.events
        assert "unsaved" not in str(caught.value)

    def test_t5_absent_ignore_rule_is_not_unsaved_occupant(self) -> None:
        self.init_bootstrap_upstream()
        self.init_repo(self.adopter)
        self.write(self.adopter, ".gitignore", "plans/.gitkeep\n")
        self._commit_owner_notes()
        assert not (self.adopter / "plans/.gitkeep").exists()
        reason = self._preflight(self.adopter, True)
        assert reason is None
        before = self.worktree_bytes(self.adopter)
        start = len(self.command_trace)
        with pytest.raises(FrozenReviewMissing):
            self._enroll(editor_confirmed=True, before=None, approval=False)
        assert self.worktree_bytes(self.adopter) == before
        assert "missing_approval" in self.events
        assert "write_controls" not in self.events
        assert "unsaved" not in " ".join(self.events)
        for argv in self.command_trace[start:]:
            assert "-f" not in argv
            assert "add" not in argv

    def test_t4_regular_and_linked_worktree_operation_paths(self) -> None:
        self.init_repo(self.adopter)
        self._commit_owner_notes()
        regular = _resolve_git_path(str(self.adopter), "MERGE_HEAD")
        assert regular is not None
        assert Path(regular).resolve() == (self.adopter / ".git" / "MERGE_HEAD").resolve()
        linked = self.root / "linked"
        self.git(self.adopter, "worktree", "add", "--detach", str(linked), "HEAD")
        assert (linked / ".git").is_file()
        assert self._preflight(linked, True) is None
        resolved = _resolve_git_path(str(linked), "MERGE_HEAD")
        assert resolved is not None
        assert resolved != str(linked / ".git" / "MERGE_HEAD")
        assert "worktrees" in resolved
        Path(resolved).write_text(self.rev(self.adopter) + "\n", encoding="utf-8")
        status = self._read(linked, *_STATUS_ARGS)
        assert status.returncode == 0
        assert status.stdout == b""
        assert self._preflight(linked, True) == "in-progress merge"

    @pytest.mark.parametrize(
        ("name", "kind", "reason"),
        (
            ("MERGE_HEAD", "file", "in-progress merge"),
            ("CHERRY_PICK_HEAD", "file", "in-progress operation"),
            ("REVERT_HEAD", "file", "in-progress operation"),
            ("rebase-merge", "directory", "in-progress rebase"),
            ("rebase-apply", "directory", "in-progress rebase"),
            ("sequencer", "directory", "in-progress operation"),
        ),
    )
    def test_t4_unfinished_operation_aborts_with_empty_porcelain(
        self, name: str, kind: str, reason: str
    ) -> None:
        self.init_repo(self.adopter)
        self._commit_owner_notes()
        resolved = _resolve_git_path(str(self.adopter), name)
        assert resolved is not None
        target = Path(resolved)
        if kind == "file":
            target.write_text(self.rev(self.adopter) + "\n", encoding="utf-8")
        else:
            target.mkdir()
        status = self._read(self.adopter, *_STATUS_ARGS)
        assert status.returncode == 0
        assert status.stdout == b""
        before = self.worktree_bytes(self.adopter)
        with pytest.raises(CleanStartAbort) as caught:
            self._enroll(editor_confirmed=True, before=None)
        assert str(caught.value) == reason
        assert self.worktree_bytes(self.adopter) == before
        assert "write_controls" not in self.events

    def test_t4_gitfile_and_clean_bisect_are_not_dirty(self) -> None:
        self.init_repo(self.adopter)
        self._commit_owner_notes()
        regular_bisect = _resolve_git_path(str(self.adopter), "BISECT_START")
        assert regular_bisect is not None
        Path(regular_bisect).write_text(self.rev(self.adopter) + "\n", encoding="utf-8")
        assert self._preflight(self.adopter, True) is None
        linked = self.root / "linked-bisect"
        self.git(self.adopter, "worktree", "add", "--detach", str(linked), "HEAD")
        assert (linked / ".git").is_file()
        linked_bisect = _resolve_git_path(str(linked), "BISECT_START")
        assert linked_bisect is not None
        assert "worktrees" in linked_bisect
        Path(linked_bisect).write_text(self.rev(self.adopter) + "\n", encoding="utf-8")
        assert self._preflight(linked, True) is None

    def test_t6_new_work_after_prepare_is_not_restored(self) -> None:
        self.init_bootstrap_upstream()
        self.init_repo(self.adopter)
        self._commit_owner_notes()

        def contaminate() -> None:
            self.write(self.adopter, "NEW.md", "sneaky\n")

        with pytest.raises(CleanStartAbort) as caught:
            self._enroll(editor_confirmed=True, before=None, after_prepare=contaminate)
        assert "unsaved" in str(caught.value)
        assert (self.adopter / "NEW.md").read_text(encoding="utf-8") == "sneaky\n"
        assert not (self.adopter / ".aicore").exists()
        assert not (self.adopter / "AGENTS.md").exists()
        assert "write_controls" not in self.events
        assert "recheck" in self.events
        assert "recheck_before_write" not in self.events


class RealCatalogEnrollmentTests(EngineTestCase, OrderedEnrollmentDriverMixin):
    """Fresh and existing enrollment against the shipped catalog and real corpus.

    Both flows drive the shared ordered driver. The fresh flow uses the null
    baseline and a reviewed whole-project ``test_runner`` with its literal
    destination grant; the existing flow accepts a predecessor lock and then
    reviews a transition bound to that baseline. Everything is built under
    ``tmp_path`` and the real checkout is only read.
    """

    def _copy_source_to(
        self, base: Path, source: str, destination: str, repository: Path
    ) -> None:
        origin = repository / source
        target = self._confined_path(base / destination, "catalog copy target")
        if origin.is_dir():
            for path in sorted(origin.rglob("*")):
                if not path.is_file():
                    continue
                relative = path.relative_to(origin)
                if _real_catalog_excluded(relative):
                    continue
                written = self._confined_path(
                    base / f"{destination.rstrip('/')}/{relative.as_posix()}",
                    "catalog copy target",
                )
                written.parent.mkdir(parents=True, exist_ok=True)
                written.write_bytes(path.read_bytes())
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(origin.read_bytes())

    def _profile(self) -> dict[str, bool]:
        return {"backend_stack": True, "python_scripts": True, "ticket_system": True}

    def _init_real_catalog(self) -> tuple[dict[str, object], dict[str, bool]]:
        """Copy the shipped catalog and complete corpus into the temporary upstream."""
        repository = repository_root()
        catalog_text = (repository / CATALOG_REL).read_text(encoding="utf-8")
        catalog = yaml.safe_load(catalog_text)
        assert isinstance(catalog, dict)
        profile = self._profile()
        self.init_repo(self.upstream)
        self.write(self.upstream, CATALOG_REL, catalog_text)
        self._real_catalog_source(catalog, profile, repository)
        self.commit(self.upstream, "shipped catalog source")
        return catalog, profile

    def _real_catalog_declaration(
        self,
        catalog: dict[str, object],
        profile: dict[str, bool],
        test_runner: dict[str, object],
    ) -> dict[str, object]:
        """Declare every catalog unit at the reviewed profile and runner."""
        units: list[dict[str, object]] = []
        for unit in cast(list[dict[str, object]], catalog["units"]):
            uid = str(unit["id"])
            if not evaluate_applicability(unit, profile):
                units.append({"id": uid, "mode": "not_applicable"})
            elif uid == _REAL_CATALOG_ROOT_UNIT:
                units.append(
                    {"id": uid, "mode": "adapted", "members": _real_catalog_members(unit)}
                )
            elif unit.get("sync_projection") == "assertions":
                units.append({"id": uid, "mode": "mirror"})
            elif uid in _REAL_CATALOG_ADAPTED_UNITS:
                units.append(
                    {"id": uid, "mode": "adapted", "members": _real_catalog_members(unit)}
                )
            else:
                units.append(
                    {"id": uid, "mode": "mirror", "members": _real_catalog_members(unit)}
                )
        return {
            "schema_version": 2,
            "upstream_repository": cast(
                dict[str, object], catalog["catalog"]
            )["upstream_repository"],
            "profile": profile,
            "test_runner": test_runner,
            "units": units,
        }

    def _real_catalog_source(
        self, catalog: dict[str, object], profile: dict[str, bool], repository: Path
    ) -> None:
        """Copy the complete applicable corpus into the temporary upstream."""
        for unit in cast(list[dict[str, object]], catalog["units"]):
            if not evaluate_applicability(unit, profile):
                continue
            if unit.get("sync_projection") == "assertions":
                continue
            for member in cast(list[dict[str, object]], unit["members"]):
                source = str(member["source"])
                self._copy_source_to(self.upstream, source, source, repository)
        self._copy_source_to(
            self.upstream,
            "user-stories/index.md",
            "user-stories/index.md",
            repository,
        )

    def _read_tree(self, origin: Path, destination: str, prepared: dict[str, str]) -> None:
        """Read one member (file or tree) from the selected source into buffers."""
        if origin.is_dir():
            for path in sorted(origin.rglob("*")):
                if not path.is_file():
                    continue
                relative = path.relative_to(origin)
                if _real_catalog_excluded(relative):
                    continue
                rendered = f"{destination.rstrip('/')}/{relative.as_posix()}"
                prepared[rendered] = path.read_text(encoding="utf-8")
        else:
            prepared[destination] = origin.read_text(encoding="utf-8")

    def _real_catalog_prepare(
        self,
        catalog: dict[str, object],
        declaration: dict[str, object],
        profile: dict[str, bool],
        before: dict[str, str] | None,
        test_runner: dict[str, object],
    ) -> tuple[dict[str, str], list[str]]:
        """Prepare every destination result outside the destination.

        Protected documents mirror the selected source; the root is prepared
        from destination identity; the debt register is created from the
        catalog's 0-entry template source and the problem register from its
        structural header; the story index is merged from the source rows.
        """
        before_map = before or {}
        declarations = {
            str(unit["id"]): unit
            for unit in cast(list[dict[str, object]], declaration["units"])
        }
        prepared: dict[str, str] = {}
        prepared["AGENTS.md"] = _prepare_root(
            (self.upstream / "AGENTS.md").read_text(encoding="utf-8"),
            before_map.get("AGENTS.md"),
        )
        debt_source = (self.upstream / _debt_source_path(catalog)).read_text(
            encoding="utf-8"
        )
        prepared["knowledge/debt.md"] = _enroll_member(
            before_map.get("knowledge/debt.md"), debt_source, REAL_CATALOG_DEBT_HEADER
        )
        symptoms_source = (self.upstream / "knowledge/symptoms.md").read_text(
            encoding="utf-8"
        )
        problems_source = (self.upstream / "knowledge/problems.md").read_text(
            encoding="utf-8"
        )
        prepared["knowledge/symptoms.md"] = _enroll_member(
            before_map.get("knowledge/symptoms.md"),
            symptoms_source,
            REAL_CATALOG_SYMPTOMS,
        )
        prepared["knowledge/problems.md"] = _enroll_member(
            before_map.get("knowledge/problems.md"),
            problems_source,
            REAL_CATALOG_PROBLEM_HEADER,
        )
        for unit in cast(list[dict[str, object]], catalog["units"]):
            uid = str(unit["id"])
            if not evaluate_applicability(unit, profile):
                continue
            if unit.get("sync_projection") == "assertions":
                continue
            if uid == _REAL_CATALOG_ROOT_UNIT or uid in _REAL_CATALOG_ADAPTED_UNITS:
                continue
            declared = {
                str(member["id"]): str(member["destination"])
                for member in cast(
                    list[dict[str, object]], declarations[uid].get("members", [])
                )
            }
            for member in cast(list[dict[str, object]], unit["members"]):
                source = str(member["source"])
                destination = declared[str(member["id"])]
                self._read_tree(self.upstream / source, destination, prepared)
        if test_runner.get("no_tests") is True:
            prepared["opencode.jsonc"] = _real_catalog_opencode_config(catalog)
        else:
            prepared["opencode.jsonc"] = _real_catalog_runner_config(catalog)
        prepared[".gitignore"] = _real_catalog_gitignore(catalog)
        story_members = self._real_catalog_story_members(catalog, declaration)
        core_index = (self.upstream / "user-stories/index.md").read_text(encoding="utf-8")
        before_index = before_map.get("user-stories/index.md")
        merged, collisions = merge_story_index(
            core_index.encode("utf-8"),
            None if before_index is None else before_index.encode("utf-8"),
            story_members,
        )
        prepared["user-stories/index.md"] = merged.decode("utf-8")
        return prepared, collisions

    def _real_catalog_story_members(
        self, catalog: dict[str, object], declaration: dict[str, object]
    ) -> list[StoryMergeMember]:
        """Collect the applicable portable story rows for the index merge."""
        declarations = {
            str(unit["id"]): unit
            for unit in cast(list[dict[str, object]], declaration["units"])
        }
        members: list[StoryMergeMember] = []
        for unit in cast(list[dict[str, object]], catalog["units"]):
            if unit.get("kind") != _REAL_CATALOG_STORY_KIND:
                continue
            decl_unit = declarations[str(unit["id"])]
            if decl_unit.get("mode") == "not_applicable":
                continue
            declared = {
                str(member["id"]): str(member["destination"])
                for member in cast(
                    list[dict[str, object]], decl_unit.get("members", [])
                )
            }
            for member in cast(list[dict[str, object]], unit["members"]):
                policy = member.get("collision_policy")
                members.append(
                    {
                        "id": str(member["id"]),
                        "destination": declared[str(member["id"])],
                        "collision_policy": (
                            str(policy) if policy is not None else None
                        ),
                    }
                )
        return members

    def _real_catalog_review(
        self,
        catalog: dict[str, object],
        declaration_text: str,
        prepared: dict[str, str],
        *,
        target: str,
        baseline_lock_digest: str | None,
    ) -> str:
        """Bind each protected or reconciled unit to the prepared result."""
        declaration = yaml.safe_load(declaration_text)
        assert isinstance(declaration, dict)
        upstream = _GitRepo(str(self.upstream))
        files = {
            relative: ("100644", text.encode("utf-8"))
            for relative, text in prepared.items()
        }
        declarations = {
            str(unit["id"]): unit
            for unit in cast(list[dict[str, object]], declaration["units"])
        }
        decisions: list[dict[str, object]] = []
        for unit in cast(list[dict[str, object]], catalog["units"]):
            uid = str(unit["id"])
            decl_unit = declarations[uid]
            mode = str(decl_unit.get("mode"))
            protected = bool(unit.get("rule_documents"))
            if mode == "not_applicable":
                continue
            if not (
                protected or mode in ("adapted", "replacement", "destination_owned")
            ):
                continue
            document: dict[str, object] = {
                "unit": uid,
                "decision": "applied",
                "reviewer": "test-suite",
                "evidence": (
                    "Reviewed the shipped catalog unit against the prepared destination."
                ),
                "reviewed_upstream_digest": _unit_upstream_digest(upstream, target, unit),
                "reviewed_destination_digest": _external_unit_digest(
                    unit, decl_unit, files
                ),
            }
            if protected:
                document["verified_layout"] = RULE_LAYOUT_VALUE
            decisions.append(document)
        review = {
            "schema_version": 2,
            "upstream_repository": cast(
                dict[str, object], catalog["catalog"]
            )["upstream_repository"],
            "transition": {
                "baseline_lock_digest": baseline_lock_digest,
                "target_source_commit": target,
                "declaration_digest": _sha256(declaration_text.encode("utf-8")),
            },
            "decisions": decisions,
        }
        return yaml.safe_dump(review, sort_keys=False)

    def _worktree_text(self, repo: Path) -> dict[str, str]:
        """Read destination text so a transition can retain owner register bytes."""
        return {
            str(path.relative_to(repo)): path.read_text(encoding="utf-8")
            for path in repo.rglob("*")
            if path.is_file() and path.relative_to(repo).parts[0] != ".git"
        }

    def _assert_real_catalog_enrolled(self, catalog: dict[str, object]) -> None:
        """Assert the complete applicable corpus is enrolled as protected."""
        adopter = self.adopter
        lock = yaml.safe_load(self.proposal_stdout)
        assert isinstance(lock, dict)
        modes = {str(row["id"]): str(row.get("mode")) for row in lock["units"]}
        assert modes[_REAL_CATALOG_ROOT_UNIT] == "adapted"
        assert modes["knowledge-debt"] == "adapted"
        assert modes["symptom-problem-register"] == "adapted"
        rule_documents = sorted(
            {
                str(document)
                for unit in cast(list[dict[str, object]], catalog["units"])
                for document in (unit.get("rule_documents") or [])
            }
        )
        assert rule_documents, "the real catalog must declare protected rule documents"
        for document in rule_documents:
            destination = (adopter / document).read_text(encoding="utf-8")
            source = (self.upstream / document).read_text(encoding="utf-8")
            destination_layout, destination_violation = _scan_rule_layout(destination)
            source_layout, source_violation = _scan_rule_layout(source)
            assert destination_layout is not None, (document, destination_violation)
            assert source_layout is not None, (document, source_violation)
            assert destination_layout.mandatory == source_layout.mandatory, document
        debt = (adopter / "knowledge/debt.md").read_text(encoding="utf-8")
        problems = (adopter / "knowledge/problems.md").read_text(encoding="utf-8")
        assert "DEBT-001" not in debt
        assert "P-001" not in problems
        index = (adopter / "user-stories/index.md").read_text(encoding="utf-8")
        assert "aicore-adoption-sync" not in index
        assert "`plan-enforce`" in index
        assert (adopter / "OWNER-NOTES.md").read_text(encoding="utf-8") == (
            "unrelated owner work\n"
        )

    def test_real_catalog_fresh_enrollment_orders_runner_flow(self) -> None:
        catalog, profile = self._init_real_catalog()
        declaration = self._real_catalog_declaration(catalog, profile, AICORE_RUNNER)
        declaration_text = yaml.safe_dump(declaration, sort_keys=False)
        self.init_repo(self.adopter)
        self.write(self.adopter, "OWNER-NOTES.md", "unrelated owner work\n")
        self.commit(self.adopter, "owner notes")
        start = len(self.command_trace)
        self._ordered_enroll(
            editor_confirmed=True,
            before=None,
            prepare=lambda before: self._real_catalog_prepare(
                catalog, declaration, profile, before, AICORE_RUNNER
            ),
            declaration_text=declaration_text,
            build_review=lambda prepared, text: self._real_catalog_review(
                catalog,
                text,
                prepared,
                target=self.rev(self.upstream),
                baseline_lock_digest=None,
            ),
        )
        self._assert_driver_trace(start)
        self._assert_real_catalog_enrolled(catalog)
        config = json.loads((self.adopter / "opencode.jsonc").read_text(encoding="utf-8"))
        executor = str(AICORE_RUNNER["executor"])
        bash = config["agent"][executor]["permission"]["bash"]
        assert bash["*"] == "deny"
        assert bash[AICORE_SUITE_COMMAND] == "allow"

    def test_real_catalog_existing_enrollment_transitions_ordered(self) -> None:
        catalog, profile = self._init_real_catalog()
        declaration = self._real_catalog_declaration(catalog, profile, NO_TESTS_RUNNER)
        declaration_text = yaml.safe_dump(declaration, sort_keys=False)
        self.init_repo(self.adopter)
        self.write(self.adopter, "OWNER-NOTES.md", "unrelated owner work\n")
        self.commit(self.adopter, "owner notes")
        # Predecessor: the same ordered driver accepts the complete enrollment.
        self._ordered_enroll(
            editor_confirmed=True,
            before=None,
            prepare=lambda before: self._real_catalog_prepare(
                catalog, declaration, profile, before, NO_TESTS_RUNNER
            ),
            declaration_text=declaration_text,
            build_review=lambda prepared, text: self._real_catalog_review(
                catalog,
                text,
                prepared,
                target=self.rev(self.upstream),
                baseline_lock_digest=None,
            ),
        )
        self.commit(self.adopter, "accept predecessor lock")
        # An existing destination-owned register keeps local rows across the
        # reviewed transition; the source registers are never copied in.
        self.write(
            self.adopter,
            "knowledge/debt.md",
            REAL_CATALOG_DEBT_HEADER + "\nDEBT-014 Relay keeps this local deferral.\n",
        )
        self.write(
            self.adopter,
            "knowledge/problems.md",
            REAL_CATALOG_PROBLEM_HEADER
            + "\nP-014 Relay keeps this local problem row.\n",
        )
        self.commit(self.adopter, "owner register rows")
        baseline_lock_digest = _raw_file_digest(
            str(self.adopter / ".aicore/adoption.lock.yaml")
        )
        advanced = (self.upstream / "knowledge/agents.md").read_text(encoding="utf-8")
        self.write(
            self.upstream,
            "knowledge/agents.md",
            advanced + "\nTRANSITION_MANDATORY_LINE\n",
        )
        self.commit(self.upstream, "advance protected rule document")
        before = self._worktree_text(self.adopter)
        start = len(self.command_trace)
        self._ordered_enroll(
            editor_confirmed=True,
            before=before,
            prepare=lambda current: self._real_catalog_prepare(
                catalog, declaration, profile, current, NO_TESTS_RUNNER
            ),
            declaration_text=declaration_text,
            build_review=lambda prepared, text: self._real_catalog_review(
                catalog,
                text,
                prepared,
                target=self.rev(self.upstream),
                baseline_lock_digest=baseline_lock_digest,
            ),
            baseline_lock=True,
        )
        self._assert_driver_trace(start)
        self._assert_real_catalog_enrolled(catalog)
        debt = (self.adopter / "knowledge/debt.md").read_text(encoding="utf-8")
        problems = (self.adopter / "knowledge/problems.md").read_text(encoding="utf-8")
        assert "DEBT-014" in debt
        assert "P-014" in problems
        lock = yaml.safe_load(self.proposal_stdout)
        assert isinstance(lock, dict)
        assert lock["accepted_source_commit"] == self.rev(self.upstream)
        declaration_document = yaml.safe_load(
            (self.adopter / ".aicore/adoption.yaml").read_text(encoding="utf-8")
        )
        assert declaration_document["test_runner"]["no_tests"] is True
