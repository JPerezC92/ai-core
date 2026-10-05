"""Temporary Git repositories and CLI helpers shared by adoption tests."""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import TypedDict

import pytest
import yaml

from adoption_constants import AICORE_SUITE_COMMAND, RULE_LAYOUT_VALUE
from adoption_loaders import _raw_file_digest
from adoption_test_acceptance_data import (
    ADAPTED_RULEBOOK,
    BOOTSTRAP_CATALOG,
    BOOTSTRAP_SOURCE_FILES,
    MIXED_CATALOG,
    MIXED_CORE_INDEX,
    MIXED_DECLARATION,
    MIXED_DESTINATION_INDEX,
    MIXED_REVIEW_ALL,
    PROTECTED_AGENT_CATALOG,
    PROTECTED_AGENT_DECLARATION,
    PROTECTED_AGENT_PROFILE,
    PROTECTED_DESTINATION_AGENT,
    PROTECTED_DESTINATION_ROOT,
    PROTECTED_ROOT_CATALOG,
    PROTECTED_ROOT_DECLARATION,
    PROTECTED_SOURCE_AGENT,
    PROTECTED_SOURCE_ROOT,
    REPLACEMENT_AGENT,
    UPSTREAM_MIXED_ROOT,
)
from adoption_test_data import (
    ASSERTION_CATALOG,
    ASSERTION_DECLARATION,
    CLEAN_DESTINATION_ROOT,
    CATALOG_REL,
    EMPTY_REVIEW,
    GREETING_CATALOG,
    GREETING_DECLARATION,
    GUARDED_ROOT_CATALOG,
    GUARDED_ROOT_DECLARATION,
    STORY_CATALOG,
    STORY_CORE_INDEX,
    STORY_DECLARATION,
    STORY_DECLARATION_NO_TICKET,
    TWO_UNIT_CATALOG,
    TWO_UNIT_DECLARATION,
    UPSTREAM_ID,
    UPSTREAM_ROOT,
    LockDocument,
    assertion_lock_document,
    greeting_lock_document,
    guarded_root_lock_document,
    two_unit_lock_document,
)
from adoption_test_runner_data import opencode_runner_config

SCRIPT_DIR = Path(__file__).resolve().parent
ENGINE_PATH = SCRIPT_DIR / "sync_aicore_adoption.py"


def repository_root() -> Path:
    """Return the repository root that owns the shipped v2 catalog."""
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".aicore" / "core-catalog-v2.yaml").is_file():
            return candidate
    raise AssertionError("repository root with the v2 catalog was not found")


def production_engine_inventory(script_dir: Path = SCRIPT_DIR) -> dict[str, str]:
    """Hash the reviewed production engine modules. Test modules are excluded."""
    paths = sorted(
        path
        for path in script_dir.glob("adoption_*.py")
        if not path.name.startswith("adoption_test_")
    )
    paths.append(script_dir / "sync_aicore_adoption.py")
    return {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths
    }

UNPROTECTED_RULE_CATALOG = """schema_version: 2
catalog:
  version: 2.5.0
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: rulebook
    kind: skill
    applicability: { always: true }
    install_strategy: copy
    sync_projection: file
    members:
      - { id: rules, source: skills/rules.md, destination: skills/rules.md }
"""
UNPROTECTED_REPLACEMENT_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: rulebook
    mode: replacement
    replacement_members:
      - { id: local-rules, destination: skills/local-rules.md, projection: file }
"""
UNPROTECTED_DESTINATION_OWNED_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: rulebook
    mode: destination_owned
    members:
      - { id: rules, destination: skills/rules.md }
"""
HISTORICAL_RULE_SOURCE = (
    "# Rulebook\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Source extension.\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "HISTORICAL_RULE_MANDATORY\n"
)
HISTORICAL_RULE_DESTINATION = (
    "# Rulebook — Destination\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Destination extension.\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "HISTORICAL_RULE_MANDATORY\n"
)


def git_environment() -> dict[str, str]:
    """Isolate fixture Git setup and supply author identity.

    Mutating temporary-repository commands use this environment. Production
    reads use ``adoption_git``'s controlled invocation; this helper does not
    copy that read policy.
    """
    environment = {
        key: value
        for key, value in os.environ.items()
        if not key.upper().startswith("GIT_")
    }
    environment.update({
        "GIT_AUTHOR_NAME": "Engine Test",
        "GIT_AUTHOR_EMAIL": "engine@test.invalid",
        "GIT_COMMITTER_NAME": "Engine Test",
        "GIT_COMMITTER_EMAIL": "engine@test.invalid",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
    })
    return environment


class AdopterFixture(TypedDict):
    """Paths and revisions shared by adopter repository fixtures."""

    accepted: str
    target: str
    adopter_rev: str
    upstream: Path
    adopter: Path
    catalog: Path
    declaration: Path
    review: Path
    lock: Path


class MixedModeFixture(AdopterFixture):
    """Adopter fixture with commits for each mixed-mode staging boundary."""

    owner_commit: str
    control_commit: str
    staged_commit: str


class VerifyFixture(TypedDict):
    """Upstream and registry paths used by verify-all tests."""

    upstream: Path
    catalog: Path
    checkouts: Path
    current_registry: Path
    stale_registry: Path
    accepted: str
    target: str


class RegistryEntry(TypedDict):
    """One adopter row in the test registry."""

    id: str
    repository: str
    default_branch: str
    declaration_path: str
    lock_path: str
    review_path: str


class RegistryDocument(TypedDict):
    """Registry document consumed by verify-all tests."""

    schema_version: int
    upstream_repository: str
    adopters: list[RegistryEntry]


class TemporaryRepositoryCliMixin:
    """Own temporary repositories and isolated Git/CLI helpers."""

    def _confined_path(self, path: Path | str, label: str) -> Path:
        candidate = Path(path)
        if ".." in candidate.parts:
            raise ValueError(f"{label} path must not traverse a parent: {candidate}")
        root = self.root.resolve()
        if not candidate.is_absolute():
            candidate = root / candidate
        resolved = candidate.resolve()
        try:
            resolved.relative_to(root)
        except ValueError as error:
            raise ValueError(f"{label} path escapes temporary root: {candidate}") from error
        return resolved

    def _relative_write_path(self, relative: str) -> Path:
        candidate = Path(relative)
        if candidate.is_absolute():
            raise ValueError(f"write path must be relative: {relative}")
        if ".." in candidate.parts:
            raise ValueError(f"write path must not traverse a parent: {relative}")
        return candidate

    @pytest.fixture(autouse=True)
    def _temp_repos(self, tmp_path: Path) -> Iterator[None]:
        """Bind shared repository IO to pytest's tmp_path. Teardown is fixture cleanup, not recovery."""
        self.root = tmp_path
        self.upstream = self.root / "upstream"
        self.adopter = self.root / "adopter"
        self.command_trace: list[tuple[str, ...]] = []
        yield

    def git(
        self, repo: Path, *args: str, check: bool = True
    ) -> subprocess.CompletedProcess[str]:
        repo = self._confined_path(repo, "repository")
        self.command_trace.append(("git", "-C", str(repo), *args))
        proc = subprocess.run(
            ["git", "-C", str(repo), *args],
            env=git_environment(),
            capture_output=True,
            text=True,
        )
        if check and proc.returncode != 0:
            pytest.fail(f"git {' '.join(args)} failed in {repo}: {proc.stderr}")
        return proc

    def git_bytes(
        self, repo: Path, *args: str
    ) -> subprocess.CompletedProcess[bytes]:
        """Run Git with byte-exact stdout for blob content comparisons."""
        repo = self._confined_path(repo, "repository")
        self.command_trace.append(("git", "-C", str(repo), *args))
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            env=git_environment(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def stage(self, repo: Path, *relatives: str) -> None:
        """Stage only the named repository-relative paths."""
        repo = self._confined_path(repo, "repository")
        self.git(repo, "add", "--", *relatives)

    def index_entry(self, repo: Path, relative: str) -> tuple[str, str] | None:
        """Return the staged ``(mode, object id)`` for one path, or ``None``."""
        proc = self.git_bytes(repo, "ls-files", "-s", "-z", "--", relative)
        records = [raw for raw in proc.stdout.split(b"\0") if raw]
        if len(records) != 1:
            return None
        meta, _, _full = records[0].partition(b"\t")
        parts = meta.split(b" ")
        if len(parts) < 3 or parts[2] != b"0":
            return None
        return parts[0].decode("ascii"), parts[1].decode("ascii")

    def index_state(self, repo: Path) -> str:
        """Return the full staged index listing for exact-state comparisons."""
        return self.git(repo, "ls-files", "-s").stdout

    def staged_bytes(self, repo: Path, relative: str) -> bytes | None:
        """Return the exact staged blob bytes for one path, or ``None``."""
        proc = self.git_bytes(repo, "show", f":{relative}")
        return proc.stdout if proc.returncode == 0 else None

    def init_repo(self, repo: Path) -> None:
        repo = self._confined_path(repo, "repository")
        repo.mkdir(parents=True, exist_ok=True)
        self.git(repo, "init", "--quiet")
        self.git(repo, "symbolic-ref", "HEAD", "refs/heads/main")
        self.git(repo, "config", "user.name", "Test")
        self.git(repo, "config", "user.email", "test@example.invalid")
        self.git(repo, "config", "commit.gpgsign", "false")

    def write(self, base: Path, relative: str, text: str) -> Path:
        base = self._confined_path(base, "write base")
        path = self._confined_path(
            base / self._relative_write_path(relative), "write target"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def commit(
        self, repo: Path, message: str = "snapshot", allow_empty: bool = False
    ) -> str:
        self.git(repo, "add", "-A")
        args = ["commit", "--quiet", "-m", message]
        if allow_empty:
            args.append("--allow-empty")
        self.git(repo, *args)
        return self.rev(repo)

    def rev(self, repo: Path, ref: str = "HEAD") -> str:
        return self.git(repo, "rev-parse", ref).stdout.strip()

    def run_cli(
        self, *args: str, cwd: Path | str | None = None
    ) -> subprocess.CompletedProcess[str]:
        working_directory = self.root if cwd is None else cwd
        argv = (sys.executable, "-B", str(ENGINE_PATH), *args)
        self.command_trace.append(argv)
        return subprocess.run(
            list(argv),
            capture_output=True,
            text=True,
            cwd=self._confined_path(working_directory, "CLI working directory"),
            env=git_environment(),
        )

    def assert_exit(
        self,
        proc: subprocess.CompletedProcess[str],
        code: int,
        contains: str | None = None,
    ) -> None:
        assert proc.returncode == code, (
            f"expected exit {code}, got {proc.returncode}\n"
            f"stdout={proc.stdout}\nstderr={proc.stderr}"
        )
        if contains is not None:
            assert contains in proc.stderr, f"stderr={proc.stderr}"

    def base_check_args(
        self,
        fixture: AdopterFixture,
        *,
        review: Path | None = None,
        lock: Path | None = None,
    ) -> list[str]:
        return [
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(review or fixture["review"]),
            "--lock", str(lock or fixture["lock"]),
        ]

    def worktree_bytes(self, repo: Path) -> dict[str, bytes]:
        repo = self._confined_path(repo, "repository")
        return {
            str(path.relative_to(repo)): path.read_bytes()
            for path in sorted(repo.rglob("*"))
            if path.is_file() and path.relative_to(repo).parts[0] != ".git"
        }

    def status(self, repo: Path) -> str:
        return self.git(repo, "status", "--porcelain").stdout

    def git_state(self, repo: Path) -> dict[str, str]:
        return {
            "head": self.git(repo, "rev-parse", "HEAD").stdout,
            "index": self.git(repo, "ls-files", "-s").stdout,
            "refs": self.git(repo, "for-each-ref").stdout,
            "status": self.status(repo),
        }


class AdoptionFixtureBuildersMixin:
    """Build focused single-adopter and adoption-state repositories."""

    def _fixture_dict(self, accepted: str, adopter_rev: str) -> AdopterFixture:
        return {
            "accepted": accepted,
            "target": self.rev(self.upstream),
            "adopter_rev": adopter_rev,
            "upstream": self.upstream,
            "adopter": self.adopter,
            "catalog": self.upstream / CATALOG_REL,
            "declaration": self.adopter / ".aicore/adoption.yaml",
            "review": self.adopter / ".aicore/adoption-review.yaml",
            "lock": self.adopter / ".aicore/adoption.lock.yaml",
        }

    def build_greeting(
        self,
        advance: str | None = None,
        destination_text: str = "hello\n",
        accepted_text: str = "hello\n",
        lock_destination_text: str | None = None,
        declaration: str = GREETING_DECLARATION,
        review: str = EMPTY_REVIEW,
        catalog: str = GREETING_CATALOG,
        mode: str = "mirror",
    ) -> AdopterFixture:
        self.init_repo(self.upstream)
        self.write(self.upstream, CATALOG_REL, catalog)
        self.write(self.upstream, "content/greeting.txt", accepted_text)
        accepted = self.commit(self.upstream, "accepted")
        if advance == "content":
            self.write(self.upstream, "content/greeting.txt", "hello world\n")
            self.commit(self.upstream, "target")
        elif advance == "empty":
            self.commit(self.upstream, "target", allow_empty=True)
        self.init_repo(self.adopter)
        self.write(self.adopter, ".aicore/adoption.yaml", declaration)
        if "transition:" in review:
            from adoption_test_data import review_with_transition, member_file
            dd = {"greeting": (member_file(accepted_text), member_file(destination_text))} if "greeting" in review else None
            review = review_with_transition(review, accepted, declaration, decision_digests=dd)
        self.write(self.adopter, ".aicore/adoption-review.yaml", review)
        self.write(self.adopter, "content/greeting.txt", destination_text)
        baseline = destination_text if lock_destination_text is None else lock_destination_text
        lock = greeting_lock_document(
            accepted, accepted_text, baseline, catalog, declaration, review, mode
        )
        self.write(self.adopter, ".aicore/adoption.lock.yaml", yaml.safe_dump(lock, sort_keys=False))
        return self._fixture_dict(accepted, self.commit(self.adopter, "adopter"))

    def build_raw(
        self,
        catalog: str,
        declaration: str,
        review: str,
        lock_builder: Callable[[str], LockDocument],
        upstream_files: dict[str, str],
        adopter_files: dict[str, str],
    ) -> AdopterFixture:
        self.init_repo(self.upstream)
        self.write(self.upstream, CATALOG_REL, catalog)
        for relative, text in upstream_files.items():
            self.write(self.upstream, relative, text)
        accepted = self.commit(self.upstream, "accepted")
        self.init_repo(self.adopter)
        self.write(self.adopter, ".aicore/adoption.yaml", declaration)
        self.write(self.adopter, ".aicore/adoption-review.yaml", review)
        for relative, text in adopter_files.items():
            self.write(self.adopter, relative, text)
        self.write(self.adopter, ".aicore/adoption.lock.yaml", yaml.safe_dump(lock_builder(accepted), sort_keys=False))
        return self._fixture_dict(accepted, self.commit(self.adopter, "adopter"))

    def build_two_unit(
        self,
        review: str,
        note_committed: str = "note v1\n",
        note_target: str = "note v2\n",
        declaration: str = TWO_UNIT_DECLARATION,
        catalog: str = TWO_UNIT_CATALOG,
    ) -> AdopterFixture:
        self.init_repo(self.upstream)
        self.write(self.upstream, CATALOG_REL, catalog)
        self.write(self.upstream, "content/greeting.txt", "hello\n")
        self.write(self.upstream, "content/note.txt", note_committed)
        accepted = self.commit(self.upstream, "accepted")
        self.write(self.upstream, "content/note.txt", note_target)
        self.commit(self.upstream, "target")
        self.init_repo(self.adopter)
        self.write(self.adopter, ".aicore/adoption.yaml", declaration)
        if "transition:" in review:
            from adoption_test_data import PLACEHOLDER_DIGEST, review_with_transition
            dd = {}
            for uid in ("greeting", "note"):
                if f"unit: {uid}" in review:
                    dd[uid] = (PLACEHOLDER_DIGEST, PLACEHOLDER_DIGEST)
            review = review_with_transition(review, accepted, declaration, decision_digests=dd or None)
        self.write(self.adopter, ".aicore/adoption-review.yaml", review)
        self.write(self.adopter, "content/greeting.txt", "hello\n")
        self.write(self.adopter, "content/note-local.txt", "note adapted v1\n")
        lock = two_unit_lock_document(
            accepted, "hello\n", note_committed, "hello\n", "note adapted v1\n",
            catalog, declaration, review,
        )
        self.write(self.adopter, ".aicore/adoption.lock.yaml", yaml.safe_dump(lock, sort_keys=False))
        return self._fixture_dict(accepted, self.commit(self.adopter, "adopter"))

    def build_assertions(
        self,
        lock_opencode: bool = True,
        current_opencode: bool = True,
        lock_gitignore: bool = True,
        current_gitignore: bool = True,
        declaration: str = ASSERTION_DECLARATION,
        review: str = EMPTY_REVIEW,
        catalog: str = ASSERTION_CATALOG,
    ) -> AdopterFixture:
        self.init_repo(self.upstream)
        self.write(self.upstream, CATALOG_REL, catalog)
        self.write(self.upstream, "content/.keep", "")
        accepted = self.commit(self.upstream, "accepted")
        self.init_repo(self.adopter)
        self.write(self.adopter, ".aicore/adoption.yaml", declaration)
        from adoption_test_data import PLACEHOLDER_DIGEST, review_with_transition
        dd = {}
        for uid in ("opencode-config", "gitignore-config"):
            if f"unit: {uid}" in review:
                dd[uid] = (PLACEHOLDER_DIGEST, PLACEHOLDER_DIGEST)
        review = review_with_transition(review, accepted, declaration, decision_digests=dd or None)
        self.write(self.adopter, ".aicore/adoption-review.yaml", review)
        self.write(
            self.adopter,
            "opencode.jsonc",
            opencode_runner_config(AICORE_SUITE_COMMAND, sudo_deny=current_opencode),
        )
        gitignore_lines = ["# managed file"]
        if current_gitignore:
            gitignore_lines.append("output/")
        self.write(self.adopter, ".gitignore", "\n".join(gitignore_lines) + "\n")
        lock = assertion_lock_document(
            accepted, lock_opencode, lock_gitignore, catalog, declaration, review
        )
        self.write(self.adopter, ".aicore/adoption.lock.yaml", yaml.safe_dump(lock, sort_keys=False))
        return self._fixture_dict(accepted, self.commit(self.adopter, "adopter"))

    def build_guarded_root(
        self,
        destination_root: str,
        *,
        upstream_root: str = UPSTREAM_ROOT,
        catalog: str = GUARDED_ROOT_CATALOG,
        declaration: str = GUARDED_ROOT_DECLARATION,
    ) -> AdopterFixture:
        self.init_repo(self.upstream)
        self.write(self.upstream, CATALOG_REL, catalog)
        self.write(self.upstream, "AGENTS.md", upstream_root)
        accepted = self.commit(self.upstream, "accepted")
        self.init_repo(self.adopter)
        self.write(self.adopter, ".aicore/adoption.yaml", declaration)
        from adoption_test_data import review_with_transition
        review = review_with_transition(EMPTY_REVIEW, accepted, declaration)
        self.write(self.adopter, ".aicore/adoption-review.yaml", review)
        self.write(self.adopter, "AGENTS.md", destination_root)
        lock = guarded_root_lock_document(
            accepted, destination_root, catalog, declaration, review, upstream_root
        )
        self.write(self.adopter, ".aicore/adoption.lock.yaml", yaml.safe_dump(lock, sort_keys=False))
        return self._fixture_dict(accepted, self.commit(self.adopter, "adopter"))

    def build_protected(
        self,
        catalog: str,
        declaration: str,
        upstream_files: dict[str, str],
        adopter_files: dict[str, str],
        unit_id: str,
        *,
        decision: str = "applied",
        verified_layout: str | None = RULE_LAYOUT_VALUE,
        reviewed_upstream_digest: str | None = None,
        reviewed_destination_digest: str | None = None,
        propose: bool = True,
    ) -> AdopterFixture:
        """Build a protected-unit enrollment with a fresh verified decision.

        Digests are computed dynamically from the committed source and prepared
        destination bytes, and the review transition binds the accepted source
        and declaration. ``propose=False`` leaves the candidate lock absent so
        a test can drive a refusal path itself.
        """
        from adoption_content import _destination_unit_digest, _unit_upstream_digest
        from adoption_git import _GitRepo, _RevisionSnapshot

        self.init_repo(self.upstream)
        self.write(self.upstream, CATALOG_REL, catalog)
        for relative, text in upstream_files.items():
            self.write(self.upstream, relative, text)
        accepted = self.commit(self.upstream, "accepted")
        self.init_repo(self.adopter)
        self.write(self.adopter, ".aicore/adoption.yaml", declaration)
        for relative, text in adopter_files.items():
            self.write(self.adopter, relative, text)
        prepared = self.commit(self.adopter, "prepared destination")
        catalog_document = yaml.safe_load(catalog)
        declaration_document = yaml.safe_load(declaration)
        unit = next(item for item in catalog_document["units"] if item["id"] == unit_id)
        declaration_unit = next(
            item for item in declaration_document["units"] if item["id"] == unit_id
        )
        source = _unit_upstream_digest(
            _GitRepo(str(self.upstream)), accepted, unit
        )
        result = _destination_unit_digest(
            unit,
            declaration_unit,
            _RevisionSnapshot(_GitRepo(str(self.adopter)), prepared),
        )
        decision_document: dict[str, object] = {
            "unit": unit_id,
            "decision": decision,
            "reviewer": "reviewer",
            "evidence": "Reviewed the complete protected document.",
            "reviewed_upstream_digest": reviewed_upstream_digest or source,
            "reviewed_destination_digest": reviewed_destination_digest or result,
        }
        if verified_layout is not None:
            decision_document["verified_layout"] = verified_layout
        review = {
            "schema_version": 2,
            "upstream_repository": catalog_document["catalog"]["upstream_repository"],
            "transition": {
                "baseline_lock_digest": None,
                "target_source_commit": accepted,
                "declaration_digest": _raw_file_digest(
                    str(self.adopter / ".aicore/adoption.yaml")
                ),
            },
            "decisions": [decision_document],
        }
        self.write(
            self.adopter,
            ".aicore/adoption-review.yaml",
            yaml.safe_dump(review, sort_keys=False),
        )
        review_rev = self.commit(self.adopter, "review")
        fixture = self._fixture_dict(accepted, review_rev)
        if propose:
            proposal = self.run_cli(
                "propose-lock",
                "--upstream-repo", str(self.upstream),
                "--catalog", str(self.upstream / CATALOG_REL),
                "--declaration", str(self.adopter / ".aicore/adoption.yaml"),
                "--review", str(self.adopter / ".aicore/adoption-review.yaml"),
                "--adopter-revision", review_rev,
            )
            assert proposal.returncode == 0, proposal.stderr
            self.write(self.adopter, ".aicore/adoption.lock.yaml", proposal.stdout)
            fixture["adopter_rev"] = self.commit(self.adopter, "lock")
        return fixture

    def build_unprotected_rule_mode(self, mode: str) -> AdopterFixture:
        """Build an accepted unprotected file unit in a non-protected ownership mode.

        ``replacement`` and ``destination_owned`` are valid before a later catalog
        adds ``rule_documents``. The returned fixture is a proposed lock at the
        accepted revision, so a pre-edit check can assess that history.
        """
        if mode == "replacement":
            declaration = UNPROTECTED_REPLACEMENT_DECLARATION
            adopter_files = {"skills/local-rules.md": "local replacement rules\n"}
        elif mode == "destination_owned":
            declaration = UNPROTECTED_DESTINATION_OWNED_DECLARATION
            adopter_files = {"skills/rules.md": "destination owned rules\n"}
        else:
            raise AssertionError(f"unsupported historical mode: {mode}")
        return self.build_protected(
            UNPROTECTED_RULE_CATALOG,
            declaration,
            {"skills/rules.md": "core rules v1\n"},
            adopter_files,
            "rulebook",
        )

    def build_protected_root(
        self,
        destination_root: str = PROTECTED_DESTINATION_ROOT,
        upstream_root: str = PROTECTED_SOURCE_ROOT,
        **kwargs: object,
    ) -> AdopterFixture:
        return self.build_protected(
            PROTECTED_ROOT_CATALOG,
            PROTECTED_ROOT_DECLARATION,
            {"AGENTS.md": upstream_root},
            {"AGENTS.md": destination_root},
            "root-runtime-spec",
            **kwargs,
        )

    def init_bootstrap_upstream(self) -> str:
        """Commit the hermetic bootstrap source tip. Does not write the adopter.

        Callers prepare destination bytes with ``write`` and ``stage`` after
        this returns. This helper does not copy source rows into the adopter
        and does not run a build or install command.
        """
        self.init_repo(self.upstream)
        self.write(self.upstream, CATALOG_REL, BOOTSTRAP_CATALOG)
        for relative, text in BOOTSTRAP_SOURCE_FILES.items():
            self.write(self.upstream, relative, text)
        return self.commit(self.upstream, "bootstrap source")

    def build_protected_agent(
        self,
        destination_agent: str = PROTECTED_DESTINATION_AGENT,
        upstream_agent: str = PROTECTED_SOURCE_AGENT,
        **kwargs: object,
    ) -> AdopterFixture:
        return self.build_protected(
            PROTECTED_AGENT_CATALOG,
            PROTECTED_AGENT_DECLARATION,
            {
                ".opencode/agents/reviewer.md": upstream_agent,
                "agents/reviewer/profile.md": PROTECTED_AGENT_PROFILE,
            },
            {
                ".opencode/agents/reviewer.md": destination_agent,
                "agents/reviewer/profile.md": PROTECTED_AGENT_PROFILE,
            },
            "reviewer-agent",
            **kwargs,
        )


class StoryMixedModeFixtureBuildersMixin:
    """Build user-story and mixed-mode adoption repositories."""

    def build_stories(
        self, destination_index: str | None, ticket: bool = True
    ) -> AdopterFixture:
        self.init_repo(self.upstream)
        self.write(self.upstream, CATALOG_REL, STORY_CATALOG)
        for slug in ("alpha", "beta", "gamma"):
            self.write(self.upstream, f"user-stories/{slug}.md", f"{slug} v1\n")
        self.write(self.upstream, "user-stories/index.md", STORY_CORE_INDEX)
        accepted = self.commit(self.upstream, "accepted")
        declaration = STORY_DECLARATION if ticket else STORY_DECLARATION_NO_TICKET
        self.init_repo(self.adopter)
        self.write(self.adopter, ".aicore/adoption.yaml", declaration)
        from adoption_test_data import review_with_transition
        review = review_with_transition(EMPTY_REVIEW, accepted, declaration)
        self.write(self.adopter, ".aicore/adoption-review.yaml", review)
        self.write(self.adopter, "user-stories/alpha.md", "alpha v1\n")
        self.write(self.adopter, "user-stories/beta.md", "beta v1\n")
        if ticket:
            self.write(self.adopter, "user-stories/gamma.md", "gamma v1\n")
        if destination_index is not None:
            self.write(self.adopter, "user-stories/index.md", destination_index)
        adopter_rev = self.commit(self.adopter, "adopter")
        proposal = self.run_cli(
            "propose-lock", "--upstream-repo", str(self.upstream),
            "--catalog", str(self.upstream / CATALOG_REL),
            "--declaration", str(self.adopter / ".aicore/adoption.yaml"),
            "--review", str(self.adopter / ".aicore/adoption-review.yaml"),
            "--adopter-revision", adopter_rev,
        )
        assert proposal.returncode == 0, proposal.stderr
        self.write(self.adopter, ".aicore/adoption.lock.yaml", proposal.stdout)
        return self._fixture_dict(accepted, self.commit(self.adopter, "lock"))

    def build_mixed_mode(self, review: str = MIXED_REVIEW_ALL) -> MixedModeFixture:
        self.init_repo(self.upstream)
        self.write(self.upstream, CATALOG_REL, MIXED_CATALOG)
        self.write(self.upstream, "skills/rules.md", "core rulebook v1\n")
        self.write(self.upstream, "agents/helper/profile.md", "core helper v1\n")
        self.write(self.upstream, "AGENTS.md", UPSTREAM_MIXED_ROOT)
        self.write(self.upstream, "user-stories/alpha.md", "alpha v1\n")
        self.write(self.upstream, "user-stories/gamma.md", "gamma v1\n")
        self.write(self.upstream, "user-stories/index.md", MIXED_CORE_INDEX)
        accepted = self.commit(self.upstream, "accepted")
        self.init_repo(self.adopter)
        self.write(self.adopter, "skills/rules.md", ADAPTED_RULEBOOK)
        self.write(self.adopter, "agents/helper/profile.md", REPLACEMENT_AGENT)
        self.write(self.adopter, "AGENTS.md", CLEAN_DESTINATION_ROOT)
        self.write(self.adopter, "user-stories/index.md", MIXED_DESTINATION_INDEX)
        owner_commit = self.commit(self.adopter, "owner content")
        self.write(self.adopter, ".aicore/adoption.yaml", MIXED_DECLARATION)
        from adoption_test_data import review_with_transition
        from adoption_content import _destination_unit_digest, _unit_upstream_digest
        from adoption_git import _GitRepo, _RevisionSnapshot
        _up = _GitRepo(str(self.upstream))
        _decl = yaml.safe_load(MIXED_DECLARATION)
        _cat = yaml.safe_load(MIXED_CATALOG)
        _tmp = self.commit(self.adopter, "temp for digests")
        _snap = _RevisionSnapshot(_GitRepo(str(self.adopter)), _tmp)
        dd = {}
        for _uid in ("root-runtime-spec", "rulebook", "helper-agent"):
            _cu = next(u for u in _cat["units"] if u["id"] == _uid)
            _du = next(u for u in _decl["units"] if u["id"] == _uid)
            _src = _unit_upstream_digest(_up, accepted, _cu)
            _dst = _destination_unit_digest(_cu, _du, _snap)
            dd[_uid] = (_src, _dst)
        review = review_with_transition(review, accepted, MIXED_DECLARATION, decision_digests=dd)
        self.write(self.adopter, ".aicore/adoption-review.yaml", review)
        control_commit = self.commit(self.adopter, "mode review recorded")
        self.write(self.adopter, "user-stories/alpha.md", "alpha v1\n")
        staged = self.commit(self.adopter, "content staged")
        proposal = self.run_cli(
            "propose-lock", "--upstream-repo", str(self.upstream),
            "--catalog", str(self.upstream / CATALOG_REL),
            "--declaration", str(self.adopter / ".aicore/adoption.yaml"),
            "--review", str(self.adopter / ".aicore/adoption-review.yaml"),
            "--adopter-revision", staged,
        )
        assert proposal.returncode == 0, proposal.stderr
        self.write(self.adopter, ".aicore/adoption.lock.yaml", proposal.stdout)
        adopter_rev = self.commit(self.adopter, "lock")
        fixture = self._fixture_dict(accepted, adopter_rev)
        return MixedModeFixture(
            accepted=fixture["accepted"],
            target=fixture["target"],
            adopter_rev=fixture["adopter_rev"],
            upstream=fixture["upstream"],
            adopter=fixture["adopter"],
            catalog=fixture["catalog"],
            declaration=fixture["declaration"],
            review=fixture["review"],
            lock=fixture["lock"],
            owner_commit=owner_commit,
            control_commit=control_commit,
            staged_commit=staged,
        )


class VerifyAllFixtureBuildersMixin:
    """Build registry and checkout repositories for verify-all tests."""

    def _verify_adopter_repo(
        self, repo: Path, accepted: str, upstream_text: str, destination_text: str
    ) -> None:
        self.init_repo(repo)
        self.write(repo, ".aicore/adoption.yaml", GREETING_DECLARATION)
        from adoption_test_data import review_with_transition
        review = review_with_transition(EMPTY_REVIEW, accepted, GREETING_DECLARATION)
        self.write(repo, ".aicore/adoption-review.yaml", review)
        self.write(repo, "content/greeting.txt", destination_text)
        lock = greeting_lock_document(
            accepted, upstream_text, destination_text,
            GREETING_CATALOG, GREETING_DECLARATION, review,
        )
        self.write(repo, ".aicore/adoption.lock.yaml", yaml.safe_dump(lock, sort_keys=False))
        self.commit(repo, "adopter")

    def _registry_text(self, adopter_ids: list[str]) -> str:
        adopters: list[RegistryEntry] = [{
            "id": adopter_id,
            "repository": f"local/{adopter_id}",
            "default_branch": "main",
            "declaration_path": ".aicore/adoption.yaml",
            "lock_path": ".aicore/adoption.lock.yaml",
            "review_path": ".aicore/adoption-review.yaml",
        } for adopter_id in adopter_ids]
        document: RegistryDocument = {
            "schema_version": 2,
            "upstream_repository": UPSTREAM_ID,
            "adopters": adopters,
        }
        return yaml.safe_dump(document, sort_keys=False)

    def build_verify(self) -> VerifyFixture:
        self.init_repo(self.upstream)
        self.write(self.upstream, CATALOG_REL, GREETING_CATALOG)
        self.write(self.upstream, "content/greeting.txt", "hello\n")
        accepted = self.commit(self.upstream, "accepted")
        self.write(self.upstream, "content/greeting.txt", "hello world\n")
        target = self.commit(self.upstream, "target")
        checkouts = self.root / "checkouts"
        self._verify_adopter_repo(checkouts / "good", target, "hello world\n", "hello world\n")
        self._verify_adopter_repo(checkouts / "stale", accepted, "hello\n", "hello\n")
        current_registry = self.write(
            self.root, "registry-current.yaml", self._registry_text(["good"])
        )
        stale_registry = self.write(
            self.root, "registry-stale.yaml", self._registry_text(["good", "stale"])
        )
        return VerifyFixture(
            upstream=self.upstream,
            catalog=self.upstream / CATALOG_REL,
            checkouts=checkouts,
            current_registry=current_registry,
            stale_registry=stale_registry,
            accepted=accepted,
            target=target,
        )


class EngineTestCase(
    TemporaryRepositoryCliMixin,
    AdoptionFixtureBuildersMixin,
    StoryMixedModeFixtureBuildersMixin,
    VerifyAllFixtureBuildersMixin,
):
    """Compose the shared repository helpers and focused fixture builders."""
