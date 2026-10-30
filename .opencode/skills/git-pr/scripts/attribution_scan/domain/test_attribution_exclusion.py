"""Test attribution policy self-exclusion over changed-file paths."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SCRIPTS))

from attribution_testkit import (  # noqa: E402
    load_approved_policy,
    make_attribution_line,
    make_changed_file,
    make_changed_files,
    make_snapshot,
)
from attribution_scan.domain.matching import scan_validated_snapshot  # noqa: E402
from attribution_scan.domain.records import PolicyValidationError  # noqa: E402


POLICY = load_approved_policy()

# Narrow the shared factory result so a broken approved-policy fixture fails here
# instead of surfacing as an unrelated rejection assertion in the cases below.
assert not isinstance(POLICY, PolicyValidationError), "approved policy must validate"


def test_only_the_exact_policy_path_is_excluded_and_exclusion_is_reported() -> None:
    matching_line = make_attribution_line(POLICY)
    excluded_path = POLICY["self_excluded_file"]
    snapshot = make_snapshot(
        changed_files=make_changed_files(
            make_changed_file(path=excluded_path, content=matching_line),
            make_changed_file(path=f"./{excluded_path}", content=matching_line),
        )
    )
    result = scan_validated_snapshot(snapshot, POLICY)
    assert result["exclusions"] == [
        {"path": excluded_path, "reason": "policy self-exclusion"}
    ]
    assert [match["path"] for match in result["matches"]] == [f"./{excluded_path}"]


def test_policy_self_exclusion_normalizes_slash_direction() -> None:
    windows_path = POLICY["self_excluded_file"].replace("/", "\\")
    snapshot = make_snapshot(
        changed_files=make_changed_files(
            make_changed_file(path=windows_path, content=make_attribution_line(POLICY))
        )
    )
    result = scan_validated_snapshot(snapshot, POLICY)
    assert result["exclusions"] == [
        {"path": windows_path, "reason": "policy self-exclusion"}
    ]
    assert result["matches"] == []
