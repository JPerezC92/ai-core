"""Specify exact persisted-body verification without upload or retry authority."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pr_review.application.verify_persisted_body import execute
from pr_review.domain.records import ReviewPreparationError
from pr_review.test_support import (
    RemoteField, create_body, create_divergence, create_metadata,
    create_metadata_with_undeclared_key,
)


def test_exact_readback_accepts_intended_body() -> None:
    result = execute(expected=create_metadata(), persisted=create_metadata(), body=create_body())
    assert not isinstance(result, ReviewPreparationError)
    assert result.body == create_body()


def test_unchanged_capture_verifies_and_a_changed_persisted_body_is_detected() -> None:
    accepted = execute(expected=create_metadata(), persisted=create_metadata(), body=create_body())
    assert not isinstance(accepted, ReviewPreparationError)
    diverged = execute(
        expected=create_metadata(), persisted=create_metadata(body="Changed remotely"), body=create_body(),
    )
    assert isinstance(diverged, ReviewPreparationError)
    assert diverged.code == "READBACK_DIVERGED"


def test_baseline_key_missing_from_the_persisted_capture_is_reported_as_divergence() -> None:
    result = execute(
        expected=create_metadata_with_undeclared_key(), persisted=create_metadata(), body=create_body(),
    )
    assert isinstance(result, ReviewPreparationError)
    assert result.code == "READBACK_DIVERGED"


def test_persisted_capture_carrying_a_field_the_intended_capture_lacks_is_rejected() -> None:
    result = execute(
        expected=create_metadata(), persisted=create_metadata_with_undeclared_key(), body=create_body(),
    )
    assert isinstance(result, ReviewPreparationError)
    assert result.code == "READBACK_DIVERGED"
    assert "url" in result.message


def test_persisted_capture_missing_a_field_the_intended_capture_carries_is_rejected() -> None:
    intended = create_metadata()
    persisted = dict(intended)
    del persisted["title"]
    result = execute(expected=intended, persisted=persisted, body=create_body())
    assert isinstance(result, ReviewPreparationError)
    assert result.code == "READBACK_DIVERGED"
    assert "title" in result.message


def test_captures_carrying_the_same_undeclared_field_are_accepted() -> None:
    capture = create_metadata_with_undeclared_key()
    result = execute(expected=capture, persisted=dict(capture), body=create_body())
    assert not isinstance(result, ReviewPreparationError)
    assert result.body == create_body()


@pytest.mark.parametrize("field", ["number", "headRefOid", "body"])
def test_divergent_readback_blocks_without_repair(field: RemoteField) -> None:
    persisted = create_divergence(field)
    original = dict(persisted)
    result = execute(expected=create_metadata(), persisted=persisted, body=create_body())
    assert isinstance(result, ReviewPreparationError)
    assert result.code == "READBACK_DIVERGED"
    assert persisted == original
