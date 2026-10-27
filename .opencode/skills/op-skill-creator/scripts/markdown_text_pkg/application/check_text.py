"""Markdown text-integrity use case: one execute() with injected policy and file ports."""

from __future__ import annotations

from markdown_text_pkg.domain.models import (
    CheckOutcome,
    DomainError,
    Finding,
    finding_sort_key,
)
from markdown_text_pkg.domain.policy import compare_editor_projection
from markdown_text_pkg.domain.ports import FilePort, PolicyPort
from markdown_text_pkg.domain.scan import scan_markdown_bytes


class CheckText:
    """Run policy-backed Markdown scans and optional editor-projection comparison."""

    def __init__(self, policy_port: PolicyPort, file_port: FilePort) -> None:
        """Store injected ports; the operation never opens paths itself."""

        self._policy_port = policy_port
        self._file_port = file_port

    def execute(
        self,
        policy_path: str,
        roots: tuple[str, ...],
        editor_path: str | None,
    ) -> CheckOutcome:
        """Return typed findings and failures; never serializes or prints."""

        policy = self._policy_port.load(policy_path)
        if isinstance(policy, DomainError):
            return CheckOutcome(findings=(), failures=(policy,))

        discovered = self._file_port.discover(roots)
        failures: list[DomainError] = list(discovered.failures)
        findings: list[Finding] = []

        for target in discovered.targets:
            payload = self._file_port.read_bytes(target)
            if isinstance(payload, DomainError):
                failures.append(payload)
                continue
            findings.extend(scan_markdown_bytes(payload, policy, target.display_path))

        if editor_path is not None:
            settings = self._file_port.load_json_object(editor_path)
            if isinstance(settings, DomainError):
                failures.append(settings)
            else:
                drift = compare_editor_projection(policy, settings, editor_path)
                if isinstance(drift, DomainError):
                    failures.append(drift)
                elif drift is not None:
                    findings.append(drift)

        ordered_findings = tuple(sorted(findings, key=finding_sort_key))
        ordered_failures = tuple(
            sorted(failures, key=lambda item: (item.code, item.message))
        )
        return CheckOutcome(findings=ordered_findings, failures=ordered_failures)
