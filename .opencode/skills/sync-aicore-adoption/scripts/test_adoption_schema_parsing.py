"""Schema parsing, digest golden-vector, and declaration validation tests."""

from __future__ import annotations

import pytest
import yaml

from adoption_test_repos import EngineTestCase

from adoption_contracts import SyncError
from adoption_digests import declaration_unit_digest, unit_digest
from adoption_loaders import (
    load_catalog,
    load_declaration,
    load_lock,
    load_review,
)
from adoption_test_data import (
    EMPTY_REVIEW,
    GREETING_CATALOG,
    GREETING_DECLARATION,
    INCOMPLETE_DECLARATION,
    NOT_APPLICABLE_DECLARATION,
    TWO_UNIT_CATALOG,
    UPSTREAM_ID,
    greeting_lock_document,
    member_file,
    sha256_text,
    snapshot_digest,
)


class DigestGoldenTests(EngineTestCase):
    def test_file_hello_golden_vector(self) -> None:
        digest = member_file("hello\n")
        assert digest == (
            "sha256:cf41078b082e3740168bd7ad534ba1b70b12489c7ab43c6fb53743b0f3527887"
        ), f"golden vector mismatch: {digest}"


class SchemaParsingTests(EngineTestCase):
    def test_v2_documents_parse(self) -> None:
        catalog = self.write(self.root, "catalog.yaml", GREETING_CATALOG)
        declaration = self.write(self.root, "declaration.yaml", GREETING_DECLARATION)
        review = self.write(self.root, "review.yaml", EMPTY_REVIEW)
        lock = greeting_lock_document("a" * 40, "hello\n", "hello\n")
        lock_path = self.write(self.root, "lock.yaml", yaml.safe_dump(lock, sort_keys=False))
        assert isinstance(load_catalog(str(catalog)), dict)
        assert isinstance(load_declaration(str(declaration)), dict)
        assert isinstance(load_review(str(review)), dict)
        assert isinstance(load_lock(str(lock_path)), dict)

    @pytest.mark.parametrize(
        "name,loader_name,text",
        [
            ("catalog", "load_catalog", "schema_version: 1\ncatalog: {}\nunits: []\n"),
            ("declaration", "load_declaration", "schema_version: 1\nunits: []\n"),
            ("review", "load_review", "schema_version: 1\ndecisions: []\n"),
            ("lock", "load_lock", "schema_version: 1\nunits: []\n"),
        ],
    )
    def test_v1_documents_require_upgrade(self, name: str, loader_name: str, text: str) -> None:
        path = self.write(self.root, f"v1-{name}.yaml", text)
        loaders = {
            "load_catalog": load_catalog,
            "load_declaration": load_declaration,
            "load_review": load_review,
            "load_lock": load_lock,
        }
        loader = loaders[loader_name]
        with pytest.raises(SyncError) as caught:
            loader(str(path))
        assert caught.value.code == "schema_upgrade_required", f"{name}: {caught.value.message}"

    def test_v1_catalog_cli_exit_2(self) -> None:
        fixture = self.build_greeting()
        v1_catalog = self.write(
            self.root, "v1-cli-catalog.yaml", "schema_version: 1\ncatalog: {}\nunits: []\n"
        )
        args = [
            "check", "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(v1_catalog), "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]), "--lock", str(fixture["lock"]),
            "--adopter-revision", fixture["adopter_rev"],
        ]
        self.assert_exit(self.run_cli(*args), 2, "schema_upgrade_required")

    def test_unknown_projection_is_fatal(self) -> None:
        catalog = self.write(
            self.root,
            "unknown-projection.yaml",
            GREETING_CATALOG.replace("sync_projection: file", "sync_projection: mystery"),
        )
        with pytest.raises(SyncError) as caught:
            load_catalog(str(catalog))
        assert caught.value.code == "unsupported_projection"

    def test_transition_bound_decision_requires_complete_fresh_evidence(self) -> None:
        review = self.write(
            self.root,
            "incomplete-transition-review.yaml",
            """schema_version: 2
upstream_repository: org/core
transition:
  baseline_lock_digest: sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
  target_source_commit: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
  declaration_digest: sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
decisions:
  - unit: greeting
    decision: applied
    reviewer: reviewer
    evidence: reviewed
""",
        )
        with pytest.raises(SyncError) as caught:
            load_review(str(review))
        assert caught.value.code == "invalid_declaration"

    def test_duplicate_review_decision_unit_is_invalid_declaration(self) -> None:
        review = self.write(
            self.root,
            "duplicate-decision-review.yaml",
            """schema_version: 2
upstream_repository: org/core
decisions:
  - unit: greeting
    decision: applied
    reviewer: reviewer
  - unit: greeting
    decision: declined
    reviewer: reviewer
""",
        )
        with pytest.raises(SyncError) as caught:
            load_review(str(review))
        assert caught.value.code == "invalid_declaration"
        assert "duplicated" in caught.value.message

    def test_transition_bound_decision_with_empty_evidence_is_rejected(self) -> None:
        template = """schema_version: 2
upstream_repository: org/core
transition:
  baseline_lock_digest: sha256:{digest}
  target_source_commit: {commit}
  declaration_digest: sha256:{digest}
decisions:
  - unit: greeting
    decision: applied
    reviewer: reviewer
    evidence: "{evidence}"
    reviewed_upstream_digest: sha256:{digest}
    reviewed_destination_digest: sha256:{digest}
"""
        digest = "a" * 64
        valid = self.write(
            self.root,
            "nonempty-evidence-review.yaml",
            template.format(digest=digest, commit="a" * 40, evidence="reviewed"),
        )
        assert isinstance(load_review(str(valid)), dict)

        empty = self.write(
            self.root,
            "empty-evidence-review.yaml",
            template.format(digest=digest, commit="a" * 40, evidence=""),
        )
        with pytest.raises(SyncError) as caught:
            load_review(str(empty))
        assert caught.value.code == "invalid_declaration"
        assert "evidence" in caught.value.message


class DeclarationValidationTests(EngineTestCase):
    def test_missing_applicable_unit_is_declaration_incomplete(self) -> None:
        fixture = self.build_greeting(declaration=INCOMPLETE_DECLARATION)
        args = ["check", *self.base_check_args(fixture), "--adopter-revision", fixture["adopter_rev"]]
        self.assert_exit(self.run_cli(*args), 2, "declaration_incomplete")

    def test_always_unit_not_applicable_is_invalid_applicability(self) -> None:
        def lock_builder(accepted: str) -> dict[str, object]:
            rows = [{"id": "greeting", "mode": "not_applicable"}]
            return {
                "schema_version": 2,
                "upstream_repository": UPSTREAM_ID,
                "accepted_source_commit": accepted,
                "accepted_catalog_digest": sha256_text(GREETING_CATALOG),
                "declaration_digest": sha256_text(NOT_APPLICABLE_DECLARATION),
                "review_digest": sha256_text(EMPTY_REVIEW),
                "accepted_snapshot_digest": snapshot_digest(NOT_APPLICABLE_DECLARATION, EMPTY_REVIEW, rows),
                "units": rows,
            }

        fixture = self.build_raw(
            GREETING_CATALOG,
            NOT_APPLICABLE_DECLARATION,
            EMPTY_REVIEW,
            lock_builder,
            {"content/greeting.txt": "hello\n"},
            {"content/greeting.txt": "hello\n"},
        )
        args = ["check", *self.base_check_args(fixture), "--adopter-revision", fixture["adopter_rev"]]
        self.assert_exit(self.run_cli(*args), 2, "invalid_applicability")

    def test_digest_bound_incomplete_accepted_mapping_exits_two(self) -> None:
        incomplete_declaration = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: greeting
    mode: mirror
    members:
      - { id: file, destination: content/greeting.txt }
  - id: note
    mode: adapted
"""

        def lock_builder(accepted: str) -> dict[str, object]:
            greeting_upstream = member_file("hello\n")
            note_upstream = member_file("note v1\n")
            rows = [
                {
                    "id": "greeting",
                    "mode": "mirror",
                    "declaration_unit_digest": declaration_unit_digest(
                        "mirror",
                        [{"id": "file", "destination": "content/greeting.txt"}],
                        [],
                    ),
                    "accepted_upstream_digest": unit_digest(
                        [("file", greeting_upstream)]
                    ),
                    "members": [{
                        "id": "file",
                        "destination": "content/greeting.txt",
                        "accepted_upstream_digest": greeting_upstream,
                        "accepted_destination_digest": member_file("hello\n"),
                    }],
                },
                {
                    "id": "note",
                    "mode": "adapted",
                    "declaration_unit_digest": declaration_unit_digest("adapted", [], []),
                    "accepted_upstream_digest": unit_digest([("file", note_upstream)]),
                    "members": [{
                        "id": "file",
                        "destination": "content/note-local.txt",
                        "accepted_upstream_digest": note_upstream,
                        "accepted_destination_digest": member_file("note adapted v1\n"),
                    }],
                },
            ]
            return {
                "schema_version": 2,
                "upstream_repository": UPSTREAM_ID,
                "accepted_source_commit": accepted,
                "accepted_catalog_digest": sha256_text(TWO_UNIT_CATALOG),
                "declaration_digest": sha256_text(incomplete_declaration),
                "review_digest": sha256_text(EMPTY_REVIEW),
                "accepted_snapshot_digest": snapshot_digest(
                    incomplete_declaration, EMPTY_REVIEW, rows
                ),
                "units": rows,
            }

        fixture = self.build_raw(
            TWO_UNIT_CATALOG,
            incomplete_declaration,
            EMPTY_REVIEW,
            lock_builder,
            {"content/greeting.txt": "hello\n", "content/note.txt": "note v1\n"},
            {
                "content/greeting.txt": "hello\n",
                "content/note-local.txt": "note adapted v1\n",
            },
        )
        proc = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(proc, 2, "invalid_declaration")
        assert proc.stdout == ""
