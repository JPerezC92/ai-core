"""Unit tests for attribution matching and reporting."""

from __future__ import annotations

import pytest

from attribution_testkit import (
    load_approved_policy,
    make_attribution_line,
    make_changed_file,
    make_changed_files,
    make_multiline_matching_contents,
    make_ordinary_identity_mention,
    make_snapshot,
    make_snapshot_with_artifact_content,
)
from scan_attribution import scan_attribution


POLICY = load_approved_policy()


def test_every_approved_marker_identity_pair_matches() -> None:
    for marker_index, marker in enumerate(POLICY["markers"]):
        for identity_index, identity in enumerate(POLICY["identities"]):
            attribution_line = make_attribution_line(
                POLICY, marker_index, identity_index
            )
            snapshot = make_snapshot_with_artifact_content(
                "commit-message",
                attribution_line,
                changed_files=make_changed_files(make_changed_file()),
            )
            result = scan_attribution(snapshot, POLICY)
            assert result["matches"] == [
                {
                    "surface": "commit-message",
                    "source": "a" * 40,
                    "path": None,
                    "line": 1,
                    "marker": marker,
                    "identity": matched_identity,
                }
                for matched_identity in POLICY["identities"]
                if matched_identity.casefold() in attribution_line.casefold()
            ]


def test_ordinary_identity_mention_without_marker_does_not_match() -> None:
    snapshot = make_snapshot_with_artifact_content(
        "pr-body",
        make_ordinary_identity_mention(POLICY),
        changed_files=make_changed_files(make_changed_file()),
    )
    assert scan_attribution(snapshot, POLICY)["matches"] == []


def test_matching_is_case_insensitive_and_reports_surface_source_path_and_line() -> None:
    artifact_content, file_content = make_multiline_matching_contents(POLICY)
    snapshot = make_snapshot_with_artifact_content(
        "commit-message",
        artifact_content,
        changed_files=make_changed_files(
            make_changed_file(path="src/example.py", content=file_content)
        ),
    )
    matches = scan_attribution(snapshot, POLICY)["matches"]
    assert matches == [
        {
            "surface": "commit-message",
            "source": "a" * 40,
            "path": None,
            "line": 3,
            "marker": POLICY["markers"][0],
            "identity": POLICY["identities"][0],
        },
        {
            "surface": "changed-file",
            "source": None,
            "path": "src/example.py",
            "line": 2,
            "marker": POLICY["markers"][0],
            "identity": POLICY["identities"][0],
        },
    ]
    assert all("content" not in match for match in matches)
