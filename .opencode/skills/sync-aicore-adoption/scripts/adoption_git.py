"""Read-only Git repository access and explicit commit/index snapshots.

One controlled invocation owns native read commands. It strips inherited
selectors, config injection, and trace destinations, then applies read policy.
It never writes the selected repository, index, or worktree.
"""

from __future__ import annotations

import argparse
import os
import subprocess
from collections.abc import Mapping, Sequence

from adoption_contracts import (
    CatalogDocument,
    ProjectedEntry,
    _Snapshot,
    _fail,
    _need,
)
from adoption_digests import _sha256
from adoption_loaders import _load_catalog_bytes

_CONTROLLED_READ_COMMANDS = frozenset({
    "cat-file",
    "check-ignore",
    "ls-files",
    "ls-tree",
    "merge-base",
    "rev-parse",
    "show",
    "status",
})
_READ_CONFIG: tuple[tuple[str, str], ...] = (
    ("core.fsmonitor", ""),
    ("credential.helper", ""),
    ("protocol.ext.allow", "never"),
    ("protocol.http.allow", "never"),
    ("protocol.https.allow", "never"),
    ("protocol.ssh.allow", "never"),
    ("protocol.git.allow", "never"),
)
_PROMISOR_FALSE = frozenset({"", "0", "false", "no", "off"})


def _controlled_git_environment(
    inherited: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Drop inherited Git selectors, config injection, and trace destinations.

    Known read-policy values are applied after the strip. Global and system
    Git config are neutralized. The selected repository's own index is used
    because ambient repository, worktree, index, and object-directory selectors
    are not forwarded. This does not record PATH or credentials.
    """
    source = os.environ if inherited is None else inherited
    environment = {
        key: value
        for key, value in source.items()
        if not key.startswith("GIT_")
    }
    environment["GIT_CONFIG_NOSYSTEM"] = "1"
    environment["GIT_CONFIG_GLOBAL"] = os.devnull
    environment["GIT_CONFIG_SYSTEM"] = os.devnull
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    environment["GIT_NO_LAZY_FETCH"] = "1"
    environment["GIT_TERMINAL_PROMPT"] = "0"
    return environment


def _controlled_read_argv(repo: str, args: Sequence[str]) -> list[str]:
    """Build one shell-free read argv. Command-local config is not a config write."""
    command = ["git", "--no-optional-locks"]
    for key, value in _READ_CONFIG:
        command.extend(("-c", f"{key}={value}"))
    command.extend(("-C", repo, *args))
    return command


def _refused_read(
    args: Sequence[str], message: str
) -> subprocess.CompletedProcess[bytes]:
    """Return a failed read without launching a fetch, helper, or mutation."""
    return subprocess.CompletedProcess(
        ["git", *args],
        128,
        b"",
        message.encode("ascii"),
    )


def _invoke_git(
    repo: str, args: Sequence[str], inherited: Mapping[str, str] | None = None
) -> subprocess.CompletedProcess[bytes]:
    """Run one list-form Git command. Missing Git fails without PATH provenance."""
    command = _controlled_read_argv(repo, args)
    try:
        return subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            check=False,
            env=_controlled_git_environment(inherited),
        )
    except FileNotFoundError:
        return _refused_read(args, "git is not available\n")


def _partial_clone_enabled(payload: bytes) -> bool:
    """True only when local config actually enables partial or promisor reads.

    Boolean false and empty values are not enabled. A non-empty partial-clone
    remote name or filter is enabled. Unexpected promisor values are enabled
    so an unreadable guarantee is not treated as safe.
    """
    enabled = False
    for raw in payload.splitlines():
        if b"=" not in raw:
            continue
        key_bytes, value_bytes = raw.split(b"=", 1)
        key = key_bytes.decode("utf-8", "replace").strip().lower()
        value = value_bytes.decode("utf-8", "replace").strip().lower()
        if key == "extensions.partialclone":
            enabled = enabled or bool(value)
        elif key.startswith("remote.") and key.endswith(".promisor"):
            enabled = enabled or value not in _PROMISOR_FALSE
        elif key.startswith("remote.") and key.endswith(".partialclonefilter"):
            enabled = enabled or bool(value)
    return enabled


def _promisor_read_blocked(
    repo: str, inherited: Mapping[str, str] | None = None
) -> bool:
    """Refuse when local partial/promisor config is enabled or cannot be read.

    The config probe is not a public read and does not fetch or edit config.
    """
    probed = _invoke_git(repo, ("config", "--local", "--list"), inherited)
    if probed.returncode not in (0, 1):
        return True
    return _partial_clone_enabled(probed.stdout)


def _run_controlled_read(
    repo: str,
    args: Sequence[str],
    inherited: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[bytes]:
    """Run one allowlisted read under the controlled environment.

    Partial or promisor repositories are refused before the requested command
    so a missing object cannot lazy-fetch. Callers keep their existing fatal
    codes; this function adds no report field.
    """
    if not args or args[0] not in _CONTROLLED_READ_COMMANDS:
        return _refused_read(args, "unsupported read\n")
    if _promisor_read_blocked(repo, inherited):
        return _refused_read(args, "partial or promisor read refused\n")
    return _invoke_git(repo, args, inherited)


def _resolve_git_path(repo: str, name: str) -> str | None:
    """Resolve one Git path against the selected repository, never ``repo/.git``.

    Relative ``rev-parse --git-path`` output is joined to the repository path
    that ``-C`` used. Absolute worktree git dirs are kept as printed.
    """
    proc = _run_controlled_read(repo, ("rev-parse", "--git-path", name))
    if proc.returncode != 0:
        return None
    raw = proc.stdout.decode("utf-8", "replace").strip()
    if not raw:
        return None
    if os.path.isabs(raw):
        return os.path.normpath(raw)
    return os.path.normpath(os.path.join(os.path.abspath(repo), raw))


class _GitRepo:
    """Read-only Git object reader; never writes the repository, index, or worktree."""

    def __init__(self, path: str) -> None:
        self.path = path

    def _run(self, *args: str) -> subprocess.CompletedProcess[bytes]:
        return _run_controlled_read(self.path, args)

    def resolve(self, rev: str) -> str | None:
        proc = self._run("rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}")
        if proc.returncode == 0:
            return proc.stdout.decode("ascii", "replace").strip()
        return None

    def toplevel(self) -> str | None:
        proc = self._run("rev-parse", "--show-toplevel")
        if proc.returncode == 0:
            return proc.stdout.decode("utf-8", "replace").strip()
        return None

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        proc = self._run("merge-base", "--is-ancestor", ancestor, descendant)
        return proc.returncode == 0

    def blob(self, object_id: str, code: str) -> bytes:
        proc = self._run("cat-file", "-p", object_id)
        if proc.returncode != 0:
            _fail(code, f"cannot read Git object {object_id}")
        return proc.stdout

    def show_blob(self, commit: str, path: str) -> bytes | None:
        proc = self._run("show", f"{commit}:{path}")
        if proc.returncode == 0:
            return proc.stdout
        return None

    def file_entry(self, rev: str, path: str, code: str) -> ProjectedEntry | None:
        blobs = [record for record in self._ls_tree(rev, path) if record[1] == "blob"]
        if len(blobs) != 1:
            return None
        return ProjectedEntry(
            path="",
            mode=blobs[0][0],
            content=self.blob(blobs[0][2], code),
        )

    def tree_entries(self, rev: str, root: str, code: str) -> list[ProjectedEntry]:
        prefix = root.rstrip("/") + "/"
        entries: list[ProjectedEntry] = []
        for mode, otype, object_id, full in self._ls_tree(rev, root):
            _need(
                otype == "blob",
                "unsupported_special_file",
                f"{root}: non-blob Git entry {full!r}",
            )
            logical = full[len(prefix):] if full.startswith(prefix) else full
            entries.append(
                ProjectedEntry(
                    path=logical,
                    mode=mode,
                    content=self.blob(object_id, code),
                )
            )
        return entries

    def _ls_tree(self, rev: str, path: str) -> list[tuple[str, str, str, str]]:
        proc = self._run("ls-tree", "-r", "-z", rev, "--", path)
        if proc.returncode != 0:
            return []
        records: list[tuple[str, str, str, str]] = []
        for raw in proc.stdout.split(b"\0"):
            if not raw:
                continue
            meta, _, full = raw.partition(b"\t")
            parts = meta.split(b" ")
            if len(parts) < 3:
                continue
            records.append(
                (
                    parts[0].decode("ascii"),
                    parts[1].decode("ascii"),
                    parts[2].decode("ascii"),
                    full.decode("utf-8", "replace"),
                )
            )
        return records

    def index_file_entry(self, path: str) -> ProjectedEntry | None:
        records = self._index_records(path)
        if len(records) != 1:
            return None
        return ProjectedEntry(
            path="",
            mode=records[0][0],
            content=self.blob(records[0][1], "adopter_snapshot_unavailable"),
        )

    def index_tree_entries(self, root: str) -> list[ProjectedEntry]:
        prefix = root.rstrip("/") + "/"
        entries: list[ProjectedEntry] = []
        for mode, object_id, full in self._index_records(root):
            logical = full[len(prefix):] if full.startswith(prefix) else full
            entries.append(
                ProjectedEntry(
                    path=logical,
                    mode=mode,
                    content=self.blob(object_id, "adopter_snapshot_unavailable"),
                )
            )
        return entries

    def _index_records(self, path: str) -> list[tuple[str, str, str]]:
        proc = self._run("ls-files", "-s", "-z", "--", path)
        if proc.returncode != 0:
            return []
        records: list[tuple[str, str, str]] = []
        for raw in proc.stdout.split(b"\0"):
            if not raw:
                continue
            meta, _, full = raw.partition(b"\t")
            parts = meta.split(b" ")
            if len(parts) < 3:
                continue
            _need(
                parts[2] == b"0",
                "adopter_snapshot_unavailable",
                f"unmerged index entry for {path}",
            )
            records.append(
                (
                    parts[0].decode("ascii"),
                    parts[1].decode("ascii"),
                    full.decode("utf-8", "replace"),
                )
            )
        return records


class _RevisionSnapshot:
    """Adopter snapshot read from the tree of one explicit commit (never the worktree)."""

    def __init__(self, repo: _GitRepo, revision: str) -> None:
        self.repo = repo
        self.revision = revision

    def file_entry(self, path: str) -> ProjectedEntry | None:
        return self.repo.file_entry(self.revision, path, "adopter_snapshot_unavailable")

    def tree_entries(self, root: str) -> list[ProjectedEntry]:
        return self.repo.tree_entries(
            self.revision, root, "adopter_snapshot_unavailable"
        )


class _IndexSnapshot:
    """Adopter snapshot read from the staged Git index only (never the worktree)."""

    def __init__(self, repo: _GitRepo) -> None:
        self.repo = repo

    def file_entry(self, path: str) -> ProjectedEntry | None:
        return self.repo.index_file_entry(path)

    def tree_entries(self, root: str) -> list[ProjectedEntry]:
        return self.repo.index_tree_entries(root)


def _adopter_repo(declaration: str) -> _GitRepo:
    repo = _GitRepo(os.path.dirname(os.path.abspath(declaration)) or os.getcwd())
    top = repo.toplevel()
    return _GitRepo(top) if top else repo


def _resolve_adopter_repo(args: argparse.Namespace) -> _GitRepo:
    explicit = getattr(args, "adopter_repo", None)
    if explicit:
        return _GitRepo(str(explicit))
    return _adopter_repo(str(args.declaration))


def _resolve_catalog_path(catalog: str, upstream_repo: str) -> str:
    if os.path.isabs(catalog) or os.path.exists(catalog):
        return catalog
    candidate = os.path.join(upstream_repo, catalog)
    return candidate if os.path.exists(candidate) else catalog


def _trusted_revision(upstream: _GitRepo, diagnostic: str | None) -> tuple[str, bool]:
    if diagnostic:
        target = upstream.resolve(diagnostic)
        _need(
            target is not None,
            "baseline_unavailable",
            f"diagnostic revision not resolvable: {diagnostic}",
        )
        return str(target), True
    for ref in ("refs/remotes/origin/main", "refs/heads/main"):
        target = upstream.resolve(ref)
        if target:
            return target, False
    _fail(
        "baseline_unavailable",
        "no protected default branch (refs/remotes/origin/main or refs/heads/main)",
    )


def _snapshot_for(args: argparse.Namespace, adopter: _GitRepo) -> _Snapshot:
    _need(
        args.adopter_revision is not None or args.adopter_index,
        "adopter_snapshot_unavailable",
        "exactly one of --adopter-revision or --adopter-index is required",
    )
    if args.adopter_index:
        return _IndexSnapshot(adopter)
    revision = adopter.resolve(str(args.adopter_revision))
    _need(
        revision is not None,
        "adopter_snapshot_unavailable",
        f"adopter revision not resolvable: {args.adopter_revision}",
    )
    return _RevisionSnapshot(adopter, str(revision))


def _repo_relative_path(repo: _GitRepo, path: str) -> str:
    top = repo.toplevel()
    absolute = os.path.abspath(path)
    if top and absolute.startswith(os.path.abspath(top) + os.sep):
        return os.path.relpath(absolute, os.path.abspath(top))
    return path


def _catalog_blob_at(upstream: _GitRepo, commit: str, catalog_path: str) -> bytes:
    relative = _repo_relative_path(upstream, catalog_path)
    blob = upstream.show_blob(commit, relative)
    if blob is None:
        _fail("catalog_changed", f"cannot read catalog at {commit}:{relative}")
    return blob


def _catalog_digest_at(upstream: _GitRepo, commit: str, catalog_path: str) -> str:
    return _sha256(_catalog_blob_at(upstream, commit, catalog_path))


def _catalog_at(
    upstream: _GitRepo, commit: str, catalog_path: str
) -> CatalogDocument:
    """Load and validate a catalog only from the requested upstream Git tree."""
    relative = _repo_relative_path(upstream, catalog_path)
    return _load_catalog_bytes(
        _catalog_blob_at(upstream, commit, catalog_path), f"{commit}:{relative}"
    )
