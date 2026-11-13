"""Test policy shape validation as returned business errors, not raised exceptions."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SCRIPTS))

from attribution_testkit import (  # noqa: E402
    load_approved_policy,
    make_malformed_policy,
)
from attribution_scan.domain.records import PolicyValidationError  # noqa: E402
from attribution_scan.domain.validation import validate_policy  # noqa: E402


POLICY = load_approved_policy()

# Narrow the shared factory result so a broken approved-policy fixture fails here
# instead of surfacing as an unrelated rejection assertion in the cases below.
assert not isinstance(POLICY, PolicyValidationError), "approved policy must validate"


def test_malformed_policy_is_rejected() -> None:
    result = validate_policy(make_malformed_policy(POLICY, "identities"))

    assert isinstance(result, PolicyValidationError)
    assert result.code == "POLICY_INVALID"
    assert result.message == "policy identities must be a non-empty string list"
