"""Test the status derived from the requirement ticks and its agreement check."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from feature_file_validation.domain._test_support import (  # noqa: E402
    make_feature_file,
    make_requirement,
)
from feature_file_validation.domain.rules import (  # noqa: E402
    assess_feature_file,
    validate_feature_file,
)

ALL_TICKED = (make_requirement(1), make_requirement(2))
SOME_TICKED = (make_requirement(1), make_requirement(2, ticked=False))
NONE_TICKED = (make_requirement(1, ticked=False), make_requirement(2, ticked=False))


def test_status_is_achieved_when_every_requirement_is_ticked() -> None:
    document = make_feature_file(status="achieved", requirement_entries=ALL_TICKED)

    assert assess_feature_file(document).status == "achieved"


def test_status_is_partial_when_some_requirements_are_ticked() -> None:
    document = make_feature_file(status="partial", requirement_entries=SOME_TICKED)

    assert assess_feature_file(document).status == "partial"


def test_status_is_not_started_when_no_requirement_is_ticked() -> None:
    document = make_feature_file(status="not started", requirement_entries=NONE_TICKED)

    assert assess_feature_file(document).status == "not started"


def test_file_without_requirement_lines_derives_no_status() -> None:
    assert assess_feature_file(make_feature_file(requirement_entries=())).status is None


def test_declared_status_matching_the_ticks_is_accepted() -> None:
    findings = validate_feature_file(make_feature_file())

    assert not any(
        finding.startswith("feature-file-status-derivation:") for finding in findings
    )


def test_declared_status_mismatch_names_both_values() -> None:
    document = make_feature_file(status="partial", requirement_entries=ALL_TICKED)

    findings = validate_feature_file(document)

    mismatch = [
        finding
        for finding in findings
        if finding.startswith("feature-file-status-derivation:")
    ]
    assert mismatch
    assert "'partial'" in mismatch[0]
    assert "'achieved'" in mismatch[0]
