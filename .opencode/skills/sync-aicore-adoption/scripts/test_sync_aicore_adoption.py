"""Hermetic stdlib-``unittest`` tests for the sync-aicore-adoption checker.

Almost every test builds its own temporary upstream Git repository and adopter
tree and never reads the real AICore repository, any checked-in fixture, or the
network. The single exception is ``test_catalog_excludes_management_tools``,
which reads the repository catalog to assert the management tools are not
adopted-content units. Tests assert exact protocol enum strings against the
implementation by importing the sibling module ``sync_aicore_adoption``
(running this file directly puts the scripts directory on ``sys.path``).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Callable

import yaml

import sync_aicore_adoption as m

CATALOG = ".aicore/core-catalog-v1.yaml"


class SyncAdoptionTestBase(unittest.TestCase):
    """Base case owning a temp dir, a hermetic upstream repo, and an adopter tree."""

    UPSTREAM = "example-project/aicore"
    UPSTREAM_IDENTITY = "JPerezC92/ai-core"

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.upstream = self.root / "upstream"
        self.adopter = self.root / "adopter"
        env = os.environ.copy()
        env.update(
            {
                "GIT_AUTHOR_NAME": "Forge Test",
                "GIT_AUTHOR_EMAIL": "forge@test.invalid",
                "GIT_COMMITTER_NAME": "Forge Test",
                "GIT_COMMITTER_EMAIL": "forge@test.invalid",
                "GIT_CONFIG_NOSYSTEM": "1",
                "GIT_CONFIG_GLOBAL": os.devnull,
                "GIT_CONFIG_SYSTEM": os.devnull,
            }
        )
        self.git_env = env
        self.declaration_path = self.adopter / ".aicore" / "adoption.yaml"
        self.lock_path = self.adopter / ".aicore" / "adoption.lock.yaml"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    # -- Git plumbing -------------------------------------------------------

    def run_git(self, repo: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
        """Run a Git command with a fixed committer identity and no GPG signing."""

        return subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "-c",
                "commit.gpgsign=false",
                "-c",
                "user.name=Forge Test",
                "-c",
                "user.email=forge@test.invalid",
                *args,
            ],
            check=True,
            capture_output=True,
            env=self.git_env,
        )

    def rev_head(self, repo: Path) -> str:
        """Return the full 40-character id of the repository's HEAD commit."""

        return self.run_git(repo, "rev-parse", "HEAD").stdout.decode("ascii").strip()

    def write_snapshot(self, repo: Path, files: dict[str, bytes]) -> None:
        """Replace the tracked worktree content with one full file snapshot."""

        for child in list(repo.iterdir()):
            if child.name == ".git":
                continue
            if child.is_dir() and not child.is_symlink():
                shutil.rmtree(child)
            else:
                child.unlink()
        for relative, content in files.items():
            target = repo / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)

    def make_upstream(self, snapshots: list[dict[str, bytes]]) -> list[str]:
        """Create the upstream repo and commit each snapshot, returning commit ids."""

        self.upstream.mkdir(parents=True, exist_ok=True)
        self.run_git(self.upstream, "init", "--quiet")
        commits: list[str] = []
        for files in snapshots:
            self.write_snapshot(self.upstream, files)
            self.run_git(self.upstream, "add", "-A")
            self.run_git(self.upstream, "commit", "--quiet", "-m", "snapshot")
            commits.append(self.rev_head(self.upstream))
        return commits

    def make_adopter(self) -> None:
        """Create a Git-backed adopter repository with the adoption directory."""

        self.adopter.mkdir(parents=True, exist_ok=True)
        self.run_git(self.adopter, "init", "--quiet")
        self.declaration_path.parent.mkdir(parents=True, exist_ok=True)

    def commit_adopter(self, message: str = "adopter snapshot") -> str:
        """Commit the current adopter worktree and return the new commit id."""

        self.run_git(self.adopter, "add", "-A")
        self.run_git(self.adopter, "commit", "--quiet", "-m", message)
        return self.rev_head(self.adopter)

    def prepare_adopter(
        self,
        destinations: dict[str, bytes],
        declaration: dict[str, object],
        commit: bool = True,
    ) -> str:
        """Create the adopter, write destinations and declaration, then commit."""

        self.make_adopter()
        for relative, content in destinations.items():
            self.write_at(self.adopter / relative, content)
        self.write_declaration(declaration)
        if not commit:
            return ""
        return self.commit_adopter()

    def write_at(self, path: Path, content: bytes) -> None:
        """Write bytes to a path, creating any missing parent directories."""

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    # -- Document builders --------------------------------------------------

    def catalog_bytes(
        self, units: list[dict[str, object]], upstream: str | None = None
    ) -> bytes:
        """Serialize a machine catalog with an explicit upstream identity."""

        document = {
            "schema_version": 1,
            "catalog": {"upstream_repository": upstream if upstream is not None else self.UPSTREAM},
            "units": units,
        }
        return yaml.safe_dump(document, sort_keys=False).encode("utf-8")

    def file_unit(
        self, unit_id: str, member_id: str, source: str, destination: str
    ) -> dict[str, object]:
        """Build a ``file`` catalog unit with one member."""

        return {
            "id": unit_id,
            "sync_projection": "file",
            "members": [{"id": member_id, "source": source, "destination": destination}],
        }

    def tree_unit(
        self, unit_id: str, member_id: str, source: str, destination: str
    ) -> dict[str, object]:
        """Build a ``tree`` catalog unit with one member."""

        return {
            "id": unit_id,
            "sync_projection": "tree",
            "members": [{"id": member_id, "source": source, "destination": destination}],
        }

    def declaration(
        self, units: list[dict[str, object]], upstream: str | None = None
    ) -> dict[str, object]:
        """Build an adoption declaration document."""

        return {
            "schema_version": 1,
            "upstream_repository": upstream if upstream is not None else self.UPSTREAM,
            "units": units,
        }

    def declared_unit(
        self,
        unit_id: str,
        mode: str,
        members: list[dict[str, object]] | None = None,
        replacement_members: list[dict[str, object]] | None = None,
    ) -> dict[str, object]:
        """Build one declaration unit row."""

        unit: dict[str, object] = {"id": unit_id, "mode": mode}
        if members is not None:
            unit["members"] = members
        if replacement_members is not None:
            unit["replacement_members"] = replacement_members
        return unit

    def declared_member(self, member_id: str, destination: str) -> dict[str, object]:
        """Build one declaration member mapping."""

        return {"id": member_id, "destination": destination}

    def replacement_member(
        self, member_id: str, destination: str, projection: str = "file"
    ) -> dict[str, object]:
        """Build one declaration replacement member."""

        return {"id": member_id, "destination": destination, "projection": projection}

    def write_declaration(self, declaration: dict[str, object]) -> bytes:
        """Write the declaration and return its raw bytes."""

        raw = yaml.safe_dump(declaration, sort_keys=False).encode("utf-8")
        self.write_at(self.declaration_path, raw)
        return raw

    def write_lock_document(self, document: dict[str, object]) -> bytes:
        """Write a lock document and return its raw bytes."""

        raw = yaml.safe_dump(document, sort_keys=False).encode("utf-8")
        self.write_at(self.lock_path, raw)
        return raw

    def empty_lock(self, declaration: dict[str, object]) -> bytes:
        """Write an empty lock bound to a declaration's raw digest."""

        declaration_raw = self.write_declaration(declaration)
        document = {
            "schema_version": 1,
            "upstream_repository": self.UPSTREAM,
            "declaration_digest": m.sha256_digest(declaration_raw),
            "units": [],
        }
        return self.write_lock_document(document)

    def read_lock(self) -> dict[str, object]:
        """Read the lock file as a YAML document."""

        return yaml.safe_load(self.lock_path.read_bytes().decode("utf-8"))

    def mutate_lock(self, mutate: Callable[[dict[str, object]], None]) -> dict[str, object]:
        """Apply a mutation to the lock document and rewrite it."""

        document = self.read_lock()
        mutate(document)
        self.write_lock_document(document)
        return document

    # -- Digest helpers -----------------------------------------------------

    def file_digest(self, content: bytes, mode: str = "100644") -> str:
        """Compute a file-member digest for raw content."""

        return m.compute_member_digest([m.ProjectedEntry(path="", mode=mode, content=content)])

    def tree_digest(self, entries: list[tuple[str, str, bytes]]) -> str:
        """Compute a tree-member digest for ``(path, mode, content)`` entries."""

        return m.compute_member_digest(
            [
                m.ProjectedEntry(path=path, mode=mode, content=content)
                for path, mode, content in entries
            ]
        )

    def unit_digest(self, members: list[tuple[str, str]]) -> str:
        """Compute a unit digest from ordered ``(member_id, member_digest)`` pairs."""

        return m.digest_unit_from_members(members)

    # -- Execution helpers --------------------------------------------------

    def propose(
        self,
        current_sha: str,
        adopter_revision: str | None = None,
        adopter_index: bool = False,
        selected: list[str] | None = None,
    ) -> str:
        """Run ``propose_lock`` against the hermetic repos and return its text."""

        return m.propose_lock(
            self.upstream,
            self.adopter,
            current_sha,
            adopter_revision,
            adopter_index,
            self.declaration_path,
            self.lock_path,
            selected if selected is not None else [],
        )

    def propose_and_write(
        self,
        current_sha: str,
        adopter_revision: str | None = None,
        adopter_index: bool = False,
        selected: list[str] | None = None,
    ) -> dict[str, object]:
        """Run ``propose_lock`` and write the candidate lock into the adopter."""

        text = self.propose(current_sha, adopter_revision, adopter_index, selected)
        self.write_at(self.lock_path, text.encode("utf-8"))
        return yaml.safe_load(text)

    def check(
        self,
        current_sha: str,
        adopter_revision: str | None = None,
        adopter_index: bool = False,
    ) -> m.CheckReport:
        """Run ``check_adoption`` against the hermetic repos."""

        return m.check_adoption(
            self.upstream,
            self.adopter,
            current_sha,
            adopter_revision,
            adopter_index,
            self.declaration_path,
            self.lock_path,
        )

    def find_unit(self, report: m.CheckReport, unit_id: str) -> m.UnitReport:
        """Return the report row for a unit id or fail the test."""

        for unit in report.units:
            if unit.id == unit_id:
                return unit
        self.fail(f"unit {unit_id!r} not present in report")
        raise AssertionError("unreachable")

    def assert_sync_error(
        self, code: str, callable_: Callable[..., object], *args: object, **kwargs: object
    ) -> None:
        """Assert that a call raises ``SyncError`` with an exact protocol code."""

        with self.assertRaises(m.SyncError) as caught:
            callable_(*args, **kwargs)
        self.assertEqual(code, caught.exception.code)

    def snapshot_adopter(self) -> dict[str, bytes]:
        """Snapshot every adopter worktree file (excluding ``.git``) and its bytes."""

        snapshot: dict[str, bytes] = {}
        for path in sorted(self.adopter.rglob("*")):
            relative = path.relative_to(self.adopter)
            if ".git" in relative.parts:
                continue
            if path.is_file():
                snapshot[str(relative)] = path.read_bytes()
        return snapshot

    def git_status(self) -> bytes:
        """Return ``git status --porcelain`` output for the adopter worktree."""

        return self.run_git(self.adopter, "status", "--porcelain").stdout

    def run_script(self, implementation: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
        """Invoke the implementation as a subprocess with the current interpreter."""

        return subprocess.run(
            [sys.executable, str(implementation), *args],
            check=False,
            capture_output=True,
        )

    # -- Digest golden vectors ---------------------------------------------

    def test_golden_digest_vectors(self) -> None:
        vectors = m.golden_vectors()
        golden_file = "sha256:cf41078b082e3740168bd7ad534ba1b70b12489c7ab43c6fb53743b0f3527887"
        golden_tree = "sha256:4b49b94b71240c8933269684873b2eecf0f53de69ed8ded25eda1e172d3637d7"
        self.assertEqual(golden_file, vectors["file"])
        self.assertEqual(golden_tree, vectors["tree"])
        self.assertEqual(golden_file, m.GOLDEN_FILE_DIGEST)
        self.assertEqual(golden_tree, m.GOLDEN_TREE_DIGEST)

    # -- Mirror file and tree dispositions ----------------------------------

    def test_mirror_file_dispositions(self) -> None:
        units = [self.file_unit("mirror-file", "main", "content.txt", "mirror/content.txt")]
        catalog = self.catalog_bytes(units)
        accepted, modified = self.make_upstream(
            [
                {CATALOG: catalog, "content.txt": b"A\n"},
                {CATALOG: catalog, "content.txt": b"B\n"},
            ]
        )
        declaration = self.declaration(
            [
                self.declared_unit(
                    "mirror-file", "mirror", [self.declared_member("main", "mirror/content.txt")]
                )
            ]
        )
        rev_a = self.prepare_adopter({"mirror/content.txt": b"A\n"}, declaration)
        self.propose_and_write(accepted, adopter_revision=rev_a)

        unit = self.find_unit(self.check(accepted, adopter_revision=rev_a), "mirror-file")
        self.assertEqual("mirror", unit.mode)
        self.assertEqual("unchanged", unit.upstream_delta)
        self.assertEqual("unchanged", unit.destination_delta)
        self.assertEqual("current", unit.disposition)

        unit = self.find_unit(self.check(modified, adopter_revision=rev_a), "mirror-file")
        self.assertEqual("modified", unit.upstream_delta)
        self.assertEqual("unchanged", unit.destination_delta)
        self.assertEqual("update_available", unit.disposition)

        self.write_at(self.adopter / "mirror" / "content.txt", b"B\n")
        rev_b = self.commit_adopter()
        unit = self.find_unit(self.check(accepted, adopter_revision=rev_b), "mirror-file")
        self.assertEqual("unchanged", unit.upstream_delta)
        self.assertEqual("modified", unit.destination_delta)
        self.assertEqual("local_drift", unit.disposition)

        self.write_at(self.adopter / "mirror" / "content.txt", b"C\n")
        rev_c = self.commit_adopter()
        unit = self.find_unit(self.check(modified, adopter_revision=rev_c), "mirror-file")
        self.assertEqual("modified", unit.upstream_delta)
        self.assertEqual("modified", unit.destination_delta)
        self.assertEqual("conflict", unit.disposition)

    def test_mirror_tree_dispositions(self) -> None:
        units = [self.tree_unit("mirror-tree", "tree", "templates", "mirror/templates")]
        catalog = self.catalog_bytes(units)
        accepted, modified = self.make_upstream(
            [
                {
                    CATALOG: catalog,
                    "templates/a.txt": b"alpha\n",
                    "templates/sub/b.txt": b"beta\n",
                },
                {
                    CATALOG: catalog,
                    "templates/a.txt": b"ALPHA\n",
                    "templates/sub/b.txt": b"beta\n",
                },
            ]
        )
        declaration = self.declaration(
            [
                self.declared_unit(
                    "mirror-tree", "mirror", [self.declared_member("tree", "mirror/templates")]
                )
            ]
        )
        rev_a = self.prepare_adopter(
            {"mirror/templates/a.txt": b"alpha\n", "mirror/templates/sub/b.txt": b"beta\n"},
            declaration,
        )
        self.propose_and_write(accepted, adopter_revision=rev_a)

        def rewrite(a_content: bytes) -> str:
            self.write_at(self.adopter / "mirror" / "templates" / "a.txt", a_content)
            return self.commit_adopter()

        unit = self.find_unit(self.check(accepted, adopter_revision=rev_a), "mirror-tree")
        self.assertEqual("unchanged", unit.upstream_delta)
        self.assertEqual("unchanged", unit.destination_delta)
        self.assertEqual("current", unit.disposition)

        unit = self.find_unit(self.check(modified, adopter_revision=rev_a), "mirror-tree")
        self.assertEqual("modified", unit.upstream_delta)
        self.assertEqual("unchanged", unit.destination_delta)
        self.assertEqual("update_available", unit.disposition)

        rev_b = rewrite(b"beta\n")
        unit = self.find_unit(self.check(accepted, adopter_revision=rev_b), "mirror-tree")
        self.assertEqual("unchanged", unit.upstream_delta)
        self.assertEqual("modified", unit.destination_delta)
        self.assertEqual("local_drift", unit.disposition)

        rev_c = rewrite(b"gamma\n")
        unit = self.find_unit(self.check(modified, adopter_revision=rev_c), "mirror-tree")
        self.assertEqual("modified", unit.upstream_delta)
        self.assertEqual("modified", unit.destination_delta)
        self.assertEqual("conflict", unit.disposition)

    # -- Rejected mirror mismatch -------------------------------------------

    def test_rejected_mirror_mismatch(self) -> None:
        units = [self.file_unit("mirror-file", "main", "content.txt", "mirror/content.txt")]
        catalog = self.catalog_bytes(units)
        accepted = self.make_upstream([{CATALOG: catalog, "content.txt": b"A\n"}])[0]
        declaration = self.declaration(
            [
                self.declared_unit(
                    "mirror-file", "mirror", [self.declared_member("main", "mirror/content.txt")]
                )
            ]
        )
        rev = self.prepare_adopter({"mirror/content.txt": b"DIFFERENT\n"}, declaration)
        self.assert_sync_error(
            m.INVALID_LOCK,
            self.propose,
            accepted,
            rev,
            False,
            [],
        )

    # -- Renamed adapted root -----------------------------------------------

    def test_renamed_adapted_root_convergence(self) -> None:
        units = [self.file_unit("root-runtime-spec", "root", "AGENTS.md", "AGENTS.md")]
        catalog = self.catalog_bytes(units)
        accepted, modified = self.make_upstream(
            [
                {CATALOG: catalog, "AGENTS.md": b"V1\n"},
                {CATALOG: catalog, "AGENTS.md": b"V2\n"},
            ]
        )
        declaration = self.declaration(
            [
                self.declared_unit(
                    "root-runtime-spec", "adapted", [self.declared_member("root", "BASE-RULES.md")]
                )
            ]
        )
        rev_a = self.prepare_adopter({"BASE-RULES.md": b"V1\n"}, declaration)
        self.propose_and_write(accepted, adopter_revision=rev_a)

        unit = self.find_unit(self.check(accepted, adopter_revision=rev_a), "root-runtime-spec")
        self.assertEqual("current", unit.disposition)

        unit = self.find_unit(self.check(modified, adopter_revision=rev_a), "root-runtime-spec")
        self.assertEqual("modified", unit.upstream_delta)
        self.assertEqual("unchanged", unit.destination_delta)
        self.assertEqual("update_available", unit.disposition)

        self.write_at(self.adopter / "BASE-RULES.md", b"LOCAL\n")
        rev_b = self.commit_adopter()
        unit = self.find_unit(self.check(accepted, adopter_revision=rev_b), "root-runtime-spec")
        self.assertEqual("local_drift", unit.disposition)

        unit = self.find_unit(self.check(modified, adopter_revision=rev_b), "root-runtime-spec")
        self.assertEqual("review_required", unit.disposition)

    # -- One-to-many replacements -------------------------------------------

    def test_replacement_members_dispositions(self) -> None:
        base = self.file_unit("base", "file", "base.txt", "base.txt")
        skill = self.tree_unit("skill-doc", "tree", "skill", "skill")
        catalog0 = self.catalog_bytes([skill, base])
        catalog1 = self.catalog_bytes([skill, base])
        catalog2 = self.catalog_bytes([base])
        accepted, modified, retired = self.make_upstream(
            [
                {CATALOG: catalog0, "skill/a.md": b"A\n", "base.txt": b"BASE\n"},
                {CATALOG: catalog1, "skill/a.md": b"B\n", "base.txt": b"BASE\n"},
                {CATALOG: catalog2, "base.txt": b"BASE\n"},
            ]
        )
        declaration = self.declaration(
            [
                {
                    "id": "skill-doc",
                    "mode": "replacement",
                    "replacement_members": [
                        self.replacement_member("role-a", "local/a.md", "file"),
                        self.replacement_member("role-b", "local/b.md", "file"),
                    ],
                }
            ]
        )
        rev = self.prepare_adopter(
            {"local/a.md": b"A\n", "local/b.md": b"B\n"}, declaration
        )
        self.propose_and_write(accepted, adopter_revision=rev)

        unit = self.find_unit(self.check(accepted, adopter_revision=rev), "skill-doc")
        self.assertEqual("replacement", unit.mode)
        self.assertEqual("unchanged", unit.upstream_delta)
        self.assertEqual("unchanged", unit.destination_delta)
        self.assertEqual("current", unit.disposition)
        self.assertEqual(("role-a", "role-b"), tuple(member.id for member in unit.members))

        self.write_at(self.adopter / "local" / "a.md", b"CHANGED\n")
        rev_drift = self.commit_adopter()
        unit = self.find_unit(self.check(accepted, adopter_revision=rev_drift), "skill-doc")
        self.assertEqual("unchanged", unit.upstream_delta)
        self.assertEqual("modified", unit.destination_delta)
        self.assertEqual("local_drift", unit.disposition)

        unit = self.find_unit(self.check(modified, adopter_revision=rev_drift), "skill-doc")
        self.assertEqual("modified", unit.upstream_delta)
        self.assertEqual("modified", unit.destination_delta)
        self.assertEqual("conflict", unit.disposition)

        self.write_at(self.adopter / "local" / "a.md", b"A\n")
        rev_clean = self.commit_adopter()
        unit = self.find_unit(self.check(modified, adopter_revision=rev_clean), "skill-doc")
        self.assertEqual("modified", unit.upstream_delta)
        self.assertEqual("unchanged", unit.destination_delta)
        self.assertEqual("review_required", unit.disposition)

        unit = self.find_unit(self.check(retired, adopter_revision=rev_clean), "skill-doc")
        self.assertEqual("removed", unit.upstream_delta)
        self.assertEqual("retirement_available", unit.disposition)

    def test_missing_replacement_member_rejected(self) -> None:
        units = [self.tree_unit("skill-doc", "tree", "skill", "skill")]
        catalog = self.catalog_bytes(units)
        accepted = self.make_upstream([{CATALOG: catalog, "skill/a.md": b"A\n"}])[0]
        declaration = self.declaration(
            [
                {
                    "id": "skill-doc",
                    "mode": "replacement",
                    "replacement_members": [
                        self.replacement_member("role-a", "local/a.md", "file")
                    ],
                }
            ]
        )
        rev = self.prepare_adopter({"local/b.md": b"B\n"}, declaration)
        self.assert_sync_error(m.INVALID_MAPPING, self.propose, accepted, rev, False, [])

    # -- Destination-owned units --------------------------------------------

    def test_destination_owned_unmanaged_and_retirement(self) -> None:
        local_unit = self.file_unit("local-config", "main", "upstream.cfg", "local/config.cfg")
        base_unit = self.file_unit("mirror-base", "main", "base.txt", "mirror/base.txt")
        catalog0 = self.catalog_bytes([local_unit, base_unit])
        catalog1 = self.catalog_bytes([base_unit])
        accepted, retired = self.make_upstream(
            [
                {CATALOG: catalog0, "upstream.cfg": b"CFG\n", "base.txt": b"BASE\n"},
                {CATALOG: catalog1, "base.txt": b"BASE\n"},
            ]
        )
        declaration = self.declaration(
            [
                self.declared_unit(
                    "local-config",
                    "destination_owned",
                    [self.declared_member("main", "local/config.cfg")],
                ),
                self.declared_unit(
                    "mirror-base", "mirror", [self.declared_member("main", "mirror/base.txt")]
                ),
            ]
        )
        rev = self.prepare_adopter(
            {"local/config.cfg": b"CFG\n", "mirror/base.txt": b"BASE\n"}, declaration
        )
        self.propose_and_write(accepted, adopter_revision=rev)

        unit = self.find_unit(self.check(accepted, adopter_revision=rev), "local-config")
        self.assertEqual("destination_owned", unit.mode)
        self.assertEqual("unmanaged", unit.disposition)

        unit = self.find_unit(self.check(retired, adopter_revision=rev), "local-config")
        self.assertEqual("removed", unit.upstream_delta)
        self.assertEqual("retirement_available", unit.disposition)

    def test_destination_owned_unknown_unit_rejected(self) -> None:
        units = [self.file_unit("known", "main", "known.txt", "known.txt")]
        catalog = self.catalog_bytes(units)
        accepted = self.make_upstream([{CATALOG: catalog, "known.txt": b"K\n"}])[0]
        self.make_adopter()
        declaration = self.declaration(
            [
                self.declared_unit(
                    "unknown-unit", "destination_owned", [self.declared_member("main", "local/x")]
                )
            ]
        )
        self.empty_lock(declaration)
        self.assert_sync_error(m.INVALID_MAPPING, self.check, accepted, None, True)

    def test_destination_owned_none_projection_rejected(self) -> None:
        none_unit = {
            "id": "installer-only",
            "sync_projection": "none",
            "members": [{"id": "main", "source": "install.sh", "destination": "install.sh"}],
        }
        catalog = self.catalog_bytes([none_unit])
        accepted = self.make_upstream(
            [{CATALOG: catalog, "install.sh": b"echo\n"}]
        )[0]
        self.make_adopter()
        declaration = self.declaration(
            [
                self.declared_unit(
                    "installer-only",
                    "destination_owned",
                    [self.declared_member("main", "local/install.sh")],
                )
            ]
        )
        self.empty_lock(declaration)
        self.assert_sync_error(m.UNSUPPORTED_PROJECTION, self.check, accepted, None, True)

    # -- Undeclared and catalog boundary ------------------------------------

    def test_undeclared_upstream_addition(self) -> None:
        base = self.file_unit("base", "main", "base.txt", "base.txt")
        new = self.file_unit("new-unit", "main", "new.txt", "new.txt")
        catalog0 = self.catalog_bytes([base])
        catalog1 = self.catalog_bytes([base, new])
        accepted, current = self.make_upstream(
            [
                {CATALOG: catalog0, "base.txt": b"BASE\n"},
                {CATALOG: catalog1, "base.txt": b"BASE\n", "new.txt": b"NEW\n"},
            ]
        )
        self.make_adopter()
        declaration = self.declaration([])
        self.empty_lock(declaration)

        report = self.check(current, None, True)
        unit = self.find_unit(report, "new-unit")
        self.assertEqual("not_declared", unit.mode)
        self.assertEqual("added", unit.upstream_delta)
        self.assertEqual("not_applicable", unit.destination_delta)
        self.assertEqual("adoption_available", unit.disposition)

    def test_upstream_unit_removal_adapted(self) -> None:
        base = self.file_unit("base", "main", "base.txt", "base.txt")
        removed = self.file_unit("removed", "main", "removed.txt", "removed.txt")
        catalog0 = self.catalog_bytes([base, removed])
        catalog1 = self.catalog_bytes([base])
        accepted, current = self.make_upstream(
            [
                {CATALOG: catalog0, "base.txt": b"B\n", "removed.txt": b"R\n"},
                {CATALOG: catalog1, "base.txt": b"B\n"},
            ]
        )
        declaration = self.declaration(
            [
                self.declared_unit(
                    "removed", "adapted", [self.declared_member("main", "removed.txt")]
                )
            ]
        )
        rev = self.prepare_adopter({"removed.txt": b"R\n"}, declaration)
        self.propose_and_write(accepted, adopter_revision=rev)

        unit = self.find_unit(self.check(current, adopter_revision=rev), "removed")
        self.assertEqual("adapted", unit.mode)
        self.assertEqual("removed", unit.upstream_delta)
        self.assertEqual("retirement_available", unit.disposition)

    def test_member_destination_removal_mirror_and_adapted(self) -> None:
        mirror_unit = self.file_unit("mirror-u", "m", "m.txt", "mirror/m.txt")
        adapted_unit = self.file_unit("adapted-u", "m", "a.txt", "adapted/a.txt")
        catalog = self.catalog_bytes([mirror_unit, adapted_unit])
        accepted = self.make_upstream(
            [
                {
                    CATALOG: catalog,
                    "m.txt": b"M\n",
                    "a.txt": b"A\n",
                }
            ]
        )[0]
        declaration = self.declaration(
            [
                self.declared_unit(
                    "mirror-u", "mirror", [self.declared_member("m", "mirror/m.txt")]
                ),
                self.declared_unit(
                    "adapted-u", "adapted", [self.declared_member("m", "adapted/a.txt")]
                ),
            ]
        )
        rev = self.prepare_adopter({"mirror/m.txt": b"M\n", "adapted/a.txt": b"A\n"}, declaration)
        self.propose_and_write(accepted, adopter_revision=rev)

        os.remove(self.adopter / "mirror" / "m.txt")
        os.remove(self.adopter / "adapted" / "a.txt")
        rev_removed = self.commit_adopter()
        report = self.check(accepted, adopter_revision=rev_removed)

        mirror_report = self.find_unit(report, "mirror-u")
        self.assertEqual("removed", mirror_report.destination_delta)
        self.assertEqual("local_drift", mirror_report.disposition)

        adapted_report = self.find_unit(report, "adapted-u")
        self.assertEqual("removed", adapted_report.destination_delta)
        self.assertEqual("local_drift", adapted_report.disposition)

    # -- Same-result convergence --------------------------------------------

    def test_same_result_convergence(self) -> None:
        units = [self.file_unit("root-runtime-spec", "root", "AGENTS.md", "LOCAL.md")]
        catalog = self.catalog_bytes(units)
        accepted, current = self.make_upstream(
            [
                {CATALOG: catalog, "AGENTS.md": b"UP1\n"},
                {CATALOG: catalog, "AGENTS.md": b"UP2\n"},
            ]
        )
        declaration = self.declaration(
            [
                self.declared_unit(
                    "root-runtime-spec", "adapted", [self.declared_member("root", "LOCAL.md")]
                )
            ]
        )
        rev = self.prepare_adopter({"LOCAL.md": b"UP2\n"}, declaration)
        self.propose_and_write(accepted, adopter_revision=rev)

        unit = self.find_unit(self.check(current, adopter_revision=rev), "root-runtime-spec")
        self.assertEqual("modified", unit.upstream_delta)
        self.assertEqual("unchanged", unit.destination_delta)
        self.assertEqual("update_available", unit.disposition)
        member = unit.members[0]
        self.assertEqual(member.current_upstream_digest, member.current_destination_digest)

    def test_changed_catalogs_reconcile_by_id(self) -> None:
        unit_u1 = self.file_unit("u1", "m1", "u1.txt", "u1.txt")
        unit_u2 = self.file_unit("u2", "m2", "u2.txt", "u2.txt")
        unit_u3 = self.file_unit("u3", "m3", "u3.txt", "u3.txt")
        catalog0 = self.catalog_bytes([unit_u1, unit_u3])
        catalog1 = self.catalog_bytes([unit_u1, unit_u2])
        accepted, current = self.make_upstream(
            [
                {CATALOG: catalog0, "u1.txt": b"U1\n", "u3.txt": b"U3\n"},
                {CATALOG: catalog1, "u1.txt": b"U1\n", "u2.txt": b"U2\n"},
            ]
        )
        declaration = self.declaration(
            [self.declared_unit("u1", "mirror", [self.declared_member("m1", "u1.txt")])]
        )
        rev = self.prepare_adopter({"u1.txt": b"U1\n"}, declaration)
        self.propose_and_write(accepted, adopter_revision=rev)

        report = self.check(current, adopter_revision=rev)
        self.assertEqual("ok", report.status)
        self.assertEqual("unchanged", self.find_unit(report, "u1").upstream_delta)
        added = self.find_unit(report, "u2")
        self.assertEqual("not_declared", added.mode)
        self.assertEqual("adoption_available", added.disposition)

    def test_changed_declaration_detected(self) -> None:
        units = [self.file_unit("u", "m", "s.txt", "d.txt")]
        catalog = self.catalog_bytes(units)
        accepted = self.make_upstream([{CATALOG: catalog, "s.txt": b"S\n"}])[0]
        declaration = self.declaration(
            [self.declared_unit("u", "adapted", [self.declared_member("m", "d.txt")])]
        )
        rev = self.prepare_adopter({"d.txt": b"S\n"}, declaration)
        self.propose_and_write(accepted, adopter_revision=rev)

        changed = self.declaration(
            [self.declared_unit("u", "adapted", [self.declared_member("m", "relocated.txt")])]
        )
        self.write_declaration(changed)
        self.assert_sync_error(m.DECLARATION_CHANGED, self.check, accepted, rev, False)

    # -- Line-ending sensitivity --------------------------------------------

    def test_line_ending_only_drift(self) -> None:
        units = [self.file_unit("mirror-file", "main", "content.txt", "mirror/content.txt")]
        catalog = self.catalog_bytes(units)
        accepted = self.make_upstream(
            [{CATALOG: catalog, "content.txt": b"line\n"}]
        )[0]
        declaration = self.declaration(
            [
                self.declared_unit(
                    "mirror-file", "mirror", [self.declared_member("main", "mirror/content.txt")]
                )
            ]
        )
        rev = self.prepare_adopter({"mirror/content.txt": b"line\n"}, declaration)
        self.propose_and_write(accepted, adopter_revision=rev)

        self.write_at(self.adopter / "mirror" / "content.txt", b"line\r\n")
        rev_crlf = self.commit_adopter()
        unit = self.find_unit(self.check(accepted, adopter_revision=rev_crlf), "mirror-file")
        self.assertEqual("unchanged", unit.upstream_delta)
        self.assertEqual("modified", unit.destination_delta)
        self.assertEqual("local_drift", unit.disposition)

    # -- Malformed schemas --------------------------------------------------

    def test_malformed_catalog_schemas(self) -> None:
        self.assert_sync_error(
            m.CATALOG_CHANGED, m.parse_catalog, b"schema_version: 1\nunits: [", "catalog"
        )
        self.assert_sync_error(
            m.CATALOG_CHANGED, m.parse_catalog, b"schema_version: 1\ncatalog: {}\n", "catalog"
        )
        wrong_version = yaml.safe_dump(
            {
                "schema_version": 9,
                "catalog": {"upstream_repository": self.UPSTREAM},
                "units": [
                    {
                        "id": "u",
                        "sync_projection": "file",
                        "members": [{"id": "m", "source": "s", "destination": "d"}],
                    }
                ],
            },
            sort_keys=False,
        ).encode("utf-8")
        self.assert_sync_error(m.CATALOG_CHANGED, m.parse_catalog, wrong_version, "catalog")
        wrong_projection = yaml.safe_dump(
            {
                "schema_version": 1,
                "catalog": {"upstream_repository": self.UPSTREAM},
                "units": [
                    {
                        "id": "u",
                        "sync_projection": "bogus",
                        "members": [{"id": "m", "source": "s", "destination": "d"}],
                    }
                ],
            },
            sort_keys=False,
        ).encode("utf-8")
        self.assert_sync_error(
            m.UNSUPPORTED_PROJECTION, m.parse_catalog, wrong_projection, "catalog"
        )

    def test_malformed_declaration_schemas(self) -> None:
        self.assert_sync_error(
            m.INVALID_MAPPING, m.parse_declaration, b"schema_version: 1\nunits: [", "declaration"
        )
        self.assert_sync_error(
            m.INVALID_MAPPING, m.parse_declaration, b"schema_version: 1\nunits: []\n", "declaration"
        )
        wrong_mode = yaml.safe_dump(
            {
                "schema_version": 1,
                "upstream_repository": "o/r",
                "units": [
                    {"id": "u", "mode": "bogus", "members": [{"id": "m", "destination": "d"}]}
                ],
            },
            sort_keys=False,
        ).encode("utf-8")
        self.assert_sync_error(m.INVALID_MAPPING, m.parse_declaration, wrong_mode, "declaration")

    def test_malformed_lock_schemas(self) -> None:
        digest = "sha256:" + "0" * 64
        self.assert_sync_error(m.INVALID_LOCK, m.parse_lock, b"schema_version: 1\nunits: [", "lock")
        missing_digest = yaml.safe_dump(
            {
                "schema_version": 1,
                "upstream_repository": "o/r",
                "units": [],
            },
            sort_keys=False,
        ).encode("utf-8")
        self.assert_sync_error(m.INVALID_LOCK, m.parse_lock, missing_digest, "lock")
        wrong_mode = yaml.safe_dump(
            {
                "schema_version": 1,
                "upstream_repository": "o/r",
                "declaration_digest": digest,
                "units": [
                    {
                        "id": "u",
                        "mode": "bogus",
                        "accepted_source_commit": "a" * 40,
                        "accepted_catalog_digest": digest,
                        "declaration_unit_digest": digest,
                        "accepted_upstream_digest": digest,
                        "members": [
                            {
                                "id": "m",
                                "destination": "d",
                                "accepted_upstream_digest": digest,
                                "accepted_destination_digest": digest,
                            }
                        ],
                    }
                ],
            },
            sort_keys=False,
        ).encode("utf-8")
        self.assert_sync_error(m.INVALID_LOCK, m.parse_lock, wrong_mode, "lock")

    def test_unknown_keys_rejected(self) -> None:
        digest = "sha256:" + "0" * 64
        catalog_unknown = yaml.safe_dump(
            {
                "schema_version": 1,
                "catalog": {"upstream_repository": "o/r", "bogus": True},
                "units": [
                    {
                        "id": "u",
                        "sync_projection": "file",
                        "members": [{"id": "m", "source": "s", "destination": "d"}],
                    }
                ],
            },
            sort_keys=False,
        ).encode("utf-8")
        self.assert_sync_error(m.UNKNOWN_KEY, m.parse_catalog, catalog_unknown, "catalog")

        declaration_unknown = yaml.safe_dump(
            {
                "schema_version": 1,
                "upstream_repository": "o/r",
                "units": [],
                "bogus": True,
            },
            sort_keys=False,
        ).encode("utf-8")
        self.assert_sync_error(m.UNKNOWN_KEY, m.parse_declaration, declaration_unknown, "declaration")

        lock_unknown = yaml.safe_dump(
            {
                "schema_version": 1,
                "upstream_repository": "o/r",
                "declaration_digest": digest,
                "units": [],
                "bogus": True,
            },
            sort_keys=False,
        ).encode("utf-8")
        self.assert_sync_error(m.UNKNOWN_KEY, m.parse_lock, lock_unknown, "lock")

        lock_unit_unknown = yaml.safe_dump(
            {
                "schema_version": 1,
                "upstream_repository": "o/r",
                "declaration_digest": digest,
                "units": [
                    {
                        "id": "u",
                        "mode": "adapted",
                        "accepted_source_commit": "a" * 40,
                        "accepted_catalog_digest": digest,
                        "declaration_unit_digest": digest,
                        "accepted_upstream_digest": digest,
                        "bogus": True,
                        "members": [
                            {
                                "id": "m",
                                "destination": "d",
                                "accepted_upstream_digest": digest,
                                "accepted_destination_digest": digest,
                            }
                        ],
                    }
                ],
            },
            sort_keys=False,
        ).encode("utf-8")
        self.assert_sync_error(m.UNKNOWN_KEY, m.parse_lock, lock_unit_unknown, "lock")

    # -- Missing catalog sources --------------------------------------------

    def test_missing_catalog_source_is_catalog_changed(self) -> None:
        units = [self.file_unit("missing", "main", "does-not-exist.txt", "local/missing.txt")]
        catalog = self.catalog_bytes(units)
        accepted, current = self.make_upstream(
            [
                {CATALOG: catalog, "does-not-exist.txt": b"1"},
                {CATALOG: catalog, "unused.txt": b"2"},
            ]
        )
        declaration = self.declaration(
            [
                self.declared_unit(
                    "missing", "adapted", [self.declared_member("main", "local/missing.txt")]
                )
            ]
        )
        rev = self.prepare_adopter({"local/missing.txt": b"y"}, declaration)
        self.propose_and_write(accepted, adopter_revision=rev)
        self.assert_sync_error(m.CATALOG_CHANGED, self.check, current, rev, False)

    # -- Baseline resolution failures ---------------------------------------

    def test_unknown_accepted_commit_is_baseline_unavailable(self) -> None:
        units = [self.file_unit("u", "m", "s.txt", "d.txt")]
        catalog = self.catalog_bytes(units)
        accepted = self.make_upstream([{CATALOG: catalog, "s.txt": b"S\n"}])[0]
        declaration = self.declaration(
            [self.declared_unit("u", "adapted", [self.declared_member("m", "d.txt")])]
        )
        rev = self.prepare_adopter({"d.txt": b"S\n"}, declaration)
        self.propose_and_write(accepted, adopter_revision=rev)

        def break_commit(document: dict[str, object]) -> None:
            units_doc = document["units"]
            assert isinstance(units_doc, list)
            units_doc[0]["accepted_source_commit"] = "0" * 40  # type: ignore[index]

        self.mutate_lock(break_commit)
        self.assert_sync_error(m.BASELINE_UNAVAILABLE, self.check, accepted, rev, False)

    def test_non_ancestor_accepted_commit_is_baseline_unavailable(self) -> None:
        units = [self.file_unit("u", "m", "s.txt", "d.txt")]
        catalog = self.catalog_bytes(units)
        first = self.make_upstream([{CATALOG: catalog, "s.txt": b"S\n"}])[0]
        declaration = self.declaration(
            [self.declared_unit("u", "adapted", [self.declared_member("m", "d.txt")])]
        )
        rev = self.prepare_adopter({"d.txt": b"S\n"}, declaration)
        self.propose_and_write(first, adopter_revision=rev)

        self.run_git(self.upstream, "checkout", "--orphan", "orphan")
        self.write_snapshot(self.upstream, {CATALOG: catalog, "s.txt": b"S\n"})
        self.run_git(self.upstream, "add", "-A")
        self.run_git(self.upstream, "commit", "--quiet", "-m", "orphan")
        orphan = self.rev_head(self.upstream)
        self.assert_sync_error(m.BASELINE_UNAVAILABLE, self.check, orphan, rev, False)

    # -- Excluded bytecode --------------------------------------------------

    def test_excluded_bytecode_paths_are_ignored(self) -> None:
        units = [self.tree_unit("mirror-tree", "tree", "templates", "mirror/templates")]
        catalog = self.catalog_bytes(units)
        base_files: dict[str, bytes] = {CATALOG: catalog, "templates/a.txt": b"alpha\n"}
        commit0, commit1, commit2 = self.make_upstream(
            [
                dict(base_files),
                {**base_files, "templates/__pycache__/x.pyc": b"v1"},
                {**base_files, "templates/__pycache__/x.pyc": b"v2"},
            ]
        )
        declaration = self.declaration(
            [
                self.declared_unit(
                    "mirror-tree", "mirror", [self.declared_member("tree", "mirror/templates")]
                )
            ]
        )
        rev = self.prepare_adopter({"mirror/templates/a.txt": b"alpha\n"}, declaration)
        self.propose_and_write(commit0, adopter_revision=rev)

        unit1 = self.find_unit(self.check(commit1, adopter_revision=rev), "mirror-tree")
        self.assertEqual("unchanged", unit1.upstream_delta)
        self.assertEqual("unchanged", unit1.destination_delta)

        self.write_at(self.adopter / "mirror" / "templates" / "__pycache__" / "y.pyc", b"local")
        rev_pyc = self.commit_adopter()
        unit2 = self.find_unit(self.check(commit2, adopter_revision=rev_pyc), "mirror-tree")
        self.assertEqual("unchanged", unit2.upstream_delta)
        self.assertEqual("unchanged", unit2.destination_delta)
        self.assertEqual(
            unit1.members[0].current_upstream_digest, unit2.members[0].current_upstream_digest
        )

    # -- Rejected mappings --------------------------------------------------

    def test_rejected_mappings(self) -> None:
        controls = m.DEFAULT_CONTROL_PATHS
        self.assert_sync_error(
            m.INVALID_MAPPING, m.validate_destination_mappings, [("/abs/path", "file")], controls
        )
        self.assert_sync_error(
            m.INVALID_MAPPING, m.validate_destination_mappings, [("a/../b", "file")], controls
        )
        self.assert_sync_error(
            m.INVALID_MAPPING,
            m.validate_destination_mappings,
            [("dup", "file"), ("dup", "file")],
            controls,
        )
        self.assert_sync_error(
            m.INVALID_MAPPING,
            m.validate_destination_mappings,
            [("tree", "tree"), ("tree/child", "file")],
            controls,
        )
        self.assert_sync_error(
            m.INVALID_MAPPING, m.validate_destination_mappings, [(".git/config", "file")], controls
        )
        self.assert_sync_error(
            m.INVALID_MAPPING,
            m.validate_destination_mappings,
            [(".aicore/adoption.yaml", "file")],
            controls,
        )
        self.assert_sync_error(
            m.INVALID_MAPPING,
            m.validate_destination_mappings,
            [(".aicore/adoption.lock.yaml", "file")],
            controls,
        )

    def test_control_path_destination_rejected_end_to_end(self) -> None:
        units = [self.file_unit("u", "m", "s.txt", ".git/config")]
        catalog = self.catalog_bytes(units)
        accepted = self.make_upstream([{CATALOG: catalog, "s.txt": b"S\n"}])[0]
        declaration = self.declaration(
            [self.declared_unit("u", "adapted", [self.declared_member("m", ".git/config")])]
        )
        rev = self.prepare_adopter({".git-config-placeholder": b"S\n"}, declaration)
        self.assert_sync_error(m.INVALID_MAPPING, self.propose, accepted, rev, False, [])

    # -- Symlink escape -----------------------------------------------------

    def test_symlink_ancestor_escape_rejected(self) -> None:
        units = [self.file_unit("u", "m", "s.txt", "escape/file.txt")]
        catalog = self.catalog_bytes(units)
        accepted = self.make_upstream([{CATALOG: catalog, "s.txt": b"S\n"}])[0]
        self.make_adopter()
        outside = self.root / "outside"
        outside.mkdir()
        os.symlink(outside, self.adopter / "escape")
        declaration = self.declaration(
            [self.declared_unit("u", "adapted", [self.declared_member("m", "escape/file.txt")])]
        )
        self.write_declaration(declaration)
        rev = self.commit_adopter()
        self.assert_sync_error(m.INVALID_MAPPING, self.propose, accepted, rev, False, [])

    # -- Baseline advance ---------------------------------------------------

    def test_baseline_advance_required_when_commit_advances(self) -> None:
        units = [self.file_unit("mirror-file", "main", "content.txt", "mirror/content.txt")]
        catalog = self.catalog_bytes(units)
        accepted, current = self.make_upstream(
            [
                {CATALOG: catalog, "content.txt": b"A\n", "notes.txt": b"1"},
                {CATALOG: catalog, "content.txt": b"A\n", "notes.txt": b"2"},
            ]
        )
        declaration = self.declaration(
            [
                self.declared_unit(
                    "mirror-file", "mirror", [self.declared_member("main", "mirror/content.txt")]
                )
            ]
        )
        rev = self.prepare_adopter({"mirror/content.txt": b"A\n"}, declaration)
        self.propose_and_write(accepted, adopter_revision=rev)

        unit = self.find_unit(self.check(current, adopter_revision=rev), "mirror-file")
        self.assertNotEqual(accepted, current)
        self.assertEqual("unchanged", unit.upstream_delta)
        self.assertEqual("unchanged", unit.destination_delta)
        self.assertEqual("baseline_advance_required", unit.disposition)

    # -- Falsified evidence -------------------------------------------------

    def test_falsified_accepted_digests_rejected(self) -> None:
        units = [self.file_unit("mirror-file", "main", "content.txt", "mirror/content.txt")]
        catalog = self.catalog_bytes(units)
        accepted = self.make_upstream(
            [{CATALOG: catalog, "content.txt": b"A\n"}]
        )[0]
        declaration = self.declaration(
            [
                self.declared_unit(
                    "mirror-file", "mirror", [self.declared_member("main", "mirror/content.txt")]
                )
            ]
        )
        rev = self.prepare_adopter({"mirror/content.txt": b"A\n"}, declaration)
        self.propose_and_write(accepted, adopter_revision=rev)
        valid = self.read_lock()

        forged_member = "sha256:" + "1" * 64

        def break_member(document: dict[str, object]) -> None:
            units_doc = document["units"]
            assert isinstance(units_doc, list)
            members = units_doc[0]["members"]  # type: ignore[index]
            assert isinstance(members, list)
            members[0]["accepted_upstream_digest"] = forged_member

        self.write_lock_document(valid)
        self.mutate_lock(break_member)
        self.assert_sync_error(m.INVALID_LOCK, self.check, accepted, rev, False)

        self.write_lock_document(valid)

        def break_unit(document: dict[str, object]) -> None:
            units_doc = document["units"]
            assert isinstance(units_doc, list)
            units_doc[0]["accepted_upstream_digest"] = forged_member  # type: ignore[index]

        self.mutate_lock(break_unit)
        self.assert_sync_error(m.INVALID_LOCK, self.check, accepted, rev, False)

        self.write_lock_document(valid)

        def break_catalog(document: dict[str, object]) -> None:
            units_doc = document["units"]
            assert isinstance(units_doc, list)
            units_doc[0]["accepted_catalog_digest"] = forged_member  # type: ignore[index]

        self.mutate_lock(break_catalog)
        self.assert_sync_error(m.CATALOG_CHANGED, self.check, accepted, rev, False)

    def test_wrong_repository_identity_rejected(self) -> None:
        units = [self.file_unit("u", "m", "s.txt", "d.txt")]
        catalog = self.catalog_bytes(units)
        wrong = self.catalog_bytes(units, upstream="some-other/adopter-core")
        accepted, current = self.make_upstream(
            [
                {CATALOG: catalog, "s.txt": b"S\n"},
                {CATALOG: wrong, "s.txt": b"S\n"},
            ]
        )
        declaration = self.declaration(
            [self.declared_unit("u", "adapted", [self.declared_member("m", "d.txt")])]
        )
        rev = self.prepare_adopter({"d.txt": b"S\n"}, declaration)
        self.propose_and_write(accepted, adopter_revision=rev)
        self.assert_sync_error(m.REPOSITORY_IDENTITY_MISMATCH, self.check, current, rev, False)

    # -- Snapshot sources ---------------------------------------------------

    def test_revision_and_index_snapshots_agree(self) -> None:
        units = [self.file_unit("mirror-file", "main", "content.txt", "mirror/content.txt")]
        catalog = self.catalog_bytes(units)
        accepted = self.make_upstream([{CATALOG: catalog, "content.txt": b"A\n"}])[0]
        declaration = self.declaration(
            [
                self.declared_unit(
                    "mirror-file", "mirror", [self.declared_member("main", "mirror/content.txt")]
                )
            ]
        )
        rev = self.prepare_adopter({"mirror/content.txt": b"A\n"}, declaration)
        self.propose_and_write(accepted, adopter_revision=rev)

        revision_unit = self.find_unit(self.check(accepted, adopter_revision=rev), "mirror-file")
        index_unit = self.find_unit(self.check(accepted, None, True), "mirror-file")
        self.assertEqual(revision_unit.disposition, index_unit.disposition)
        self.assertEqual(revision_unit.destination_delta, index_unit.destination_delta)

    def test_unstaged_content_excluded_from_index(self) -> None:
        units = [self.file_unit("mirror-file", "main", "content.txt", "mirror/content.txt")]
        catalog = self.catalog_bytes(units)
        accepted = self.make_upstream([{CATALOG: catalog, "content.txt": b"A\n"}])[0]
        declaration = self.declaration(
            [
                self.declared_unit(
                    "mirror-file", "mirror", [self.declared_member("main", "mirror/content.txt")]
                )
            ]
        )
        rev = self.prepare_adopter({"mirror/content.txt": b"A\n"}, declaration)
        self.propose_and_write(accepted, adopter_index=True)

        # An unstaged edit must not appear in the staged-index snapshot.
        self.write_at(self.adopter / "mirror" / "content.txt", b"B\n")
        unit = self.find_unit(self.check(accepted, None, True), "mirror-file")
        self.assertEqual("unchanged", unit.destination_delta)
        self.assertEqual("current", unit.disposition)

        self.run_git(self.adopter, "add", "mirror/content.txt")
        unit = self.find_unit(self.check(accepted, None, True), "mirror-file")
        self.assertEqual("modified", unit.destination_delta)
        self.assertEqual("local_drift", unit.disposition)
        self.assertEqual(rev, self.rev_head(self.adopter))

    # -- Incremental acceptance ---------------------------------------------

    def test_selected_unit_lock_advancement_preserves_unselected(self) -> None:
        u1 = self.file_unit("u1", "m", "u1.txt", "u1.txt")
        u2 = self.file_unit("u2", "m", "u2.txt", "u2.txt")
        catalog = self.catalog_bytes([u1, u2])
        accepted, current = self.make_upstream(
            [
                {CATALOG: catalog, "u1.txt": b"A\n", "u2.txt": b"X\n"},
                {CATALOG: catalog, "u1.txt": b"B\n", "u2.txt": b"X\n"},
            ]
        )
        declaration = self.declaration(
            [
                self.declared_unit("u1", "mirror", [self.declared_member("m", "u1.txt")]),
                self.declared_unit("u2", "mirror", [self.declared_member("m", "u2.txt")]),
            ]
        )
        rev = self.prepare_adopter({"u1.txt": b"A\n", "u2.txt": b"X\n"}, declaration)
        initial = self.propose_and_write(accepted, adopter_revision=rev)
        initial_u2 = [row for row in initial["units"] if row["id"] == "u2"][0]  # type: ignore[index]

        self.write_at(self.adopter / "u1.txt", b"B\n")
        rev_updated = self.commit_adopter()
        updated = self.propose_and_write(
            current, adopter_revision=rev_updated, selected=["u1"]
        )
        rows = {row["id"]: row for row in updated["units"]}  # type: ignore[index]
        self.assertEqual(current, rows["u1"]["accepted_source_commit"])
        self.assertEqual(accepted, rows["u2"]["accepted_source_commit"])
        self.assertEqual(initial_u2, rows["u2"])

        unit = self.find_unit(self.check(current, adopter_revision=rev_updated), "u1")
        self.assertEqual("unchanged", unit.upstream_delta)
        self.assertEqual("unchanged", unit.destination_delta)
        self.assertEqual("current", unit.disposition)

        old = self.find_unit(self.check(current, adopter_revision=rev_updated), "u2")
        self.assertEqual("baseline_advance_required", old.disposition)

    def test_unselected_intent_change_rejected(self) -> None:
        u1 = self.file_unit("u1", "m", "u1.txt", "u1.txt")
        u2 = self.file_unit("u2", "m", "u2.txt", "u2.txt")
        catalog = self.catalog_bytes([u1, u2])
        accepted, current = self.make_upstream(
            [
                {CATALOG: catalog, "u1.txt": b"A\n", "u2.txt": b"X\n"},
                {CATALOG: catalog, "u1.txt": b"B\n", "u2.txt": b"X\n"},
            ]
        )
        declaration = self.declaration(
            [
                self.declared_unit("u1", "mirror", [self.declared_member("m", "u1.txt")]),
                self.declared_unit("u2", "mirror", [self.declared_member("m", "u2.txt")]),
            ]
        )
        rev = self.prepare_adopter({"u1.txt": b"A\n", "u2.txt": b"X\n"}, declaration)
        self.propose_and_write(accepted, adopter_revision=rev)

        remapped = self.declaration(
            [
                self.declared_unit("u1", "mirror", [self.declared_member("m", "u1.txt")]),
                self.declared_unit("u2", "mirror", [self.declared_member("m", "relocated.txt")]),
            ]
        )
        self.write_declaration(remapped)
        self.assert_sync_error(
            m.INVALID_SELECTION,
            self.propose,
            current,
            rev,
            False,
            ["u1"],
        )

    # -- Bootstrap ----------------------------------------------------------

    def test_initial_bootstrap_requires_adopter_snapshot(self) -> None:
        units = [self.file_unit("u", "m", "s.txt", "d.txt")]
        catalog = self.catalog_bytes(units)
        accepted = self.make_upstream([{CATALOG: catalog, "s.txt": b"S\n"}])[0]
        declaration = self.declaration(
            [self.declared_unit("u", "adapted", [self.declared_member("m", "d.txt")])]
        )
        rev = self.prepare_adopter({"d.txt": b"S\n"}, declaration)
        self.assert_sync_error(m.ADOPTER_SNAPSHOT_UNAVAILABLE, self.propose, accepted, None, False, [])
        self.assert_sync_error(
            m.ADOPTER_SNAPSHOT_UNAVAILABLE, self.propose, accepted, rev, True, []
        )
        self.assert_sync_error(
            m.ADOPTER_SNAPSHOT_UNAVAILABLE, self.propose, accepted, "HEAD", False, []
        )

    def test_initial_bootstrap_requires_catalog_bearing_source(self) -> None:
        units = [self.file_unit("u", "m", "s.txt", "d.txt")]
        catalog = self.catalog_bytes(units)
        first, catalog_commit = self.make_upstream(
            [
                {"README.md": b"no catalog\n"},
                {"README.md": b"no catalog\n", CATALOG: catalog, "s.txt": b"S\n"},
            ]
        )
        declaration = self.declaration(
            [self.declared_unit("u", "adapted", [self.declared_member("m", "d.txt")])]
        )
        rev = self.prepare_adopter({"d.txt": b"S\n"}, declaration)
        self.assert_sync_error(
            m.CATALOG_CHANGED, self.propose, first, rev, False, []
        )
        # A catalog-bearing revision is still accepted.
        text = self.propose(catalog_commit, rev, False, [])
        self.assertIn("units:", text)

    # -- Management-tool boundary -------------------------------------------

    def test_catalog_excludes_management_tools(self) -> None:
        repo_root = Path(m.__file__).resolve().parents[4]
        catalog_path = repo_root / CATALOG
        catalog = m.parse_catalog(catalog_path.read_bytes(), str(catalog_path))
        ids = {unit.id for unit in catalog.units}
        self.assertNotIn("sync-aicore-adoption", ids)
        self.assertNotIn("migrate-core-to-project", ids)
        self.assertEqual(self.UPSTREAM_IDENTITY, catalog.upstream_repository)

    # -- Read-only guarantees and CLI surface -------------------------------

    def test_commands_write_nothing(self) -> None:
        units = [self.file_unit("mirror-file", "main", "content.txt", "mirror/content.txt")]
        catalog = self.catalog_bytes(units)
        accepted = self.make_upstream(
            [{CATALOG: catalog, "content.txt": b"hello\n"}]
        )[0]
        declaration = self.declaration(
            [
                self.declared_unit(
                    "mirror-file", "mirror", [self.declared_member("main", "mirror/content.txt")]
                )
            ]
        )
        rev = self.prepare_adopter({"mirror/content.txt": b"hello\n"}, declaration)

        implementation = Path(m.__file__).resolve()
        before_files = self.snapshot_adopter()
        before_status = self.git_status()

        propose_result = self.run_script(
            implementation,
            "propose-lock",
            "--upstream-repo",
            str(self.upstream),
            "--adopter-repo",
            str(self.adopter),
            "--current-revision",
            accepted,
            "--adopter-revision",
            rev,
        )
        self.assertEqual(0, propose_result.returncode)
        stdout = propose_result.stdout
        self.assertTrue(stdout.endswith(b"\n"))
        self.assertFalse(stdout.endswith(b"\n\n"))
        self.assertEqual(before_files, self.snapshot_adopter())
        self.assertEqual(before_status, self.git_status())

        self.write_at(self.lock_path, stdout)
        self.commit_adopter()
        before_check_files = self.snapshot_adopter()
        before_check_status = self.git_status()

        check_result = self.run_script(
            implementation,
            "check",
            "--upstream-repo",
            str(self.upstream),
            "--adopter-repo",
            str(self.adopter),
            "--current-revision",
            accepted,
            "--adopter-revision",
            rev,
        )
        self.assertEqual(0, check_result.returncode)
        self.assertEqual(before_check_files, self.snapshot_adopter())
        self.assertEqual(before_check_status, self.git_status())

    def test_cli_surface(self) -> None:
        implementation = Path(m.__file__).resolve()
        top_help = self.run_script(implementation, "--help")
        text = top_help.stdout.decode("utf-8")
        self.assertIn("check", text)
        self.assertIn("propose-lock", text)
        for forbidden in ("apply", "copy", "merge", "delete"):
            self.assertNotIn(forbidden, text.lower())

        check_help = self.run_script(implementation, "check", "--help")
        check_text = check_help.stdout.decode("utf-8")
        self.assertIn("--format", check_text)
        self.assertIn("--adopter-revision", check_text)
        self.assertIn("--adopter-index", check_text)

        propose_help = self.run_script(implementation, "propose-lock", "--help")
        propose_text = propose_help.stdout.decode("utf-8")
        self.assertIn("--unit", propose_text)
        self.assertNotIn("--format", propose_text)


if __name__ == "__main__":
    unittest.main()
