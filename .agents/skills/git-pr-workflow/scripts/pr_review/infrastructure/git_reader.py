"""Read local Git inventory through argv-only commands with no network or GitHub access."""

from __future__ import annotations

import os
import shutil
import subprocess

from pr_review.domain.ports import GitInventoryPort

GIT_EXECUTABLE = "git"
COMMAND_TIMEOUT_SECONDS = 120


class GitBoundaryError(RuntimeError):
    """Report an unavailable or failing Git process as a boundary failure, not a business value."""


def parse_status_entries(text: str) -> list[tuple[str, str]]:
    """Map NUL-separated name-status fields to a status and destination-path pair."""
    fields = text.split("\0")
    entries: list[tuple[str, str]] = []
    index = 0
    while index < len(fields):
        status = fields[index]
        index += 1
        if not status:
            continue
        width = 2 if status[0] in ("R", "C") else 1
        paths = fields[index:index + width]
        if len(paths) != width or not paths[-1]:
            raise GitBoundaryError("git name-status output was malformed")
        entries.append((status, paths[-1]))
        index += width
    return entries


class GitReader(GitInventoryPort):
    """Read immutable commit inventory and file bodies from the local repository."""

    def __init__(self, cwd: str | None = None) -> None:
        self._executable = shutil.which(GIT_EXECUTABLE)
        self._cwd = cwd

    def resolve_commit(self, revision: str) -> str | None:
        """Return the object id a revision resolves to, or absence when it does not resolve."""
        completed = self._run(("rev-parse", "--verify", revision), allow_failure=True)
        if completed.returncode != 0:
            return None
        commit = self._text(completed.stdout).strip()
        return commit or None

    def merge_base(self, first: str, second: str) -> str | None:
        """Return the common ancestor of two revisions, or absence when they share none."""
        completed = self._run(("merge-base", first, second), allow_failure=True)
        if completed.returncode != 0:
            return None
        ancestor = self._text(completed.stdout).strip()
        return ancestor or None

    def list_commits(self, ancestor: str, head: str) -> list[str]:
        """Return the commit ids contained in one revision range in Git order."""
        completed = self._run(("rev-list", self._range(ancestor, head)))
        return [line for line in self._text(completed.stdout).splitlines() if line]

    def read_message(self, commit: str) -> str:
        """Return one commit message without the trailing newlines the log format appends."""
        completed = self._run(("log", "--format=%B", "-1", commit))
        return self._text(completed.stdout).rstrip("\n")

    def list_changed_paths(self, ancestor: str, head: str) -> list[str]:
        """Return the exact changed path inventory, including deleted paths."""
        completed = self._run(("diff", "--name-only", "-z", self._range(ancestor, head)))
        return [path for path in self._text(completed.stdout).split("\0") if path]

    def list_deleted_paths(self, ancestor: str, head: str) -> list[str]:
        """Return the paths the range deletes, so no body is read for them."""
        completed = self._run(("diff", "--name-status", "-z", self._range(ancestor, head)))
        entries = parse_status_entries(self._text(completed.stdout))
        return [path for status, path in entries if status.endswith("D")]

    def read_file(self, commit: str, path: str) -> str:
        """Return one file body as committed at the supplied commit."""
        completed = self._run(("show", f"{commit}:{path}"))
        return self._text(completed.stdout)

    @staticmethod
    def _range(ancestor: str, head: str) -> str:
        """Compose the revision range one inventory read covers."""
        return f"{ancestor}..{head}"

    def _run(
        self, arguments: tuple[str, ...], *, allow_failure: bool = False
    ) -> subprocess.CompletedProcess[bytes]:
        """Run one read-only Git argv with no shell, no optional locks, and a bounded timeout."""
        if self._executable is None:
            raise GitBoundaryError(f"{GIT_EXECUTABLE} executable was not found on PATH")
        environment = os.environ.copy()
        environment["GIT_OPTIONAL_LOCKS"] = "0"
        try:
            completed = subprocess.run(
                [self._executable, *arguments], cwd=self._cwd, capture_output=True,
                check=False, shell=False, timeout=COMMAND_TIMEOUT_SECONDS, env=environment,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise GitBoundaryError(f"{GIT_EXECUTABLE} could not be executed: {error}") from error
        if completed.returncode != 0 and not allow_failure:
            detail = self._text(completed.stderr).strip()
            raise GitBoundaryError(f"{GIT_EXECUTABLE} exited with {completed.returncode}: {detail}")
        return completed

    @staticmethod
    def _text(raw: bytes) -> str:
        """Decode captured Git output strictly so no content is silently replaced."""
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError as error:
            raise GitBoundaryError("git output was not valid UTF-8") from error
