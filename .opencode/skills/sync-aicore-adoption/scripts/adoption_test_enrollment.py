"""Shared enrollment helpers for the adoption tests.

This is a non-collected support module (``adoption_test_*``). It holds the
clean-start enrollment driver, declaration/manifest preparation helpers, and
the real-catalog helpers shared by the concern-scoped enrollment test modules.
It defines no collected test class.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import cast

import yaml

from adoption_constants import AICORE_SUITE_COMMAND
from adoption_content import _rule_layout
from adoption_contracts import StoryMergeMember
from adoption_git import _resolve_git_path, _run_controlled_read
from adoption_stories import merge_story_index
from adoption_test_acceptance_data import (
    BOOTSTRAP_ADOPTED_PATHS,
    BOOTSTRAP_AGENT_EXTENSION,
    BOOTSTRAP_ASSERTION_CONTAINS,
    BOOTSTRAP_FORBIDDEN_COMMANDS,
    BOOTSTRAP_FRESH_CONFIG,
)
from adoption_test_data import CATALOG_REL
from adoption_test_prepared import _check_index, _propose_index
from adoption_test_repos import AdopterFixture
from adoption_test_runner_data import AICORE_RUNNER


class PinConflict(Exception):
    """A prepared skill pin disagrees with an existing manifest pin."""

    def __init__(self, name: str, existing: str, required: str) -> None:
        self.name = name
        self.existing = existing
        self.required = required
        super().__init__(
            f"{name} pin {existing} conflicts with required {required}"
        )


class FrozenReviewMissing(Exception):
    """An adopted-content write was attempted without the frozen review file."""


class CleanStartAbort(Exception):
    """Whole-destination preflight refused before any destination mutation."""


class PartialWriteStopped(Exception):
    """A simulated write failure stopped the run without restoration."""


_DEPENDENCY_SLOT = re.compile(r"^dependencies = (\[.*\])$", re.MULTILINE)
_ENROLL_EVENTS = (
    "preflight",
    "prepare_external",
    "recheck",
    "freeze_controls",
    "recheck_before_write",
    "write_controls",
    "write_content",
    "stage_reviewed",
    "propose",
    "check_candidate",
    "stage_lock_only",
    "check_final",
)
_PLANNED_WRITE_PATHS: tuple[str, ...] = (
    *BOOTSTRAP_ADOPTED_PATHS,
    ".aicore/adoption.yaml",
    ".aicore/adoption-review.yaml",
    ".aicore/adoption.lock.yaml",
)
_OPERATION_PATHS: tuple[tuple[str, str, str], ...] = (
    ("MERGE_HEAD", "file", "in-progress merge"),
    ("CHERRY_PICK_HEAD", "file", "in-progress operation"),
    ("REVERT_HEAD", "file", "in-progress operation"),
    ("rebase-merge", "directory", "in-progress rebase"),
    ("rebase-apply", "directory", "in-progress rebase"),
    ("sequencer", "directory", "in-progress operation"),
)
_STATUS_ARGS: tuple[str, ...] = (
    "status",
    "--porcelain=v2",
    "-z",
    "--untracked-files=all",
    "--ignore-submodules=none",
)


def _skill_dependency_requirements(skill_text: str) -> tuple[str, ...]:
    """Read dependency pins from one enrolled skill's prepared metadata."""
    if not skill_text.startswith("---\n"):
        return ()
    end = skill_text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("enrolled skill frontmatter is not closed")
    document = yaml.safe_load(skill_text[4:end])
    if not isinstance(document, dict):
        return ()
    metadata = document.get("metadata")
    if not isinstance(metadata, dict):
        return ()
    dependencies = metadata.get("dependencies") or []
    if not isinstance(dependencies, list):
        raise ValueError("skill metadata.dependencies must be a list")
    return tuple(str(item) for item in dependencies)


def _manifest_dependencies(manifest: str) -> list[str]:
    match = _DEPENDENCY_SLOT.search(manifest)
    if match is None:
        raise ValueError("manifest has no dependencies slot")
    parsed = ast.literal_eval(match.group(1))
    if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
        raise ValueError("dependencies slot must be a list of strings")
    return list(parsed)


def _pin(spec: str) -> tuple[str, str]:
    name, separator, version = spec.partition("==")
    if not separator or not name or not version:
        raise ValueError(f"dependency is not an exact pin: {spec}")
    return name, version


def _union_manifest_dependencies(before: str, requirements: tuple[str, ...]) -> str:
    """Edit only the dependencies slot. Conflicts abort; empty union is a no-op."""
    current = _manifest_dependencies(before)
    if not requirements:
        return before
    present = {name: version for name, version in (_pin(item) for item in current)}
    merged = list(current)
    for requirement in requirements:
        name, version = _pin(requirement)
        if name in present:
            if present[name] != version:
                raise PinConflict(name, present[name], version)
            continue
        merged.append(requirement)
        present[name] = version
    if merged == current:
        return before
    rendered = "[" + ", ".join(f'"{item}"' for item in merged) + "]"
    match = _DEPENDENCY_SLOT.search(before)
    assert match is not None
    return before[: match.start(1)] + rendered + before[match.end(1) :]


def _prepare_config(before: str | None) -> str:
    """Return valid JSONC containing the required assertion.

    An existing document is edited inside the object. The assertion is never
    appended after the JSON document.
    """
    if before is None:
        rendered = BOOTSTRAP_FRESH_CONFIG
    else:
        if BOOTSTRAP_ASSERTION_CONTAINS in before:
            raise AssertionError("existing config must not already contain the assertion")
        document = json.loads(before)
        if not isinstance(document, dict):
            raise AssertionError("existing config must be a JSON object")
        permission = document.get("permission")
        if not isinstance(permission, dict):
            permission = {}
        bash = permission.get("bash")
        if not isinstance(bash, dict):
            bash = {}
        bash["sudo *"] = "deny"
        permission["bash"] = bash
        document["permission"] = permission
        rendered = json.dumps(document, indent=2) + "\n"
    parsed = json.loads(rendered)
    if not isinstance(parsed, dict) or not rendered.strip().endswith("}"):
        raise AssertionError("prepared config is not a JSON object")
    if BOOTSTRAP_ASSERTION_CONTAINS not in rendered:
        raise AssertionError("prepared config is missing the required assertion")
    return rendered


def _prepare_root(source: str, before: str | None) -> str:
    """Build a destination root from identity plus the source mandatory bytes."""
    source_layout = _rule_layout(source)
    assert source_layout is not None
    spec_match = re.search(
        r"^> \*\*Spec version:\*\* (\d+\.\d+\.\d+)\s*$", source, re.MULTILINE
    )
    assert spec_match is not None
    spec = spec_match.group(1)
    mandatory = source_layout.mandatory.decode("utf-8")
    if before is None:
        framing = (
            "# Relay Runtime\n"
            "> **Project identity:** Relay\n"
            f"> **Spec version:** {spec}\n"
            "> **Local version:** 1.0.0\n"
            "> **Rule layout:** two-section-v1\n"
            "\n"
        )
        extensions = "## Project extensions\n\nDestination-local extension rules.\n\n"
        return framing + extensions + mandatory
    before_layout = _rule_layout(before)
    assert before_layout is not None
    framing = re.sub(
        r"(^> \*\*Spec version:\*\* )\d+\.\d+\.\d+",
        rf"\g<1>{spec}",
        before_layout.framing.decode("utf-8"),
        count=1,
        flags=re.MULTILINE,
    )
    return framing + before_layout.extensions.decode("utf-8") + mandatory


def _prepare_agent(source: str, before: str | None) -> str:
    """Replace agent extensions from destination identity; keep source mandatory."""
    source_layout = _rule_layout(source)
    assert source_layout is not None
    extensions = (
        "## Project extensions\n\n" + BOOTSTRAP_AGENT_EXTENSION.rstrip("\n") + "\n\n"
    )
    mandatory = source_layout.mandatory.decode("utf-8")
    if before is None:
        framing = source_layout.framing.decode("utf-8").replace(
            "# Reviewer\n", "# Reviewer — Relay\n", 1
        )
        return framing + extensions + mandatory
    before_layout = _rule_layout(before)
    assert before_layout is not None
    return before_layout.framing.decode("utf-8") + extensions + mandatory


def _enroll_member(before: str | None, source: str, created: str) -> str:
    """Retain an existing owner member, or create the absent-only header."""
    if before is None:
        return created
    if before == source:
        raise AssertionError("existing member bytes must differ from the source")
    return before


def _prepare_story_index(
    source_index: str, before: str | None
) -> tuple[str, list[str]]:
    members: list[StoryMergeMember] = [
        {
            "id": "alpha",
            "destination": "user-stories/alpha.md",
            "collision_policy": "core_wins",
        }
    ]
    merged, collisions = merge_story_index(
        source_index.encode("utf-8"),
        None if before is None else before.encode("utf-8"),
        members,
    )
    return merged.decode("utf-8"), collisions


class OrderedEnrollmentDriverMixin:
    """Ordered clean-start driver reused by synthetic and real-catalog flows.

    The driver owns the reviewed sequence: controlled preflight, external
    complete preparation, recheck, freeze controls, recheck before write, write
    controls then content, stage reviewed paths, propose an external candidate,
    check that candidate, install the lock only, and final-check. Preparation,
    declaration, and review generation are supplied by the caller.
    """

    def _fixture(self, accepted: str) -> AdopterFixture:
        return {
            "accepted": accepted,
            "target": self.rev(self.upstream),
            "adopter_rev": accepted,
            "upstream": self.upstream,
            "adopter": self.adopter,
            "catalog": self.upstream / CATALOG_REL,
            "declaration": self.adopter / ".aicore/adoption.yaml",
            "review": self.adopter / ".aicore/adoption-review.yaml",
            "lock": self.adopter / ".aicore/adoption.lock.yaml",
        }

    def _write_adopted(
        self,
        adopter: Path,
        relative: str,
        text: str,
        declaration_text: str,
        review_text: str,
    ) -> None:
        review = adopter / ".aicore/adoption-review.yaml"
        declaration = adopter / ".aicore/adoption.yaml"
        if not review.is_file() or review.read_text(encoding="utf-8") != review_text:
            raise FrozenReviewMissing("frozen review file is absent")
        if (
            not declaration.is_file()
            or declaration.read_text(encoding="utf-8") != declaration_text
        ):
            raise FrozenReviewMissing("frozen declaration file is absent")
        self.write(adopter, relative, text)

    def _assert_driver_trace(self, start: int) -> list[tuple[str, ...]]:
        trace = self.command_trace[start:]
        assert trace, "the test driver recorded no commands"
        for argv in trace:
            rendered = " ".join(argv)
            for forbidden in BOOTSTRAP_FORBIDDEN_COMMANDS:
                assert forbidden not in rendered, rendered
            for mutation in ("stash", "reset", "clean", "restore"):
                assert mutation not in argv, rendered
            if "sync_aicore_adoption.py" in rendered:
                assert "propose-lock" in argv or "check" in argv, rendered
            else:
                assert argv[0] == "git", rendered
        return trace

    def _read(self, repo: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
        """Inspect through the shared controlled read. Fixture mutations stay on ``git``."""
        return _run_controlled_read(str(repo), args)

    def _in_progress_operation(self, repo: Path) -> str | None:
        """Resolve policy paths with ``--git-path``. A gitfile is not dirtiness."""
        for name, kind, reason in _OPERATION_PATHS:
            resolved = _resolve_git_path(str(repo), name)
            if resolved is None:
                return "cleanliness cannot be confirmed"
            path = Path(resolved)
            if kind == "file" and path.is_file():
                return reason
            if kind == "directory" and path.exists():
                return reason
        return None

    def _index_flag_block(self, payload: bytes) -> str | None:
        """Abort on skip-worktree, assume-unchanged, or an unknown index flag."""
        for raw in payload.split(b"\0"):
            if not raw:
                continue
            flag = chr(raw[0])
            if flag == "H":
                continue
            if flag == "S" or flag.islower():
                return "assume-unchanged or skip-worktree entry"
            return "cleanliness cannot be confirmed"
        return None

    def _ignored_write_occupant(self, repo: Path) -> str | None:
        """Block an existing ignored occupant. An absent ignore-rule path is not one."""
        for relative in _PLANNED_WRITE_PATHS:
            ignored = self._read(repo, "check-ignore", "-q", "--", relative)
            if ignored.returncode not in (0, 1):
                return "cleanliness cannot be confirmed"
            if ignored.returncode != 0:
                continue
            occupant = repo / relative
            if occupant.exists() or occupant.is_symlink():
                return f"ignored path would be overwritten: {relative}"
        return None

    def _preflight(self, repo: Path, editor_confirmed: bool | None) -> str | None:
        """Read-only whole-destination gate. Uncertainty blocks; it does not default true."""
        if editor_confirmed is not True:
            return "saved-editor confirmation is required"
        inside = self._read(repo, "rev-parse", "--is-inside-work-tree")
        if inside.returncode != 0 or inside.stdout.strip() != b"true":
            return "repository state is unknown"
        head = self._read(repo, "rev-parse", "--verify", "HEAD")
        if head.returncode != 0:
            return "destination has no committed HEAD"
        operation = self._in_progress_operation(repo)
        if operation is not None:
            return operation
        status = self._read(repo, *_STATUS_ARGS)
        if status.returncode != 0:
            return "cleanliness cannot be confirmed"
        if status.stdout:
            return "destination has unsaved or uncommitted work"
        flags = self._read(repo, "ls-files", "-v", "-z")
        if flags.returncode != 0:
            return "cleanliness cannot be confirmed"
        flag_block = self._index_flag_block(flags.stdout)
        if flag_block is not None:
            return flag_block
        return self._ignored_write_occupant(repo)

    def _ordered_enroll(
        self,
        *,
        editor_confirmed: bool | None,
        before: dict[str, str] | None,
        prepare: "Callable[[dict[str, str] | None], tuple[dict[str, str], list[str]]]",
        declaration_text: str,
        build_review: "Callable[[dict[str, str], str], str]",
        baseline_lock: bool = False,
        fail_after_content_writes: int | None = None,
        approval: bool = True,
        after_prepare: Callable[[], None] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        """Run one ordered enrollment over caller-supplied preparation."""
        adopter = self.adopter
        self.events: list[str] = []
        reason = self._preflight(adopter, editor_confirmed)
        self.events.append("preflight")
        if reason is not None:
            self.events.append("abort")
            raise CleanStartAbort(reason)
        prepared, collisions = prepare(before)
        self.collisions = collisions
        self.events.append("prepare_external")
        if after_prepare is not None:
            after_prepare()
        reason = self._preflight(adopter, editor_confirmed)
        self.events.append("recheck")
        if reason is not None:
            self.events.append("abort")
            raise CleanStartAbort(reason)
        if not approval:
            self.events.append("missing_approval")
            raise FrozenReviewMissing("review was not frozen")
        review_text = build_review(prepared, declaration_text)
        self.events.append("freeze_controls")
        reason = self._preflight(adopter, editor_confirmed)
        self.events.append("recheck_before_write")
        if reason is not None:
            self.events.append("abort")
            raise CleanStartAbort(reason)
        self.write(adopter, ".aicore/adoption.yaml", declaration_text)
        self.write(adopter, ".aicore/adoption-review.yaml", review_text)
        self.events.append("write_controls")
        written = 0
        for relative, text in prepared.items():
            if (
                fail_after_content_writes is not None
                and written >= fail_after_content_writes
            ):
                self.events.append("stop_partial")
                raise PartialWriteStopped(relative)
            self._write_adopted(adopter, relative, text, declaration_text, review_text)
            written += 1
        frozen_review = (adopter / ".aicore/adoption-review.yaml").read_bytes()
        self.events.append("write_content")
        assert (adopter / ".aicore/adoption-review.yaml").read_bytes() == frozen_review
        self.stage(
            adopter,
            ".aicore/adoption.yaml",
            ".aicore/adoption-review.yaml",
            *prepared,
        )
        self.events.append("stage_reviewed")
        fixture = self._fixture(self.rev(self.upstream))
        proposal = _propose_index(self, fixture, update=baseline_lock)
        self.events.append("propose")
        self.assert_exit(proposal, 0)
        candidate = self.write(self.root, "ordered-candidate.lock.yaml", proposal.stdout)
        checked = _check_index(self, fixture, lock=candidate, json_output=True)
        self.events.append("check_candidate")
        self.assert_exit(checked, 0)
        report = json.loads(checked.stdout)
        assert report["compliance"] is True
        assert report["diagnostic"] is False
        assert report["blocking_reasons"] == []
        self.write(adopter, ".aicore/adoption.lock.yaml", proposal.stdout)
        self.stage(adopter, ".aicore/adoption.lock.yaml")
        self.events.append("stage_lock_only")
        final = _check_index(self, fixture, json_output=True)
        self.events.append("check_final")
        self.assert_exit(final, 0)
        final_report = json.loads(final.stdout)
        assert final_report["compliance"] is True
        assert final_report["diagnostic"] is False
        assert final_report["blocking_reasons"] == []
        assert self.events == list(_ENROLL_EVENTS)
        self.proposal_stdout = proposal.stdout
        return proposal


_REAL_CATALOG_ROOT_UNIT = "root-runtime-spec"
_REAL_CATALOG_ADAPTED_UNITS = frozenset({"knowledge-debt", "symptom-problem-register"})
_REAL_CATALOG_STORY_KIND = "user-story"
_REAL_CATALOG_COPY_SKIP = frozenset({"__pycache__", ".git"})


def _real_catalog_excluded(relative: Path) -> bool:
    """Return whether a copied corpus path is generated rather than source."""
    return any(
        part in _REAL_CATALOG_COPY_SKIP or part.endswith(".pyc")
        for part in relative.parts
    )


def _real_catalog_members(unit: dict[str, object]) -> list[dict[str, str]]:
    """Map one catalog unit's member ids to their declared destination paths."""
    return [
        {"id": str(member["id"]), "destination": str(member["destination"])}
        for member in cast(list[dict[str, object]], unit["members"])
    ]


def _real_catalog_assertions(
    catalog: dict[str, object], unit_id: str
) -> list[dict[str, object]]:
    """Return one catalog config unit's reviewed assertion entries."""
    unit = next(
        item
        for item in cast(list[dict[str, object]], catalog["units"])
        if str(item["id"]) == unit_id
    )
    return list(cast(list[dict[str, object]], unit.get("assertions", [])))


def _real_catalog_bash_fragment(catalog: dict[str, object]) -> dict[str, str]:
    """Build the destination bash mapping from the catalog's key/value assertions.

    The opencode-config assertions are JSON ``key: value`` fragments, so the
    destination fragment is a projection of the catalog rather than a
    hand-copied token table. A renamed or reformatted assertion fails here.
    """
    fragment: dict[str, str] = {}
    for assertion in _real_catalog_assertions(catalog, "opencode-config"):
        contains = str(assertion["contains"])
        parsed = json.loads("{" + contains + "}")
        if not isinstance(parsed, dict) or len(parsed) != 1:
            raise AssertionError(
                f"opencode-config assertion {assertion['id']!r} is not a key/value pair"
            )
        for key, value in parsed.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise AssertionError(
                    f"opencode-config assertion {assertion['id']!r} is not a string pair"
                )
            fragment[key] = value
    return fragment


def _real_catalog_gitignore_fragment(catalog: dict[str, object]) -> str:
    """Build the destination ignore lines from the catalog's ignore assertions."""
    lines = [
        str(assertion["contains"])
        for assertion in _real_catalog_assertions(catalog, "gitignore-config")
    ]
    return "\n".join(lines) + "\n"


def _real_catalog_opencode_config(catalog: dict[str, object]) -> str:
    """A destination config carrying the catalog's reviewed assertions."""
    return (
        json.dumps(
            {"permission": {"bash": _real_catalog_bash_fragment(catalog)}},
            indent=2,
        )
        + "\n"
    )


def _real_catalog_runner_config(catalog: dict[str, object]) -> str:
    """A destination config with the catalog assertions plus the executor grant."""
    return (
        json.dumps(
            {
                "permission": {"bash": _real_catalog_bash_fragment(catalog)},
                "agent": {
                    str(AICORE_RUNNER["executor"]): {
                        "permission": {
                            "bash": {
                                "*": "deny",
                                AICORE_SUITE_COMMAND: "allow",
                            }
                        }
                    }
                },
            },
            indent=2,
        )
        + "\n"
    )


def _real_catalog_gitignore(catalog: dict[str, object]) -> str:
    """A destination .gitignore carrying the catalog's reviewed ignore assertions."""
    return _real_catalog_gitignore_fragment(catalog)
