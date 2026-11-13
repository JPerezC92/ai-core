"""Unit tests for CheckText.execute with typed port fakes and no filesystem."""

from __future__ import annotations

import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from markdown_text_pkg.application.check_text import CheckText  # noqa: E402
from markdown_text_pkg.domain.models import (  # noqa: E402
    CODE_INPUT,
    CODE_IO,
    CODE_POLICY,
    DiscoverResult,
    DomainError,
    EditorDriftFinding,
    FileTarget,
    Policy,
    ScalarFinding,
    Utf8Finding,
)
from markdown_text_pkg.domain.policy import parse_policy  # noqa: E402

POLICY_PATH = "policy.json"
ROOT_A = "a.md"
ROOT_B = "b.md"
EDITOR_PATH = "settings.json"
ABS_A = "/tmp/a.md"
ABS_B = "/tmp/b.md"


def create(**overrides: object) -> dict[str, object]:
    """Return the fixed minimum valid schema v1 policy document."""

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
        "rules": [
            {
                "id": "ERR-NUL",
                "severity": "error",
                "class": "nul",
                "rationale": "NUL",
                "codepoints": [{"cp": 0, "hex": "U+0000"}],
            },
            {
                "id": "WARN-ZWSP",
                "severity": "warning",
                "class": "zero_width_space",
                "rationale": "ZWSP",
                "codepoints": [{"cp": 8203, "hex": "U+200B"}],
            },
        ],
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
    document.update(copy.deepcopy(overrides))
    return document


def parsed() -> Policy:
    """Parse the minimum policy for execute() cases."""

    result = parse_policy(create())
    assert isinstance(result, Policy)
    return result


def create_settings() -> dict[str, object]:
    """Return a matching representable editor projection."""

    return {
        "[markdown]": {
            "gremlins.characters": {
                "2013": {"level": "none", "description": "en dash"},
            }
        }
    }


def create_drift_settings() -> dict[str, object]:
    """Return a projection with an extra cloned Gremlins key."""

    settings = create_settings()
    markdown = settings["[markdown]"]
    assert isinstance(markdown, dict)
    characters = markdown["gremlins.characters"]
    assert isinstance(characters, dict)
    characters["200b"] = {"level": "error", "description": "zwsp"}
    return settings


class FakePolicyPort:
    """Typed PolicyPort fake returning a prepared Policy or DomainError."""

    def __init__(self, result: Policy | DomainError) -> None:
        self._result = result
        self.loaded: list[str] = []

    def load(self, path: str) -> Policy | DomainError:
        """Record the path and return the prepared result."""

        self.loaded.append(path)
        return self._result


class FakeFilePort:
    """Typed FilePort fake with prepared discovery, bytes, and editor JSON."""

    def __init__(
        self,
        *,
        discovered: DiscoverResult,
        payloads: dict[str, bytes | DomainError],
        editor: dict[str, object] | DomainError | None = None,
    ) -> None:
        self._discovered = discovered
        self._payloads = payloads
        self._editor = editor
        self.discover_roots: list[tuple[str, ...]] = []

    def discover(self, roots: tuple[str, ...]) -> DiscoverResult:
        """Return the prepared discovery result."""

        self.discover_roots.append(roots)
        return self._discovered

    def read_bytes(self, target: FileTarget) -> bytes | DomainError:
        """Return prepared bytes or a typed IO failure."""

        return self._payloads[target.abs_norm]

    def load_json_object(self, path: str) -> dict[str, object] | DomainError:
        """Return prepared editor JSON or a typed failure."""

        if self._editor is None:
            return DomainError(CODE_INPUT, f"missing editor path: {path}")
        return self._editor


def _target(display: str, abs_norm: str) -> FileTarget:
    """Build one FileTarget from prepared identities."""

    return FileTarget(display_path=display, abs_norm=abs_norm)


class CheckTextExecuteTests:
    """execute() returns typed findings and failures without opening paths."""

    def test_policy_failure_skips_discovery(self) -> None:
        policy_port = FakePolicyPort(DomainError(CODE_POLICY, "bad policy"))
        file_port = FakeFilePort(
            discovered=DiscoverResult(targets=(), failures=()),
            payloads={},
        )
        outcome = CheckText(policy_port, file_port).execute(
            POLICY_PATH, (ROOT_A,), None
        )
        assert outcome.findings == ()
        assert outcome.failures == (DomainError(CODE_POLICY, "bad policy"),)
        assert file_port.discover_roots == []

    def test_warning_bytes_are_findings_not_failures(self) -> None:
        target = _target(ROOT_A, ABS_A)
        file_port = FakeFilePort(
            discovered=DiscoverResult(targets=(target,), failures=()),
            payloads={ABS_A: "a\u200bok".encode("utf-8")},
        )
        outcome = CheckText(FakePolicyPort(parsed()), file_port).execute(
            POLICY_PATH, (ROOT_A,), None
        )
        assert outcome.failures == ()
        assert len(outcome.findings) == 1
        finding = outcome.findings[0]
        assert isinstance(finding, ScalarFinding)
        assert finding.rule_id == "WARN-ZWSP"
        assert finding.severity == "warning"

    def test_nul_and_utf8_findings_are_returned(self) -> None:
        nul_target = _target(ROOT_A, ABS_A)
        utf_target = _target(ROOT_B, ABS_B)
        file_port = FakeFilePort(
            discovered=DiscoverResult(
                targets=(nul_target, utf_target), failures=()
            ),
            payloads={ABS_A: b"\x00", ABS_B: b"\xff"},
        )
        outcome = CheckText(FakePolicyPort(parsed()), file_port).execute(
            POLICY_PATH, (ROOT_A, ROOT_B), None
        )
        assert outcome.failures == ()
        assert len(outcome.findings) == 2
        assert isinstance(outcome.findings[0], ScalarFinding)
        assert isinstance(outcome.findings[1], Utf8Finding)

    def test_discover_and_read_failures_are_collected(self) -> None:
        readable = _target(ROOT_A, ABS_A)
        file_port = FakeFilePort(
            discovered=DiscoverResult(
                targets=(readable,),
                failures=(DomainError(CODE_INPUT, "missing path: gone.md"),),
            ),
            payloads={ABS_A: DomainError(CODE_IO, "unreadable path: a.md")},
        )
        outcome = CheckText(FakePolicyPort(parsed()), file_port).execute(
            POLICY_PATH, (ROOT_A, "gone.md"), None
        )
        assert outcome.findings == ()
        assert len(outcome.failures) == 2
        assert {item.code for item in outcome.failures} == {CODE_INPUT, CODE_IO}

    def test_matching_editor_adds_no_finding(self) -> None:
        target = _target(ROOT_A, ABS_A)
        file_port = FakeFilePort(
            discovered=DiscoverResult(targets=(target,), failures=()),
            payloads={ABS_A: b"ok"},
            editor=create_settings(),
        )
        outcome = CheckText(FakePolicyPort(parsed()), file_port).execute(
            POLICY_PATH, (ROOT_A,), EDITOR_PATH
        )
        assert outcome.findings == ()
        assert outcome.failures == ()

    def test_editor_drift_is_a_finding(self) -> None:
        target = _target(ROOT_A, ABS_A)
        file_port = FakeFilePort(
            discovered=DiscoverResult(targets=(target,), failures=()),
            payloads={ABS_A: b"ok"},
            editor=create_drift_settings(),
        )
        outcome = CheckText(FakePolicyPort(parsed()), file_port).execute(
            POLICY_PATH, (ROOT_A,), EDITOR_PATH
        )
        assert outcome.failures == ()
        assert len(outcome.findings) == 1
        finding = outcome.findings[0]
        assert isinstance(finding, EditorDriftFinding)
        assert finding.extra == ("200b",)

    def test_editor_io_failure_is_collected_with_content_findings(self) -> None:
        target = _target(ROOT_A, ABS_A)
        file_port = FakeFilePort(
            discovered=DiscoverResult(targets=(target,), failures=()),
            payloads={ABS_A: b"\x00"},
            editor=DomainError(CODE_INPUT, "invalid editor JSON: extra data"),
        )
        outcome = CheckText(FakePolicyPort(parsed()), file_port).execute(
            POLICY_PATH, (ROOT_A,), EDITOR_PATH
        )
        assert len(outcome.findings) == 1
        assert isinstance(outcome.findings[0], ScalarFinding)
        assert outcome.failures == (
            DomainError(CODE_INPUT, "invalid editor JSON: extra data"),
        )

    def test_findings_sort_by_path_line_column_and_id(self) -> None:
        later = _target("z.md", "/tmp/z.md")
        earlier = _target("a.md", "/tmp/a.md")
        file_port = FakeFilePort(
            discovered=DiscoverResult(targets=(later, earlier), failures=()),
            payloads={
                "/tmp/z.md": b"\x00",
                "/tmp/a.md": b"\x00",
            },
        )
        outcome = CheckText(FakePolicyPort(parsed()), file_port).execute(
            POLICY_PATH, ("z.md", "a.md"), None
        )
        assert [item.path for item in outcome.findings] == ["a.md", "z.md"]
