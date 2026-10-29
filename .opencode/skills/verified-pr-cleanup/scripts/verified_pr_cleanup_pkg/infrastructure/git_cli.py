"""Read-only Git subprocess adapter for cleanup preflight validation."""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from verified_pr_cleanup_pkg.domain.guards import (
    GITHUB_HOST,
    GITHUB_SSH_USER,
    github_repository_from_url,
    is_full_oid,
    is_safe_ssh_alias_host,
    parse_ssh_remote,
)
from verified_pr_cleanup_pkg.domain.models import (
    BoundaryFailure,
    RepositoryIdentity,
    Worktree,
)

COMMAND_TIMEOUT_SECONDS = 60


@dataclass(frozen=True)
class _SshSettings:
    """Effective hostname and user reported by `ssh -G`."""

    hostname: str | None
    user: str | None


class GitCli:
    """Expose only Git identity, ref, occupancy, and proof reads; no mutating command."""

    def __init__(self) -> None:
        executable = shutil.which("git")
        if executable is None:
            raise BoundaryFailure("Git executable was not found on PATH.")
        self._executable = executable

    def remote_identity(self, remote: str) -> RepositoryIdentity:
        """Require singular fetch/push URLs identifying one GitHub repository."""
        fetch_urls = self._lines(self._git("remote", "get-url", "--all", remote))
        push_urls = self._lines(self._git("remote", "get-url", "--push", "--all", remote))
        if len(fetch_urls) != 1 or len(push_urls) != 1:
            raise BoundaryFailure("Base remote must have exactly one fetch and push URL.")
        fetch_identity = self._identity_from_url(fetch_urls[0])
        push_identity = self._identity_from_url(push_urls[0])
        if fetch_identity.full_name.casefold() != push_identity.full_name.casefold():
            raise BoundaryFailure("Base remote URLs do not identify one GitHub repository.")
        return fetch_identity

    def _identity_from_url(self, value: str) -> RepositoryIdentity:
        """Map one exact GitHub URL or resolve one SSH host alias through local config."""
        identity = github_repository_from_url(value)
        if identity is not None:
            return identity
        ssh_remote = parse_ssh_remote(value)
        if ssh_remote is None or ssh_remote.user != GITHUB_SSH_USER:
            raise BoundaryFailure("Base remote URL is not a recognised GitHub remote.")
        self._require_github_ssh_alias(ssh_remote.host)
        return RepositoryIdentity(owner=ssh_remote.owner, name=ssh_remote.repository)

    def _require_github_ssh_alias(self, host: str) -> None:
        """Expand one alias without connecting; require github.com and the git user."""
        if not is_safe_ssh_alias_host(host):
            raise BoundaryFailure("SSH host alias is not safe to expand.")
        settings = self._parse_ssh_config(self._ssh("-G", host))
        if settings.hostname is None or settings.user is None:
            raise BoundaryFailure("SSH configuration expansion was inconclusive.")
        if settings.hostname.casefold() != GITHUB_HOST or settings.user != GITHUB_SSH_USER:
            raise BoundaryFailure("SSH host alias does not resolve to GitHub.")

    @staticmethod
    def _parse_ssh_config(output: bytes) -> _SshSettings:
        """Extract hostname and user from `ssh -G` output; ambiguity fails closed."""
        try:
            text = output.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise BoundaryFailure(
                "SSH configuration expansion returned non-UTF-8 output."
            ) from exc
        values: dict[str, str] = {}
        for line in text.splitlines():
            if not line.strip():
                continue
            fields = line.split(None, 1)
            if len(fields) != 2 or any(ord(character) < 32 for character in line):
                raise BoundaryFailure("SSH configuration expansion was inconclusive.")
            key, value = fields[0], fields[1].strip()
            if key in {"hostname", "user"}:
                if key in values:
                    raise BoundaryFailure("SSH configuration expansion was ambiguous.")
                values[key] = value
        return _SshSettings(values.get("hostname"), values.get("user"))

    def validate_branch(self, branch: str) -> bool:
        """Check one base/head value as a valid refs/heads name."""
        if not branch or branch.startswith("-") or any(
            ord(character) < 32 or ord(character) == 127 for character in branch
        ):
            return False
        return self._run(("check-ref-format", f"refs/heads/{branch}")).returncode == 0

    def remote_branch_oid(self, remote: str, branch: str) -> str | None:
        """Read one remote branch using ls-remote without updating local state."""
        ref = f"refs/heads/{branch}"
        lines = self._lines(self._git("ls-remote", "--refs", remote, ref))
        return self._parse_single_ls_remote(lines, ref)

    def local_branch_oid(self, branch: str) -> str | None:
        """Read one local branch ref by exact full name, ignoring nested refs."""
        ref = f"refs/heads/{branch}"
        lines = self._lines(
            self._git("for-each-ref", "--format=%(refname)%09%(objectname)", ref)
        )
        observed = [self._parse_local_ref_record(line) for line in lines]
        matched = [oid for refname, oid in observed if refname == ref]
        if not matched:
            return None
        if len(matched) != 1:
            raise BoundaryFailure("Local branch ref lookup was ambiguous.")
        oid = matched[0]
        if not is_full_oid(oid):
            raise BoundaryFailure("Local branch ref did not resolve to a full OID.")
        return oid.lower()

    def object_exists(self, oid: str) -> bool:
        """Check an already-local commit object without downloading missing objects."""
        if not is_full_oid(oid):
            return False
        completed = self._run(("rev-parse", "--verify", "--quiet", f"{oid}^{{commit}}"))
        if completed.returncode == 1 and not completed.stdout:
            return False
        if completed.returncode != 0:
            raise BoundaryFailure("Could not inspect local commit-object availability.")
        observed = self._decode(completed.stdout).strip()
        if not is_full_oid(observed):
            raise BoundaryFailure("Commit-object lookup returned an invalid OID.")
        return observed.lower() == oid.lower()

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        """Check ancestry; distinguish non-ancestry from process errors."""
        completed = self._run(("merge-base", "--is-ancestor", ancestor, descendant))
        if completed.returncode == 0:
            return True
        if completed.returncode == 1:
            return False
        raise BoundaryFailure("Could not establish commit ancestry from local objects.")

    def merge_base(self, base_oid: str, head_oid: str) -> str:
        """Read the merge-base of verified base and immutable PR head."""
        if not is_full_oid(base_oid) or not is_full_oid(head_oid):
            raise BoundaryFailure("Refused merge-base lookup without full OIDs.")
        value = self._text(self._git("merge-base", base_oid, head_oid))
        if not is_full_oid(value):
            raise BoundaryFailure("Git merge-base returned an invalid OID.")
        return value.lower()

    def changed_paths(self, merge_base_oid: str, head_oid: str) -> tuple[str, ...]:
        """Extract NUL-delimited changed paths and check command success."""
        if not is_full_oid(merge_base_oid) or not is_full_oid(head_oid):
            raise BoundaryFailure("Refused changed-path extraction without full OIDs.")
        output = self._git_bytes("diff", "--name-only", "-z", merge_base_oid, head_oid)
        if not output:
            return ()
        if not output.endswith(b"\0"):
            raise BoundaryFailure("Git changed-path output was not NUL terminated.")
        records = output[:-1].split(b"\0")
        if any(not record for record in records):
            raise BoundaryFailure("Git changed-path output contained an empty path.")
        return tuple(os.fsdecode(record) for record in records)

    def paths_match(self, base_oid: str, head_oid: str, paths: tuple[str, ...]) -> bool:
        """Run Herald's checked changed-path parity command; exit 1 means mismatch."""
        if not is_full_oid(base_oid) or not is_full_oid(head_oid):
            raise BoundaryFailure("Refused path parity check without full OIDs.")
        completed = self._run((
            "--literal-pathspecs", "diff", "--quiet", "--exit-code",
            base_oid, head_oid, "--", *paths,
        ))
        if completed.returncode == 0:
            return True
        if completed.returncode == 1:
            return False
        raise BoundaryFailure("Git changed-path parity command failed.")

    def inspect_worktrees(self) -> tuple[Worktree, ...]:
        """Read each linked worktree's path and checked-out branch only."""
        records = self._text(self._git("worktree", "list", "--porcelain"))
        groups: list[list[str]] = []
        current: list[str] = []
        for line in records.splitlines():
            if not line:
                if current:
                    groups.append(current)
                    current = []
            else:
                current.append(line)
        if current:
            groups.append(current)
        worktrees: list[Worktree] = []
        seen: set[str] = set()
        for group in groups:
            paths = [line[9:] for line in group if line.startswith("worktree ")]
            branches = [line[7:] for line in group if line.startswith("branch ")]
            if len(paths) != 1 or len(branches) > 1:
                raise BoundaryFailure("Linked worktree inventory is malformed.")
            canonical = os.path.normcase(os.path.abspath(paths[0]))
            if canonical in seen:
                raise BoundaryFailure("Linked worktree inventory has duplicate paths.")
            seen.add(canonical)
            branch_ref = branches[0] if branches else None
            if branch_ref is not None and not branch_ref.startswith("refs/heads/"):
                raise BoundaryFailure("Linked worktree branch ref is malformed.")
            worktrees.append(Worktree(
                paths[0], branch_ref.removeprefix("refs/heads/") if branch_ref else None
            ))
        if not worktrees:
            raise BoundaryFailure("Linked worktree inventory was empty.")
        return tuple(worktrees)

    def _parse_single_ls_remote(self, lines: list[str], ref: str) -> str | None:
        """Validate ls-remote output against exactly one requested full ref."""
        if not lines:
            return None
        if len(lines) != 1:
            raise BoundaryFailure("Remote ref lookup was ambiguous.")
        fields = lines[0].split("\t")
        if len(fields) != 2 or fields[1] != ref or not is_full_oid(fields[0]):
            raise BoundaryFailure("Remote ref lookup returned an invalid record.")
        return fields[0].lower()

    @staticmethod
    def _parse_local_ref_record(line: str) -> tuple[str, str]:
        """Split one exact refname/objectname record; nested refs remain distinguishable."""
        refname, separator, oid = line.partition("\t")
        if (
            not separator
            or not refname.startswith("refs/heads/")
            or not oid
            or "\t" in oid
        ):
            raise BoundaryFailure("Local branch ref lookup returned an invalid record.")
        return refname, oid

    def _lines(self, output: bytes) -> list[str]:
        """Decode newline records; TAB is the only allowed control character."""
        text = self._decode(output)
        if not text:
            return []
        if text.endswith("\n"):
            text = text[:-1]
        lines = text.split("\n")
        for line in lines:
            if not line or any(
                ord(character) < 32 and character != "\t" for character in line
            ):
                raise BoundaryFailure("Git returned malformed line-delimited output.")
        return lines

    def _text(self, output: bytes) -> str:
        """Decode one required non-empty UTF-8 value."""
        text = self._decode(output).strip()
        if not text:
            raise BoundaryFailure("Git returned an empty required value.")
        return text

    def _decode(self, output: bytes) -> str:
        """Decode control output strictly; path records use os.fsdecode."""
        try:
            return output.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise BoundaryFailure("Git returned non-UTF-8 control output.") from exc

    def _git(self, *arguments: str, cwd: Path | None = None) -> bytes:
        """Run a checked argv-only Git inventory command with no shell."""
        completed = self._run(arguments, cwd=cwd)
        if completed.returncode != 0:
            raise BoundaryFailure(f"git {' '.join(arguments[:2])} failed (exit {completed.returncode}).")
        return completed.stdout

    def _git_bytes(self, *arguments: str, cwd: Path | None = None) -> bytes:
        """Identify commands whose output is parsed as bytes/NUL-delimited records."""
        return self._git(*arguments, cwd=cwd)

    def _ssh(self, *arguments: str) -> bytes:
        """Expand one SSH host alias using Git's configured SSH command, connecting to nothing."""
        configured = self._run(("config", "--get", "core.sshcommand"))
        if configured.returncode == 0:
            executable, command_arguments = self._parse_ssh_command(configured.stdout)
        elif configured.returncode == 1:
            resolved = shutil.which("ssh")
            if resolved is None:
                raise BoundaryFailure("SSH executable was not found on PATH.")
            executable, command_arguments = resolved, ()
        else:
            raise BoundaryFailure("Could not read the configured SSH command.")
        completed = self._run_process(executable, (*command_arguments, *arguments))
        if completed.returncode != 0:
            raise BoundaryFailure("SSH configuration expansion failed.")
        return completed.stdout

    @staticmethod
    def _parse_ssh_command(output: bytes) -> tuple[str, tuple[str, ...]]:
        """Split Git's configured SSH command into one executable and argv tokens."""
        try:
            text = output.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise BoundaryFailure("Configured SSH command was not valid UTF-8.") from exc
        text = text.strip()
        if not text:
            raise BoundaryFailure("Configured SSH command was empty.")
        if any(ord(character) < 32 for character in text):
            raise BoundaryFailure("Configured SSH command was malformed.")
        try:
            tokens = shlex.split(text)
        except ValueError as exc:
            raise BoundaryFailure("Configured SSH command was malformed.") from exc
        if not tokens or not tokens[0]:
            raise BoundaryFailure("Configured SSH command named no executable.")
        expanded = tuple(os.path.expanduser(token) for token in tokens)
        return expanded[0], expanded[1:]

    def _run(
        self, arguments: tuple[str, ...], cwd: Path | None = None
    ) -> subprocess.CompletedProcess[bytes]:
        """Run the supplied read-only Git argv without shell interpolation or optional locks."""
        environment = os.environ.copy()
        environment["GIT_OPTIONAL_LOCKS"] = "0"
        return self._run_process(self._executable, arguments, cwd, environment)

    @staticmethod
    def _run_process(
        executable: str,
        arguments: tuple[str, ...],
        cwd: Path | None = None,
        environment: Mapping[str, str] | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        """Run one argv-only process with no shell and a bounded timeout."""
        try:
            return subprocess.run(
                [executable, *arguments], cwd=cwd, capture_output=True,
                check=False, shell=False, timeout=COMMAND_TIMEOUT_SECONDS,
                env=environment,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise BoundaryFailure("Process execution could not be completed safely.") from exc

