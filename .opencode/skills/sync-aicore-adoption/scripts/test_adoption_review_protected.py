"""Protected-document resolution through file and tree member mappings."""

from __future__ import annotations

import json

import pytest

from adoption_test_repos import EngineTestCase

from adoption_contracts import SyncError
from adoption_mapping import _rule_document_destination

FAKE_MARKER_ONLY_AGENT = (
    "# Reviewer — Destination\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Marker added without a mandatory core region.\n"
)

TREE_MANDATORY = "## Mandatory core\n\nTREE_MANDATORY_RULE\n"
TREE_SKILL_SOURCE = (
    "# Skill\n> **Rule layout:** two-section-v1\n\n## Project extensions\n\n"
    "Source skill note.\n\n" + TREE_MANDATORY
)
TREE_SKILL_DESTINATION = (
    "# Skill — Destination\n> **Rule layout:** two-section-v1\n\n## Project extensions\n\n"
    "Destination skill note.\n\n" + TREE_MANDATORY
)
TREE_REFERENCE_MANDATORY = "## Mandatory core\n\nREFERENCE_MANDATORY_RULE\n"
TREE_REFERENCE_SOURCE = (
    "# Reference\n> **Rule layout:** two-section-v1\n\n## Project extensions\n\n"
    "Source reference note.\n\n" + TREE_REFERENCE_MANDATORY
)
TREE_REFERENCE_DESTINATION = (
    "# Reference — Destination\n> **Rule layout:** two-section-v1\n\n## Project extensions\n\n"
    "Destination reference note.\n\n" + TREE_REFERENCE_MANDATORY
)

TREE_PROTECTED_CATALOG = """schema_version: 2
catalog:
  version: 2.5.0
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: protected-skill
    kind: skill
    applicability: { always: true }
    install_strategy: copy
    sync_projection: tree
    rule_documents:
      - .opencode/skills/protected/SKILL.md
      - .opencode/skills/protected/reference.md
    members:
      - { id: tree, source: .opencode/skills/protected, destination: .opencode/skills/protected }
"""

TREE_PROTECTED_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: protected-skill
    mode: adapted
    members:
      - { id: tree, destination: .opencode/skills/protected }
"""


class ProtectedDocumentTests(EngineTestCase):
    """Protected documents resolve through file and tree member mappings."""

    def test_file_projection_round_trips(self) -> None:
        fixture = self.build_protected_agent()
        proc = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision",
            fixture["adopter_rev"],
            "--format",
            "json",
        )
        self.assert_exit(proc, 0)
        assert json.loads(proc.stdout)["compliance"]

    def test_fake_marker_only_boundary_rejected(self) -> None:
        fixture = self.build_protected_agent(
            destination_agent=FAKE_MARKER_ONLY_AGENT, propose=False
        )
        proposal = self.run_cli(
            "propose-lock",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(proposal, 2, "policy_violation")
        assert proposal.stdout == ""

    def test_tree_projection_resolves_every_rule_document(self) -> None:
        fixture = self.build_protected(
            TREE_PROTECTED_CATALOG,
            TREE_PROTECTED_DECLARATION,
            {
                ".opencode/skills/protected/SKILL.md": TREE_SKILL_SOURCE,
                ".opencode/skills/protected/reference.md": TREE_REFERENCE_SOURCE,
                ".opencode/skills/protected/notes.txt": "non-rule member\n",
            },
            {
                ".opencode/skills/protected/SKILL.md": TREE_SKILL_DESTINATION,
                ".opencode/skills/protected/reference.md": TREE_REFERENCE_DESTINATION,
                ".opencode/skills/protected/notes.txt": "non-rule member\n",
            },
            "protected-skill",
        )
        proc = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision",
            fixture["adopter_rev"],
            "--format",
            "json",
        )
        self.assert_exit(proc, 0)
        assert json.loads(proc.stdout)["compliance"]

    def test_ambiguous_resolution_has_no_first_match(self) -> None:
        duplicate = {
            "id": "dup",
            "sync_projection": "file",
            "members": [
                {"id": "first", "source": "first.md"},
                {"id": "second", "source": "./first.md"},
            ],
        }
        duplicate_decl = {
            "members": [
                {"id": "first", "destination": "only-first.md"},
                {"id": "second", "destination": "second.md"},
            ],
        }
        with pytest.raises(SyncError) as caught:
            _rule_document_destination(duplicate, duplicate_decl, "first.md")
        assert caught.value.code == "invalid_mapping"
        assert "exactly one" in caught.value.message
        assert "only-first.md" not in caught.value.message
        overlap = {
            "id": "tree",
            "sync_projection": "tree",
            "members": [
                {"id": "outer", "source": "skills"},
                {"id": "inner", "source": "skills/protected"},
            ],
        }
        overlap_decl = {
            "members": [
                {"id": "outer", "destination": "dest-skills"},
                {"id": "inner", "destination": "dest-inner"},
            ],
        }
        with pytest.raises(SyncError) as overlap_caught:
            _rule_document_destination(
                overlap, overlap_decl, "skills/protected/SKILL.md"
            )
        assert overlap_caught.value.code == "invalid_mapping"
        assert "matched 2" in overlap_caught.value.message

    def test_unique_resolution_returns_only_the_matching_destination(self) -> None:
        catalog_unit = {
            "id": "rules",
            "sync_projection": "file",
            "members": [
                {"id": "spec", "source": "skills/rules.md"},
                {"id": "notes", "source": "skills/notes.txt"},
            ],
        }
        declaration_unit = {
            "members": [
                {"id": "spec", "destination": "local/rules.md"},
                {"id": "notes", "destination": "local/notes.txt"},
            ],
        }
        assert (
            _rule_document_destination(
                catalog_unit, declaration_unit, "skills/rules.md"
            )
            == "local/rules.md"
        )
