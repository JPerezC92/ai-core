"""Stdlib ``unittest`` suite for the sync-aicore-adoption protocol-v2 engine.

Run directly with:
    python3 .opencode/skills/sync-aicore-adoption/scripts/test_sync_aicore_adoption.py

The suite never touches the network and never calls ``gh``: every fixture is a
temporary git repository created under ``tempfile.mkdtemp()`` and removed in
``tearDown``. CLI behavior is exercised through ``subprocess``; pure helpers are
imported directly from the sibling engine module.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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


def snapshot_digest(declaration: str, review: str, rows: list) -> str:
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


def greeting_lock_document(
    accepted: str,
    accepted_text: str,
    destination_text: str,
    catalog: str = GREETING_CATALOG,
    declaration: str = GREETING_DECLARATION,
    review: str = EMPTY_REVIEW,
    mode: str = "mirror",
) -> dict:
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
) -> dict:
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
) -> dict:
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


class EngineTestCase(unittest.TestCase):
    """Base case owning a temporary upstream repository and adopter repository."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.upstream = self.root / "upstream"
        self.adopter = self.root / "adopter"

    def tearDown(self) -> None:
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
            self.fail(f"git {' '.join(args)} failed in {repo}: {proc.stderr}")
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
        self.assertEqual(
            proc.returncode,
            code,
            f"expected exit {code}, got {proc.returncode}\n"
            f"stdout={proc.stdout}\nstderr={proc.stderr}",
        )
        if contains is not None:
            self.assertIn(contains, proc.stderr, f"stderr={proc.stderr}")

    def base_check_args(
        self, fixture: dict, *, review: Path | None = None, lock: Path | None = None
    ) -> list[str]:
        return [
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(review or fixture["review"]),
            "--lock", str(lock or fixture["lock"]),
        ]

    # -- snapshots ----------------------------------------------------------

    def worktree_bytes(self, repo: Path) -> dict:
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

    def git_state(self, repo: Path) -> dict:
        return {
            "head": self.git(repo, "rev-parse", "HEAD").stdout,
            "index": self.git(repo, "ls-files", "-s").stdout,
            "refs": self.git(repo, "for-each-ref").stdout,
            "status": self.status(repo),
        }

    # -- fixture builders ---------------------------------------------------

    def _fixture_dict(self, accepted: str, adopter_rev: str) -> dict:
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
    ) -> dict:
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
        lock_builder,
        upstream_files: dict,
        adopter_files: dict,
    ) -> dict:
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
    ) -> dict:
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

    def build_assertions(
        self,
        lock_opencode: bool = True,
        current_opencode: bool = True,
        lock_gitignore: bool = True,
        current_gitignore: bool = True,
        declaration: str = ASSERTION_DECLARATION,
        review: str = EMPTY_REVIEW,
        catalog: str = ASSERTION_CATALOG,
    ) -> dict:
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

    def build_verify(self) -> dict:
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


class DigestGoldenTests(EngineTestCase):
    def test_file_hello_golden_vector(self) -> None:
        digest = member_file("hello\n")
        self.assertEqual(
            digest,
            "sha256:cf41078b082e3740168bd7ad534ba1b70b12489c7ab43c6fb53743b0f3527887",
            f"golden vector mismatch: {digest}",
        )


class SchemaParsingTests(EngineTestCase):
    def test_v2_documents_parse(self) -> None:
        catalog = self.write(self.root, "catalog.yaml", GREETING_CATALOG)
        declaration = self.write(self.root, "declaration.yaml", GREETING_DECLARATION)
        review = self.write(self.root, "review.yaml", EMPTY_REVIEW)
        lock = greeting_lock_document("a" * 40, "hello\n", "hello\n")
        lock_path = self.write(
            self.root, "lock.yaml", yaml.safe_dump(lock, sort_keys=False)
        )
        self.assertIsInstance(engine.load_catalog(str(catalog)), dict)
        self.assertIsInstance(engine.load_declaration(str(declaration)), dict)
        self.assertIsInstance(engine.load_review(str(review)), dict)
        self.assertIsInstance(engine.load_lock(str(lock_path)), dict)

    def test_v1_documents_require_upgrade(self) -> None:
        cases = {
            "catalog": (
                "load_catalog",
                "schema_version: 1\ncatalog: {}\nunits: []\n",
            ),
            "declaration": ("load_declaration", "schema_version: 1\nunits: []\n"),
            "review": ("load_review", "schema_version: 1\ndecisions: []\n"),
            "lock": ("load_lock", "schema_version: 1\nunits: []\n"),
        }
        for name, (loader_name, text) in cases.items():
            with self.subTest(document=name):
                path = self.write(self.root, f"v1-{name}.yaml", text)
                loader = getattr(engine, loader_name)
                with self.assertRaises(engine.SyncError) as caught:
                    loader(str(path))
                self.assertEqual(
                    caught.exception.code,
                    "schema_upgrade_required",
                    f"{name}: {caught.exception.message}",
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


class LockValidityTests(EngineTestCase):
    def test_lock_row_with_source_commit_is_invalid_lock(self) -> None:
        lock = greeting_lock_document("a" * 40, "hello\n", "hello\n")
        lock["units"][0]["accepted_source_commit"] = "b" * 40
        path = self.write(
            self.root, "row-source.lock.yaml", yaml.safe_dump(lock, sort_keys=False)
        )
        with self.assertRaises(engine.SyncError) as caught:
            engine.load_lock(str(path))
        self.assertEqual(caught.exception.code, "invalid_lock")
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
    def _check(self, fixture: dict, *extra: str) -> subprocess.CompletedProcess:
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
        self.assertTrue(report["compliance"])
        self.assertEqual(report["units"][0]["disposition"], "current")

    def test_update_available_exit_1(self) -> None:
        fixture = self.build_greeting(advance="content")
        proc = self._check(fixture)
        self.assert_exit(proc, 1)
        report = json.loads(proc.stdout)
        self.assertFalse(report["compliance"])
        self.assertEqual(report["units"][0]["disposition"], "update_available")

    def test_baseline_advance_required_exit_1(self) -> None:
        fixture = self.build_greeting(advance="empty")
        proc = self._check(fixture)
        self.assert_exit(proc, 1)
        report = json.loads(proc.stdout)
        self.assertEqual(
            report["units"][0]["disposition"], "baseline_advance_required"
        )

    def test_mirror_changed_on_both_sides_is_conflict_exit_1(self) -> None:
        fixture = self.build_greeting(
            advance="content",
            destination_text="hello world\n",
            lock_destination_text="hello\n",
        )
        proc = self._check(fixture)
        self.assert_exit(proc, 1)
        report = json.loads(proc.stdout)
        self.assertFalse(report["compliance"])
        self.assertEqual(report["units"][0]["disposition"], "conflict")

    def test_destination_owned_steady_state_is_unmanaged_exit_0(self) -> None:
        fixture = self.build_greeting(
            declaration=DESTINATION_OWNED_DECLARATION,
            mode="destination_owned",
        )
        proc = self._check(fixture)
        self.assert_exit(proc, 0)
        report = json.loads(proc.stdout)
        self.assertTrue(report["compliance"])
        self.assertEqual(report["units"][0]["disposition"], "unmanaged")

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
        self.assertNotEqual(
            proc.returncode, 2, f"reviewed change must be non-fatal\n{proc.stderr}"
        )
        report = json.loads(proc.stdout)
        self.assertEqual(report["units"][0]["disposition"], "review_required")

    def test_diagnostic_never_exit_0(self) -> None:
        fixture = self.build_greeting(advance="content")
        proc = self._check(fixture, "--diagnostic-revision", fixture["accepted"])
        self.assert_exit(proc, 1)
        report = json.loads(proc.stdout)
        self.assertFalse(report["compliance"])
        self.assertTrue(report["diagnostic"])

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
        def lock_builder(accepted: str) -> dict:
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
    def _check(self, fixture: dict) -> subprocess.CompletedProcess:
        return self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision", fixture["adopter_rev"],
            "--format", "json",
        )

    def _propose(self, fixture: dict) -> subprocess.CompletedProcess:
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
        self.assertTrue(json.loads(proc.stdout)["compliance"])
        self.assert_exit(self._propose(fixture), 0)

    def test_missing_opencode_gate_noncompliant_and_propose_refuses(self) -> None:
        fixture = self.build_assertions(current_opencode=False)
        proc = self._check(fixture)
        self.assert_exit(proc, 1)
        self.assertFalse(json.loads(proc.stdout)["compliance"])
        self.assert_exit(self._propose(fixture), 2, "local_drift")

    def test_missing_gitignore_entry_noncompliant_and_propose_refuses(self) -> None:
        fixture = self.build_assertions(current_gitignore=False)
        proc = self._check(fixture)
        self.assert_exit(proc, 1)
        self.assertFalse(json.loads(proc.stdout)["compliance"])
        self.assert_exit(self._propose(fixture), 2, "local_drift")


class ReviewEvidenceTests(EngineTestCase):
    def _propose(self, fixture: dict) -> subprocess.CompletedProcess:
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
        self.assertEqual(note["disposition"], "update_available")
        self.assert_exit(self._propose(fixture), 0)


class SnapshotExplicitnessTests(EngineTestCase):
    def test_index_ignores_unstaged_worktree_edit(self) -> None:
        fixture = self.build_greeting()
        worktree = fixture["adopter"] / "content/greeting.txt"
        worktree.write_text("DIRTY WORKTREE\n", encoding="utf-8")
        args = ["check", *self.base_check_args(fixture), "--adopter-index"]
        self.assert_exit(self.run_cli(*args), 0)
        self.assertEqual(worktree.read_text(encoding="utf-8"), "DIRTY WORKTREE\n")

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
        self.assertEqual(before_files, self.worktree_bytes(fixture["adopter"]))
        self.assertEqual(before_git, self.git_state(fixture["adopter"]))

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
        self.assertIn("schema_version: 2", proc.stdout)
        self.assertEqual(proc.stderr, "")
        self.assertEqual(adopter_before, self.worktree_bytes(fixture["adopter"]))
        self.assertEqual(upstream_before, self.worktree_bytes(fixture["upstream"]))
        self.assertEqual(adopter_git, self.git_state(fixture["adopter"]))
        self.assertEqual(upstream_git, self.git_state(fixture["upstream"]))

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
            self.assertEqual(before[str(path)], self.worktree_bytes(path))
            self.assertEqual(before_git[str(path)], self.git_state(path))


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
        self.assertEqual(candidate["accepted_source_commit"], fixture["target"])
        catalog = yaml.safe_load(GREETING_CATALOG)
        self.assertEqual(
            {row["id"] for row in candidate["units"]},
            {unit["id"] for unit in catalog["units"]},
        )
        for row in candidate["units"]:
            self.assertNotIn("accepted_source_commit", row)
        reproduced_snapshot = engine._snapshot_digest(
            sha256_text(GREETING_DECLARATION),
            sha256_text(EMPTY_REVIEW),
            candidate["units"],
        )
        self.assertEqual(
            candidate["accepted_snapshot_digest"],
            reproduced_snapshot,
            "the engine must reproduce propose-lock's accepted_snapshot_digest",
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
        self, fixture: dict, registry: Path
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
        self.assertTrue(report["compliance"])
        by_id = {adopter["id"]: adopter for adopter in report["adopters"]}
        self.assertTrue(by_id["good"]["compliance"])
        self.assertEqual(report["blocking_reasons"], [])

    def test_stale_registered_adopter_exit_1_without_required_field(self) -> None:
        fixture = self.build_verify()
        proc = self._verify(fixture, fixture["stale_registry"])
        self.assert_exit(proc, 1)
        report = json.loads(proc.stdout)
        self.assertFalse(report["compliance"])
        by_id = {adopter["id"]: adopter for adopter in report["adopters"]}
        self.assertTrue(by_id["good"]["compliance"])
        self.assertFalse(by_id["stale"]["compliance"])
        self.assertTrue(
            any("stale" in reason for reason in report["blocking_reasons"]),
            report["blocking_reasons"],
        )

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
        self.assertEqual(code, 1, "missing required checkout must block")
        report = json.loads(buffer.getvalue())
        ghost = next(a for a in report["adopters"] if a["id"] == "ghost")
        self.assertFalse(ghost["compliance"])
        self.assertIn("repository_unavailable", ghost["error"])
        self.assertTrue(
            any("ghost" in reason for reason in report["blocking_reasons"]),
            report["blocking_reasons"],
        )

    def test_registry_entries_have_no_required_field(self) -> None:
        fixture = self.build_verify()
        document = yaml.safe_load(
            fixture["stale_registry"].read_text(encoding="utf-8")
        )
        self.assertTrue(document["adopters"])
        for adopter in document["adopters"]:
            self.assertNotIn("required", adopter)
        self.assertIsInstance(
            engine.load_registry(str(fixture["stale_registry"])), dict
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)


