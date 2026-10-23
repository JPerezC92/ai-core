"""Unit tests for attribution policy self-exclusion."""

from __future__ import annotations

from attribution_testkit import (
    load_approved_policy,
    make_attribution_line,
    make_changed_file,
    make_changed_files,
    make_snapshot,
)
from scan_attribution import scan_attribution


POLICY = load_approved_policy()


def test_only_the_exact_policy_path_is_excluded_and_exclusion_is_reported() -> None:
    matching_line = make_attribution_line(POLICY)
    excluded_path = POLICY["self_excluded_file"]
    snapshot = make_snapshot(
        changed_files=make_changed_files(
            make_changed_file(path=excluded_path, content=matching_line),
            make_changed_file(path=f"./{excluded_path}", content=matching_line),
        )
    )
    result = scan_attribution(snapshot, POLICY)
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
    result = scan_attribution(snapshot, POLICY)
    assert result["exclusions"] == [
        {"path": windows_path, "reason": "policy self-exclusion"}
    ]
    assert result["matches"] == []
