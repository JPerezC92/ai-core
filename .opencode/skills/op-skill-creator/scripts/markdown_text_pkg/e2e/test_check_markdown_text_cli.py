"""End-to-end CLI tests via the real check_markdown_text.py subprocess entry."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ENTRY = Path(__file__).resolve().parents[2] / "check_markdown_text.py"
REPO_ROOT = Path(__file__).resolve().parents[6]
CANONICAL_POLICY = REPO_ROOT / "knowledge" / "unicode-policy.json"
CANONICAL_SETTINGS = REPO_ROOT / ".vscode" / "settings.json"

EN_DASH = "\u2013"
EM_DASH = "\u2014"
LSQ = "\u2018"
RSQ = "\u2019"
LDQ = "\u201c"
RDQ = "\u201d"
ZWSP = "\u200b"
ZWNJ = "\u200c"
ZWJ = "\u200d"
VS16 = "\ufe0f"
NBSP = "\u00a0"
SHY = "\u00ad"
FFFD = "\ufffd"
ALM = "\u061c"
NUL = "\x00"
BEL = "\x07"
C1 = "\x85"
TAB = "\t"
CR = "\r"
FAMILY = "\U0001f468" + ZWJ + "\U0001f469" + ZWJ + "\U0001f467"
SUN = "\u2600" + VS16
PYTHON = sys.executable
EMOJI = "😀"
NON_ASCII_MARKDOWN_NAME = "café.md"
NON_ASCII_POLICY_NAME = "café-policy.json"


def create_allowed_markdown() -> str:
    """Return S7 permitted prose, ranges, Unicode, emoji, joiners, and escaped spelling."""

    return "\n".join(
        [
            "ASCII text",
            "café Привет 😀",
            FAMILY,
            f"a{ZWNJ}b {SUN}",
            f"pages 1{EN_DASH}3 and `1{EN_DASH}3`",
            f"{EM_DASH} {LSQ}q{RSQ} {LDQ}q{RDQ}",
            f"see U+200B {TAB} done{CR}",
            "",
        ]
    )


def create_warning_markdown() -> str:
    """Return one of each canonical warning control."""

    return f"zwsp{ZWSP} nbsp{NBSP} shy{SHY} fffd{FFFD} alm{ALM}\n"


def create_fffd_emoji_markdown() -> str:
    """Return a warning line whose excerpt includes emoji and U+FFFD."""

    return f"{EMOJI}{FFFD}\n"


def create_error_markdown() -> str:
    """Return canonical error scalars NUL, unexpected C0, and C1."""

    return f"{NUL}{BEL}{C1}ok\n"


def create(**overrides: object) -> dict[str, object]:
    """Return a tiny valid policy for CLI argument-failure isolation."""

    document: dict[str, object] = {
        "version": 1,
        "id": "min-markdown-text",
        "default_classification": "allow",
        "decoding": {
            "encoding": "utf-8",
            "invalid_sequence": {
                "id": "ERR-UTF8",
                "severity": "error",
                "class": "invalid_utf8",
                "rationale": "ill-formed UTF-8",
            },
        },
        "rules": [],
        "editor_projection": {
            "scope": "[markdown]",
            "setting_key": "gremlins.characters",
            "overrides": [
                {
                    "codepoint": 8211,
                    "hex": "U+2013",
                    "gremlins_key": "2013",
                    "severity": "none",
                    "description": "en dash",
                }
            ],
        },
    }
    document.update(overrides)
    return document


def _copy_canonical_policy(tmp_path: Path) -> Path:
    """Copy the repository policy into the isolated tree."""

    dest = tmp_path / "unicode-policy.json"
    dest.write_bytes(CANONICAL_POLICY.read_bytes())
    return dest


def _copy_canonical_settings(tmp_path: Path) -> Path:
    """Copy the repository Markdown editor projection into the isolated tree."""

    dest = tmp_path / "settings.json"
    dest.write_bytes(CANONICAL_SETTINGS.read_bytes())
    return dest


def _write_md(path: Path, body: str) -> Path:
    """Write UTF-8 Markdown without newline translation."""

    path.write_bytes(body.encode("utf-8"))
    return path


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    """Invoke the real CLI entry; decode captured stdio as UTF-8, not the parent locale.

    The CLI contract writes UTF-8 with LF newlines after stdio configuration.
    """

    return subprocess.run(
        [PYTHON, str(ENTRY), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def _run_ascii_env_bytes(args: list[str]) -> subprocess.CompletedProcess[bytes]:
    """Invoke the CLI with PYTHONIOENCODING=ascii and capture raw stdio bytes."""

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "ascii"
    return subprocess.run(
        [PYTHON, str(ENTRY), *args],
        capture_output=True,
        env=env,
        check=False,
    )


class CliArgumentTests:
    """Required --policy and explicit Markdown paths; editor-only is invalid."""

    def test_missing_policy_exits_two(self, tmp_path: Path) -> None:
        markdown = _write_md(tmp_path / "note.md", create_allowed_markdown())
        completed = _run([str(markdown)])
        assert completed.returncode == 2
        assert completed.stdout == ""
        assert completed.stderr != ""

    def test_editor_only_without_markdown_paths_exits_two(self, tmp_path: Path) -> None:
        policy = tmp_path / "policy.json"
        policy.write_text(json.dumps(create()), encoding="utf-8")
        settings = tmp_path / "settings.json"
        settings.write_text("{}", encoding="utf-8")
        completed = _run(
            ["--policy", str(policy), "--check-editor", str(settings)]
        )
        assert completed.returncode == 2
        assert completed.stdout == ""

    def test_invalid_policy_exits_two(self, tmp_path: Path) -> None:
        policy = tmp_path / "policy.json"
        policy.write_text("{", encoding="utf-8")
        markdown = _write_md(tmp_path / "note.md", create_allowed_markdown())
        completed = _run(["--policy", str(policy), str(markdown)])
        assert completed.returncode == 2
        assert "policy" in completed.stderr
        assert completed.stdout == ""


class CliContentExitTests:
    """Exit 0 for warnings, 1 for errors/drift, 2 for input with precedence."""

    def test_allowed_canonical_content_exits_zero(self, tmp_path: Path) -> None:
        policy = _copy_canonical_policy(tmp_path)
        markdown = _write_md(tmp_path / "note.md", create_allowed_markdown())
        before = markdown.read_bytes()
        completed = _run(["--policy", str(policy), str(markdown)])
        assert completed.returncode == 0
        assert completed.stdout == ""
        assert completed.stderr == ""
        assert markdown.read_bytes() == before

    def test_warnings_exit_zero_and_escape_controls(self, tmp_path: Path) -> None:
        policy = _copy_canonical_policy(tmp_path)
        markdown = _write_md(tmp_path / "warn.md", create_warning_markdown())
        completed = _run(["--policy", str(policy), str(markdown)])
        assert completed.returncode == 0
        assert completed.stderr == ""
        assert "warning WARN-ZWSP U+200B" in completed.stdout
        assert "warning WARN-NBSP U+00A0" in completed.stdout
        assert "warning WARN-SHY U+00AD" in completed.stdout
        assert "warning WARN-FFFD U+FFFD" in completed.stdout
        assert "warning WARN-BIDI U+061C" in completed.stdout
        assert NUL not in completed.stdout
        assert ZWSP not in completed.stdout
        assert ALM not in completed.stdout
        assert NBSP not in completed.stdout

    def test_errors_exit_one(self, tmp_path: Path) -> None:
        policy = _copy_canonical_policy(tmp_path)
        markdown = _write_md(tmp_path / "bad.md", create_error_markdown())
        completed = _run(["--policy", str(policy), str(markdown)])
        assert completed.returncode == 1
        assert "error ERR-NUL U+0000" in completed.stdout
        assert "error ERR-C0 U+0007" in completed.stdout
        assert "error ERR-C1 U+0085" in completed.stdout
        assert completed.stderr == ""
        assert NUL not in completed.stdout
        assert BEL not in completed.stdout
        assert C1 not in completed.stdout

    def test_invalid_utf8_exit_one_reports_byte_offset(self, tmp_path: Path) -> None:
        policy = _copy_canonical_policy(tmp_path)
        markdown = tmp_path / "bad.md"
        markdown.write_bytes(b"ab\nc\xff")
        completed = _run(["--policy", str(policy), str(markdown)])
        assert completed.returncode == 1
        assert "error ERR-UTF8 byte 5" in completed.stdout
        assert completed.stderr == ""

    def test_matching_editor_with_allowed_content_exits_zero(
        self, tmp_path: Path
    ) -> None:
        policy = _copy_canonical_policy(tmp_path)
        settings = _copy_canonical_settings(tmp_path)
        markdown = _write_md(tmp_path / "note.md", create_allowed_markdown())
        completed = _run(
            [
                "--policy",
                str(policy),
                "--check-editor",
                str(settings),
                str(markdown),
            ]
        )
        assert completed.returncode == 0
        assert completed.stdout == ""
        assert completed.stderr == ""

    def test_editor_drift_exits_one(self, tmp_path: Path) -> None:
        policy = _copy_canonical_policy(tmp_path)
        settings = json.loads(CANONICAL_SETTINGS.read_text(encoding="utf-8"))
        markdown_scope = settings["[markdown]"]
        characters = markdown_scope["gremlins.characters"]
        characters["200b"] = {"level": "error", "description": "zwsp"}
        settings_path = tmp_path / "settings.json"
        settings_path.write_text(json.dumps(settings), encoding="utf-8")
        note = _write_md(tmp_path / "note.md", create_allowed_markdown())
        completed = _run(
            [
                "--policy",
                str(policy),
                "--check-editor",
                str(settings_path),
                str(note),
            ]
        )
        assert completed.returncode == 1
        assert "error EDITOR-DRIFT" in completed.stdout
        assert "extra=200b" in completed.stdout
        assert completed.stderr == ""

    def test_missing_input_takes_exit_two_precedence(self, tmp_path: Path) -> None:
        policy = _copy_canonical_policy(tmp_path)
        bad = _write_md(tmp_path / "bad.md", create_error_markdown())
        missing = tmp_path / "gone.md"
        completed = _run(["--policy", str(policy), str(missing), str(bad)])
        assert completed.returncode == 2
        assert "missing path" in completed.stderr
        assert "error ERR-NUL" in completed.stdout


class CliUtf8StdioTests:
    """CLI stdio stays UTF-8 even when the process inherits an ASCII IO encoding."""

    def test_ascii_env_writes_utf8_fffd_and_emoji(self, tmp_path: Path) -> None:
        policy = _copy_canonical_policy(tmp_path)
        markdown = _write_md(
            tmp_path / NON_ASCII_MARKDOWN_NAME, create_fffd_emoji_markdown()
        )
        completed = _run_ascii_env_bytes(["--policy", str(policy), str(markdown)])
        stdout = completed.stdout.decode("utf-8")
        stderr = completed.stderr.decode("utf-8")
        assert completed.returncode == 0
        assert "UnicodeEncodeError" not in stderr
        assert "warning WARN-FFFD U+FFFD" in stdout
        assert EMOJI in stdout
        assert FFFD in stdout
        assert stderr == ""

    def test_ascii_env_invalid_policy_stderr_utf8(self, tmp_path: Path) -> None:
        policy = tmp_path / NON_ASCII_POLICY_NAME
        policy.write_text("{", encoding="utf-8")
        markdown = _write_md(
            tmp_path / NON_ASCII_MARKDOWN_NAME, create_allowed_markdown()
        )
        completed = _run_ascii_env_bytes(["--policy", str(policy), str(markdown)])
        stdout = completed.stdout.decode("utf-8")
        stderr = completed.stderr.decode("utf-8")
        assert completed.returncode == 2
        assert stdout == ""
        assert "policy" in stderr
        assert "UnicodeEncodeError" not in stderr
