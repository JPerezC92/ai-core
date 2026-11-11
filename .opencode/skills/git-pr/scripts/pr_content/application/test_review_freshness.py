"""Specify prepublication remote freshness independently of body structure cases."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pr_content.application.validate_final_body import execute
from pr_content.domain.records import ReviewPreparationError
from pr_content.test_support import RemoteField, create_body, create_divergence, create_metadata


@pytest.mark.parametrize("field", ["number", "headRefOid", "body"])
def test_remote_divergence_rejects_candidate(field: RemoteField) -> None:
    result = execute(baseline=create_metadata(), current=create_divergence(field), body=create_body())
    assert isinstance(result, ReviewPreparationError)
    assert result.code == "REMOTE_DIVERGED"
