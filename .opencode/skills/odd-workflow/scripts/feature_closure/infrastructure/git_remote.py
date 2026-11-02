"""Ask a remote whether a branch still exists through one argv-only Git query."""

from __future__ import annotations

import os
import shutil
import subprocess

from feature_closure.domain.ports import RemoteBranchProbe

GIT_EXECUTABLE = "git"
COMMAND_TIMEOUT_SECONDS = 120
MATCHING_REF_EXIT_CODE = 0
ABSENT_REF_EXIT_CODE = 2


class GitBoundaryError(RuntimeError):
    """Report an unavailable or failing Git process as a boundary failure, not a business value."""


class GitRemoteBranchProbe(RemoteBranchProbe):
    """Map one `git ls-remote` query per branch to remote branch presence."""

    def __init__(self, cwd: str | None = None) -> None:
        self._executable = shutil.which(GIT_EXECUTABLE)
        self._cwd = cwd

    def exists(self, remote: str, branch: str) -> bool:
        """Return True when the remote still advertises the branch."""
        completed = self._run(
            ("ls-remote", "--exit-code", "--heads", remote, f"refs/heads/{branch}")
        )
        if completed.returncode == MATCHING_REF_EXIT_CODE:
            return True
        if completed.returncode == ABSENT_REF_EXIT_CODE:
            return False
        raise GitBoundaryError(
            f"{GIT_EXECUTABLE} ls-remote exited with {completed.returncode}: "
            f"{self._text(completed.stderr).strip()}"
        )

    def _run(self, arguments: tuple[str, ...]) -> subprocess.CompletedProcess[bytes]:
        """Run one read-only Git argv with no shell, no prompting, and a bounded timeout."""
        if self._executable is None:
            raise GitBoundaryError(f"{GIT_EXECUTABLE} executable was not found on PATH")
        environment = os.environ.copy()
        environment["GIT_OPTIONAL_LOCKS"] = "0"
        environment["GIT_TERMINAL_PROMPT"] = "0"
        try:
            return subprocess.run(
                [self._executable, *arguments],
                cwd=self._cwd,
                capture_output=True,
                check=False,
                shell=False,
                timeout=COMMAND_TIMEOUT_SECONDS,
                env=environment,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise GitBoundaryError(f"{GIT_EXECUTABLE} could not be executed: {error}") from error

    @staticmethod
    def _text(raw: bytes) -> str:
        """Decode captured Git output strictly so no diagnostic is silently replaced."""
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError as error:
            raise GitBoundaryError("git output was not valid UTF-8") from error
