"""Specify exact persisted-body verification without upload or retry authority."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pr_review.application.verify_persisted_body import execute
from pr_review.domain.records import ReviewPreparationError
from pr_review.test_support import (
    MetadataExtraSite, RemoteField, create_body, create_divergence, create_metadata,
    create_metadata_with_undeclared_key,
)


def test_exact_readback_accepts_intended_body() -> None:
    result = execute(expected=create_metadata(), persisted=create_metadata(), body=create_body())
    assert not isinstance(result, ReviewPreparationError)
    assert result.body == create_body()


def test_documented_seven_field_metadata_still_verifies_and_still_detects_divergence() -> None:
    documented = create_metadata()
    assert set(documented) == {
        "number", "headRefOid", "baseRefName", "headRefName", "state", "title", "body",
    }
    accepted = execute(expected=documented, persisted=create_metadata(), body=create_body())
    assert not isinstance(accepted, ReviewPreparationError)
    diverged = execute(expected=documented, persisted=create_metadata(body="Changed remotely"), body=create_body())
    assert isinstance(diverged, ReviewPreparationError)
    assert diverged.code == "READBACK_DIVERGED"


@pytest.mark.parametrize("site", ["expected", "persisted", "both"])
def test_undeclared_metadata_key_rejects_without_a_key_error(site: MetadataExtraSite) -> None:
    undeclared = create_metadata_with_undeclared_key()
    expected = undeclared if site in ("expected", "both") else create_metadata()
    persisted = undeclared if site in ("persisted", "both") else create_metadata()
    result = execute(expected=expected, persisted=persisted, body=create_body())
    assert isinstance(result, ReviewPreparationError)
    assert result.code == "METADATA_INVALID"


@pytest.mark.parametrize("field", ["number", "headRefOid", "body"])
def test_divergent_readback_blocks_without_repair(field: RemoteField) -> None:
    persisted = create_divergence(field)
    original = dict(persisted)
    result = execute(expected=create_metadata(), persisted=persisted, body=create_body())
    assert isinstance(result, ReviewPreparationError)
    assert result.code == "READBACK_DIVERGED"
    assert persisted == original
