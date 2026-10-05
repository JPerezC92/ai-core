"""Protected rule-document catalog schema and ``verified_layout`` shape tests."""

from __future__ import annotations

import pytest

from adoption_test_repos import EngineTestCase

from adoption_contracts import SyncError
from adoption_mapping import _validate_catalog_unit_framing
from adoption_loaders import load_catalog, load_review
from adoption_test_data import CATALOG_REL

PROTECTED_TREE_CATALOG = """schema_version: 2
catalog:
  version: 2.5.0
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: protected
    kind: skill
    applicability: { always: true }
    install_strategy: copy
    sync_projection: tree
__RULE_DOCUMENTS__    members:
      - { id: tree, source: .opencode/skills/protected, destination: .opencode/skills/protected }
"""


class ProtectedRuleDocumentSchemaTests(EngineTestCase):
    """`rule_documents` inventory and `verified_layout` attestation shape."""

    def _catalog(self, rule_documents: str) -> str:
        return PROTECTED_TREE_CATALOG.replace("__RULE_DOCUMENTS__", rule_documents)

    def test_valid_rule_documents_parse_and_are_unique(self) -> None:
        catalog = self.write(
            self.root,
            "protected-valid.yaml",
            self._catalog(
                "    rule_documents:\n"
                "      - .opencode/skills/protected/SKILL.md\n"
                "      - .opencode/skills/protected/reference.md\n"
            ),
        )
        assert isinstance(load_catalog(str(catalog)), dict)

    @pytest.mark.parametrize(
        "case_id,rule_documents",
        [
            ("duplicate", "    rule_documents:\n      - .opencode/skills/protected/SKILL.md\n      - ./.opencode/skills/protected/SKILL.md\n"),
            ("non-markdown", "    rule_documents:\n      - .opencode/skills/protected/README.txt\n"),
            ("outside-member", "    rule_documents:\n      - elsewhere/file.md\n"),
            ("absolute", "    rule_documents:\n      - /abs.md\n"),
            ("empty", "    rule_documents: []\n"),
            ("null", "    rule_documents: null\n"),
            ("wrong-type", "    rule_documents: AGENTS.md\n"),
        ],
    )
    def test_malformed_rule_documents_are_invalid_mapping(
        self, case_id: str, rule_documents: str
    ) -> None:
        catalog = self.write(
            self.root, f"protected-{case_id}.yaml", self._catalog(rule_documents)
        )
        with pytest.raises(SyncError) as caught:
            load_catalog(str(catalog))
        assert caught.value.code == "invalid_mapping", case_id

    def test_omitted_rule_documents_remain_unprotected(self) -> None:
        catalog = self.write(
            self.root, "unprotected-tree.yaml", self._catalog("")
        )
        loaded = load_catalog(str(catalog))
        assert "rule_documents" not in loaded["units"][0]

    def test_duplicate_file_source_and_overlapping_trees_reject(self) -> None:
        duplicate = self.write(
            self.root,
            "duplicate-file-source.yaml",
            """schema_version: 2
catalog:
  version: 2.5.0
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: protected
    kind: skill
    applicability: { always: true }
    install_strategy: copy
    sync_projection: file
    rule_documents:
      - skills/rules.md
    members:
      - { id: first, source: skills/rules.md, destination: first.md }
      - { id: second, source: ./skills/rules.md, destination: second.md }
""",
        )
        overlap = self.write(
            self.root,
            "overlapping-trees.yaml",
            """schema_version: 2
catalog:
  version: 2.5.0
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: protected
    kind: skill
    applicability: { always: true }
    install_strategy: copy
    sync_projection: tree
    rule_documents:
      - skills/protected/SKILL.md
    members:
      - { id: outer, source: skills, destination: skills }
      - { id: inner, source: skills/protected, destination: skills-inner }
""",
        )
        for path in (duplicate, overlap):
            with pytest.raises(SyncError) as caught:
                load_catalog(str(path))
            assert caught.value.code == "invalid_mapping"
            assert "coverage" in caught.value.message

    def test_unique_file_mapping_accepts_one_protected_member(self) -> None:
        catalog = self.write(
            self.root,
            "unique-file-mapping.yaml",
            """schema_version: 2
catalog:
  version: 2.5.0
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: protected
    kind: skill
    applicability: { always: true }
    install_strategy: copy
    sync_projection: file
    rule_documents:
      - skills/rules.md
    members:
      - { id: rules, source: skills/rules.md, destination: skills/rules.md }
      - { id: notes, source: skills/notes.txt, destination: skills/notes.txt }
""",
        )
        loaded = load_catalog(str(catalog))
        assert loaded["units"][0]["rule_documents"] == ["skills/rules.md"]

    def test_unprotected_overlapping_trees_remain_allowed(self) -> None:
        catalog = self.write(
            self.root,
            "unprotected-overlap.yaml",
            """schema_version: 2
catalog:
  version: 2.5.0
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: files
    kind: skill
    applicability: { always: true }
    install_strategy: copy
    sync_projection: tree
    members:
      - { id: outer, source: skills, destination: skills }
      - { id: inner, source: skills/protected, destination: skills-inner }
""",
        )
        assert isinstance(load_catalog(str(catalog)), dict)

    def test_ambiguous_protected_catalog_is_rejected_by_propose(self) -> None:
        catalog = """schema_version: 2
catalog:
  version: 2.5.0
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: protected
    kind: skill
    applicability: { always: true }
    install_strategy: copy
    sync_projection: file
    rule_documents:
      - skills/rules.md
    members:
      - { id: first, source: skills/rules.md, destination: first.md }
      - { id: second, source: skills/rules.md, destination: second.md }
"""
        declaration = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: protected
    mode: adapted
    members:
      - { id: first, destination: first.md }
      - { id: second, destination: second.md }
"""
        self.init_repo(self.upstream)
        self.write(self.upstream, CATALOG_REL, catalog)
        self.write(self.upstream, "skills/rules.md", "source\n")
        self.commit(self.upstream, "ambiguous catalog")
        self.init_repo(self.adopter)
        self.write(self.adopter, ".aicore/adoption.yaml", declaration)
        revision = self.commit(self.adopter, "declaration")
        before = self.worktree_bytes(self.upstream)
        proposal = self.run_cli(
            "propose-lock",
            "--upstream-repo", str(self.upstream),
            "--catalog", str(self.upstream / CATALOG_REL),
            "--declaration", str(self.adopter / ".aicore/adoption.yaml"),
            "--adopter-revision", revision,
        )
        self.assert_exit(proposal, 2, "invalid_mapping")
        assert proposal.stdout == ""
        assert "coverage" in proposal.stderr
        assert self.worktree_bytes(self.upstream) == before

    def test_assertions_unit_rejects_rule_documents(self) -> None:
        catalog = self.write(
            self.root,
            "assertions-protected.yaml",
            """schema_version: 2
catalog:
  version: 2.5.0
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: config
    kind: config
    applicability: { always: true }
    install_strategy: merge
    sync_projection: assertions
    destination: opencode.jsonc
    rule_documents:
      - opencode.jsonc
    assertions:
      - { id: sudo-deny, contains: '"sudo *": "deny"' }
""",
        )
        with pytest.raises(SyncError) as caught:
            load_catalog(str(catalog))
        assert caught.value.code == "invalid_mapping"

    def test_verified_layout_is_a_closed_value(self) -> None:
        valid = self.write(
            self.root,
            "verified-layout-valid.yaml",
            """schema_version: 2
upstream_repository: example/upstream
decisions:
  - unit: protected
    decision: applied
    reviewer: reviewer
    evidence: reviewed
    verified_layout: two-section-v1
""",
        )
        assert isinstance(load_review(str(valid)), dict)
        invalid = self.write(
            self.root,
            "verified-layout-invalid.yaml",
            """schema_version: 2
upstream_repository: example/upstream
decisions:
  - unit: protected
    decision: applied
    reviewer: reviewer
    evidence: reviewed
    verified_layout: two-section-v2
""",
        )
        with pytest.raises(SyncError) as caught:
            load_review(str(invalid))
        assert caught.value.code == "invalid_declaration"
        assert "verified_layout" in caught.value.message

    def test_protected_units_reject_bypass_modes(self) -> None:
        catalog_units = {
            "protected": {
                "id": "protected",
                "sync_projection": "tree",
                "rule_documents": [".opencode/skills/protected/SKILL.md"],
            }
        }
        for mode, extra in (
            (
                "replacement",
                {"replacement_members": [{"id": "tree", "destination": "x", "projection": "file"}]},
            ),
            ("destination_owned", {"members": [{"id": "tree", "destination": "x"}]}),
        ):
            declaration = {"protected": {"id": "protected", "mode": mode, **extra}}
            with pytest.raises(SyncError) as caught:
                _validate_catalog_unit_framing(catalog_units, declaration)
            assert caught.value.code == "invalid_declaration", mode
        _validate_catalog_unit_framing(
            catalog_units, {"protected": {"id": "protected", "mode": "not_applicable"}}
        )
