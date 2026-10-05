"""Regression guard: AICore debt never reaches a destination.

The debt register is destination-owned. Its catalog source is the shipped
0-entry ``knowledge/debt.template.md`` and a ``mirror`` declaration is rejected,
so a source register can never converge into a destination. These tests bind the
shipped template bytes and the engine's fail-closed rejection. They never parse
or classify debt prose.
"""

from __future__ import annotations

import yaml

import pytest

from adoption_contracts import SyncError
from adoption_loaders import load_catalog
from adoption_mapping import _validate_catalog_unit_framing
from adoption_reconciliation import _debt_mirror_disposition
from adoption_test_acceptance_data import (
    BOOTSTRAP_DECLARATION,
    BOOTSTRAP_EXISTING_DEBT,
    DEBT_TEMPLATE,
)
from adoption_test_data import CATALOG_REL, EMPTY_REVIEW
from adoption_test_enrollment import _enroll_member
from adoption_test_repos import EngineTestCase, repository_root

# A simulated copied source register. The guard must never let its marker reach a
# destination. This is a byte fixture, not a parsed debt record.
COPIED_SOURCE_REGISTER = "DEBT-AICORE source history must never be imported.\n"

UNKNOWN_STRATEGY_CATALOG = """schema_version: 2
catalog:
  version: 2.5.0
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: thing
    kind: infra
    applicability: { always: true }
    install_strategy: symlink
    sync_projection: file
    members:
      - { id: file, source: a.txt, destination: a.txt }
"""


def _mirror_debt_declaration() -> str:
    """Return the bootstrap declaration with ``knowledge-debt`` set to mirror."""
    document = yaml.safe_load(BOOTSTRAP_DECLARATION)
    assert isinstance(document, dict)
    for unit in document["units"]:
        if unit["id"] == "knowledge-debt":
            unit["mode"] = "mirror"
    return yaml.safe_dump(document, sort_keys=False)


class DebtGuardTests(EngineTestCase):
    """The debt template ships empty and the debt unit rejects ``mirror``."""

    def test_shipped_debt_template_is_zero_entry(self) -> None:
        template = (
            repository_root() / "knowledge" / "debt.template.md"
        ).read_text(encoding="utf-8")
        assert template == DEBT_TEMPLATE
        assert "DEBT-" not in template
        assert template.rstrip("\n").endswith("## Register")

    def test_catalog_debt_unit_targets_template_and_preserves(self) -> None:
        catalog = yaml.safe_load(
            (repository_root() / CATALOG_REL).read_text(encoding="utf-8")
        )
        assert isinstance(catalog, dict)
        unit = next(item for item in catalog["units"] if item["id"] == "knowledge-debt")
        assert unit["install_strategy"] == "preserve"
        assert unit["members"] == [
            {
                "id": "file",
                "source": "knowledge/debt.template.md",
                "destination": "knowledge/debt.md",
            }
        ]

    def test_unknown_install_strategy_is_invalid_mapping(self) -> None:
        path = self.write(self.root, "unknown-strategy.yaml", UNKNOWN_STRATEGY_CATALOG)
        with pytest.raises(SyncError) as caught:
            load_catalog(str(path))
        assert caught.value.code == "invalid_mapping"
        assert "install_strategy" in caught.value.message

    def test_fresh_preparation_is_zero_entry_template(self) -> None:
        source = (
            repository_root() / "knowledge" / "debt.template.md"
        ).read_text(encoding="utf-8")
        prepared = _enroll_member(None, source, DEBT_TEMPLATE)
        assert prepared == DEBT_TEMPLATE
        assert "DEBT-" not in prepared

    def test_copied_source_register_never_becomes_the_fresh_result(self) -> None:
        prepared = _enroll_member(None, COPIED_SOURCE_REGISTER, DEBT_TEMPLATE)
        assert prepared == DEBT_TEMPLATE
        assert "DEBT-AICORE" not in prepared
        assert "DEBT-" not in prepared

    def test_existing_destination_debt_is_retained(self) -> None:
        prepared = _enroll_member(
            BOOTSTRAP_EXISTING_DEBT, COPIED_SOURCE_REGISTER, DEBT_TEMPLATE
        )
        assert prepared == BOOTSTRAP_EXISTING_DEBT
        assert "DEBT-014" in prepared
        assert "DEBT-AICORE" not in prepared
        assert "DEBT-001" not in prepared

    def test_debt_mirror_declaration_is_rejected_by_framing(self) -> None:
        catalog_units = {
            "knowledge-debt": {
                "id": "knowledge-debt",
                "sync_projection": "file",
                "members": [
                    {
                        "id": "file",
                        "source": "knowledge/debt.template.md",
                        "destination": "knowledge/debt.md",
                    }
                ],
            }
        }
        declaration_units = {
            "knowledge-debt": {
                "id": "knowledge-debt",
                "mode": "mirror",
                "members": [{"id": "file", "destination": "knowledge/debt.md"}],
            }
        }
        with pytest.raises(SyncError) as caught:
            _validate_catalog_unit_framing(catalog_units, declaration_units)
        assert caught.value.code == "invalid_declaration"
        assert "knowledge-debt" in caught.value.message

    def test_debt_mirror_is_a_blocking_disposition(self) -> None:
        assert _debt_mirror_disposition("knowledge-debt", "mirror") == "policy_violation"
        assert _debt_mirror_disposition("knowledge-debt", "adapted") is None
        assert _debt_mirror_disposition("plans", "mirror") is None
        assert _debt_mirror_disposition("user-stories", "mirror") is None

    def test_debt_mirror_declaration_is_rejected_by_propose_lock(self) -> None:
        self.init_bootstrap_upstream()
        self.init_repo(self.adopter)
        self.write(self.adopter, ".aicore/adoption.yaml", _mirror_debt_declaration())
        self.write(self.adopter, ".aicore/adoption-review.yaml", EMPTY_REVIEW)
        revision = self.commit(self.adopter, "mirror debt declaration")
        proposal = self.run_cli(
            "propose-lock",
            "--upstream-repo", str(self.upstream),
            "--catalog", str(self.upstream / CATALOG_REL),
            "--declaration", str(self.adopter / ".aicore/adoption.yaml"),
            "--review", str(self.adopter / ".aicore/adoption-review.yaml"),
            "--adopter-revision", revision,
        )
        self.assert_exit(proposal, 2, "invalid_declaration")
        assert "knowledge-debt" in proposal.stderr
