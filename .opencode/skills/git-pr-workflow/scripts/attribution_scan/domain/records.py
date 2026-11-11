"""Define attribution input, scan-result records and returned validation errors."""

from dataclasses import dataclass
from typing import ClassVar, TypedDict


class AttributionPolicy(TypedDict):
    """The validated markers and identities used by the scanner."""

    schema: int
    self_excluded_file: str
    markers: list[str]
    identities: list[str]


class Artifact(TypedDict):
    """One complete PR or commit-message artifact."""

    surface: str
    source: str
    content: str


class ChangedFile(TypedDict):
    """One changed-file body in the immutable snapshot."""

    path: str
    content: str


class Snapshot(TypedDict):
    """The complete PR content snapshot evaluated by the scanner."""

    schema: int
    pr_number: int
    head_sha: str
    base: str
    artifacts: list[Artifact]
    changed_files: list[ChangedFile]


class Match(TypedDict):
    """A line-level attribution finding without source-text disclosure."""

    surface: str
    source: str | None
    path: str | None
    line: int
    marker: str
    identity: str


class Exclusion(TypedDict):
    """The one policy-file exclusion applied to changed-file bodies."""

    path: str
    reason: str


class ScanResult(TypedDict):
    """Deterministic scan metadata, findings, and applied exclusions."""

    pr_number: int
    head_sha: str
    base: str
    matches: list[Match]
    exclusions: list[Exclusion]


@dataclass(frozen=True)
class ScanInput:
    """Carry decoded, not yet validated inputs into the scan operation."""

    snapshot_value: object
    policy_value: object


@dataclass(frozen=True)
class PolicyValidationError:
    """Describe a rejected policy as a returned business-error value."""

    message: str
    code: ClassVar[str] = "POLICY_INVALID"


@dataclass(frozen=True)
class SnapshotValidationError:
    """Describe a rejected snapshot as a returned business-error value."""

    message: str
    code: ClassVar[str] = "SNAPSHOT_INVALID"
