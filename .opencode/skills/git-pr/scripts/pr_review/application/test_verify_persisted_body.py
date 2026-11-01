"""Specify exact persisted-body verification without upload or retry authority."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pr_review.application.verify_persisted_body import execute
from pr_review.domain.records import ReviewPreparationError
from pr_review.test_support import RemoteField, create_body, create_divergence, create_metadata


def test_exact_readback_accepts_intended_body() -> None:
    result = execute(expected=create_metadata(), persisted=create_metadata(), body=create_body())
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
