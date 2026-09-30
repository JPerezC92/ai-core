"""Pytest suite for the sync-aicore-adoption protocol-v2 engine.

Run: uv run --frozen --group dev pytest .opencode/skills/sync-aicore-adoption/scripts/test_sync_aicore_adoption.py

The suite never touches the network and never calls ``gh``: every fixture is a
temporary git repository created under ``tempfile.mkdtemp()`` and removed by
the autouse fixture. CLI behavior is exercised through ``subprocess``; pure
helpers are imported directly from the sibling engine module.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable, Iterator
from pathlib import Path
from unittest import mock

import pytest
import yaml

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import sync_aicore_adoption as engine  # noqa: E402

ENGINE_PATH = os.path.join(SCRIPT_DIR, "sync_aicore_adoption.py")
UPSTREAM_ID = "example/upstream"
CATALOG_REL = ".aicore/core-catalog-v2.yaml"
GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "Engine Test",
    "GIT_AUTHOR_EMAIL": "engine@test.invalid",
    "GIT_COMMITTER_NAME": "Engine Test",
    "GIT_COMMITTER_EMAIL": "engine@test.invalid",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
}


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def member_file(text: str) -> str:
    return engine.member_digest(
        [engine.ProjectedEntry(path="", mode="100644", content=text.encode("utf-8"))]
    )


def unit_file(text: str) -> str:
    return engine.unit_digest([("file", member_file(text))])


def placeholder_digest(seed: str) -> str:
    return sha256_text("placeholder:" + seed)


def snapshot_digest(declaration: str, review: str, rows: list[object]) -> str:
    return engine._snapshot_digest(sha256_text(declaration), sha256_text(review), rows)


GREETING_CATALOG = """schema_version: 2
catalog:
  version: 2.0.0
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: greeting
    kind: infra
    applicability: { always: true }
    install_strategy: copy
    sync_projection: file
    members:
      - { id: file, source: content/greeting.txt, destination: content/greeting.txt }
"""

GREETING_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: greeting
    mode: mirror
    members:
      - { id: file, destination: content/greeting.txt }
"""

TWO_UNIT_CATALOG = """schema_version: 2
catalog:
  version: 2.0.0
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: greeting
    kind: infra
    applicability: { always: true }
    install_strategy: copy
    sync_projection: file
    members:
      - { id: file, source: content/greeting.txt, destination: content/greeting.txt }
  - id: note
    kind: infra
    applicability: { always: true }
    install_strategy: copy
    sync_projection: file
    members:
      - { id: file, source: content/note.txt, destination: content/note.txt }
"""

TWO_UNIT_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: greeting
    mode: mirror
    members:
      - { id: file, destination: content/greeting.txt }
  - id: note
    mode: adapted
    members:
      - { id: file, destination: content/note-local.txt }
"""

TWO_UNIT_DECISION_REVIEW = """schema_version: 2
upstream_repository: example/upstream
decisions:
  - unit: note
    decision: applied
    evidence: "Local note reconciled with the upstream rewrite."
    reviewer: test-suite
"""

ASSERTION_CATALOG = """schema_version: 2
catalog:
  version: 2.0.0
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: opencode-config
    kind: config
    applicability: { always: true }
    install_strategy: merge
    sync_projection: assertions
    destination: opencode.jsonc
    assertions:
      - { id: sudo-deny, contains: '"sudo *": "deny"' }
  - id: gitignore-config
    kind: config
    applicability: { always: true }
    install_strategy: merge
    sync_projection: assertions
    destination: .gitignore
    assertions:
      - { id: output-ignored, contains: 'output/' }
"""

ASSERTION_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: opencode-config
    mode: mirror
  - id: gitignore-config
    mode: mirror
"""

GUARDED_ROOT_CATALOG = """schema_version: 2
catalog:
  version: 2.1.0
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: root-runtime-spec
    kind: config
    applicability: { always: true }
    install_strategy: merge
    sync_projection: guarded_file
    destination_policy: adopter_root_runtime
    members:
      - { id: root, source: AGENTS.md, destination: AGENTS.md }
"""

GUARDED_ROOT_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: root-runtime-spec
    mode: adapted
    members:
      - { id: root, destination: AGENTS.md }
"""

UPSTREAM_ROOT = """# Cipher — AICore
> **Spec version:** 2.1.0

## Reuse guide (adopting this core)
Run migrate-core-to-project to adopt AICore.
"""

CLEAN_DESTINATION_ROOT = """# Relay project runtime
> **Project identity:** Relay
> **Spec version:** 2.1.0
> **Local version:** 1.0.0

## Identity & Role
Project-local orchestration rules.
"""

ORIGINAL_REUSE_GUIDE_ROOT = CLEAN_DESTINATION_ROOT + """
## Reuse guide (adopting this core)
Run migrate-core-to-project to install AICore and retain its operator guidance.
"""

VERBOSE_UPSTREAM_LINEAGE_ROOT = CLEAN_DESTINATION_ROOT + """
## Upstream lineage
Use migrate-core-to-project and sync-aicore-adoption for future updates.
Retain upstream stack, token, and registry guidance in this runtime.
"""

MINIMAL_UPSTREAM_LINEAGE_ROOT = CLEAN_DESTINATION_ROOT + """
> **Upstream provenance:** AICore (`JPerezC92/ai-core`)

AICore (`JPerezC92/ai-core`) is upstream provenance only.
"""

EMPTY_REVIEW = """schema_version: 2
upstream_repository: example/upstream
decisions: []
"""

GREETING_DECISION_REVIEW = """schema_version: 2
upstream_repository: example/upstream
decisions:
  - unit: greeting
    decision: applied
    evidence: "Destination-owned fork re-based on the upstream change."
    reviewer: test-suite
"""

OPENCODE_ASSERTIONS = [{"id": "sudo-deny", "contains": '"sudo *": "deny"'}]
GITIGNORE_ASSERTIONS = [{"id": "output-ignored", "contains": "output/"}]

STORY_CATALOG = """schema_version: 2
catalog:
  version: 2.4.0
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: portable-stories-always
    kind: user-story
    applicability: { always: true }
    install_strategy: copy
    sync_projection: file
    members:
      - { id: alpha, source: user-stories/alpha.md, destination: user-stories/alpha.md, collision_policy: core_wins }
      - { id: beta, source: user-stories/beta.md, destination: user-stories/beta.md }
  - id: portable-stories-ticket
    kind: user-story
    applicability: { requires: [ticket_system] }
    install_strategy: copy
    sync_projection: file
    members:
      - { id: gamma, source: user-stories/gamma.md, destination: user-stories/gamma.md, collision_policy: core_wins }
"""

STORY_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: true }
units:
  - id: portable-stories-always
    mode: mirror
    members:
      - { id: alpha, destination: user-stories/alpha.md }
      - { id: beta, destination: user-stories/beta.md }
  - id: portable-stories-ticket
    mode: mirror
    members:
      - { id: gamma, destination: user-stories/gamma.md }
"""

STORY_DECLARATION_NO_TICKET = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: portable-stories-always
    mode: mirror
    members:
      - { id: alpha, destination: user-stories/alpha.md }
      - { id: beta, destination: user-stories/beta.md }
  - id: portable-stories-ticket
    mode: not_applicable
"""

STORY_CORE_INDEX = """# User Stories

| Slug | Title | Status | Epic | Affected areas |
|---|---|---|---|---|
| `alpha` | Alpha | active | ep-a | `a` |
| `beta` | Beta | active | ep-b | `b` |
| `gamma` | Gamma | active | ep-g | `g` |
| `aicore-only` | AICore only | active | ep-core | `core` |

## Appendices

Core appendix notes.
"""

# alpha differs (core_wins -> replaced + reported); beta and gamma are
# byte-identical to the core rows; `dest-own` is destination-only; the
# trailing section must survive every merge byte-for-byte.
STORY_DESTINATION_INDEX = """# User Stories

| Slug | Title | Status | Epic | Affected areas |
|---|---|---|---|---|
| `alpha` | Alpha local edit | active | ep-a | `a` |
| `beta` | Beta | active | ep-b | `b` |
| `dest-own` | Destination owned | active | local | `d` |
| `gamma` | Gamma | active | ep-g | `g` |

## Destination notes

Local trailing section that must survive byte-for-byte.
"""

# Mixed-mode first-adoption fixture: adapted rulebook, replacement agent,
# reviewed guarded root, mirror portable story, and an inapplicable ticket
# story unit. The destination owner's bytes pre-exist; only the control
# surfaces and the mirror member's core bytes are staged afterwards.
MIXED_CATALOG = """schema_version: 2
catalog:
  version: 2.4.0
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
  - id: helper-agent
    kind: agent
    applicability: { always: true }
    install_strategy: copy
    sync_projection: file
    members:
      - { id: cv, source: agents/helper/profile.md, destination: agents/helper/profile.md }
  - id: root-runtime-spec
    kind: config
    applicability: { always: true }
    install_strategy: merge
    sync_projection: guarded_file
    destination_policy: adopter_root_runtime
    members:
      - { id: root, source: AGENTS.md, destination: AGENTS.md }
  - id: portable-stories-always
    kind: user-story
    applicability: { always: true }
    install_strategy: copy
    sync_projection: file
    members:
      - { id: alpha, source: user-stories/alpha.md, destination: user-stories/alpha.md, collision_policy: core_wins }
  - id: portable-stories-ticket
    kind: user-story
    applicability: { requires: [ticket_system] }
    install_strategy: copy
    sync_projection: file
    members:
      - { id: gamma, source: user-stories/gamma.md, destination: user-stories/gamma.md, collision_policy: core_wins }
"""

MIXED_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: true, python_scripts: true, ticket_system: false }
units:
  - id: rulebook
    mode: adapted
    members:
      - { id: rules, destination: skills/rules.md }
  - id: helper-agent
    mode: replacement
    replacement_members:
      - { id: helper-local, destination: agents/helper/profile.md, projection: file }
  - id: root-runtime-spec
    mode: adapted
    members:
      - { id: root, destination: AGENTS.md }
  - id: portable-stories-always
    mode: mirror
    members:
      - { id: alpha, destination: user-stories/alpha.md }
  - id: portable-stories-ticket
    mode: not_applicable
"""

MIXED_REVIEW = """schema_version: 2
upstream_repository: example/upstream
decisions:
  - unit: root-runtime-spec
    decision: applied
    evidence: "Destination root runtime reviewed with destination-only identity."
    reviewer: test-suite
"""

MIXED_REVIEW_RULEBOOK = MIXED_REVIEW + """  - unit: rulebook
    decision: applied
    evidence: "Destination rulebook adaptation reviewed against the upstream rewrite."
    reviewer: test-suite
"""

MIXED_CORE_INDEX = """# User Stories

| Slug | Title | Status | Epic | Affected areas |
|---|---|---|---|---|
| `alpha` | Alpha | active | ep-a | `a` |
| `gamma` | Gamma | active | ep-g | `g` |
| `aicore-only` | AICore only | active | ep-core | `core` |

## Appendices

Core appendix notes.
"""

MIXED_DESTINATION_INDEX = """# User Stories

| Slug | Title | Status | Epic | Affected areas |
|---|---|---|---|---|
| `alpha` | Alpha | active | ep-a | `a` |
| `dest-own` | Destination owned | active | local | `d` |

## Destination notes

Local trailing section that must survive byte-for-byte.
"""

UPSTREAM_MIXED_ROOT = """# Upstream runtime spec
> **Spec version:** 2.4.0

Upstream agent rules.
"""

ADAPTED_RULEBOOK = "destination-adapted rulebook\n"
REPLACEMENT_AGENT = "destination replacement agent bytes\n"


def greeting_lock_document(
    accepted: str,
    accepted_text: str,
    destination_text: str,
    catalog: str = GREETING_CATALOG,
    declaration: str = GREETING_DECLARATION,
    review: str = EMPTY_REVIEW,
    mode: str = "mirror",
) -> dict[str, object]:
    upstream_member = member_file(accepted_text)
    destination_member = member_file(destination_text)
    rows = [
        {
            "id": "greeting",
            "mode": mode,
            "declaration_unit_digest": engine.declaration_unit_digest(
                mode,
                [{"id": "file", "destination": "content/greeting.txt"}],
                [],
            ),
            "accepted_upstream_digest": engine.unit_digest([("file", upstream_member)]),
            "members": [
                {
                    "id": "file",
                    "destination": "content/greeting.txt",
                    "accepted_upstream_digest": upstream_member,
                    "accepted_destination_digest": destination_member,
                }
            ],
        }
    ]
    return {
        "schema_version": 2,
        "upstream_repository": UPSTREAM_ID,
        "accepted_source_commit": accepted,
        "accepted_catalog_digest": sha256_text(catalog),
        "declaration_digest": sha256_text(declaration),
        "review_digest": sha256_text(review),
        "accepted_snapshot_digest": snapshot_digest(declaration, review, rows),
        "units": rows,
    }


def two_unit_lock_document(
    accepted: str,
    greeting_committed: str,
    note_committed: str,
    greeting_destination: str,
    note_destination: str,
    catalog: str = TWO_UNIT_CATALOG,
    declaration: str = TWO_UNIT_DECLARATION,
    review: str = EMPTY_REVIEW,
) -> dict[str, object]:
    greeting_upstream = member_file(greeting_committed)
    note_upstream = member_file(note_committed)
    rows = [
        {
            "id": "greeting",
            "mode": "mirror",
            "declaration_unit_digest": engine.declaration_unit_digest(
                "mirror",
                [{"id": "file", "destination": "content/greeting.txt"}],
                [],
            ),
            "accepted_upstream_digest": engine.unit_digest([("file", greeting_upstream)]),
            "members": [
                {
                    "id": "file",
                    "destination": "content/greeting.txt",
                    "accepted_upstream_digest": greeting_upstream,
                    "accepted_destination_digest": member_file(greeting_destination),
                }
            ],
        },
        {
            "id": "note",
            "mode": "adapted",
            "declaration_unit_digest": engine.declaration_unit_digest(
                "adapted",
                [{"id": "file", "destination": "content/note-local.txt"}],
                [],
            ),
            "accepted_upstream_digest": engine.unit_digest([("file", note_upstream)]),
            "members": [
                {
                    "id": "file",
                    "destination": "content/note-local.txt",
                    "accepted_upstream_digest": note_upstream,
                    "accepted_destination_digest": member_file(note_destination),
                }
            ],
        },
    ]
    return {
        "schema_version": 2,
        "upstream_repository": UPSTREAM_ID,
        "accepted_source_commit": accepted,
        "accepted_catalog_digest": sha256_text(catalog),
        "declaration_digest": sha256_text(declaration),
        "review_digest": sha256_text(review),
        "accepted_snapshot_digest": snapshot_digest(declaration, review, rows),
        "units": rows,
    }


def assertion_lock_document(
    accepted: str,
    opencode_present: bool = True,
    gitignore_present: bool = True,
    catalog: str = ASSERTION_CATALOG,
    declaration: str = ASSERTION_DECLARATION,
    review: str = EMPTY_REVIEW,
) -> dict[str, object]:
    opencode_list = engine.assertion_list_digest(OPENCODE_ASSERTIONS)
    gitignore_list = engine.assertion_list_digest(GITIGNORE_ASSERTIONS)
    opencode_status = engine.assertion_status_digest([("sudo-deny", opencode_present)])
    gitignore_status = engine.assertion_status_digest(
        [("output-ignored", gitignore_present)]
    )
    unit_digest = engine.declaration_unit_digest("mirror", [], [])
    rows = [
        {
            "id": "opencode-config",
            "mode": "mirror",
            "declaration_unit_digest": unit_digest,
            "accepted_upstream_digest": opencode_list,
            "members": [
                {
                    "id": "assertions",
                    "destination": "opencode.jsonc",
                    "accepted_upstream_digest": opencode_list,
                    "accepted_destination_digest": opencode_status,
                }
            ],
        },
        {
            "id": "gitignore-config",
            "mode": "mirror",
            "declaration_unit_digest": unit_digest,
            "accepted_upstream_digest": gitignore_list,
            "members": [
                {
                    "id": "assertions",
                    "destination": ".gitignore",
                    "accepted_upstream_digest": gitignore_list,
                    "accepted_destination_digest": gitignore_status,
                }
            ],
        },
    ]
    return {
        "schema_version": 2,
        "upstream_repository": UPSTREAM_ID,
        "accepted_source_commit": accepted,
        "accepted_catalog_digest": sha256_text(catalog),
        "declaration_digest": sha256_text(declaration),
        "review_digest": sha256_text(review),
        "accepted_snapshot_digest": snapshot_digest(declaration, review, rows),
        "units": rows,
    }


def guarded_root_lock_document(
    accepted: str,
    destination_root: str,
    catalog: str = GUARDED_ROOT_CATALOG,
    declaration: str = GUARDED_ROOT_DECLARATION,
) -> dict[str, object]:
    upstream_member = member_file(UPSTREAM_ROOT)
    destination_member = member_file(destination_root)
    rows = [
        {
            "id": "root-runtime-spec",
            "mode": "adapted",
            "declaration_unit_digest": engine.declaration_unit_digest(
                "adapted",
                [{"id": "root", "destination": "AGENTS.md"}],
                [],
            ),
            "accepted_upstream_digest": engine.unit_digest(
                [("root", upstream_member)]
            ),
            "members": [
                {
                    "id": "root",
                    "destination": "AGENTS.md",
                    "accepted_upstream_digest": upstream_member,
                    "accepted_destination_digest": destination_member,
                }
            ],
        }
    ]
    return {
        "schema_version": 2,
        "upstream_repository": UPSTREAM_ID,
        "accepted_source_commit": accepted,
        "accepted_catalog_digest": sha256_text(catalog),
        "declaration_digest": sha256_text(declaration),
        "review_digest": sha256_text(EMPTY_REVIEW),
        "accepted_snapshot_digest": snapshot_digest(
            declaration, EMPTY_REVIEW, rows
        ),
        "units": rows,
    }


class EngineTestCase:
    """Base case owning a temporary upstream repository and adopter repository."""

    @pytest.fixture(autouse=True)
    def _temp_repos(self) -> Iterator[None]:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.upstream = self.root / "upstream"
        self.adopter = self.root / "adopter"
        yield
        self._tmp.cleanup()

    # -- git plumbing -------------------------------------------------------

    def git(self, repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        proc = subprocess.run(
            ["git", "-C", str(repo), *args],
            env=GIT_ENV,
            capture_output=True,
            text=True,
        )
        if check and proc.returncode != 0:
                pytest.fail(f"git {' '.join(args)} failed in {repo}: {proc.stderr}")
        return proc

    def init_repo(self, repo: Path) -> None:
        repo.mkdir(parents=True, exist_ok=True)
        self.git(repo, "init", "--quiet")
        self.git(repo, "symbolic-ref", "HEAD", "refs/heads/main")
        self.git(repo, "config", "user.name", "Test")
        self.git(repo, "config", "user.email", "test@example.invalid")
        self.git(repo, "config", "commit.gpgsign", "false")

    def write(self, base: Path, relative: str, text: str) -> Path:
        path = Path(base) / relative
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
        return self.rev(repo, "HEAD")

    def rev(self, repo: Path, ref: str = "HEAD") -> str:
        return self.git(repo, "rev-parse", ref).stdout.strip()

    # -- CLI ----------------------------------------------------------------

    def run_cli(self, *args: str, cwd: str | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, ENGINE_PATH, *args],
            capture_output=True,
            text=True,
            cwd=cwd,
            env=os.environ.copy(),
        )

    def assert_exit(
        self, proc: subprocess.CompletedProcess, code: int, contains: str | None = None
    ) -> None:
        assert proc.returncode == code, (
            f"expected exit {code}, got {proc.returncode}\n"
            f"stdout={proc.stdout}\nstderr={proc.stderr}"
        )
        if contains is not None:
            assert contains in proc.stderr, f"stderr={proc.stderr}"

    def base_check_args(
        self, fixture: dict[str, object], *, review: Path | None = None, lock: Path | None = None
    ) -> list[str]:
        return [
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(review or fixture["review"]),
            "--lock", str(lock or fixture["lock"]),
        ]

    # -- snapshots ----------------------------------------------------------

    def worktree_bytes(self, repo: Path) -> dict[str, object]:
        snapshot = {}
        for path in sorted(Path(repo).rglob("*")):
            rel = path.relative_to(repo)
            if not path.is_file():
                continue
            if rel.parts and rel.parts[0] == ".git":
                continue
            snapshot[str(rel)] = path.read_bytes()
        return snapshot

    def status(self, repo: Path) -> str:
        return self.git(repo, "status", "--porcelain").stdout

    def git_state(self, repo: Path) -> dict[str, object]:
        return {
            "head": self.git(repo, "rev-parse", "HEAD").stdout,
            "index": self.git(repo, "ls-files", "-s").stdout,
            "refs": self.git(repo, "for-each-ref").stdout,
            "status": self.status(repo),
        }

    # -- fixture builders ---------------------------------------------------

    def _fixture_dict(self, accepted: str, adopter_rev: str) -> dict[str, object]:
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
    ) -> dict[str, object]:
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
        self.write(self.adopter, ".aicore/adoption-review.yaml", review)
        self.write(self.adopter, "content/greeting.txt", destination_text)
        baseline_destination = (
            destination_text if lock_destination_text is None else lock_destination_text
        )
        lock = greeting_lock_document(
            accepted,
            accepted_text,
            baseline_destination,
            catalog,
            declaration,
            review,
            mode,
        )
        self.write(
            self.adopter,
            ".aicore/adoption.lock.yaml",
            yaml.safe_dump(lock, sort_keys=False),
        )
        adopter_rev = self.commit(self.adopter, "adopter")
        return self._fixture_dict(accepted, adopter_rev)

    def build_raw(
        self,
        catalog: str,
        declaration: str,
        review: str,
        lock_builder: Callable[[str], dict[str, object]],
        upstream_files: dict[str, object],
        adopter_files: dict[str, object],
    ) -> dict[str, object]:
        """Build a fixture from explicit documents; ``lock_builder`` gets the accepted sha."""
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
        lock = lock_builder(accepted)
        self.write(
            self.adopter,
            ".aicore/adoption.lock.yaml",
            yaml.safe_dump(lock, sort_keys=False),
        )
        adopter_rev = self.commit(self.adopter, "adopter")
        return self._fixture_dict(accepted, adopter_rev)

    def build_two_unit(
        self,
        review: str,
        note_committed: str = "note v1\n",
        note_target: str = "note v2\n",
        declaration: str = TWO_UNIT_DECLARATION,
        catalog: str = TWO_UNIT_CATALOG,
    ) -> dict[str, object]:
        self.init_repo(self.upstream)
        self.write(self.upstream, CATALOG_REL, catalog)
        self.write(self.upstream, "content/greeting.txt", "hello\n")
        self.write(self.upstream, "content/note.txt", note_committed)
        accepted = self.commit(self.upstream, "accepted")
        self.write(self.upstream, "content/note.txt", note_target)
        self.commit(self.upstream, "target")
        self.init_repo(self.adopter)
        self.write(self.adopter, ".aicore/adoption.yaml", declaration)
        self.write(self.adopter, ".aicore/adoption-review.yaml", review)
        self.write(self.adopter, "content/greeting.txt", "hello\n")
        self.write(self.adopter, "content/note-local.txt", "note adapted v1\n")
        lock = two_unit_lock_document(
            accepted,
            "hello\n",
            note_committed,
            "hello\n",
            "note adapted v1\n",
            catalog,
            declaration,
            review,
        )
        self.write(
            self.adopter,
            ".aicore/adoption.lock.yaml",
            yaml.safe_dump(lock, sort_keys=False),
        )
        adopter_rev = self.commit(self.adopter, "adopter")
        return self._fixture_dict(accepted, adopter_rev)

    def build_destination_owned_pair(self) -> dict[str, object]:
        """Mirror ``greeting`` beside a steady ``destination_owned`` unit.

        The lock is generated through the real ``propose-lock`` path, so the
        pair is baselined exactly as a first adoption would be: ``greeting``
        stays writable when its upstream file advances, while ``owned-note``
        — whose destination file is the adopter's own bytes over its own
        upstream source — never enters a write set.
        """
        self.init_repo(self.upstream)
        self.write(self.upstream, CATALOG_REL, DESTINATION_OWNED_PAIR_CATALOG)
        self.write(self.upstream, "content/greeting.txt", "hello\n")
        self.write(self.upstream, "content/owned-note.txt", "owned upstream v1\n")
        accepted = self.commit(self.upstream, "accepted")
        self.init_repo(self.adopter)
        self.write(
            self.adopter,
            ".aicore/adoption.yaml",
            DESTINATION_OWNED_PAIR_DECLARATION,
        )
        self.write(self.adopter, ".aicore/adoption-review.yaml", EMPTY_REVIEW)
        self.write(self.adopter, "content/greeting.txt", "hello\n")
        self.write(self.adopter, "content/owned-local.txt", OWNED_DESTINATION_TEXT)
        adopter_rev = self.commit(self.adopter, "adopter")
        proposal = self.run_cli(
            "propose-lock",
            "--upstream-repo", str(self.upstream),
            "--catalog", str(self.upstream / CATALOG_REL),
            "--declaration", str(self.adopter / ".aicore/adoption.yaml"),
            "--review", str(self.adopter / ".aicore/adoption-review.yaml"),
            "--adopter-revision", adopter_rev,
        )
        assert proposal.returncode == 0, proposal.stderr
        self.write(self.adopter, ".aicore/adoption.lock.yaml", proposal.stdout)
        adopter_rev = self.commit(self.adopter, "lock")
        return self._fixture_dict(accepted, adopter_rev)

    def build_assertions(
        self,
        lock_opencode: bool = True,
        current_opencode: bool = True,
        lock_gitignore: bool = True,
        current_gitignore: bool = True,
        declaration: str = ASSERTION_DECLARATION,
        review: str = EMPTY_REVIEW,
        catalog: str = ASSERTION_CATALOG,
    ) -> dict[str, object]:
        self.init_repo(self.upstream)
        self.write(self.upstream, CATALOG_REL, catalog)
        self.write(self.upstream, "content/.keep", "")
        accepted = self.commit(self.upstream, "accepted")
        self.init_repo(self.adopter)
        self.write(self.adopter, ".aicore/adoption.yaml", declaration)
        self.write(self.adopter, ".aicore/adoption-review.yaml", review)
        opencode_lines = ["// managed file"]
        if current_opencode:
            opencode_lines.append('    "sudo *": "deny",')
        self.write(self.adopter, "opencode.jsonc", "\n".join(opencode_lines) + "\n")
        gitignore_lines = ["# managed file"]
        if current_gitignore:
            gitignore_lines.append("output/")
        self.write(self.adopter, ".gitignore", "\n".join(gitignore_lines) + "\n")
        lock = assertion_lock_document(
            accepted, lock_opencode, lock_gitignore, catalog, declaration, review
        )
        self.write(
            self.adopter,
            ".aicore/adoption.lock.yaml",
            yaml.safe_dump(lock, sort_keys=False),
        )
        adopter_rev = self.commit(self.adopter, "adopter")
        return self._fixture_dict(accepted, adopter_rev)

    def build_guarded_root(self, destination_root: str) -> dict[str, object]:
        self.init_repo(self.upstream)
        self.write(self.upstream, CATALOG_REL, GUARDED_ROOT_CATALOG)
        self.write(self.upstream, "AGENTS.md", UPSTREAM_ROOT)
        accepted = self.commit(self.upstream, "accepted")
        self.init_repo(self.adopter)
        self.write(
            self.adopter, ".aicore/adoption.yaml", GUARDED_ROOT_DECLARATION
        )
        self.write(self.adopter, ".aicore/adoption-review.yaml", EMPTY_REVIEW)
        self.write(self.adopter, "AGENTS.md", destination_root)
        lock = guarded_root_lock_document(accepted, destination_root)
        self.write(
            self.adopter,
            ".aicore/adoption.lock.yaml",
            yaml.safe_dump(lock, sort_keys=False),
        )
        adopter_rev = self.commit(self.adopter, "adopter")
        return self._fixture_dict(accepted, adopter_rev)

    def build_stories(
        self,
        destination_index: str | None,
        ticket: bool = True,
    ) -> dict[str, object]:
        """Story fixture: story files converge; only the destination index may differ.

        The lock is generated through the real ``propose-lock`` path so the
        fixture never hand-builds digests.
        """
        self.init_repo(self.upstream)
        self.write(self.upstream, CATALOG_REL, STORY_CATALOG)
        self.write(self.upstream, "user-stories/alpha.md", "alpha v1\n")
        self.write(self.upstream, "user-stories/beta.md", "beta v1\n")
        self.write(self.upstream, "user-stories/gamma.md", "gamma v1\n")
        self.write(self.upstream, "user-stories/index.md", STORY_CORE_INDEX)
        accepted = self.commit(self.upstream, "accepted")
        declaration = STORY_DECLARATION if ticket else STORY_DECLARATION_NO_TICKET
        self.init_repo(self.adopter)
        self.write(self.adopter, ".aicore/adoption.yaml", declaration)
        self.write(self.adopter, ".aicore/adoption-review.yaml", EMPTY_REVIEW)
        self.write(self.adopter, "user-stories/alpha.md", "alpha v1\n")
        self.write(self.adopter, "user-stories/beta.md", "beta v1\n")
        if ticket:
            self.write(self.adopter, "user-stories/gamma.md", "gamma v1\n")
        if destination_index is not None:
            self.write(self.adopter, "user-stories/index.md", destination_index)
        adopter_rev = self.commit(self.adopter, "adopter")
        proposal = self.run_cli(
            "propose-lock",
            "--upstream-repo", str(self.upstream),
            "--catalog", str(self.upstream / CATALOG_REL),
            "--declaration", str(self.adopter / ".aicore/adoption.yaml"),
            "--review", str(self.adopter / ".aicore/adoption-review.yaml"),
            "--adopter-revision", adopter_rev,
        )
        assert proposal.returncode == 0, proposal.stderr
        self.write(self.adopter, ".aicore/adoption.lock.yaml", proposal.stdout)
        adopter_rev = self.commit(self.adopter, "lock")
        return self._fixture_dict(accepted, adopter_rev)

    def build_mixed_mode(self, review: str = MIXED_REVIEW) -> dict[str, object]:
        """First-adoption fixture: modes recorded before any staged core byte.

        Stage A commits the owner's pre-existing destination content (adapted
        rulebook, replacement agent, reviewed root, destination index), stage
        B commits only the declaration and review — the mode-review record —
        and stage C commits the ``mirror`` member's core bytes. The lock is
        generated through the real ``propose-lock`` path.
        """
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
        # Stage A — pre-existing owner content, read at the mode review.
        self.write(self.adopter, "skills/rules.md", ADAPTED_RULEBOOK)
        self.write(self.adopter, "agents/helper/profile.md", REPLACEMENT_AGENT)
        self.write(self.adopter, "AGENTS.md", CLEAN_DESTINATION_ROOT)
        self.write(self.adopter, "user-stories/index.md", MIXED_DESTINATION_INDEX)
        owner_commit = self.commit(self.adopter, "owner content")
        # Stage B — the mode-review record: control surfaces only.
        self.write(self.adopter, ".aicore/adoption.yaml", MIXED_DECLARATION)
        self.write(self.adopter, ".aicore/adoption-review.yaml", review)
        control_commit = self.commit(self.adopter, "mode review recorded")
        # Stage C — the first copy: the mirror member's core bytes.
        self.write(self.adopter, "user-stories/alpha.md", "alpha v1\n")
        staged = self.commit(self.adopter, "content staged")
        proposal = self.run_cli(
            "propose-lock",
            "--upstream-repo", str(self.upstream),
            "--catalog", str(self.upstream / CATALOG_REL),
            "--declaration", str(self.adopter / ".aicore/adoption.yaml"),
            "--review", str(self.adopter / ".aicore/adoption-review.yaml"),
            "--adopter-revision", staged,
        )
        assert proposal.returncode == 0, proposal.stderr
        self.write(self.adopter, ".aicore/adoption.lock.yaml", proposal.stdout)
        adopter_rev = self.commit(self.adopter, "lock")
        fixture = self._fixture_dict(accepted, adopter_rev)
        fixture["owner_commit"] = owner_commit
        fixture["control_commit"] = control_commit
        fixture["staged_commit"] = staged
        return fixture

    # -- verify-all fixture -------------------------------------------------

    def _verify_adopter_repo(
        self,
        repo: Path,
        accepted: str,
        upstream_text: str,
        destination_text: str,
    ) -> None:
        self.init_repo(repo)
        self.write(repo, ".aicore/adoption.yaml", GREETING_DECLARATION)
        self.write(repo, ".aicore/adoption-review.yaml", EMPTY_REVIEW)
        self.write(repo, "content/greeting.txt", destination_text)
        lock = greeting_lock_document(
            accepted,
            upstream_text,
            destination_text,
            GREETING_CATALOG,
            GREETING_DECLARATION,
            EMPTY_REVIEW,
        )
        self.write(
            repo,
            ".aicore/adoption.lock.yaml",
            yaml.safe_dump(lock, sort_keys=False),
        )
        self.commit(repo, "adopter")

    def _registry_text(self, adopter_ids: list[str]) -> str:
        adopters = []
        for adopter_id in adopter_ids:
            adopters.append(
                {
                    "id": adopter_id,
                    "repository": f"local/{adopter_id}",
                    "default_branch": "main",
                    "declaration_path": ".aicore/adoption.yaml",
                    "lock_path": ".aicore/adoption.lock.yaml",
                    "review_path": ".aicore/adoption-review.yaml",
                }
            )
        document = {
            "schema_version": 2,
            "upstream_repository": UPSTREAM_ID,
            "adopters": adopters,
        }
        return yaml.safe_dump(document, sort_keys=False)

    def build_verify(self) -> dict[str, object]:
        self.init_repo(self.upstream)
        self.write(self.upstream, CATALOG_REL, GREETING_CATALOG)
        self.write(self.upstream, "content/greeting.txt", "hello\n")
        accepted = self.commit(self.upstream, "accepted")
        self.write(self.upstream, "content/greeting.txt", "hello world\n")
        target = self.commit(self.upstream, "target")
        checkouts = self.root / "checkouts"
        self._verify_adopter_repo(
            checkouts / "good", target, "hello world\n", "hello world\n"
        )
        self._verify_adopter_repo(
            checkouts / "stale", accepted, "hello\n", "hello\n"
        )
        current_registry = self.root / "registry-current.yaml"
        current_registry.write_text(self._registry_text(["good"]), encoding="utf-8")
        stale_registry = self.root / "registry-stale.yaml"
        stale_registry.write_text(
            self._registry_text(["good", "stale"]), encoding="utf-8"
        )
        return {
            "upstream": self.upstream,
            "catalog": self.upstream / CATALOG_REL,
            "checkouts": checkouts,
            "current_registry": current_registry,
            "stale_registry": stale_registry,
            "accepted": accepted,
            "target": target,
        }


INCOMPLETE_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units: []
"""

NOT_APPLICABLE_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: greeting
    mode: not_applicable
"""

DESTINATION_OWNED_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: greeting
    mode: destination_owned
    members:
      - { id: file, destination: content/greeting.txt }
"""

# Two units with independent upstream deltas: ``greeting`` is a plain
# copy/mirror unit ``apply`` may write, ``owned-note`` is ``destination_owned``
# over its own source file, so advancing one upstream file never moves the
# other unit's disposition.
DESTINATION_OWNED_PAIR_CATALOG = """schema_version: 2
catalog:
  version: 2.0.0
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: greeting
    kind: infra
    applicability: { always: true }
    install_strategy: copy
    sync_projection: file
    members:
      - { id: file, source: content/greeting.txt, destination: content/greeting.txt }
  - id: owned-note
    kind: infra
    applicability: { always: true }
    install_strategy: copy
    sync_projection: file
    members:
      - { id: file, source: content/owned-note.txt, destination: content/owned-local.txt }
"""

DESTINATION_OWNED_PAIR_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: greeting
    mode: mirror
    members:
      - { id: file, destination: content/greeting.txt }
  - id: owned-note
    mode: destination_owned
    members:
      - { id: file, destination: content/owned-local.txt }
"""

OWNED_DESTINATION_TEXT = "owned destination bytes\n"


class DigestGoldenTests(EngineTestCase):
    def test_file_hello_golden_vector(self) -> None:
        digest = member_file("hello\n")
        assert digest == (
            "sha256:cf41078b082e3740168bd7ad534ba1b70b12489c7ab43c6fb53743b0f3527887"
        ), f"golden vector mismatch: {digest}"


class SchemaParsingTests(EngineTestCase):
    def test_v2_documents_parse(self) -> None:
        catalog = self.write(self.root, "catalog.yaml", GREETING_CATALOG)
        declaration = self.write(self.root, "declaration.yaml", GREETING_DECLARATION)
        review = self.write(self.root, "review.yaml", EMPTY_REVIEW)
        lock = greeting_lock_document("a" * 40, "hello\n", "hello\n")
        lock_path = self.write(
            self.root, "lock.yaml", yaml.safe_dump(lock, sort_keys=False)
        )
        assert isinstance(engine.load_catalog(str(catalog)), dict)
        assert isinstance(engine.load_declaration(str(declaration)), dict)
        assert isinstance(engine.load_review(str(review)), dict)
        assert isinstance(engine.load_lock(str(lock_path)), dict)

    @pytest.mark.parametrize(
        "name,loader_name,text",
        [
            (
                "catalog",
                "load_catalog",
                "schema_version: 1\ncatalog: {}\nunits: []\n",
            ),
            ("declaration", "load_declaration", "schema_version: 1\nunits: []\n"),
            ("review", "load_review", "schema_version: 1\ndecisions: []\n"),
            ("lock", "load_lock", "schema_version: 1\nunits: []\n"),
        ],
    )
    def test_v1_documents_require_upgrade(
        self, name: str, loader_name: str, text: str
    ) -> None:
        path = self.write(self.root, f"v1-{name}.yaml", text)
        loader = getattr(engine, loader_name)
        with pytest.raises(engine.SyncError) as caught:
            loader(str(path))
        assert caught.value.code == "schema_upgrade_required", (
            f"{name}: {caught.value.message}"
        )

    def test_v1_catalog_cli_exit_2(self) -> None:
        fixture = self.build_greeting()
        v1_catalog = self.write(
            self.root,
            "v1-cli-catalog.yaml",
            "schema_version: 1\ncatalog: {}\nunits: []\n",
        )
        args = [
            "check",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(v1_catalog),
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--lock", str(fixture["lock"]),
            "--adopter-revision", fixture["adopter_rev"],
        ]
        self.assert_exit(self.run_cli(*args), 2, "schema_upgrade_required")

    def test_unknown_projection_is_fatal(self) -> None:
        catalog = self.write(
            self.root,
            "unknown-projection.yaml",
            GREETING_CATALOG.replace(
                "sync_projection: file", "sync_projection: mystery"
            ),
        )
        with pytest.raises(engine.SyncError) as caught:
            engine.load_catalog(str(catalog))
        assert caught.value.code == "unsupported_projection"


class LockValidityTests(EngineTestCase):
    def test_lock_row_with_source_commit_is_invalid_lock(self) -> None:
        lock = greeting_lock_document("a" * 40, "hello\n", "hello\n")
        lock["units"][0]["accepted_source_commit"] = "b" * 40
        path = self.write(
            self.root, "row-source.lock.yaml", yaml.safe_dump(lock, sort_keys=False)
        )
        with pytest.raises(engine.SyncError) as caught:
            engine.load_lock(str(path))
        assert caught.value.code == "invalid_lock"
        fixture = self.build_greeting()
        args = [
            "check",
            *self.base_check_args(fixture, lock=path),
            "--adopter-revision", fixture["adopter_rev"],
        ]
        self.assert_exit(self.run_cli(*args), 2, "invalid_lock")

    def test_mixed_baseline_lock_is_rejected(self) -> None:
        fixture = self.build_two_unit(EMPTY_REVIEW)
        lock_document = yaml.safe_load(fixture["lock"].read_text(encoding="utf-8"))
        target_note = self.git(
            fixture["upstream"], "show", f"{fixture['target']}:content/note.txt"
        ).stdout
        for row in lock_document["units"]:
            if row["id"] == "note":
                row["accepted_upstream_digest"] = engine.unit_digest(
                    [("file", member_file(target_note))]
                )
        lock_document["accepted_snapshot_digest"] = snapshot_digest(
            TWO_UNIT_DECLARATION, EMPTY_REVIEW, lock_document["units"]
        )
        mixed = self.write(
            self.root,
            "mixed-baseline.lock.yaml",
            yaml.safe_dump(lock_document, sort_keys=False),
        )
        args = [
            "check",
            *self.base_check_args(fixture, lock=mixed),
            "--adopter-revision", fixture["adopter_rev"],
        ]
        self.assert_exit(self.run_cli(*args), 2, "invalid_lock")

    def test_tampered_snapshot_digest_is_invalid_lock(self) -> None:
        fixture = self.build_greeting()
        lock_document = yaml.safe_load(fixture["lock"].read_text(encoding="utf-8"))
        lock_document["accepted_snapshot_digest"] = placeholder_digest("tampered")
        tampered = self.write(
            self.root,
            "tampered-snapshot.lock.yaml",
            yaml.safe_dump(lock_document, sort_keys=False),
        )
        args = [
            "check",
            *self.base_check_args(fixture, lock=tampered),
            "--adopter-revision", fixture["adopter_rev"],
        ]
        self.assert_exit(self.run_cli(*args), 2, "invalid_lock")


class ExitContractTests(EngineTestCase):
    def _check(self, fixture: dict[str, object], *extra: str) -> subprocess.CompletedProcess:
        return self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision", fixture["adopter_rev"],
            "--format", "json",
            *extra,
        )

    def test_compliant_exit_0(self) -> None:
        fixture = self.build_greeting()
        proc = self._check(fixture)
        self.assert_exit(proc, 0)
        report = json.loads(proc.stdout)
        assert report["compliance"]
        assert report["units"][0]["disposition"] == "current"

    def test_update_available_exit_1(self) -> None:
        fixture = self.build_greeting(advance="content")
        proc = self._check(fixture)
        self.assert_exit(proc, 1)
        report = json.loads(proc.stdout)
        assert not report["compliance"]
        assert report["units"][0]["disposition"] == "update_available"

    def test_baseline_advance_required_exit_1(self) -> None:
        fixture = self.build_greeting(advance="empty")
        proc = self._check(fixture)
        self.assert_exit(proc, 1)
        report = json.loads(proc.stdout)
        assert report["units"][0]["disposition"] == "baseline_advance_required"

    def test_mirror_changed_on_both_sides_is_conflict_exit_1(self) -> None:
        fixture = self.build_greeting(
            advance="content",
            destination_text="hello world\n",
            lock_destination_text="hello\n",
        )
        proc = self._check(fixture)
        self.assert_exit(proc, 1)
        report = json.loads(proc.stdout)
        assert not report["compliance"]
        assert report["units"][0]["disposition"] == "conflict"

    def test_destination_owned_steady_state_is_unmanaged_exit_0(self) -> None:
        fixture = self.build_greeting(
            declaration=DESTINATION_OWNED_DECLARATION,
            mode="destination_owned",
        )
        proc = self._check(fixture)
        self.assert_exit(proc, 0)
        report = json.loads(proc.stdout)
        assert report["compliance"]
        assert report["units"][0]["disposition"] == "unmanaged"

    def test_destination_owned_upstream_changed_without_decision_exit_2(self) -> None:
        fixture = self.build_greeting(
            advance="content",
            declaration=DESTINATION_OWNED_DECLARATION,
            mode="destination_owned",
        )
        proc = self._check(fixture)
        self.assert_exit(proc, 2, "review_changed")

    def test_destination_owned_upstream_changed_with_decision_is_nonfatal(self) -> None:
        fixture = self.build_greeting(
            advance="content",
            declaration=DESTINATION_OWNED_DECLARATION,
            review=GREETING_DECISION_REVIEW,
            mode="destination_owned",
        )
        proc = self._check(fixture)
        assert proc.returncode != 2, (
            f"reviewed change must be non-fatal\n{proc.stderr}"
        )
        report = json.loads(proc.stdout)
        assert report["units"][0]["disposition"] == "review_required"

    def test_diagnostic_never_exit_0(self) -> None:
        fixture = self.build_greeting(advance="content")
        proc = self._check(fixture, "--diagnostic-revision", fixture["accepted"])
        self.assert_exit(proc, 1)
        report = json.loads(proc.stdout)
        assert not report["compliance"]
        assert report["diagnostic"]

    def test_fatal_missing_declaration_exit_2(self) -> None:
        fixture = self.build_greeting()
        missing = self.root / "absent" / "adoption.yaml"
        args = [
            "check",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(missing),
            "--review", str(fixture["review"]),
            "--lock", str(fixture["lock"]),
            "--adopter-revision", fixture["adopter_rev"],
        ]
        self.assert_exit(self.run_cli(*args), 2, "invalid_declaration")

    def test_missing_snapshot_selection_exit_2(self) -> None:
        fixture = self.build_greeting()
        proc = self.run_cli("check", *self.base_check_args(fixture))
        self.assert_exit(proc, 2, "adopter_snapshot_unavailable")


class DeclarationValidationTests(EngineTestCase):
    def test_missing_applicable_unit_is_declaration_incomplete(self) -> None:
        fixture = self.build_greeting(declaration=INCOMPLETE_DECLARATION)
        args = [
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision", fixture["adopter_rev"],
        ]
        self.assert_exit(self.run_cli(*args), 2, "declaration_incomplete")

    def test_always_unit_not_applicable_is_invalid_applicability(self) -> None:
        def lock_builder(accepted: str) -> dict[str, object]:
            rows = [{"id": "greeting", "mode": "not_applicable"}]
            return {
                "schema_version": 2,
                "upstream_repository": UPSTREAM_ID,
                "accepted_source_commit": accepted,
                "accepted_catalog_digest": sha256_text(GREETING_CATALOG),
                "declaration_digest": sha256_text(NOT_APPLICABLE_DECLARATION),
                "review_digest": sha256_text(EMPTY_REVIEW),
                "accepted_snapshot_digest": snapshot_digest(
                    NOT_APPLICABLE_DECLARATION, EMPTY_REVIEW, rows
                ),
                "units": rows,
            }

        fixture = self.build_raw(
            GREETING_CATALOG,
            NOT_APPLICABLE_DECLARATION,
            EMPTY_REVIEW,
            lock_builder,
            {"content/greeting.txt": "hello\n"},
            {"content/greeting.txt": "hello\n"},
        )
        args = [
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision", fixture["adopter_rev"],
        ]
        self.assert_exit(self.run_cli(*args), 2, "invalid_applicability")


class AssertionTests(EngineTestCase):
    def _check(self, fixture: dict[str, object]) -> subprocess.CompletedProcess:
        return self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision", fixture["adopter_rev"],
            "--format", "json",
        )

    def _propose(self, fixture: dict[str, object]) -> subprocess.CompletedProcess:
        return self.run_cli(
            "propose-lock",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--lock", str(fixture["lock"]),
            "--adopter-revision", fixture["adopter_rev"],
        )

    def test_assertions_present_compliant_and_proposable(self) -> None:
        fixture = self.build_assertions()
        proc = self._check(fixture)
        self.assert_exit(proc, 0)
        assert json.loads(proc.stdout)["compliance"]
        self.assert_exit(self._propose(fixture), 0)

    def test_missing_opencode_gate_noncompliant_and_propose_refuses(self) -> None:
        fixture = self.build_assertions(current_opencode=False)
        proc = self._check(fixture)
        self.assert_exit(proc, 1)
        assert not json.loads(proc.stdout)["compliance"]
        self.assert_exit(self._propose(fixture), 2, "local_drift")

    def test_missing_gitignore_entry_noncompliant_and_propose_refuses(self) -> None:
        fixture = self.build_assertions(current_gitignore=False)
        proc = self._check(fixture)
        self.assert_exit(proc, 1)
        assert not json.loads(proc.stdout)["compliance"]
        self.assert_exit(self._propose(fixture), 2, "local_drift")


class GuardedRootPolicyTests(EngineTestCase):
    def _check(self, fixture: dict[str, object]) -> subprocess.CompletedProcess:
        return self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision", fixture["adopter_rev"],
            "--format", "json",
        )

    def _propose(self, fixture: dict[str, object]) -> subprocess.CompletedProcess:
        return self.run_cli(
            "propose-lock",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--lock", str(fixture["lock"]),
            "--adopter-revision", fixture["adopter_rev"],
        )

    def assert_proposal_policy_violation(self, root: str) -> None:
        fixture = self.build_guarded_root(root)
        proc = self._propose(fixture)
        self.assert_exit(proc, 2, "policy_violation")
        assert proc.stdout == "", "a rejected proposal must emit no YAML"

    def test_clean_destination_root_passes_with_unchanged_lock_shape(self) -> None:
        fixture = self.build_guarded_root(CLEAN_DESTINATION_ROOT)
        check = self._check(fixture)
        self.assert_exit(check, 0)
        report = json.loads(check.stdout)
        assert report["compliance"]
        assert report["units"][0]["disposition"] == "current"
        proposal = self._propose(fixture)
        self.assert_exit(proposal, 0)
        unit = yaml.safe_load(proposal.stdout)["units"][0]
        member = unit["members"][0]
        upstream_member = member_file(UPSTREAM_ROOT)
        assert unit["accepted_upstream_digest"] == engine.unit_digest(
            [("root", upstream_member)]
        )
        assert member["accepted_upstream_digest"] == upstream_member
        assert member["accepted_destination_digest"] == member_file(
            CLEAN_DESTINATION_ROOT
        )
        assert set(member) == {
            "id",
            "destination",
            "accepted_upstream_digest",
            "accepted_destination_digest",
        }

    def test_missing_required_destination_markers_rejects_proposal(self) -> None:
        self.assert_proposal_policy_violation(
            "# Relay project runtime\n> **Project identity:** Relay\n"
        )

    @pytest.mark.parametrize(
        "marker",
        [
            "> **Project identity:** Relay\n",
            "> **Spec version:** 2.1.0\n",
            "> **Local version:** 1.0.0\n",
        ],
    )
    def test_each_required_destination_marker_is_enforced(self, marker: str) -> None:
        violation = engine._adopter_root_policy_violation(
            CLEAN_DESTINATION_ROOT.replace(marker, "").encode("utf-8")
        )
        assert violation is not None

    @pytest.mark.parametrize(
        "reference",
        [
            "AiCoRe",
            "AI-CORE",
            "MIGRATE-CORE-TO-PROJECT",
            "SYNC-AICORE-ADOPTION",
            ".AICORE/",
            "UPSTREAM PROVENANCE",
            "UPSTREAM LINEAGE",
            "REUSE GUIDE",
        ],
    )
    def test_all_forbidden_references_are_case_insensitive(
        self, reference: str
    ) -> None:
        content = (CLEAN_DESTINATION_ROOT + "\n" + reference).encode("utf-8")
        assert engine._adopter_root_policy_violation(content) is not None

    def test_original_reuse_guide_rejects_proposal(self) -> None:
        self.assert_proposal_policy_violation(ORIGINAL_REUSE_GUIDE_ROOT)

    def test_renamed_verbose_upstream_lineage_rejects_proposal(self) -> None:
        self.assert_proposal_policy_violation(VERBOSE_UPSTREAM_LINEAGE_ROOT)

    def test_current_minimal_aicore_lineage_rejects_proposal(self) -> None:
        self.assert_proposal_policy_violation(MINIMAL_UPSTREAM_LINEAGE_ROOT)

    def test_locked_prohibited_root_is_policy_violation(self) -> None:
        fixture = self.build_guarded_root(MINIMAL_UPSTREAM_LINEAGE_ROOT)
        proc = self._check(fixture)
        self.assert_exit(proc, 1)
        report = json.loads(proc.stdout)
        assert not report["compliance"]
        assert report["units"][0]["upstream_delta"] == "unchanged"
        assert report["units"][0]["destination_delta"] == "unchanged"
        assert report["units"][0]["disposition"] == "policy_violation"
        assert "root-runtime-spec: policy_violation" in report["blocking_reasons"]

    def test_non_utf8_destination_root_rejects_proposal(self) -> None:
        fixture = self.build_guarded_root(CLEAN_DESTINATION_ROOT)
        (fixture["adopter"] / "AGENTS.md").write_bytes(b"\xff\xfe")
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "non-utf8 root")
        proc = self._propose(fixture)
        self.assert_exit(proc, 2, "policy_violation")
        assert proc.stdout == ""


class StoryIndexProjectionTests(EngineTestCase):
    """Portable-story index merge: seeding, row replacement, collision reporting."""

    def _members(
        self, *entries: tuple[str, str, str | None]
    ) -> list[engine.StoryMergeMember]:
        members: list[engine.StoryMergeMember] = []
        for slug, destination, policy in entries:
            member: engine.StoryMergeMember = {
                "id": slug,
                "destination": destination,
                "collision_policy": policy,
            }
            members.append(member)
        return members

    def test_unknown_collision_policy_is_invalid_mapping(self) -> None:
        catalog = self.write(
            self.root,
            "bad-collision-policy.yaml",
            STORY_CATALOG.replace(
                "collision_policy: core_wins", "collision_policy: always_wins"
            ),
        )
        with pytest.raises(engine.SyncError) as caught:
            engine.load_catalog(str(catalog))
        assert caught.value.code == "invalid_mapping", caught.value.message

    def test_fresh_index_seeds_only_applicable_core_rows(self) -> None:
        # The passed member set models the applicable units: gamma (ticket)
        # and the AICore-only story are not members here, so neither is seeded.
        merged, collisions = engine.merge_story_index(
            STORY_CORE_INDEX.encode("utf-8"),
            None,
            self._members(
                ("alpha", "user-stories/alpha.md", "core_wins"),
                ("beta", "user-stories/beta.md", "core_wins"),
            ),
        )
        text = merged.decode("utf-8")
        assert "| `alpha` | Alpha | active | ep-a | `a` |" in text
        assert "| `beta` | Beta | active | ep-b | `b` |" in text
        assert "| `gamma` |" not in text
        assert "| `aicore-only` |" not in text
        assert text.startswith("# User Stories\n")
        assert text.endswith("## Appendices\n\nCore appendix notes.\n")
        assert collisions == []

    def test_existing_index_merge_preserves_crlf_destination_rows_and_trailing(
        self,
    ) -> None:
        destination = (
            "# User Stories\r\n"
            "\r\n"
            "| Slug | Title | Status | Epic | Affected areas |\r\n"
            "|---|---|---|---|---|\r\n"
            "| `alpha` | Alpha local edit | active | ep-a | `a` |\r\n"
            "| `dest-own` | Destination owned | active | local | `d` |\r\n"
            "\r\n"
            "## Trailing\r\n"
            "\r\n"
            "keep trailing\r\n"
        ).encode("utf-8")
        merged, collisions = engine.merge_story_index(
            STORY_CORE_INDEX.encode("utf-8"),
            destination,
            self._members(
                ("alpha", "user-stories/alpha.md", "core_wins"),
                ("beta", "user-stories/beta.md", "core_wins"),
            ),
        )
        assert b"\n" not in merged.replace(b"\r\n", b""), (
            "every line ending must stay CRLF"
        )
        assert b"| `alpha` | Alpha | active | ep-a | `a` |\r\n" in merged
        assert b"| `beta` | Beta | active | ep-b | `b` |\r\n" in merged
        assert b"| `dest-own` | Destination owned | active | local | `d` |\r\n" in merged
        assert merged.endswith(b"\r\n## Trailing\r\n\r\nkeep trailing\r\n")
        assert collisions == [
            "collision: path user-stories/alpha.md; core wins",
            "collision: slug alpha; core wins",
        ]

    def test_identical_rows_report_no_collisions_and_bytes_unchanged(self) -> None:
        core = STORY_CORE_INDEX.encode("utf-8")
        merged, collisions = engine.merge_story_index(
            core,
            core,
            self._members(
                ("alpha", "user-stories/alpha.md", "core_wins"),
                ("beta", "user-stories/beta.md", "core_wins"),
                ("gamma", "user-stories/gamma.md", "core_wins"),
            ),
        )
        assert merged == core
        assert collisions == []

    def test_differing_core_wins_rows_report_path_and_slug_once(self) -> None:
        destination = STORY_DESTINATION_INDEX.encode("utf-8")
        merged, collisions = engine.merge_story_index(
            STORY_CORE_INDEX.encode("utf-8"),
            destination,
            self._members(
                ("alpha", "user-stories/alpha.md", "core_wins"),
                ("beta", "user-stories/beta.md", "core_wins"),
            ),
        )
        assert collisions == [
            "collision: path user-stories/alpha.md; core wins",
            "collision: slug alpha; core wins",
        ]
        assert b"| `alpha` | Alpha | active | ep-a | `a` |" in merged
        assert b"| `alpha` | Alpha local edit |" not in merged
        assert b"| `dest-own` | Destination owned | active | local | `d` |" in merged
        assert merged.endswith(
            b"\n## Destination notes\n\n"
            b"Local trailing section that must survive byte-for-byte.\n"
        )

    def test_differing_non_core_wins_member_writes_nothing_and_reports_nothing(
        self,
    ) -> None:
        destination = (
            "# User Stories\n"
            "\n"
            "| Slug | Title | Status | Epic | Affected areas |\n"
            "|---|---|---|---|---|\n"
            "| `beta` | Beta local edit | active | ep-b | `b` |\n"
            "| `dest-own` | Destination owned | active | local | `d` |\n"
        ).encode("utf-8")
        merged, collisions = engine.merge_story_index(
            STORY_CORE_INDEX.encode("utf-8"),
            destination,
            self._members(("beta", "user-stories/beta.md", None)),
        )
        assert merged == destination, "a non-core_wins member must not be written"
        assert collisions == []

    def test_core_index_missing_member_row_is_invalid_mapping(self) -> None:
        core_without_alpha = STORY_CORE_INDEX.replace(
            "| `alpha` | Alpha | active | ep-a | `a` |\n", ""
        )
        with pytest.raises(engine.SyncError) as caught:
            engine.merge_story_index(
                core_without_alpha.encode("utf-8"),
                STORY_DESTINATION_INDEX.encode("utf-8"),
                self._members(
                    ("alpha", "user-stories/alpha.md", "core_wins"),
                    ("beta", "user-stories/beta.md", "core_wins"),
                ),
            )
        assert caught.value.code == "invalid_mapping", caught.value.message

        # Same guard on the IO boundary: the core index beside the catalog
        # member sources has no row for the core_wins alpha member.
        self.init_repo(self.upstream)
        self.write(self.upstream, "user-stories/index.md", core_without_alpha)
        commit = self.commit(self.upstream, "core index without alpha")
        self.init_repo(self.adopter)
        self.write(self.adopter, "user-stories/index.md", STORY_DESTINATION_INDEX)
        adopter_rev = self.commit(self.adopter, "destination index")
        catalog_unit = yaml.safe_load(STORY_CATALOG)["units"][0]
        decl_unit = yaml.safe_load(STORY_DECLARATION)["units"][0]
        with pytest.raises(engine.SyncError) as caught:
            engine._story_index_collisions(
                "portable-stories-always",
                catalog_unit,
                decl_unit,
                engine._GitRepo(str(self.upstream)),
                commit,
                engine._RevisionSnapshot(
                    engine._GitRepo(str(self.adopter)), adopter_rev
                ),
            )
        assert caught.value.code == "invalid_mapping", caught.value.message

    def test_check_reports_exactly_one_core_wins_collision_pair(self) -> None:
        fixture = self.build_stories(STORY_DESTINATION_INDEX)
        index_path = fixture["adopter"] / "user-stories/index.md"
        index_before = index_path.read_bytes()
        proc = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision", fixture["adopter_rev"],
            "--format", "json",
        )
        self.assert_exit(proc, 0)
        report = json.loads(proc.stdout)
        assert report["collisions"] == [
            "collision: path user-stories/alpha.md; core wins",
            "collision: slug alpha; core wins",
        ]
        assert all(
            unit["disposition"] == "current" for unit in report["units"]
        ), report["units"]
        assert index_path.read_bytes() == index_before, (
            "check must keep destination rows and trailing bytes byte-for-byte"
        )

    def test_propose_lock_prints_collisions_to_stderr_only(self) -> None:
        fixture = self.build_stories(STORY_DESTINATION_INDEX)
        proc = self.run_cli(
            "propose-lock",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--lock", str(fixture["lock"]),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(proc, 0)
        candidate = yaml.safe_load(proc.stdout)
        assert candidate["schema_version"] == 2
        assert "collision" not in proc.stdout, (
            "collisions must be emitted on stderr only"
        )
        assert proc.stderr.splitlines() == [
            "collision: path user-stories/alpha.md; core wins",
            "collision: slug alpha; core wins",
        ]

    def test_inapplicable_story_units_are_never_projected(self) -> None:
        destination_index = STORY_DESTINATION_INDEX.replace(
            "| `gamma` | Gamma | active | ep-g | `g` |",
            "| `gamma` | Gamma local edit | active | ep-g | `g` |",
        )
        fixture = self.build_stories(destination_index, ticket=False)
        proc = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision", fixture["adopter_rev"],
            "--format", "json",
        )
        self.assert_exit(proc, 0)
        collisions = json.loads(proc.stdout)["collisions"]
        assert collisions == [
            "collision: path user-stories/alpha.md; core wins",
            "collision: slug alpha; core wins",
        ]
        assert not any("gamma" in line for line in collisions)


class FirstAdoptionSequenceTests(EngineTestCase):
    """Prepared-snapshot tests for the reordered first-adoption sequence.

    Each fixture models the skill's staged ordering — owner content first,
    then the recorded mode review, then the first copy — and the tests assert
    engine behavior on that prepared snapshot. No test executes the prose
    skill itself.
    """

    def _propose_args(self, fixture: dict[str, object], *extra: str) -> list[str]:
        return [
            "propose-lock",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--lock", str(fixture["lock"]),
            "--adopter-revision", str(fixture["adopter_rev"]),
            *extra,
        ]

    def _check_json(self, fixture: dict[str, object]) -> dict[str, object]:
        proc = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision", str(fixture["adopter_rev"]),
            "--format", "json",
        )
        self.assert_exit(proc, 0)
        return json.loads(proc.stdout)

    def test_modes_and_review_are_recorded_before_any_core_byte_is_staged(
        self,
    ) -> None:
        fixture = self.build_mixed_mode()
        adopter = fixture["adopter"]
        # Stage A holds only the owner's content: no controls, no core bytes.
        owner_names = self.git(
            adopter, "ls-tree", "-r", "--name-only", fixture["owner_commit"]
        ).stdout.splitlines()
        assert ".aicore/adoption.yaml" not in owner_names
        assert ".aicore/adoption-review.yaml" not in owner_names
        assert "user-stories/alpha.md" not in owner_names
        control_names = self.git(
            adopter, "ls-tree", "-r", "--name-only", fixture["control_commit"]
        ).stdout.splitlines()
        # The record commit carries the owner's reviewed bytes plus exactly the
        # two control documents; no core-derived content has been staged yet.
        assert sorted(control_names) == sorted(
            [
                ".aicore/adoption-review.yaml",
                ".aicore/adoption.yaml",
                "AGENTS.md",
                "agents/helper/profile.md",
                "skills/rules.md",
                "user-stories/index.md",
            ]
        )
        assert "user-stories/alpha.md" not in control_names
        declaration = yaml.safe_load(
            self.git(
                adopter,
                "show",
                f"{fixture['control_commit']}:.aicore/adoption.yaml",
            ).stdout
        )
        catalog = yaml.safe_load(MIXED_CATALOG)
        assert [unit["id"] for unit in declaration["units"]] == [
            unit["id"] for unit in catalog["units"]
        ], "every catalog unit must be classified before the first copy"
        modes = {unit["id"]: unit["mode"] for unit in declaration["units"]}
        assert modes == {
            "rulebook": "adapted",
            "helper-agent": "replacement",
            "root-runtime-spec": "adapted",
            "portable-stories-always": "mirror",
            "portable-stories-ticket": "not_applicable",
        }
        review = yaml.safe_load(
            self.git(
                adopter,
                "show",
                f"{fixture['control_commit']}:.aicore/adoption-review.yaml",
            ).stdout
        )
        assert [decision["unit"] for decision in review["decisions"]] == [
            "root-runtime-spec"
        ]
        # The owner's reviewed bytes are untouched by the record step.
        rules_at_control = self.git(
            adopter, "show", f"{fixture['control_commit']}:skills/rules.md"
        ).stdout
        assert rules_at_control == ADAPTED_RULEBOOK
        # The first core byte lands only in the commit after the record.
        parent = self.git(
            adopter, "rev-parse", f"{fixture['staged_commit']}^"
        ).stdout.strip()
        assert parent == fixture["control_commit"]
        staged_names = self.git(
            adopter, "ls-tree", "-r", "--name-only", fixture["staged_commit"]
        ).stdout.splitlines()
        assert "user-stories/alpha.md" in staged_names

    def test_mixed_mode_fixture_passes_check_with_recorded_decisions(self) -> None:
        fixture = self.build_mixed_mode()
        report = self._check_json(fixture)
        assert report["compliance"]
        dispositions = {
            unit["id"]: unit["disposition"] for unit in report["units"]
        }
        assert dispositions == {
            "rulebook": "current",
            "helper-agent": "current",
            "root-runtime-spec": "current",
            "portable-stories-always": "current",
            "portable-stories-ticket": "not_applicable",
        }
        assert report["collisions"] == []

    def test_unreviewed_differing_non_mirror_blocks_propose_before_stdout(
        self,
    ) -> None:
        fixture = self.build_mixed_mode()
        # The adapted rulebook's upstream source moves, so the non-mirror unit
        # now differs from the accepted baseline while its review has no
        # decision for it.
        self.write(fixture["upstream"], "skills/rules.md", "core rulebook v2\n")
        self.commit(fixture["upstream"], "rulebook v2")
        blocked = self.run_cli(*self._propose_args(fixture))
        self.assert_exit(blocked, 2, "review_changed")
        assert "rulebook" in blocked.stderr
        assert blocked.stdout == "", (
            "no lock YAML may reach stdout before the decision is recorded"
        )
        # With the decision recorded, the same fixture proposes and passes check.
        self.write(
            fixture["adopter"],
            ".aicore/adoption-review.yaml",
            MIXED_REVIEW_RULEBOOK,
        )
        fixture["adopter_rev"] = self.commit(
            fixture["adopter"], "rulebook decision recorded"
        )
        proposal = self.run_cli(*self._propose_args(fixture))
        self.assert_exit(proposal, 0)
        assert "schema_version: 2" in proposal.stdout
        self.write(fixture["adopter"], ".aicore/adoption.lock.yaml", proposal.stdout)
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "reviewed lock")
        report = self._check_json(fixture)
        assert report["compliance"], report["blocking_reasons"]

    def test_adapted_bytes_survive_a_careful_edit(self) -> None:
        fixture = self.build_mixed_mode()
        adopter = fixture["adopter"]
        rules_path = adopter / "skills/rules.md"
        core_bytes = (fixture["upstream"] / "skills/rules.md").read_bytes()
        reviewed = rules_path.read_bytes()
        assert reviewed == ADAPTED_RULEBOOK.encode("utf-8")
        assert reviewed != core_bytes, (
            "the adapted destination must differ from the core bytes"
        )
        edited = reviewed + b"# Reviewed local extension.\n"
        rules_path.write_bytes(edited)
        fixture["adopter_rev"] = self.commit(adopter, "careful adapted edit")
        proposal = self.run_cli(*self._propose_args(fixture))
        self.assert_exit(proposal, 0)
        lock = yaml.safe_load(proposal.stdout)
        rulebook_row = next(
            row for row in lock["units"] if row["id"] == "rulebook"
        )
        assert rulebook_row["accepted_upstream_digest"] == engine.unit_digest(
            [("rules", member_file("core rulebook v1\n"))]
        ), "the lock must keep binding the upstream digest, not destination bytes"
        assert rulebook_row["members"][0]["accepted_destination_digest"] == (
            member_file(edited.decode("utf-8"))
        ), "the lock must record the reviewed destination bytes, never core bytes"
        self.write(adopter, ".aicore/adoption.lock.yaml", proposal.stdout)
        fixture["adopter_rev"] = self.commit(adopter, "lock after edit")
        before_check = self.worktree_bytes(adopter)
        report = self._check_json(fixture)
        assert report["compliance"], report["blocking_reasons"]
        assert rules_path.read_bytes() == edited, (
            "adapted bytes must survive the edit path byte-for-byte"
        )
        assert self.worktree_bytes(adopter) == before_check, (
            "check must keep the adopter worktree byte-identical"
        )

    def test_only_applicable_story_units_arrive_and_index_bytes_survive(
        self,
    ) -> None:
        fixture = self.build_mixed_mode()
        adopter = fixture["adopter"]
        index_path = adopter / "user-stories/index.md"
        index_before = index_path.read_bytes()
        assert (adopter / "user-stories/alpha.md").read_bytes() == b"alpha v1\n"
        assert not (adopter / "user-stories/gamma.md").exists(), (
            "the inapplicable ticket story unit must never arrive"
        )
        report = self._check_json(fixture)
        assert report["collisions"] == []
        ticket = next(
            unit for unit in report["units"] if unit["id"] == "portable-stories-ticket"
        )
        assert ticket["disposition"] == "not_applicable"
        proposal = self.run_cli(*self._propose_args(fixture))
        self.assert_exit(proposal, 0)
        assert index_path.read_bytes() == index_before, (
            "destination-only rows and trailing bytes must survive byte-for-byte"
        )
        assert b"| `dest-own` | Destination owned |" in index_before
        assert index_before.endswith(
            b"Local trailing section that must survive byte-for-byte.\n"
        )
        assert b"| `gamma` |" not in index_before, (
            "an inapplicable story unit's rows must never be projected"
        )


class ReviewEvidenceTests(EngineTestCase):
    def _propose(self, fixture: dict[str, object]) -> subprocess.CompletedProcess:
        return self.run_cli(
            "propose-lock",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--lock", str(fixture["lock"]),
            "--adopter-revision", fixture["adopter_rev"],
        )

    def test_changed_non_mirror_without_decision_exit_2(self) -> None:
        fixture = self.build_two_unit(EMPTY_REVIEW)
        args = [
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision", fixture["adopter_rev"],
        ]
        self.assert_exit(self.run_cli(*args), 2, "review_changed")
        self.assert_exit(self._propose(fixture), 2, "review_changed")

    def test_changed_non_mirror_with_decision_allowed(self) -> None:
        fixture = self.build_two_unit(TWO_UNIT_DECISION_REVIEW)
        proc = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision", fixture["adopter_rev"],
            "--format", "json",
        )
        self.assert_exit(proc, 1)
        report = json.loads(proc.stdout)
        note = next(unit for unit in report["units"] if unit["id"] == "note")
        assert note["disposition"] == "update_available"
        self.assert_exit(self._propose(fixture), 0)


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
            "--adopter-revision", fixture["adopter_rev"],
        ]
        self.assert_exit(self.run_cli(*args), 0)


class ReadOnlyTests(EngineTestCase):
    def test_check_writes_nothing_to_adopter(self) -> None:
        fixture = self.build_greeting()
        before_files = self.worktree_bytes(fixture["adopter"])
        before_git = self.git_state(fixture["adopter"])
        proc = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(proc, 0)
        assert before_files == self.worktree_bytes(fixture["adopter"])
        assert before_git == self.git_state(fixture["adopter"])

    def test_propose_lock_writes_stdout_only(self) -> None:
        fixture = self.build_greeting()
        adopter_before = self.worktree_bytes(fixture["adopter"])
        upstream_before = self.worktree_bytes(fixture["upstream"])
        adopter_git = self.git_state(fixture["adopter"])
        upstream_git = self.git_state(fixture["upstream"])
        proc = self.run_cli(
            "propose-lock",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--lock", str(fixture["lock"]),
            "--adopter-revision", fixture["adopter_rev"],
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
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--registry", str(fixture["current_registry"]),
            "--checkouts-root", str(fixture["checkouts"]),
        )
        self.assert_exit(proc, 0)
        for path in adopters:
            assert before[str(path)] == self.worktree_bytes(path)
            assert before_git[str(path)] == self.git_state(path)


class ProposeLockTests(EngineTestCase):
    def test_unit_option_is_unrecognized(self) -> None:
        proc = self.run_cli("propose-lock", "--unit", "greeting")
        self.assert_exit(proc, 2, "unrecognized arguments")

    def test_candidate_is_single_revision_and_round_trips(self) -> None:
        fixture = self.build_greeting()
        proc = self.run_cli(
            "propose-lock",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--lock", str(fixture["lock"]),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(proc, 0)
        candidate = yaml.safe_load(proc.stdout)
        assert candidate["accepted_source_commit"] == fixture["target"]
        catalog = yaml.safe_load(GREETING_CATALOG)
        assert {row["id"] for row in candidate["units"]} == {
            unit["id"] for unit in catalog["units"]
        }
        for row in candidate["units"]:
            assert "accepted_source_commit" not in row
        reproduced_snapshot = engine._snapshot_digest(
            sha256_text(GREETING_DECLARATION),
            sha256_text(EMPTY_REVIEW),
            candidate["units"],
        )
        assert candidate["accepted_snapshot_digest"] == reproduced_snapshot, (
            "the engine must reproduce propose-lock's accepted_snapshot_digest"
        )
        candidate_path = self.write(
            self.root, "candidate.lock.yaml", proc.stdout
        )
        args = [
            "check",
            *self.base_check_args(fixture, lock=candidate_path),
            "--adopter-revision", fixture["adopter_rev"],
        ]
        self.assert_exit(self.run_cli(*args), 0)


class VerifyAllTests(EngineTestCase):
    def _verify(
        self, fixture: dict[str, object], registry: Path
    ) -> subprocess.CompletedProcess:
        return self.run_cli(
            "verify-all",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--registry", str(registry),
            "--checkouts-root", str(fixture["checkouts"]),
            "--format", "json",
        )

    def test_all_current_registry_exit_0(self) -> None:
        fixture = self.build_verify()
        proc = self._verify(fixture, fixture["current_registry"])
        self.assert_exit(proc, 0)
        report = json.loads(proc.stdout)
        assert report["compliance"]
        by_id = {adopter["id"]: adopter for adopter in report["adopters"]}
        assert by_id["good"]["compliance"]
        assert report["blocking_reasons"] == []

    def test_stale_registered_adopter_exit_1_without_required_field(self) -> None:
        fixture = self.build_verify()
        proc = self._verify(fixture, fixture["stale_registry"])
        self.assert_exit(proc, 1)
        report = json.loads(proc.stdout)
        assert not report["compliance"]
        by_id = {adopter["id"]: adopter for adopter in report["adopters"]}
        assert by_id["good"]["compliance"]
        assert not by_id["stale"]["compliance"]
        assert any(
            "stale" in reason for reason in report["blocking_reasons"]
        ), report["blocking_reasons"]

    def test_missing_checkout_is_blocking_without_network(self) -> None:
        fixture = self.build_verify()
        registry = self.write(
            self.root,
            "registry-missing.yaml",
            self._registry_text(["good", "ghost"]),
        )
        namespace = argparse.Namespace(
            upstream_repo=str(fixture["upstream"]),
            catalog=str(fixture["catalog"]),
            registry=str(registry),
            checkouts_root=str(fixture["checkouts"]),
            format="json",
        )
        buffer = io.StringIO()
        with mock.patch.object(
            engine, "_git_clone", return_value="simulated offline checkout"
        ):
            with contextlib.redirect_stdout(buffer):
                code = engine.run_verify(namespace)
        assert code == 1, "missing required checkout must block"
        report = json.loads(buffer.getvalue())
        ghost = next(a for a in report["adopters"] if a["id"] == "ghost")
        assert not ghost["compliance"]
        assert "repository_unavailable" in ghost["error"]
        assert any(
            "ghost" in reason for reason in report["blocking_reasons"]
        ), report["blocking_reasons"]

    def test_registry_entries_have_no_required_field(self) -> None:
        fixture = self.build_verify()
        document = yaml.safe_load(
            fixture["stale_registry"].read_text(encoding="utf-8")
        )
        assert document["adopters"]
        for adopter in document["adopters"]:
            assert "required" not in adopter
        assert isinstance(
            engine.load_registry(str(fixture["stale_registry"])), dict
        )


class ApplyTests(EngineTestCase):
    """The ``apply`` subcommand: bounded write set, refusals, preservation.

    Every case runs against a temporary fixture, asserts the exit code plus
    the stdout/stderr contract, and compares the adopter worktree captured
    before and after the run so a refusal or a no-op can be proven
    byte-for-byte write-free. All but the shared-index case drive the CLI
    through ``subprocess``; the shared-index case runs ``engine.main``
    in-process under a write recorder so its single index write is
    countable. Nothing here commits, fetches, or touches anything outside
    the temp fixture.
    """

    def _apply(
        self, fixture: dict[str, object], *extra: str
    ) -> subprocess.CompletedProcess:
        return self.run_cli(
            "apply",
            *self.base_check_args(fixture),
            "--adopter-revision", str(fixture["adopter_rev"]),
            "--format", "json",
            *extra,
        )

    def _apply_in_process(
        self, fixture: dict[str, object], *extra: str
    ) -> tuple[int, str, str]:
        """Run ``apply`` in-process so a write seam can be recorded."""
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = engine.main(
                [
                    "apply",
                    *self.base_check_args(fixture),
                    "--adopter-revision", str(fixture["adopter_rev"]),
                    "--format", "json",
                    *extra,
                ]
            )
        return int(code), stdout.getvalue(), stderr.getvalue()

    def _success_report(
        self, proc: subprocess.CompletedProcess
    ) -> dict[str, object]:
        self.assert_exit(proc, 0)
        assert proc.stdout.startswith("{"), f"stdout={proc.stdout}"
        return json.loads(proc.stdout)

    def _assert_only_changed(
        self,
        before: dict[str, object],
        after: dict[str, object],
        expected: set[str],
    ) -> None:
        assert set(before) == set(after), (
            "apply must not add or remove adopter files: "
            f"added={sorted(set(after) - set(before))} "
            f"removed={sorted(set(before) - set(after))}"
        )
        changed = {path for path in before if before[path] != after[path]}
        assert changed == expected, (
            f"expected only {sorted(expected)} to change, changed={sorted(changed)}"
        )

    def _assert_adopter_untouched(
        self, fixture: dict[str, object], before: dict[str, object]
    ) -> None:
        after = self.worktree_bytes(fixture["adopter"])
        changed = sorted(
            path for path in before if before[path] != after.get(path)
        )
        assert before == after, f"adopter bytes changed: {changed}"
        assert self.status(fixture["adopter"]) == "", (
            "a refused or empty run must leave the worktree clean"
        )

    def test_update_available_copy_mirror_writes_unit_and_regenerates_lock(
        self,
    ) -> None:
        fixture = self.build_greeting()
        self.write(fixture["upstream"], "content/greeting.txt", "hello world\n")
        self.commit(fixture["upstream"], "greeting v2")
        target = self.rev(fixture["upstream"])
        assert target != fixture["accepted"], "the upstream fixture must advance"
        adopter = fixture["adopter"]
        before = self.worktree_bytes(adopter)
        proc = self._apply(fixture)
        report = self._success_report(proc)
        assert report["apply"] == "success"
        assert report["written"] == ["greeting"], "the unit id must be reported"
        assert report["verify"] == "pass"
        assert report["blocking"] == []
        assert report["lock"] == str(fixture["lock"])
        assert "greeting" in proc.stdout, f"stdout={proc.stdout}"
        assert proc.stderr == "", f"no diagnostics expected: {proc.stderr}"
        assert (adopter / "content/greeting.txt").read_bytes() == b"hello world\n"
        lock = yaml.safe_load(
            (adopter / ".aicore/adoption.lock.yaml").read_text(encoding="utf-8")
        )
        assert lock["accepted_source_commit"] == target, (
            "apply must regenerate the lock at the target revision"
        )
        self._assert_only_changed(
            before,
            self.worktree_bytes(adopter),
            {"content/greeting.txt", ".aicore/adoption.lock.yaml"},
        )
        assert self.rev(adopter) == fixture["adopter_rev"], (
            "apply writes the worktree only; it never commits"
        )

    def test_noop_write_set_exits_zero_and_writes_nothing(self) -> None:
        fixture = self.build_greeting()
        before = self.worktree_bytes(fixture["adopter"])
        before_git = self.git_state(fixture["adopter"])
        proc = self._apply(fixture)
        report = self._success_report(proc)
        assert report["apply"] == "noop"
        assert report["written"] == []
        assert report["lock"] is None
        assert report["verify"] == "skipped"
        assert report["blocking"] == []
        assert "noop" in proc.stdout, f"stdout={proc.stdout}"
        assert proc.stderr == "", f"no diagnostics expected: {proc.stderr}"
        self._assert_adopter_untouched(fixture, before)
        assert before_git == self.git_state(fixture["adopter"]), (
            "a no-op must leave the git state untouched"
        )

    def test_conflict_refusal_exits_2_without_writing(self) -> None:
        # Both sides moved: upstream advanced and the destination holds bytes
        # the accepted baseline never recorded.
        fixture = self.build_greeting(
            advance="content",
            destination_text="hello world\n",
            lock_destination_text="hello\n",
        )
        before = self.worktree_bytes(fixture["adopter"])
        before_git = self.git_state(fixture["adopter"])
        proc = self._apply(fixture)
        self.assert_exit(proc, 2, "conflict")
        assert "apply refused" in proc.stderr, f"stderr={proc.stderr}"
        assert "greeting" in proc.stderr, f"stderr={proc.stderr}"
        assert proc.stdout == "", "a refusal must emit no report on stdout"
        self._assert_adopter_untouched(fixture, before)
        assert before_git == self.git_state(fixture["adopter"])

    def test_local_drift_refusal_exits_2_without_writing(self) -> None:
        fixture = self.build_greeting()
        adopter = fixture["adopter"]
        self.write(adopter, "content/greeting.txt", "drifted\n")
        fixture["adopter_rev"] = self.commit(adopter, "destination drift")
        before = self.worktree_bytes(adopter)
        before_git = self.git_state(adopter)
        proc = self._apply(fixture)
        self.assert_exit(proc, 2, "local_drift")
        assert "apply refused" in proc.stderr, f"stderr={proc.stderr}"
        assert proc.stdout == "", "a refusal must emit no report on stdout"
        self._assert_adopter_untouched(fixture, before)
        assert before_git == self.git_state(adopter)

    def test_unreviewed_non_mirror_refusal_exits_2_without_writing(self) -> None:
        # The adapted ``note`` unit's upstream moved with no review decision.
        fixture = self.build_two_unit(EMPTY_REVIEW)
        before = self.worktree_bytes(fixture["adopter"])
        before_git = self.git_state(fixture["adopter"])
        proc = self._apply(fixture)
        self.assert_exit(proc, 2, "review_changed")
        assert "note" in proc.stderr, f"stderr={proc.stderr}"
        assert "apply refused" in proc.stderr, f"stderr={proc.stderr}"
        assert proc.stdout == "", "a refusal must emit no report on stdout"
        self._assert_adopter_untouched(fixture, before)
        assert before_git == self.git_state(fixture["adopter"])

    def test_policy_violation_refusal_exits_2_without_writing(self) -> None:
        # The guarded adopter root still carries a prohibited upstream
        # reference, so the unit is observed as ``policy_violation`` and the
        # refusal lands before any write can be staged.
        fixture = self.build_guarded_root(ORIGINAL_REUSE_GUIDE_ROOT)
        before = self.worktree_bytes(fixture["adopter"])
        before_git = self.git_state(fixture["adopter"])
        proc = self._apply(fixture)
        self.assert_exit(proc, 2, "policy_violation")
        assert "apply refused" in proc.stderr, f"stderr={proc.stderr}"
        assert "root-runtime-spec" in proc.stderr, f"stderr={proc.stderr}"
        assert proc.stdout == "", "a refusal must emit no report on stdout"
        self._assert_adopter_untouched(fixture, before)
        assert before_git == self.git_state(fixture["adopter"])

    def test_non_copy_blocking_refusal_exits_2_without_writing(self) -> None:
        # ``opencode-config`` is a ``merge`` unit whose destination lost a
        # required assertion: a blocking ``local_drift`` on a unit apply
        # never writes must refuse the run instead of writing around it.
        fixture = self.build_assertions(current_opencode=False)
        before = self.worktree_bytes(fixture["adopter"])
        before_git = self.git_state(fixture["adopter"])
        proc = self._apply(fixture)
        self.assert_exit(proc, 2, "local_drift")
        assert "apply refused" in proc.stderr, f"stderr={proc.stderr}"
        assert "opencode-config" in proc.stderr, f"stderr={proc.stderr}"
        assert "install_strategy merge is never written by apply" in proc.stderr, (
            f"stderr={proc.stderr}"
        )
        assert proc.stdout == "", "a refusal must emit no report on stdout"
        self._assert_adopter_untouched(fixture, before)
        assert before_git == self.git_state(fixture["adopter"])

    def test_reviewed_copy_adapted_blocking_refusal_exits_2_without_writing(
        self,
    ) -> None:
        # The widened refusal shape: ``copy`` + ``adapted`` + a blocking
        # disposition, with the review decision present so the unit is NOT
        # refused through ``review_changed`` — the disposition branch itself
        # must still refuse fail-closed.
        fixture = self.build_two_unit(TWO_UNIT_DECISION_REVIEW)
        before = self.worktree_bytes(fixture["adopter"])
        before_git = self.git_state(fixture["adopter"])
        proc = self._apply(fixture)
        self.assert_exit(proc, 2, "update_available")
        assert "apply refused" in proc.stderr, f"stderr={proc.stderr}"
        assert "note: adapted unit is never written by apply" in proc.stderr, (
            f"stderr={proc.stderr}"
        )
        assert "review_changed" not in proc.stderr, (
            "the review decision must rule out the review_changed path: "
            f"{proc.stderr}"
        )
        assert proc.stdout == "", "a refusal must emit no report on stdout"
        self._assert_adopter_untouched(fixture, before)
        assert before_git == self.git_state(fixture["adopter"])

    def test_preserves_owner_bytes_and_destination_index_on_success(self) -> None:
        fixture = self.build_mixed_mode()
        adopter = fixture["adopter"]
        index_path = adopter / "user-stories/index.md"
        preserved = {
            "skills/rules.md": ADAPTED_RULEBOOK.encode("utf-8"),
            "agents/helper/profile.md": REPLACEMENT_AGENT.encode("utf-8"),
            "AGENTS.md": CLEAN_DESTINATION_ROOT.encode("utf-8"),
        }
        for relative, expected in preserved.items():
            assert (adopter / relative).read_bytes() == expected, relative
        index_before = index_path.read_bytes()
        assert (
            b"| `dest-own` | Destination owned | active | local | `d` |"
            in index_before
        )
        assert index_before.endswith(
            b"Local trailing section that must survive byte-for-byte.\n"
        )
        self.write(fixture["upstream"], "user-stories/alpha.md", "alpha v2\n")
        self.commit(fixture["upstream"], "alpha v2")
        before = self.worktree_bytes(adopter)
        proc = self._apply(fixture)
        report = self._success_report(proc)
        assert report["apply"] == "success"
        assert report["written"] == ["portable-stories-always"]
        assert report["verify"] == "pass"
        assert report["blocking"] == []
        assert proc.stderr == "", f"no collisions expected: {proc.stderr}"
        assert (adopter / "user-stories/alpha.md").read_bytes() == b"alpha v2\n"
        for relative, expected in preserved.items():
            assert (adopter / relative).read_bytes() == expected, (
                f"{relative} must survive apply byte-for-byte"
            )
        assert index_path.read_bytes() == index_before, (
            "destination-only rows and the trailing section must survive "
            "byte-for-byte"
        )
        self._assert_only_changed(
            before,
            self.worktree_bytes(adopter),
            {"user-stories/alpha.md", ".aicore/adoption.lock.yaml"},
        )

    def test_destination_owned_bytes_survive_apply(self) -> None:
        # ``greeting`` is the writable mirror unit; ``owned-note`` is a
        # steady ``destination_owned`` unit whose upstream and destination
        # are both unchanged, so its disposition never leaves ``unmanaged``.
        fixture = self.build_destination_owned_pair()
        self.write(fixture["upstream"], "content/greeting.txt", "hello world\n")
        self.commit(fixture["upstream"], "greeting v2")
        adopter = fixture["adopter"]
        owned = adopter / "content/owned-local.txt"
        owned_expected = OWNED_DESTINATION_TEXT.encode("utf-8")
        assert owned.read_bytes() == owned_expected, (
            "the fixture must start with the adopter's own bytes"
        )
        before = self.worktree_bytes(adopter)
        proc = self._apply(fixture)
        report = self._success_report(proc)
        assert report["apply"] == "success", report
        assert report["written"] == ["greeting"], report
        assert report["verify"] == "pass", report
        assert report["blocking"] == [], report
        assert proc.stderr == "", f"no diagnostics expected: {proc.stderr}"
        assert owned.read_bytes() == owned_expected, (
            "destination_owned bytes must survive apply byte-for-byte"
        )
        self._assert_only_changed(
            before,
            self.worktree_bytes(adopter),
            {"content/greeting.txt", ".aicore/adoption.lock.yaml"},
        )

    def test_writable_story_member_merges_and_reports_collision_on_stderr_only(
        self,
    ) -> None:
        destination_index = STORY_DESTINATION_INDEX.replace(
            "| `gamma` | Gamma | active | ep-g | `g` |",
            "| `gamma` | Gamma local edit | active | ep-g | `g` |",
        )
        fixture = self.build_stories(destination_index)
        self.write(fixture["upstream"], "user-stories/alpha.md", "alpha v2\n")
        self.commit(fixture["upstream"], "alpha v2")
        adopter = fixture["adopter"]
        before = self.worktree_bytes(adopter)
        proc = self._apply(fixture)
        report = self._success_report(proc)
        assert report["apply"] == "success"
        assert report["written"] == ["portable-stories-always"]
        assert report["verify"] == "pass"
        assert report["blocking"] == []
        assert "collision" not in proc.stdout, (
            "the stdout report must stay clean of story collisions"
        )
        assert proc.stderr.splitlines() == [
            "collision: path user-stories/gamma.md; core wins",
            "collision: slug gamma; core wins",
        ], f"stderr={proc.stderr}"
        index = (adopter / "user-stories/index.md").read_bytes()
        assert b"| `alpha` | Alpha | active | ep-a | `a` |" in index, (
            "the writable core_wins member's row must merge to the core row"
        )
        assert b"| `alpha` | Alpha local edit |" not in index
        assert b"| `dest-own` | Destination owned | active | local | `d` |" in index
        assert b"| `gamma` | Gamma local edit | active | ep-g | `g` |" in index, (
            "a story unit apply does not write must keep its index row"
        )
        assert index.endswith(
            b"## Destination notes\n\n"
            b"Local trailing section that must survive byte-for-byte.\n"
        )
        assert (adopter / "user-stories/alpha.md").read_bytes() == b"alpha v2\n"
        assert (adopter / "user-stories/beta.md").read_bytes() == b"beta v1\n"
        assert (adopter / "user-stories/gamma.md").read_bytes() == b"gamma v1\n"
        self._assert_only_changed(
            before,
            self.worktree_bytes(adopter),
            {
                "user-stories/alpha.md",
                "user-stories/index.md",
                ".aicore/adoption.lock.yaml",
            },
        )

    def test_two_writable_story_units_write_one_shared_index(self) -> None:
        # Both portable-story units are simultaneously ``update_available``
        # and writable, and both target ``user-stories/index.md``: the two
        # merges must compose in exactly one index write, never overwrite
        # each other, and never drop a destination-only row or the trailing
        # section.
        destination_index = STORY_DESTINATION_INDEX.replace(
            "| `gamma` | Gamma | active | ep-g | `g` |",
            "| `gamma` | Gamma local edit | active | ep-g | `g` |",
        )
        fixture = self.build_stories(destination_index)
        self.write(fixture["upstream"], "user-stories/alpha.md", "alpha v2\n")
        self.write(fixture["upstream"], "user-stories/gamma.md", "gamma v2\n")
        self.commit(fixture["upstream"], "alpha and gamma v2")
        adopter = fixture["adopter"]
        index_path = adopter / "user-stories/index.md"
        index_before = index_path.read_bytes()
        trailing = (
            b"## Destination notes\n\n"
            b"Local trailing section that must survive byte-for-byte.\n"
        )
        assert b"| `alpha` | Alpha local edit |" in index_before
        assert b"| `gamma` | Gamma local edit |" in index_before
        assert (
            b"| `dest-own` | Destination owned | active | local | `d` |"
            in index_before
        )
        assert index_before.endswith(trailing), "the fixture must carry the tail"
        before = self.worktree_bytes(adopter)

        staged: list[str] = []
        real_write = engine._apply_write_file

        def recording_write(
            path: str, relative: str, content: bytes, mode: int
        ) -> None:
            staged.append(relative)
            real_write(path, relative, content, mode)

        with mock.patch.object(engine, "_apply_write_file", recording_write):
            code, out, err = self._apply_in_process(fixture)

        assert code == 0, f"a composed apply must succeed: exit {code}\n{err}"
        assert err == "", f"no collisions expected: {err}"
        report = json.loads(out)
        assert report["apply"] == "success", report
        assert report["written"] == [
            "portable-stories-always",
            "portable-stories-ticket",
        ], report
        assert report["verify"] == "pass", report
        assert report["blocking"] == [], report
        assert report["lock"] == str(fixture["lock"]), report
        assert staged.count("user-stories/index.md") == 1, (
            "the shared destination index must be written exactly once: "
            f"{staged}"
        )
        index = index_path.read_bytes()
        assert b"| `alpha` | Alpha | active | ep-a | `a` |" in index, (
            "the first unit's core row must land"
        )
        assert b"| `gamma` | Gamma | active | ep-g | `g` |" in index, (
            "the second unit's core row must land"
        )
        assert b"| `alpha` | Alpha local edit |" not in index
        assert b"| `gamma` | Gamma local edit |" not in index
        assert b"| `beta` | Beta | active | ep-b | `b` |" in index, (
            "no unit's content may be lost from the composed index"
        )
        assert (
            b"| `dest-own` | Destination owned | active | local | `d` |" in index
        ), "destination-only rows must survive the composed merge"
        assert index.endswith(trailing), (
            "the trailing section must survive byte-for-byte"
        )
        assert (adopter / "user-stories/alpha.md").read_bytes() == b"alpha v2\n"
        assert (adopter / "user-stories/gamma.md").read_bytes() == b"gamma v2\n"
        assert (adopter / "user-stories/beta.md").read_bytes() == b"beta v1\n"
        self._assert_only_changed(
            before,
            self.worktree_bytes(adopter),
            {
                "user-stories/alpha.md",
                "user-stories/gamma.md",
                "user-stories/index.md",
                ".aicore/adoption.lock.yaml",
            },
        )


class ApplyHardeningTests(EngineTestCase):
    """Failure restore, read-only regression, and the ``apply`` exit contract.

    The two forced-failure cases patch the narrow seams the guarded apply
    region exposes — the staged-write helper and the journal-restore helper —
    with ``unittest.mock``, then drive ``apply`` in-process, so the original
    failure, the best-effort restore, and the ``apply_restore_failed``
    recovery record are all asserted through the engine's real control flow.
    The read-only and exit-contract cases drive the CLI through ``subprocess``
    against the same temporary fixtures. Nothing here touches the network or
    any path outside the temp tree, and no existing test is relaxed.
    """

    # -- helpers -----------------------------------------------------------

    def _apply(
        self, fixture: dict[str, object], *extra: str
    ) -> subprocess.CompletedProcess:
        return self.run_cli(
            "apply",
            *self.base_check_args(fixture),
            "--adopter-revision", str(fixture["adopter_rev"]),
            "--format", "json",
            *extra,
        )

    def _apply_in_process(
        self, fixture: dict[str, object], *extra: str
    ) -> tuple[int, str, str]:
        """Run ``apply`` in-process so a failure seam can be patched."""
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = engine.main(
                [
                    "apply",
                    *self.base_check_args(fixture),
                    "--adopter-revision", str(fixture["adopter_rev"]),
                    "--format", "json",
                    *extra,
                ]
            )
        return int(code), stdout.getvalue(), stderr.getvalue()

    def _file_modes(self, repo: Path) -> dict[str, int]:
        """POSIX permission bits of every non-git regular file under ``repo``."""
        modes: dict[str, int] = {}
        for path in sorted(Path(repo).rglob("*")):
            rel = path.relative_to(repo)
            if not path.is_file():
                continue
            if rel.parts and rel.parts[0] == ".git":
                continue
            modes[str(rel)] = os.stat(path).st_mode & 0o777
        return modes

    def _assert_read_only(
        self,
        repo: Path,
        before_files: dict[str, object],
        before_git: dict[str, object],
        command: str,
    ) -> None:
        """One read-only command must leave a byte-identical, clean repo."""
        assert self.worktree_bytes(repo) == before_files, (
            f"{command} rewrote or created files under {repo}"
        )
        assert self.git_state(repo) == before_git, (
            f"{command} changed git state under {repo}"
        )
        assert self.status(repo) == "", f"{command} must leave a clean porcelain"

    # -- 1. forced mid-write failure ---------------------------------------

    def test_forced_mid_write_failure_restores_prior_bytes_and_modes(self) -> None:
        fixture = self.build_greeting(advance="content")
        adopter = fixture["adopter"]
        destination = adopter / "content/greeting.txt"
        # A distinctive mode makes the mode assertion bite: the staged write
        # would leave 0o644 behind if the journal could not put it back.
        os.chmod(destination, 0o600)
        before = self.worktree_bytes(adopter)
        before_modes = self._file_modes(adopter)
        assert before_modes["content/greeting.txt"] == 0o600

        real_write = engine._apply_write_file
        staged: list[tuple[str, bytes]] = []

        def flaky_write(path: str, relative: str, content: bytes, mode: int) -> None:
            staged.append((relative, content))
            if relative == ".aicore/adoption.lock.yaml":
                raise engine.SyncError("apply_write_failed", "simulated device full")
            real_write(path, relative, content, mode)

        with mock.patch.object(engine, "_apply_write_file", flaky_write):
            code, out, err = self._apply_in_process(fixture)

        assert code != 0, f"a failed apply must exit non-zero: {out}"
        assert code == 2, f"unexpected exit code: {code}"
        assert staged[:1] == [("content/greeting.txt", b"hello world\n")], (
            f"the failure must land after a content byte was staged: {staged}"
        )
        assert "apply_write_failed" in err, f"stderr must name the failure: {err}"
        assert "every journaled path was restored" in err, f"stderr={err}"
        assert out == "", f"a failed apply must emit no report on stdout: {out}"
        after = self.worktree_bytes(adopter)
        assert set(after) == set(before), (
            "no orphan or partial file may remain: "
            f"{sorted(set(after) ^ set(before))}"
        )
        assert after == before, (
            "every adopter byte must be back to its pre-apply state"
        )
        assert self._file_modes(adopter) == before_modes, (
            "restored files must keep their pre-apply modes"
        )
        assert self.status(adopter) == "", "the restored worktree must be clean"

    # -- 2. forced restore failure -----------------------------------------

    def test_forced_restore_failure_emits_recovery_record(self) -> None:
        fixture = self.build_greeting(advance="content")
        adopter = fixture["adopter"]
        before = self.worktree_bytes(adopter)

        real_write = engine._apply_write_file
        real_restore_entry = engine._apply_restore_entry

        def flaky_write(path: str, relative: str, content: bytes, mode: int) -> None:
            if relative == ".aicore/adoption.lock.yaml":
                raise engine.SyncError("apply_write_failed", "simulated device full")
            real_write(path, relative, content, mode)

        def broken_restore(entry: dict) -> bool:
            if str(entry["relative"]) == "content/greeting.txt":
                return False  # the mutated content path cannot be put back
            return real_restore_entry(entry)

        with (
            mock.patch.object(engine, "_apply_write_file", flaky_write),
            mock.patch.object(engine, "_apply_restore_entry", broken_restore),
        ):
            code, out, err = self._apply_in_process(fixture)

        assert code == 2, f"a failed restore must exit non-zero: {code}"
        assert code != 0
        assert out == "", f"a failed apply must emit no report on stdout: {out}"
        lines = err.splitlines()
        assert len(lines) == 2, f"expected exactly two stderr lines: {lines}"
        for line in lines:
            assert "apply_restore_failed" in line, f"stderr={err}"
        prefix = "sync-aicore-adoption: apply_restore_failed: recovery record: "
        assert lines[0].startswith(prefix), f"stderr={err}"
        record = json.loads(lines[0][len(prefix):])
        assert set(record) == {"original", "paths"}, record
        assert record["original"].startswith("apply_write_failed"), record
        assert record["paths"] == ["content/greeting.txt"], record
        assert lines[1].startswith(
            "sync-aicore-adoption: apply_restore_failed:"
        ), f"stderr={err}"
        after = self.worktree_bytes(adopter)
        assert set(after) == set(before), (
            "no orphan or partial file may appear: "
            f"{sorted(set(after) ^ set(before))}"
        )
        assert after["content/greeting.txt"] != before["content/greeting.txt"], (
            "the named path must still be inconsistent with the journal"
        )
        assert after[".aicore/adoption.lock.yaml"] == before[
            ".aicore/adoption.lock.yaml"
        ], "the untouched journaled path must keep its original bytes"

    # -- 3. read-only regression -------------------------------------------

    def test_check_and_propose_lock_write_nothing_on_a_clean_worktree(self) -> None:
        fixture = self.build_greeting()
        adopter = fixture["adopter"]
        upstream = fixture["upstream"]
        before_files = self.worktree_bytes(adopter)
        before_git = self.git_state(adopter)
        before_upstream = self.worktree_bytes(upstream)
        before_upstream_git = self.git_state(upstream)
        assert self.status(adopter) == "", "the fixture must start clean"
        assert self.status(upstream) == "", "the fixture must start clean"

        check = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision", str(fixture["adopter_rev"]),
        )
        self.assert_exit(check, 0)
        self._assert_read_only(adopter, before_files, before_git, "check")
        self._assert_read_only(upstream, before_upstream, before_upstream_git, "check")

        propose = self.run_cli(
            "propose-lock",
            "--upstream-repo", str(upstream),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--lock", str(fixture["lock"]),
            "--adopter-revision", str(fixture["adopter_rev"]),
        )
        self.assert_exit(propose, 0)
        candidate = yaml.safe_load(propose.stdout)
        assert isinstance(candidate, dict) and candidate["schema_version"] == 2, (
            "propose-lock stdout must stay pure YAML"
        )
        assert propose.stderr == "", f"no diagnostics expected: {propose.stderr}"
        self._assert_read_only(adopter, before_files, before_git, "propose-lock")
        self._assert_read_only(
            upstream, before_upstream, before_upstream_git, "propose-lock"
        )

    def test_check_writes_nothing_while_apply_is_the_only_writer(self) -> None:
        fixture = self.build_greeting(advance="content")
        adopter = fixture["adopter"]
        upstream = fixture["upstream"]
        before_files = self.worktree_bytes(adopter)
        before_git = self.git_state(adopter)
        before_upstream = self.worktree_bytes(upstream)
        before_upstream_git = self.git_state(upstream)

        # The update is available: check reports it without writing a byte.
        check = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision", str(fixture["adopter_rev"]),
        )
        self.assert_exit(check, 1)
        self._assert_read_only(adopter, before_files, before_git, "check")
        self._assert_read_only(upstream, before_upstream, before_upstream_git, "check")

        # The post-apply shape of this engine: ``apply`` is the only writer,
        # so the read-only assertions above have a live contrast to fail on.
        proc = self._apply(fixture)
        self.assert_exit(proc, 0)
        report = json.loads(proc.stdout)
        assert report["apply"] == "success", report
        after = self.worktree_bytes(adopter)
        assert after != before_files, "apply must be the command that writes"
        assert set(after) == set(before_files), (
            "apply must not add or remove adopter files: "
            f"{sorted(set(after) ^ set(before_files))}"
        )
        changed = {path for path in before_files if before_files[path] != after[path]}
        assert changed == {"content/greeting.txt", ".aicore/adoption.lock.yaml"}, (
            sorted(changed)
        )
        assert self.worktree_bytes(upstream) == before_upstream, (
            "apply must never write the upstream"
        )
        assert self.git_state(upstream) == before_upstream_git, (
            "apply must never change upstream git state"
        )

    def test_verify_all_writes_nothing_to_checkouts_or_upstream(self) -> None:
        fixture = self.build_verify()
        repos = [
            fixture["checkouts"] / "good",
            fixture["checkouts"] / "stale",
            fixture["upstream"],
        ]
        before = {str(repo): self.worktree_bytes(repo) for repo in repos}
        before_git = {str(repo): self.git_state(repo) for repo in repos}
        proc = self.run_cli(
            "verify-all",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--registry", str(fixture["current_registry"]),
            "--checkouts-root", str(fixture["checkouts"]),
            "--format", "json",
        )
        self.assert_exit(proc, 0)
        report = json.loads(proc.stdout)
        assert report["compliance"], report
        for repo in repos:
            self._assert_read_only(
                repo, before[str(repo)], before_git[str(repo)], "verify-all"
            )

    def test_propose_lock_stdout_stays_pure_yaml_with_collisions_on_stderr(
        self,
    ) -> None:
        fixture = self.build_stories(STORY_DESTINATION_INDEX)
        adopter = fixture["adopter"]
        upstream = fixture["upstream"]
        before_files = self.worktree_bytes(adopter)
        before_git = self.git_state(adopter)
        before_upstream = self.worktree_bytes(upstream)
        before_upstream_git = self.git_state(upstream)
        proc = self.run_cli(
            "propose-lock",
            "--upstream-repo", str(upstream),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--lock", str(fixture["lock"]),
            "--adopter-revision", str(fixture["adopter_rev"]),
        )
        self.assert_exit(proc, 0)
        candidate = yaml.safe_load(proc.stdout)
        assert isinstance(candidate, dict) and candidate["schema_version"] == 2, (
            "stdout must parse as the candidate lock document"
        )
        assert "collision" not in proc.stdout, (
            "collisions must be emitted on stderr only"
        )
        assert proc.stderr.splitlines() == [
            "collision: path user-stories/alpha.md; core wins",
            "collision: slug alpha; core wins",
        ], f"stderr={proc.stderr}"
        self._assert_read_only(adopter, before_files, before_git, "propose-lock")
        self._assert_read_only(
            upstream, before_upstream, before_upstream_git, "propose-lock"
        )

    # -- 4. exit-code contract ---------------------------------------------

    def test_refusal_exits_two(self) -> None:
        fixture = self.build_greeting(
            advance="content",
            destination_text="hello world\n",
            lock_destination_text="hello\n",
        )
        before = self.worktree_bytes(fixture["adopter"])
        proc = self._apply(fixture)
        self.assert_exit(proc, 2, "conflict")
        assert proc.stdout == "", "a refusal must emit no report on stdout"
        assert self.worktree_bytes(fixture["adopter"]) == before, (
            "a refusal must not write"
        )

    def test_verify_noncompliance_on_written_state_exits_one(self) -> None:
        # The written worktree and its regenerated lock are consistent by
        # construction, so the non-compliant verify branch is forced through
        # the narrowest seam: the check report the guarded region consumes.
        fixture = self.build_greeting(advance="content")
        adopter = fixture["adopter"]
        before = self.worktree_bytes(adopter)
        real_report = engine._check_report

        def noncompliant_report(*args: object, **kwargs: object) -> dict:
            report = real_report(*args, **kwargs)  # type: ignore[arg-type]
            report["compliance"] = False
            report["blocking_reasons"] = list(report["blocking_reasons"]) + [
                "greeting: simulated_verify_failure"
            ]
            return report

        with mock.patch.object(engine, "_check_report", noncompliant_report):
            code, out, err = self._apply_in_process(fixture)

        assert code == 1, f"a non-compliant verify must exit 1: {code}"
        assert err == "", f"a non-compliant verify raises no error: {err}"
        report = json.loads(out)
        assert report["apply"] == "failure", report
        assert report["verify"] == "fail", report
        assert report["blocking"] == ["greeting: simulated_verify_failure"], report
        assert report["written"] == ["greeting"], report
        assert report["lock"] == str(fixture["lock"]), report
        after = self.worktree_bytes(adopter)
        assert after["content/greeting.txt"] == b"hello world\n", (
            "the failing verify must run on a written state"
        )
        assert after[".aicore/adoption.lock.yaml"] != before[
            ".aicore/adoption.lock.yaml"
        ], "the failing verify must run on a written state"
        assert set(after) == set(before), (
            "the written failure must not add or remove adopter files: "
            f"{sorted(set(after) ^ set(before))}"
        )
        changed = {path for path in before if before[path] != after[path]}
        assert changed == {"content/greeting.txt", ".aicore/adoption.lock.yaml"}, (
            "only the written unit and its regenerated lock may differ: "
            f"{sorted(changed)}"
        )

    def test_success_exits_zero(self) -> None:
        fixture = self.build_greeting(advance="content")
        proc = self._apply(fixture)
        self.assert_exit(proc, 0)
        report = json.loads(proc.stdout)
        assert report["apply"] == "success", report
        assert report["verify"] == "pass", report
        assert proc.stderr == "", f"no diagnostics expected: {proc.stderr}"

    def test_noop_exits_zero(self) -> None:
        fixture = self.build_greeting()
        before = self.worktree_bytes(fixture["adopter"])
        proc = self._apply(fixture)
        self.assert_exit(proc, 0)
        report = json.loads(proc.stdout)
        assert report["apply"] == "noop", report
        assert proc.stderr == "", f"no diagnostics expected: {proc.stderr}"
        assert self.worktree_bytes(fixture["adopter"]) == before, (
            "a no-op must not write"
        )


# A ``test_*.py`` written outside ``.opencode/`` by the discovery probe below;
# its class name matches ``python_classes = ["*Tests"]`` and its method matches
# the default ``test*`` function pattern, so it is collectable from anywhere in
# the workspace.
DISCOVERY_PROBE_TEMPLATE = '''"""Temporary discovery probe; removed by the test that wrote it."""


class {class_name}:
    def test_probe_marker(self) -> None:
        assert True
'''


class TestpathsDiscoveryTests(EngineTestCase):
    """Project-wide ``testpaths`` discovery, proven by a live probe.

    ``pyproject.toml`` declares ``testpaths = ["."]`` plus an explicit
    ``norecursedirs`` list, so a ``test_*.py`` in *any* non-excluded directory
    is in scope — the former four-skill-scripts allowlist is gone, and a test
    dropped anywhere else is collected instead of silently skipped while pytest
    still exits 0.

    The probe writes two ``test_*.py`` files into directories **outside**
    ``.opencode/`` (``tests/`` and ``src/``), then runs the granted suite
    command from the workspace root — ``uv run --frozen --group dev pytest -q``
    plus ``--collect-only``, because collection is exactly what is under test
    and a full nested run would re-enter this very method. Both probes must
    appear as collected node ids, and every node id collected before the probes
    existed must still be collected afterwards, so the pre-existing suite can
    never shrink.

    Hermeticity: probes and the directories created to hold them are removed,
    ``.pytest_cache`` is restored byte-for-byte to the state it was found in
    (deleted outright when it was absent), no ``__pycache__`` can appear
    (``PYTHONDONTWRITEBYTECODE``), and ``uv`` is forced offline with no sync
    and a cache inside the test's temporary tree — so the workspace is
    byte-identical when this method returns, on success and on failure alike.
    """

    PROBES: tuple[tuple[str, str], ...] = (
        ("tests/test_discovery_probe_alpha.py", "DiscoveryProbeAlphaTests"),
        ("src/test_discovery_probe_beta.py", "DiscoveryProbeBetaTests"),
    )
    SUITE_COMMAND: tuple[str, ...] = (
        "uv",
        "run",
        "--frozen",
        "--group",
        "dev",
        "pytest",
        "-q",
    )

    # -- helpers -----------------------------------------------------------

    @staticmethod
    def _workspace_root() -> Path:
        """The directory holding this project's ``pyproject.toml``."""
        for candidate in Path(SCRIPT_DIR).parents:
            if (candidate / "pyproject.toml").is_file() and (
                candidate / ".opencode"
            ).is_dir():
                return candidate
        raise AssertionError(f"no workspace root above {SCRIPT_DIR}")

    @staticmethod
    def _snapshot_tree(root: Path) -> dict[str, bytes] | None:
        """Bytes of every file under ``root``; ``None`` when ``root`` is absent."""
        if not root.exists():
            return None
        return {
            str(path.relative_to(root)): path.read_bytes()
            for path in sorted(root.rglob("*"))
            if path.is_file()
        }

    @staticmethod
    def _restore_tree(root: Path, snapshot: dict[str, bytes] | None) -> None:
        """Put ``root`` back exactly as ``_snapshot_tree`` recorded it."""
        if root.exists():
            shutil.rmtree(root)
        if snapshot is None:
            return
        root.mkdir(parents=True, exist_ok=True)
        for relative, data in sorted(snapshot.items()):
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)

    @staticmethod
    def _collected_node_ids(stdout: str) -> list[str]:
        """One node id per collected test from ``pytest -q --collect-only``."""
        return [line.strip() for line in stdout.splitlines() if "::" in line]

    def _collect_suite(self, workspace: Path, env: dict[str, str]) -> list[str]:
        """Run the granted suite command against ``workspace`` and collect."""
        proc = subprocess.run(
            [*self.SUITE_COMMAND, "--collect-only"],
            cwd=str(workspace),
            capture_output=True,
            text=True,
            env=env,
            timeout=300,
        )
        assert proc.returncode == 0, (
            "the suite command must collect cleanly: "
            f"exit {proc.returncode}\n"
            f"stdout={proc.stdout}\nstderr={proc.stderr}"
        )
        node_ids = self._collected_node_ids(proc.stdout)
        assert node_ids, f"no node ids collected:\n{proc.stdout}{proc.stderr}"
        return node_ids

    # -- probe -------------------------------------------------------------

    def test_testpaths_discovers_probes_outside_opencode(self) -> None:
        workspace = self._workspace_root()
        cache_root = workspace / ".pytest_cache"
        cache_before = self._snapshot_tree(cache_root)
        uv_cache = self.root / "uv-cache"
        uv_cache.mkdir(parents=True, exist_ok=True)
        env = {
            **os.environ,
            # The ``uv`` cache, the sync step, and every byte of network access
            # stay outside the workspace; the venv already exists.
            "UV_CACHE_DIR": str(uv_cache),
            "UV_NO_SYNC": "1",
            "UV_OFFLINE": "1",
            # Collection must not leave a single ``__pycache__`` behind.
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        created_dirs: list[Path] = []
        try:
            baseline = self._collect_suite(workspace, env)
            for relative, _class_name in self.PROBES:
                assert not any(
                    node_id.startswith(relative + "::") for node_id in baseline
                ), f"{relative} must not exist in the workspace at rest"

            for relative, class_name in self.PROBES:
                probe_path = workspace / relative
                if not probe_path.parent.exists():
                    created_dirs.append(probe_path.parent)
                probe_path.parent.mkdir(parents=True, exist_ok=True)
                probe_path.write_text(
                    DISCOVERY_PROBE_TEMPLATE.format(class_name=class_name),
                    encoding="utf-8",
                )

            collected = self._collect_suite(workspace, env)
            for relative, class_name in self.PROBES:
                hits = [
                    node_id
                    for node_id in collected
                    if node_id.startswith(relative + "::")
                ]
                assert hits, (
                    f"project-wide discovery must collect {relative}: {collected}"
                )
                assert any(class_name in node_id for node_id in hits), (
                    f"project-wide discovery must collect {class_name}: {hits}"
                )
            missing = sorted(set(baseline) - set(collected))
            assert not missing, (
                "the pre-existing suite must still be collected: "
                f"{missing}"
            )
        finally:
            for relative, _class_name in self.PROBES:
                probe_path = workspace / relative
                if probe_path.is_file():
                    probe_path.unlink()
            for directory in created_dirs:
                shutil.rmtree(directory, ignore_errors=True)
            self._restore_tree(cache_root, cache_before)

        # The probe must leave the workspace byte-identical to how it was found.
        for relative, _class_name in self.PROBES:
            assert not (workspace / relative).exists(), (
                f"{relative} must be removed after the probe"
            )
        for directory in created_dirs:
            assert not directory.exists(), f"{directory} must be removed"
        assert self._snapshot_tree(cache_root) == cache_before, (
            ".pytest_cache must be byte-identical to its pre-probe state"
        )


class RunnerPolicyTests(EngineTestCase):
    """Runner-policy validation of the adopter ``opencode.jsonc``.

    Pure cases drive the classifier directly; CLI cases rebuild an assertions
    fixture whose ``opencode.jsonc`` carries the grant under test, then run the
    real ``check`` and ``propose-lock`` subcommands.
    """

    def _grant_config(self, *allows: str) -> str:
        entries = ['"*": "deny"', '"sudo *": "deny"']
        entries.extend(f'"{grant}": "allow"' for grant in allows)
        body = ",\n".join(f"          {entry}" for entry in entries)
        return (
            "// managed file\n"
            "{\n"
            '  "agent": {\n'
            '    "crucible": {\n'
            '      "permission": {\n'
            '        "bash": {\n'
            f"{body}\n"
            "        }\n"
            "      }\n"
            "    }\n"
            "  }\n"
            "}\n"
        )

    def _with_grants(self, fixture: dict[str, object], *allows: str) -> None:
        adopter = fixture["adopter"]
        self.write(adopter, "opencode.jsonc", self._grant_config(*allows))
        # Both `check` and `propose-lock` read the committed snapshot, so the
        # grant under test must land in a commit before either subcommand runs.
        fixture["adopter_rev"] = self.commit(adopter, "runner grants")

    def _check(self, fixture: dict[str, object]) -> subprocess.CompletedProcess:
        return self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision", fixture["adopter_rev"],
            "--format", "json",
        )

    def _propose(self, fixture: dict[str, object]) -> subprocess.CompletedProcess:
        return self.run_cli(
            "propose-lock",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--lock", str(fixture["lock"]),
            "--adopter-revision", fixture["adopter_rev"],
        )

    # -- pure classifier cases ------------------------------------------

    def test_aicore_own_grant_shape_has_no_violation(self) -> None:
        config = self._grant_config(engine.AICORE_SUITE_COMMAND)
        assert engine._opencode_config_policy_violation(config.encode()) is None

    def test_exact_fixed_suite_command_accepted(self) -> None:
        assert engine._runner_policy_violation(engine.AICORE_SUITE_COMMAND) is None

    def test_destination_package_test_commands_accepted(self) -> None:
        for grant in ("pnpm test", "npm test", "yarn test", "cargo test"):
            assert engine._runner_policy_violation(grant) is None, grant

    def test_path_wildcard_reordered_and_whitespace_variants_rejected(self) -> None:
        variants = (
            "uv run --frozen --group dev pytest tests/ -q",
            "uv run --frozen --group dev pytest .opencode/skills/x/test_*.py -q",
            "uv run --frozen --group  dev pytest -q",
            "uv run --frozen --group dev pytest -q --collect-only",
            "uv run --frozen pytest --group dev -q",
        )
        for variant in variants:
            reason = engine._runner_policy_violation(variant)
            assert reason is not None, variant

    def test_broad_catch_all_allow_rejected_and_deny_never_judged(self) -> None:
        assert engine._catch_all_policy_violation("*") is not None
        assert engine._catch_all_policy_violation("uv *") is not None
        assert engine._catch_all_policy_violation("pytest *") is not None
        assert engine._catch_all_policy_violation(engine.AICORE_SUITE_COMMAND) is None
        deny_only = self._grant_config()
        assert engine._opencode_config_policy_violation(deny_only.encode()) is None

    def test_non_test_allow_entries_are_skipped(self) -> None:
        config = self._grant_config("pnpm install")
        assert engine._opencode_config_policy_violation(config.encode()) is None

    # -- CLI cases -------------------------------------------------------

    def test_check_accepts_reviewed_runner(self) -> None:
        fixture = self.build_assertions()
        self._with_grants(fixture, engine.AICORE_SUITE_COMMAND)
        proc = self._check(fixture)
        assert proc.returncode in (0, 1), proc.stderr
        report = json.loads(proc.stdout)
        assert report["units"][0]["disposition"] != "policy_violation"

    def test_check_reports_policy_violation_for_path_variant(self) -> None:
        fixture = self.build_assertions()
        self._with_grants(fixture, "uv run --frozen --group dev pytest tests/ -q")
        proc = self._check(fixture)
        assert proc.returncode == 1, (proc.returncode, proc.stderr)
        report = json.loads(proc.stdout)
        assert not report["compliance"]
        assert any(
            reason.endswith("policy_violation") for reason in report["blocking_reasons"]
        ), report["blocking_reasons"]

    def test_check_reports_policy_violation_for_catch_all_allow(self) -> None:
        fixture = self.build_assertions()
        self._with_grants(fixture, "*")
        proc = self._check(fixture)
        assert proc.returncode == 1, (proc.returncode, proc.stderr)
        report = json.loads(proc.stdout)
        assert not report["compliance"]

    def test_propose_lock_refuses_bad_runner_with_empty_stdout(self) -> None:
        fixture = self.build_assertions()
        self._with_grants(fixture, "uv run --frozen --group dev pytest tests/ -q")
        proc = self._propose(fixture)
        self.assert_exit(proc, 2, "policy_violation")
        assert proc.stdout == "", "a rejected proposal must emit no YAML"

    def test_propose_lock_accepts_destination_package_test(self) -> None:
        fixture = self.build_assertions()
        self._with_grants(fixture, "pnpm test")
        proc = self._propose(fixture)
        assert proc.returncode == 0, (proc.returncode, proc.stderr)
        yaml.safe_load(proc.stdout)

    def test_wrong_runner_is_not_replaced_by_aicore_command(self) -> None:
        fixture = self.build_assertions()
        self._with_grants(fixture, "pnpm test")
        proc = self._check(fixture)
        assert proc.returncode in (0, 1), proc.stderr
        report = json.loads(proc.stdout)
        assert engine.AICORE_SUITE_COMMAND not in proc.stdout
        assert report["units"][0]["disposition"] != "policy_violation"
