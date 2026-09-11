"""Hermetic stdlib-``unittest`` tests for the sync-aicore-adoption checker.

Every test builds its own temporary upstream Git repository and adopter tree and
never reads the real AICore repository, any checked-in fixture, or the network.
Tests assert exact protocol enum strings against the implementation by importing
the sibling module ``sync_aicore_adoption`` (running this file directly puts the
scripts directory on ``sys.path``).
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


class SyncAdoptionTestBase(unittest.TestCase):
    """Base case owning a temp dir, a hermetic upstream repo, and an adopter tree."""

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
        self.declaration_path = self.adopter / ".aicore" / "adoption.yaml"
        self.lock_path = self.adopter / ".aicore" / "adoption.lock.yaml"

    def commit_adopter(self) -> None:
        """Commit the current adopter worktree as a clean baseline."""

        self.run_git(self.adopter, "add", "-A")
        self.run_git(self.adopter, "commit", "--quiet", "-m", "adopter baseline")

    def write_at(self, path: Path, content: bytes) -> None:
        """Write bytes to a path, creating any missing parent directories."""

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    # -- Document builders --------------------------------------------------

    def catalog_bytes(self, units: list[dict[str, object]]) -> bytes:
        """Serialize a machine catalog with default exclusions and control paths."""

        document = {"schema_version": 1, "catalog": {}, "units": units}
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
        self, units: list[dict[str, object]], upstream: str = "owner/repo"
    ) -> dict[str, object]:
        """Build an adoption declaration document."""

        return {"schema_version": 1, "upstream_repository": upstream, "units": units}

    def declared_unit(
        self,
        unit_id: str,
        mode: str,
        members: list[dict[str, object]] | None = None,
        replacement_destinations: list[str] | None = None,
    ) -> dict[str, object]:
        """Build one declaration unit row."""

        unit: dict[str, object] = {"id": unit_id, "mode": mode}
        if members is not None:
            unit["members"] = members
        if replacement_destinations is not None:
            unit["replacement_destinations"] = replacement_destinations
        return unit

    def declared_member(self, member_id: str, destination: str) -> dict[str, object]:
        """Build one declaration member mapping."""

        return {"id": member_id, "destination": destination}

    def lock_document(
        self,
        accepted_commit: str,
        catalog_digest: str,
        units: list[dict[str, object]],
        upstream: str = "owner/repo",
    ) -> dict[str, object]:
        """Build a lock document without its declaration digest."""

        return {
            "schema_version": 1,
            "upstream_repository": upstream,
            "accepted_source_commit": accepted_commit,
            "catalog_digest": catalog_digest,
            "units": units,
        }

    def lock_member(
        self,
        member_id: str,
        destination: str,
        upstream_digest: str,
        destination_digest: str,
    ) -> dict[str, object]:
        """Build one lock member with accepted upstream and destination digests."""

        return {
            "id": member_id,
            "destination": destination,
            "accepted_upstream_digest": upstream_digest,
            "accepted_destination_digest": destination_digest,
        }

    def write_declaration(self, declaration: dict[str, object]) -> bytes:
        """Write the declaration and return its raw bytes."""

        raw = yaml.safe_dump(declaration, sort_keys=False).encode("utf-8")
        self.write_at(self.declaration_path, raw)
        return raw

    def write_lock(self, lock: dict[str, object]) -> bytes:
        """Write the lock document and return its raw bytes."""

        raw = yaml.safe_dump(lock, sort_keys=False).encode("utf-8")
        self.write_at(self.lock_path, raw)
        return raw

    def setup_adoption(
        self, declaration: dict[str, object], lock: dict[str, object]
    ) -> None:
        """Write the declaration then the lock bound to its raw digest."""

        declaration_raw = self.write_declaration(declaration)
        bound = dict(lock)
        bound["declaration_digest"] = m.sha256_digest(declaration_raw)
        self.write_lock(bound)

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

    def check(
        self,
        current_sha: str,
        declaration_path: Path | None = None,
        lock_path: Path | None = None,
    ) -> m.CheckReport:
        """Run ``check_adoption`` against the hermetic repos."""

        return m.check_adoption(
            self.upstream,
            self.adopter,
            current_sha,
            declaration_path if declaration_path is not None else self.declaration_path,
            lock_path if lock_path is not None else self.lock_path,
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
                {".aicore/core-catalog-v1.yaml": catalog, "content.txt": b"A\n"},
                {".aicore/core-catalog-v1.yaml": catalog, "content.txt": b"B\n"},
            ]
        )
        self.make_adopter()
        declaration = self.declaration(
            [
                self.declared_unit(
                    "mirror-file", "mirror", [self.declared_member("main", "mirror/content.txt")]
                )
            ]
        )
        lock = self.lock_document(
            accepted,
            m.sha256_digest(catalog),
            [
                {
                    "id": "mirror-file",
                    "mode": "mirror",
                    "members": [
                        self.lock_member(
                            "main",
                            "mirror/content.txt",
                            self.file_digest(b"A\n"),
                            self.file_digest(b"A\n"),
                        )
                    ],
                }
            ],
        )
        self.setup_adoption(declaration, lock)
        target = self.adopter / "mirror" / "content.txt"

        self.write_at(target, b"A\n")
        unit = self.find_unit(self.check(accepted), "mirror-file")
        self.assertEqual("mirror", unit.mode)
        self.assertEqual("unchanged", unit.upstream_delta)
        self.assertEqual("unchanged", unit.destination_delta)
        self.assertEqual("current", unit.disposition)

        self.write_at(target, b"A\n")
        unit = self.find_unit(self.check(modified), "mirror-file")
        self.assertEqual("modified", unit.upstream_delta)
        self.assertEqual("unchanged", unit.destination_delta)
        self.assertEqual("update_available", unit.disposition)

        self.write_at(target, b"B\n")
        unit = self.find_unit(self.check(accepted), "mirror-file")
        self.assertEqual("unchanged", unit.upstream_delta)
        self.assertEqual("modified", unit.destination_delta)
        self.assertEqual("local_drift", unit.disposition)

        self.write_at(target, b"C\n")
        unit = self.find_unit(self.check(modified), "mirror-file")
        self.assertEqual("modified", unit.upstream_delta)
        self.assertEqual("modified", unit.destination_delta)
        self.assertEqual("conflict", unit.disposition)

    def test_mirror_tree_dispositions(self) -> None:
        units = [self.tree_unit("mirror-tree", "tree", "templates", "mirror/templates")]
        catalog = self.catalog_bytes(units)
        accepted, modified = self.make_upstream(
            [
                {
                    ".aicore/core-catalog-v1.yaml": catalog,
                    "templates/a.txt": b"alpha\n",
                    "templates/sub/b.txt": b"beta\n",
                },
                {
                    ".aicore/core-catalog-v1.yaml": catalog,
                    "templates/a.txt": b"ALPHA\n",
                    "templates/sub/b.txt": b"beta\n",
                },
            ]
        )
        self.make_adopter()
        declaration = self.declaration(
            [
                self.declared_unit(
                    "mirror-tree", "mirror", [self.declared_member("tree", "mirror/templates")]
                )
            ]
        )
        accepted_digest = self.tree_digest(
            [("a.txt", "100644", b"alpha\n"), ("sub/b.txt", "100644", b"beta\n")]
        )
        lock = self.lock_document(
            accepted,
            m.sha256_digest(catalog),
            [
                {
                    "id": "mirror-tree",
                    "mode": "mirror",
                    "members": [
                        self.lock_member(
                            "tree", "mirror/templates", accepted_digest, accepted_digest
                        )
                    ],
                }
            ],
        )
        self.setup_adoption(declaration, lock)
        tree = self.adopter / "mirror" / "templates"

        def write_tree(a_content: bytes) -> None:
            if tree.exists():
                shutil.rmtree(tree)
            (tree / "sub").mkdir(parents=True)
            self.write_at(tree / "a.txt", a_content)
            self.write_at(tree / "sub" / "b.txt", b"beta\n")

        write_tree(b"alpha\n")
        unit = self.find_unit(self.check(accepted), "mirror-tree")
        self.assertEqual("unchanged", unit.upstream_delta)
        self.assertEqual("unchanged", unit.destination_delta)
        self.assertEqual("current", unit.disposition)

        write_tree(b"alpha\n")
        unit = self.find_unit(self.check(modified), "mirror-tree")
        self.assertEqual("modified", unit.upstream_delta)
        self.assertEqual("unchanged", unit.destination_delta)
        self.assertEqual("update_available", unit.disposition)

        write_tree(b"beta\n")
        unit = self.find_unit(self.check(accepted), "mirror-tree")
        self.assertEqual("unchanged", unit.upstream_delta)
        self.assertEqual("modified", unit.destination_delta)
        self.assertEqual("local_drift", unit.disposition)

        write_tree(b"gamma\n")
        unit = self.find_unit(self.check(modified), "mirror-tree")
        self.assertEqual("modified", unit.upstream_delta)
        self.assertEqual("modified", unit.destination_delta)
        self.assertEqual("conflict", unit.disposition)

    # -- Rejected mirror mismatch -------------------------------------------

    def test_rejected_mirror_mismatch(self) -> None:
        units = [self.file_unit("mirror-file", "main", "content.txt", "mirror/content.txt")]
        catalog = self.catalog_bytes(units)
        accepted = self.make_upstream(
            [{".aicore/core-catalog-v1.yaml": catalog, "content.txt": b"A\n"}]
        )[0]
        self.make_adopter()
        declaration = self.declaration(
            [
                self.declared_unit(
                    "mirror-file", "mirror", [self.declared_member("main", "mirror/content.txt")]
                )
            ]
        )
        self.write_at(self.adopter / "mirror" / "content.txt", b"A\n")
        lock = self.lock_document(
            accepted,
            m.sha256_digest(catalog),
            [
                {
                    "id": "mirror-file",
                    "mode": "mirror",
                    "members": [
                        self.lock_member(
                            "main",
                            "mirror/content.txt",
                            self.file_digest(b"A\n"),
                            self.file_digest(b"DIFFERENT\n"),
                        )
                    ],
                }
            ],
        )
        self.setup_adoption(declaration, lock)
        self.assert_sync_error(m.INVALID_LOCK, self.check, accepted)

        self.write_at(self.adopter / "mirror" / "content.txt", b"DIFFERENT\n")
        self.assert_sync_error(
            m.INVALID_LOCK,
            m.propose_lock,
            self.upstream,
            self.adopter,
            accepted,
            self.declaration_path,
        )

    # -- Renamed adapted root -----------------------------------------------

    def test_renamed_adapted_root_convergence(self) -> None:
        units = [self.file_unit("root-runtime-spec", "root", "AGENTS.md", "AGENTS.md")]
        catalog = self.catalog_bytes(units)
        accepted, modified = self.make_upstream(
            [
                {".aicore/core-catalog-v1.yaml": catalog, "AGENTS.md": b"V1\n"},
                {".aicore/core-catalog-v1.yaml": catalog, "AGENTS.md": b"V2\n"},
            ]
        )
        self.make_adopter()
        declaration = self.declaration(
            [
                self.declared_unit(
                    "root-runtime-spec", "adapted", [self.declared_member("root", "BASE-RULES.md")]
                )
            ]
        )
        lock = self.lock_document(
            accepted,
            m.sha256_digest(catalog),
            [
                {
                    "id": "root-runtime-spec",
                    "mode": "adapted",
                    "members": [
                        self.lock_member(
                            "root",
                            "BASE-RULES.md",
                            self.file_digest(b"V1\n"),
                            self.file_digest(b"V1\n"),
                        )
                    ],
                }
            ],
        )
        self.setup_adoption(declaration, lock)
        target = self.adopter / "BASE-RULES.md"

        self.write_at(target, b"V1\n")
        unit = self.find_unit(self.check(accepted), "root-runtime-spec")
        self.assertEqual("adapted", unit.mode)
        self.assertEqual("unchanged", unit.upstream_delta)
        self.assertEqual("unchanged", unit.destination_delta)
        self.assertEqual("current", unit.disposition)

        self.write_at(target, b"V1\n")
        unit = self.find_unit(self.check(modified), "root-runtime-spec")
        self.assertEqual("modified", unit.upstream_delta)
        self.assertEqual("unchanged", unit.destination_delta)
        self.assertEqual("update_available", unit.disposition)

        self.write_at(target, b"LOCAL\n")
        unit = self.find_unit(self.check(accepted), "root-runtime-spec")
        self.assertEqual("unchanged", unit.upstream_delta)
        self.assertEqual("modified", unit.destination_delta)
        self.assertEqual("local_drift", unit.disposition)

        self.write_at(target, b"LOCAL\n")
        unit = self.find_unit(self.check(modified), "root-runtime-spec")
        self.assertEqual("modified", unit.upstream_delta)
        self.assertEqual("modified", unit.destination_delta)
        self.assertEqual("review_required", unit.disposition)

    # -- Split-role replacement ---------------------------------------------

    def test_split_role_replacement(self) -> None:
        units = [self.tree_unit("skill-doc", "tree", "skill", "skill")]
        catalog = self.catalog_bytes(units)
        accepted = self.make_upstream(
            [{".aicore/core-catalog-v1.yaml": catalog, "skill/a.md": b"A\n"}]
        )[0]
        self.make_adopter()
        declaration = self.declaration(
            [
                {
                    "id": "skill-doc",
                    "mode": "replacement",
                    "replacement_destinations": ["local/a.md", "local/b.md"],
                }
            ]
        )
        skill_digest = self.tree_digest([("a.md", "100644", b"A\n")])
        lock = self.lock_document(
            accepted,
            m.sha256_digest(catalog),
            [
                {
                    "id": "skill-doc",
                    "mode": "replacement",
                    "replacement_destinations": ["local/a.md", "local/b.md"],
                    "accepted_upstream_digest": skill_digest,
                    "accepted_destination_digest": "not_applicable",
                }
            ],
        )
        self.setup_adoption(declaration, lock)
        (self.adopter / "local").mkdir(parents=True)
        self.write_at(self.adopter / "local" / "a.md", b"A\n")
        self.write_at(self.adopter / "local" / "b.md", b"B\n")

        unit = self.find_unit(self.check(accepted), "skill-doc")
        self.assertEqual("replacement", unit.mode)
        self.assertEqual("not_applicable", unit.destination_delta)
        self.assertEqual("review_required", unit.disposition)
        self.assertEqual(("local/a.md", "local/b.md"), unit.replacement_destinations)

    # -- Destination-owned units --------------------------------------------

    def test_destination_owned_unmanaged_and_retirement(self) -> None:
        local_unit = self.file_unit("local-config", "main", "upstream.cfg", "local/config.cfg")
        base_unit = self.file_unit("mirror-base", "main", "base.txt", "mirror/base.txt")
        catalog0 = self.catalog_bytes([local_unit, base_unit])
        catalog1 = self.catalog_bytes([base_unit])
        accepted, retired = self.make_upstream(
            [
                {".aicore/core-catalog-v1.yaml": catalog0, "upstream.cfg": b"CFG\n", "base.txt": b"BASE\n"},
                {".aicore/core-catalog-v1.yaml": catalog1, "base.txt": b"BASE\n"},
            ]
        )
        self.make_adopter()
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
        lock = self.lock_document(
            accepted,
            m.sha256_digest(catalog0),
            [
                {
                    "id": "local-config",
                    "mode": "destination_owned",
                    "members": [
                        self.lock_member(
                            "main",
                            "local/config.cfg",
                            self.file_digest(b"CFG\n"),
                            self.file_digest(b"CFG\n"),
                        )
                    ],
                },
                {
                    "id": "mirror-base",
                    "mode": "mirror",
                    "members": [
                        self.lock_member(
                            "main",
                            "mirror/base.txt",
                            self.file_digest(b"BASE\n"),
                            self.file_digest(b"BASE\n"),
                        )
                    ],
                },
            ],
        )
        self.setup_adoption(declaration, lock)
        (self.adopter / "local").mkdir(parents=True)
        self.write_at(self.adopter / "local" / "config.cfg", b"CFG\n")
        (self.adopter / "mirror").mkdir(parents=True)
        self.write_at(self.adopter / "mirror" / "base.txt", b"BASE\n")

        unit = self.find_unit(self.check(accepted), "local-config")
        self.assertEqual("destination_owned", unit.mode)
        self.assertEqual("unmanaged", unit.disposition)

        unit = self.find_unit(self.check(retired), "local-config")
        self.assertEqual("removed", unit.upstream_delta)
        self.assertEqual("retirement_available", unit.disposition)

    def test_destination_owned_unknown_unit_rejected(self) -> None:
        units = [self.file_unit("known", "main", "known.txt", "known.txt")]
        catalog = self.catalog_bytes(units)
        accepted = self.make_upstream(
            [{".aicore/core-catalog-v1.yaml": catalog, "known.txt": b"K\n"}]
        )[0]
        self.make_adopter()
        declaration = self.declaration(
            [
                self.declared_unit(
                    "unknown-unit", "destination_owned", [self.declared_member("main", "local/x")]
                )
            ]
        )
        declaration_raw = self.write_declaration(declaration)
        lock = self.lock_document(accepted, m.sha256_digest(catalog), [])
        lock["declaration_digest"] = m.sha256_digest(declaration_raw)
        self.write_lock(lock)
        self.assert_sync_error(m.INVALID_MAPPING, self.check, accepted)

    def test_destination_owned_none_projection_rejected(self) -> None:
        none_unit = {
            "id": "installer-only",
            "sync_projection": "none",
            "members": [{"id": "main", "source": "install.sh", "destination": "install.sh"}],
        }
        catalog = self.catalog_bytes([none_unit])
        accepted = self.make_upstream(
            [{".aicore/core-catalog-v1.yaml": catalog, "install.sh": b"echo\n"}]
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
        declaration_raw = self.write_declaration(declaration)
        lock = self.lock_document(accepted, m.sha256_digest(catalog), [])
        lock["declaration_digest"] = m.sha256_digest(declaration_raw)
        self.write_lock(lock)
        self.assert_sync_error(m.UNSUPPORTED_PROJECTION, self.check, accepted)

    # -- Undeclared upstream addition ---------------------------------------

    def test_undeclared_upstream_addition(self) -> None:
        base = self.file_unit("base", "main", "base.txt", "base.txt")
        new = self.file_unit("new-unit", "main", "new.txt", "new.txt")
        catalog0 = self.catalog_bytes([base])
        catalog1 = self.catalog_bytes([base, new])
        accepted, current = self.make_upstream(
            [
                {".aicore/core-catalog-v1.yaml": catalog0, "base.txt": b"BASE\n"},
                {
                    ".aicore/core-catalog-v1.yaml": catalog1,
                    "base.txt": b"BASE\n",
                    "new.txt": b"NEW\n",
                },
            ]
        )
        self.make_adopter()
        declaration = self.declaration([])
        declaration_raw = self.write_declaration(declaration)
        lock = self.lock_document(accepted, m.sha256_digest(catalog0), [])
        lock["declaration_digest"] = m.sha256_digest(declaration_raw)
        self.write_lock(lock)

        report = self.check(current)
        self.assertEqual("ok", report.status)
        unit = self.find_unit(report, "new-unit")
        self.assertEqual("not_declared", unit.mode)
        self.assertEqual("added", unit.upstream_delta)
        self.assertEqual("not_applicable", unit.destination_delta)
        self.assertEqual("adoption_available", unit.disposition)

    # -- Upstream unit additions and removals -------------------------------

    def test_upstream_unit_addition_mirror(self) -> None:
        base = self.file_unit("base", "main", "base.txt", "base.txt")
        added = self.file_unit("added", "main", "added.txt", "added.txt")
        catalog0 = self.catalog_bytes([base])
        catalog1 = self.catalog_bytes([base, added])
        accepted, current = self.make_upstream(
            [
                {".aicore/core-catalog-v1.yaml": catalog0, "base.txt": b"B\n"},
                {
                    ".aicore/core-catalog-v1.yaml": catalog1,
                    "base.txt": b"B\n",
                    "added.txt": b"NEW\n",
                },
            ]
        )
        self.make_adopter()
        declaration = self.declaration(
            [
                self.declared_unit(
                    "added", "mirror", [self.declared_member("main", "added.txt")]
                )
            ]
        )
        lock = self.lock_document(
            accepted,
            m.sha256_digest(catalog0),
            [
                {
                    "id": "added",
                    "mode": "mirror",
                    "members": [
                        self.lock_member(
                            "main",
                            "added.txt",
                            self.file_digest(b"NEW\n"),
                            self.file_digest(b"NEW\n"),
                        )
                    ],
                }
            ],
        )
        self.setup_adoption(declaration, lock)
        self.write_at(self.adopter / "added.txt", b"NEW\n")

        unit = self.find_unit(self.check(current), "added")
        self.assertEqual("mirror", unit.mode)
        self.assertEqual("added", unit.upstream_delta)
        self.assertEqual("unchanged", unit.destination_delta)
        self.assertEqual("update_available", unit.disposition)

    def test_upstream_unit_removal_adapted(self) -> None:
        base = self.file_unit("base", "main", "base.txt", "base.txt")
        removed = self.file_unit("removed", "main", "removed.txt", "removed.txt")
        catalog0 = self.catalog_bytes([base, removed])
        catalog1 = self.catalog_bytes([base])
        accepted, current = self.make_upstream(
            [
                {
                    ".aicore/core-catalog-v1.yaml": catalog0,
                    "base.txt": b"B\n",
                    "removed.txt": b"R\n",
                },
                {".aicore/core-catalog-v1.yaml": catalog1, "base.txt": b"B\n"},
            ]
        )
        self.make_adopter()
        declaration = self.declaration(
            [
                self.declared_unit(
                    "removed", "adapted", [self.declared_member("main", "removed.txt")]
                )
            ]
        )
        lock = self.lock_document(
            accepted,
            m.sha256_digest(catalog0),
            [
                {
                    "id": "removed",
                    "mode": "adapted",
                    "members": [
                        self.lock_member(
                            "main",
                            "removed.txt",
                            self.file_digest(b"R\n"),
                            self.file_digest(b"R\n"),
                        )
                    ],
                }
            ],
        )
        self.setup_adoption(declaration, lock)
        self.write_at(self.adopter / "removed.txt", b"R\n")

        unit = self.find_unit(self.check(current), "removed")
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
                    ".aicore/core-catalog-v1.yaml": catalog,
                    "m.txt": b"M\n",
                    "a.txt": b"A\n",
                }
            ]
        )[0]
        self.make_adopter()
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
        lock = self.lock_document(
            accepted,
            m.sha256_digest(catalog),
            [
                {
                    "id": "mirror-u",
                    "mode": "mirror",
                    "members": [
                        self.lock_member(
                            "m", "mirror/m.txt", self.file_digest(b"M\n"), self.file_digest(b"M\n")
                        )
                    ],
                },
                {
                    "id": "adapted-u",
                    "mode": "adapted",
                    "members": [
                        self.lock_member(
                            "m",
                            "adapted/a.txt",
                            self.file_digest(b"A\n"),
                            self.file_digest(b"A\n"),
                        )
                    ],
                },
            ],
        )
        self.setup_adoption(declaration, lock)
        report = self.check(accepted)

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
                {".aicore/core-catalog-v1.yaml": catalog, "AGENTS.md": b"UP1\n"},
                {".aicore/core-catalog-v1.yaml": catalog, "AGENTS.md": b"UP2\n"},
            ]
        )
        self.make_adopter()
        declaration = self.declaration(
            [
                self.declared_unit(
                    "root-runtime-spec", "adapted", [self.declared_member("root", "LOCAL.md")]
                )
            ]
        )
        lock = self.lock_document(
            accepted,
            m.sha256_digest(catalog),
            [
                {
                    "id": "root-runtime-spec",
                    "mode": "adapted",
                    "members": [
                        self.lock_member(
                            "root",
                            "LOCAL.md",
                            self.file_digest(b"UP1\n"),
                            self.file_digest(b"UP2\n"),
                        )
                    ],
                }
            ],
        )
        self.setup_adoption(declaration, lock)
        self.write_at(self.adopter / "LOCAL.md", b"UP2\n")

        unit = self.find_unit(self.check(current), "root-runtime-spec")
        self.assertEqual("modified", unit.upstream_delta)
        self.assertEqual("unchanged", unit.destination_delta)
        self.assertEqual("update_available", unit.disposition)
        self.assertNotEqual("conflict", unit.disposition)
        member = unit.members[0]
        self.assertEqual(member.current_upstream_digest, member.current_destination_digest)

    # -- Catalog and declaration change detection ---------------------------

    def test_changed_catalogs_reconcile_by_id(self) -> None:
        unit_u1 = self.file_unit("u1", "m1", "u1.txt", "u1.txt")
        unit_u2 = self.file_unit("u2", "m2", "u2.txt", "u2.txt")
        unit_u3 = self.file_unit("u3", "m3", "u3.txt", "u3.txt")
        catalog0 = self.catalog_bytes([unit_u1, unit_u3])
        catalog1 = self.catalog_bytes([unit_u1, unit_u2])
        accepted, current = self.make_upstream(
            [
                {
                    ".aicore/core-catalog-v1.yaml": catalog0,
                    "u1.txt": b"U1\n",
                    "u3.txt": b"U3\n",
                },
                {
                    ".aicore/core-catalog-v1.yaml": catalog1,
                    "u1.txt": b"U1\n",
                    "u2.txt": b"U2\n",
                },
            ]
        )
        self.make_adopter()
        declaration = self.declaration(
            [self.declared_unit("u1", "mirror", [self.declared_member("m1", "u1.txt")])]
        )
        lock = self.lock_document(
            accepted,
            m.sha256_digest(catalog0),
            [
                {
                    "id": "u1",
                    "mode": "mirror",
                    "members": [
                        self.lock_member(
                            "m1", "u1.txt", self.file_digest(b"U1\n"), self.file_digest(b"U1\n")
                        )
                    ],
                }
            ],
        )
        self.setup_adoption(declaration, lock)
        self.write_at(self.adopter / "u1.txt", b"U1\n")

        report = self.check(current)
        self.assertEqual("ok", report.status)
        self.assertEqual("unchanged", self.find_unit(report, "u1").upstream_delta)

        added = self.find_unit(report, "u2")
        self.assertEqual("not_declared", added.mode)
        self.assertEqual("added", added.upstream_delta)
        self.assertEqual("adoption_available", added.disposition)

        removed = self.find_unit(report, "u3")
        self.assertEqual("not_declared", removed.mode)
        self.assertEqual("removed", removed.upstream_delta)
        self.assertEqual("retirement_available", removed.disposition)

    def test_changed_declaration_detected(self) -> None:
        units = [self.file_unit("u", "m", "s.txt", "d.txt")]
        catalog = self.catalog_bytes(units)
        accepted = self.make_upstream(
            [{".aicore/core-catalog-v1.yaml": catalog, "s.txt": b"S\n"}]
        )[0]
        self.make_adopter()
        declaration = self.declaration(
            [self.declared_unit("u", "adapted", [self.declared_member("m", "d.txt")])]
        )
        self.write_at(self.adopter / "d.txt", b"S\n")
        self.write_declaration(declaration)
        lock = self.lock_document(
            accepted,
            m.sha256_digest(catalog),
            [
                {
                    "id": "u",
                    "mode": "adapted",
                    "members": [
                        self.lock_member(
                            "m", "d.txt", self.file_digest(b"S\n"), self.file_digest(b"S\n")
                        )
                    ],
                }
            ],
        )
        lock["declaration_digest"] = m.sha256_digest(b"a different declaration")
        self.write_lock(lock)
        self.assert_sync_error(m.DECLARATION_CHANGED, self.check, accepted)

    # -- Line-ending sensitivity --------------------------------------------

    def test_line_ending_only_drift(self) -> None:
        units = [self.file_unit("mirror-file", "main", "content.txt", "mirror/content.txt")]
        catalog = self.catalog_bytes(units)
        accepted = self.make_upstream(
            [{".aicore/core-catalog-v1.yaml": catalog, "content.txt": b"line\n"}]
        )[0]
        self.make_adopter()
        declaration = self.declaration(
            [
                self.declared_unit(
                    "mirror-file", "mirror", [self.declared_member("main", "mirror/content.txt")]
                )
            ]
        )
        lock = self.lock_document(
            accepted,
            m.sha256_digest(catalog),
            [
                {
                    "id": "mirror-file",
                    "mode": "mirror",
                    "members": [
                        self.lock_member(
                            "main",
                            "mirror/content.txt",
                            self.file_digest(b"line\n"),
                            self.file_digest(b"line\n"),
                        )
                    ],
                }
            ],
        )
        self.setup_adoption(declaration, lock)
        self.write_at(self.adopter / "mirror" / "content.txt", b"line\r\n")

        unit = self.find_unit(self.check(accepted), "mirror-file")
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
                "catalog": {},
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
                "catalog": {},
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
        missing_commit = yaml.safe_dump(
            {
                "schema_version": 1,
                "upstream_repository": "o/r",
                "catalog_digest": digest,
                "declaration_digest": digest,
                "units": [],
            },
            sort_keys=False,
        ).encode("utf-8")
        self.assert_sync_error(m.INVALID_LOCK, m.parse_lock, missing_commit, "lock")
        wrong_mode = yaml.safe_dump(
            {
                "schema_version": 1,
                "upstream_repository": "o/r",
                "accepted_source_commit": "a" * 40,
                "catalog_digest": digest,
                "declaration_digest": digest,
                "units": [
                    {
                        "id": "u",
                        "mode": "bogus",
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

    # -- Missing catalog sources --------------------------------------------

    def test_missing_catalog_source_is_catalog_changed(self) -> None:
        units = [self.file_unit("missing", "main", "does-not-exist.txt", "local/missing.txt")]
        catalog = self.catalog_bytes(units)
        accepted, current = self.make_upstream(
            [
                {".aicore/core-catalog-v1.yaml": catalog, "unused.txt": b"1"},
                {".aicore/core-catalog-v1.yaml": catalog, "unused.txt": b"2"},
            ]
        )
        self.make_adopter()
        declaration = self.declaration(
            [
                self.declared_unit(
                    "missing", "adapted", [self.declared_member("main", "local/missing.txt")]
                )
            ]
        )
        lock = self.lock_document(
            accepted,
            m.sha256_digest(catalog),
            [
                {
                    "id": "missing",
                    "mode": "adapted",
                    "members": [
                        self.lock_member(
                            "main",
                            "local/missing.txt",
                            self.file_digest(b"x"),
                            self.file_digest(b"y"),
                        )
                    ],
                }
            ],
        )
        self.setup_adoption(declaration, lock)
        self.write_at(self.adopter / "local" / "missing.txt", b"y")
        self.assert_sync_error(m.CATALOG_CHANGED, self.check, current)

    # -- Baseline resolution failures ---------------------------------------

    def test_unknown_accepted_commit_is_baseline_unavailable(self) -> None:
        units = [self.file_unit("u", "m", "s.txt", "d.txt")]
        catalog = self.catalog_bytes(units)
        accepted = self.make_upstream(
            [{".aicore/core-catalog-v1.yaml": catalog, "s.txt": b"S\n"}]
        )[0]
        self.make_adopter()
        declaration = self.declaration(
            [self.declared_unit("u", "adapted", [self.declared_member("m", "d.txt")])]
        )
        self.write_at(self.adopter / "d.txt", b"S\n")
        lock = self.lock_document(
            "0" * 40,
            m.sha256_digest(catalog),
            [
                {
                    "id": "u",
                    "mode": "adapted",
                    "members": [
                        self.lock_member(
                            "m", "d.txt", self.file_digest(b"S\n"), self.file_digest(b"S\n")
                        )
                    ],
                }
            ],
        )
        self.setup_adoption(declaration, lock)
        self.assert_sync_error(m.BASELINE_UNAVAILABLE, self.check, accepted)

    def test_non_ancestor_accepted_commit_is_baseline_unavailable(self) -> None:
        units = [self.file_unit("u", "m", "s.txt", "d.txt")]
        catalog = self.catalog_bytes(units)
        first = self.make_upstream(
            [{".aicore/core-catalog-v1.yaml": catalog, "s.txt": b"S\n"}]
        )[0]
        self.run_git(self.upstream, "checkout", "--orphan", "orphan")
        self.write_snapshot(self.upstream, {".aicore/core-catalog-v1.yaml": catalog, "s.txt": b"S\n"})
        self.run_git(self.upstream, "add", "-A")
        self.run_git(self.upstream, "commit", "--quiet", "-m", "orphan")
        orphan = self.rev_head(self.upstream)

        self.make_adopter()
        declaration = self.declaration(
            [self.declared_unit("u", "adapted", [self.declared_member("m", "d.txt")])]
        )
        self.write_at(self.adopter / "d.txt", b"S\n")
        lock = self.lock_document(
            first,
            m.sha256_digest(catalog),
            [
                {
                    "id": "u",
                    "mode": "adapted",
                    "members": [
                        self.lock_member(
                            "m", "d.txt", self.file_digest(b"S\n"), self.file_digest(b"S\n")
                        )
                    ],
                }
            ],
        )
        self.setup_adoption(declaration, lock)
        self.assert_sync_error(m.BASELINE_UNAVAILABLE, self.check, orphan)

    # -- Excluded bytecode --------------------------------------------------

    def test_excluded_bytecode_paths_are_ignored(self) -> None:
        units = [self.tree_unit("mirror-tree", "tree", "templates", "mirror/templates")]
        catalog = self.catalog_bytes(units)
        base_files: dict[str, bytes] = {
            ".aicore/core-catalog-v1.yaml": catalog,
            "templates/a.txt": b"alpha\n",
        }
        commit0, commit1, commit2 = self.make_upstream(
            [
                dict(base_files),
                {**base_files, "templates/__pycache__/x.pyc": b"v1"},
                {**base_files, "templates/__pycache__/x.pyc": b"v2"},
            ]
        )
        self.make_adopter()
        declaration = self.declaration(
            [
                self.declared_unit(
                    "mirror-tree", "mirror", [self.declared_member("tree", "mirror/templates")]
                )
            ]
        )
        accepted_digest = self.tree_digest([("a.txt", "100644", b"alpha\n")])
        lock = self.lock_document(
            commit0,
            m.sha256_digest(catalog),
            [
                {
                    "id": "mirror-tree",
                    "mode": "mirror",
                    "members": [
                        self.lock_member(
                            "tree", "mirror/templates", accepted_digest, accepted_digest
                        )
                    ],
                }
            ],
        )
        self.setup_adoption(declaration, lock)
        tree = self.adopter / "mirror" / "templates"
        self.write_at(tree / "a.txt", b"alpha\n")

        unit1 = self.find_unit(self.check(commit1), "mirror-tree")
        self.assertEqual("unchanged", unit1.upstream_delta)
        self.assertEqual("unchanged", unit1.destination_delta)

        self.write_at(tree / "__pycache__" / "y.pyc", b"local")
        unit2 = self.find_unit(self.check(commit2), "mirror-tree")
        self.assertEqual("unchanged", unit2.upstream_delta)
        self.assertEqual("unchanged", unit2.destination_delta)
        self.assertEqual(
            unit1.members[0].current_upstream_digest, unit2.members[0].current_upstream_digest
        )
        self.assertEqual(
            unit1.members[0].current_destination_digest,
            unit2.members[0].current_destination_digest,
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
        accepted = self.make_upstream(
            [{".aicore/core-catalog-v1.yaml": catalog, "s.txt": b"S\n"}]
        )[0]
        self.make_adopter()
        declaration = self.declaration(
            [self.declared_unit("u", "adapted", [self.declared_member("m", ".git/config")])]
        )
        declaration_raw = self.write_declaration(declaration)
        lock = self.lock_document(accepted, m.sha256_digest(catalog), [])
        lock["declaration_digest"] = m.sha256_digest(declaration_raw)
        self.write_lock(lock)
        self.assert_sync_error(m.INVALID_MAPPING, self.check, accepted)

    # -- Read-only guarantees and CLI surface -------------------------------

    def test_commands_write_nothing(self) -> None:
        units = [self.file_unit("mirror-file", "main", "content.txt", "mirror/content.txt")]
        catalog = self.catalog_bytes(units)
        accepted = self.make_upstream(
            [{".aicore/core-catalog-v1.yaml": catalog, "content.txt": b"hello\n"}]
        )[0]
        self.make_adopter()
        declaration = self.declaration(
            [
                self.declared_unit(
                    "mirror-file", "mirror", [self.declared_member("main", "mirror/content.txt")]
                )
            ]
        )
        self.write_at(self.adopter / "mirror" / "content.txt", b"hello\n")
        digest = self.file_digest(b"hello\n")
        lock = self.lock_document(
            accepted,
            m.sha256_digest(catalog),
            [
                {
                    "id": "mirror-file",
                    "mode": "mirror",
                    "members": [self.lock_member("main", "mirror/content.txt", digest, digest)],
                }
            ],
        )
        self.setup_adoption(declaration, lock)
        self.commit_adopter()

        implementation = Path(m.__file__).resolve()
        before_files = self.snapshot_adopter()
        before_status = self.git_status()

        check_result = self.run_script(
            implementation,
            "check",
            "--upstream-repo",
            str(self.upstream),
            "--adopter-repo",
            str(self.adopter),
            "--current-revision",
            accepted,
        )
        self.assertEqual(0, check_result.returncode)
        self.assertEqual(before_files, self.snapshot_adopter())
        self.assertEqual(before_status, self.git_status())

        propose_result = self.run_script(
            implementation,
            "propose-lock",
            "--upstream-repo",
            str(self.upstream),
            "--adopter-repo",
            str(self.adopter),
            "--current-revision",
            accepted,
        )
        self.assertEqual(0, propose_result.returncode)
        stdout = propose_result.stdout
        self.assertTrue(stdout.endswith(b"\n"))
        self.assertFalse(stdout.endswith(b"\n\n"))
        self.assertEqual(stdout.count(b"\n"), stdout.rstrip(b"\n").count(b"\n") + 1)
        parsed = yaml.safe_load(stdout.decode("utf-8"))
        self.assertEqual(1, parsed["schema_version"])
        self.assertEqual(accepted, parsed["accepted_source_commit"])
        self.assertEqual(before_files, self.snapshot_adopter())
        self.assertEqual(before_status, self.git_status())

    def test_cli_surface(self) -> None:
        implementation = Path(m.__file__).resolve()
        top_help = self.run_script(implementation, "--help")
        text = top_help.stdout.decode("utf-8")
        self.assertIn("check", text)
        self.assertIn("propose-lock", text)
        for forbidden in ("apply", "copy", "merge", "delete"):
            self.assertNotIn(forbidden, text.lower())

        check_help = self.run_script(implementation, "check", "--help")
        self.assertIn("--format", check_help.stdout.decode("utf-8"))

        propose_help = self.run_script(implementation, "propose-lock", "--help")
        self.assertNotIn("--format", propose_help.stdout.decode("utf-8"))

    # -- Symlink, baseline advance, special files, catalog binding ----------

    def test_symlink_root_escape_rejected(self) -> None:
        units = [self.file_unit("u", "m", "s.txt", "escape/file.txt")]
        catalog = self.catalog_bytes(units)
        accepted = self.make_upstream(
            [{".aicore/core-catalog-v1.yaml": catalog, "s.txt": b"S\n"}]
        )[0]
        self.make_adopter()
        outside = self.root / "outside"
        outside.mkdir()
        os.symlink(outside, self.adopter / "escape")

        declaration = self.declaration(
            [self.declared_unit("u", "adapted", [self.declared_member("m", "escape/file.txt")])]
        )
        declaration_raw = self.write_declaration(declaration)
        lock = self.lock_document(
            accepted,
            m.sha256_digest(catalog),
            [
                {
                    "id": "u",
                    "mode": "adapted",
                    "members": [
                        self.lock_member(
                            "m",
                            "escape/file.txt",
                            self.file_digest(b"S\n"),
                            self.file_digest(b"S\n"),
                        )
                    ],
                }
            ],
        )
        lock["declaration_digest"] = m.sha256_digest(declaration_raw)
        self.write_lock(lock)

        self.assert_sync_error(m.INVALID_MAPPING, self.check, accepted)
        self.assert_sync_error(
            m.INVALID_MAPPING,
            m.propose_lock,
            self.upstream,
            self.adopter,
            accepted,
            self.declaration_path,
        )

    def test_baseline_advance_required_when_commit_advances(self) -> None:
        units = [self.file_unit("mirror-file", "main", "content.txt", "mirror/content.txt")]
        catalog = self.catalog_bytes(units)
        accepted, current = self.make_upstream(
            [
                {
                    ".aicore/core-catalog-v1.yaml": catalog,
                    "content.txt": b"A\n",
                    "notes.txt": b"1",
                },
                {
                    ".aicore/core-catalog-v1.yaml": catalog,
                    "content.txt": b"A\n",
                    "notes.txt": b"2",
                },
            ]
        )
        self.make_adopter()
        declaration = self.declaration(
            [
                self.declared_unit(
                    "mirror-file", "mirror", [self.declared_member("main", "mirror/content.txt")]
                )
            ]
        )
        lock = self.lock_document(
            accepted,
            m.sha256_digest(catalog),
            [
                {
                    "id": "mirror-file",
                    "mode": "mirror",
                    "members": [
                        self.lock_member(
                            "main",
                            "mirror/content.txt",
                            self.file_digest(b"A\n"),
                            self.file_digest(b"A\n"),
                        )
                    ],
                }
            ],
        )
        self.setup_adoption(declaration, lock)
        self.write_at(self.adopter / "mirror" / "content.txt", b"A\n")

        unit = self.find_unit(self.check(current), "mirror-file")
        self.assertNotEqual(accepted, current)
        self.assertEqual("unchanged", unit.upstream_delta)
        self.assertEqual("unchanged", unit.destination_delta)
        self.assertEqual("baseline_advance_required", unit.disposition)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFOs are unavailable on this platform")
    def test_unsupported_special_file_fifo(self) -> None:
        units = [self.file_unit("u", "m", "s.txt", "special.fifo")]
        catalog = self.catalog_bytes(units)
        accepted = self.make_upstream(
            [{".aicore/core-catalog-v1.yaml": catalog, "s.txt": b"S\n"}]
        )[0]
        self.make_adopter()
        declaration = self.declaration(
            [self.declared_unit("u", "adapted", [self.declared_member("m", "special.fifo")])]
        )
        lock = self.lock_document(
            accepted,
            m.sha256_digest(catalog),
            [
                {
                    "id": "u",
                    "mode": "adapted",
                    "members": [
                        self.lock_member(
                            "m",
                            "special.fifo",
                            self.file_digest(b"S\n"),
                            self.file_digest(b"S\n"),
                        )
                    ],
                }
            ],
        )
        self.setup_adoption(declaration, lock)
        os.mkfifo(self.adopter / "special.fifo")

        self.assert_sync_error(m.UNSUPPORTED_SPECIAL_FILE, self.check, accepted)

    def test_accepted_catalog_digest_binding(self) -> None:
        units = [self.file_unit("u", "m", "s.txt", "d.txt")]
        catalog = self.catalog_bytes(units)
        accepted = self.make_upstream(
            [{".aicore/core-catalog-v1.yaml": catalog, "s.txt": b"S\n"}]
        )[0]
        self.make_adopter()
        declaration = self.declaration(
            [self.declared_unit("u", "adapted", [self.declared_member("m", "d.txt")])]
        )
        self.write_at(self.adopter / "d.txt", b"S\n")
        declaration_raw = self.write_declaration(declaration)
        lock = self.lock_document(
            accepted,
            "sha256:" + "0" * 64,
            [
                {
                    "id": "u",
                    "mode": "adapted",
                    "members": [
                        self.lock_member(
                            "m", "d.txt", self.file_digest(b"S\n"), self.file_digest(b"S\n")
                        )
                    ],
                }
            ],
        )
        lock["declaration_digest"] = m.sha256_digest(declaration_raw)
        self.write_lock(lock)

        self.assert_sync_error(m.CATALOG_CHANGED, self.check, accepted)


if __name__ == "__main__":
    unittest.main()
