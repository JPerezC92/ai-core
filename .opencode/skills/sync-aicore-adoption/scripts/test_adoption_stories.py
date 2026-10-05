"""Portable-story index projection and collision behavior tests."""

from __future__ import annotations

import json

import yaml

import pytest

from adoption_test_repos import EngineTestCase

from adoption_content import _story_index_collisions
from adoption_contracts import (
    StoryMergeMember,
    SyncError,
)
from adoption_git import (
    _GitRepo,
    _RevisionSnapshot,
)
from adoption_loaders import _raw_file_digest, load_catalog
from adoption_stories import merge_story_index
from adoption_test_data import (
    EMPTY_REVIEW,
    STORY_CATALOG,
    STORY_CORE_INDEX,
    STORY_DECLARATION,
    STORY_DESTINATION_INDEX,
    review_with_transition,
)
class StoryIndexProjectionTests(EngineTestCase):
    """Portable-story index merge: seeding, replacement, and collision reporting."""

    def _members(self, *entries: tuple[str, str, str | None]) -> list[StoryMergeMember]:
        members: list[StoryMergeMember] = []
        for slug, destination, policy in entries:
            member: StoryMergeMember = {
                "id": slug,
                "destination": destination,
                "collision_policy": policy,
            }
            members.append(member)
        return members

    def test_unknown_collision_policy_is_invalid_mapping(self) -> None:
        catalog = self.write(
            self.root,
            "bad-collision-policy.yaml",
            STORY_CATALOG.replace("collision_policy: core_wins", "collision_policy: always_wins"),
        )
        with pytest.raises(SyncError) as caught:
            load_catalog(str(catalog))
        assert caught.value.code == "invalid_mapping", caught.value.message

    def test_fresh_index_seeds_only_applicable_core_rows(self) -> None:
        merged, collisions = merge_story_index(
            STORY_CORE_INDEX.encode("utf-8"),
            None,
            self._members(
                ("alpha", "user-stories/alpha.md", "core_wins"),
                ("beta", "user-stories/beta.md", "core_wins"),
            ),
        )
        text = merged.decode("utf-8")
        assert "| `alpha` | Alpha | active | ep-a | `a` |" in text
        assert "| `beta` | Beta | active | ep-b | `b` |" in text
        assert "| `gamma` |" not in text
        assert "| `aicore-only` |" not in text
        assert text.startswith("# User Stories\n")
        assert text.endswith("## Appendices\n\nCore appendix notes.\n")
        assert collisions == []

    def test_existing_index_merge_preserves_crlf_destination_rows_and_trailing(self) -> None:
        destination = (
            "# User Stories\r\n\r\n"
            "| Slug | Title | Status | Epic | Affected areas |\r\n"
            "|---|---|---|---|---|\r\n"
            "| `alpha` | Alpha local edit | active | ep-a | `a` |\r\n"
            "| `dest-own` | Destination owned | active | local | `d` |\r\n"
            "\r\n## Trailing\r\n\r\nkeep trailing\r\n"
        ).encode("utf-8")
        merged, collisions = merge_story_index(
            STORY_CORE_INDEX.encode("utf-8"),
            destination,
            self._members(
                ("alpha", "user-stories/alpha.md", "core_wins"),
                ("beta", "user-stories/beta.md", "core_wins"),
            ),
        )
        assert b"\n" not in merged.replace(b"\r\n", b""), "every line ending must stay CRLF"
        assert b"| `alpha` | Alpha | active | ep-a | `a` |\r\n" in merged
        assert b"| `beta` | Beta | active | ep-b | `b` |\r\n" in merged
        assert b"| `dest-own` | Destination owned | active | local | `d` |\r\n" in merged
        assert merged.endswith(b"\r\n## Trailing\r\n\r\nkeep trailing\r\n")
        assert collisions == [
            "collision: path user-stories/alpha.md; core wins",
            "collision: slug alpha; core wins",
        ]

    def test_identical_rows_report_no_collisions_and_bytes_unchanged(self) -> None:
        core = STORY_CORE_INDEX.encode("utf-8")
        merged, collisions = merge_story_index(
            core,
            core,
            self._members(
                ("alpha", "user-stories/alpha.md", "core_wins"),
                ("beta", "user-stories/beta.md", "core_wins"),
                ("gamma", "user-stories/gamma.md", "core_wins"),
            ),
        )
        assert merged == core
        assert collisions == []

    def test_differing_core_wins_rows_report_path_and_slug_once(self) -> None:
        destination = STORY_DESTINATION_INDEX.encode("utf-8")
        merged, collisions = merge_story_index(
            STORY_CORE_INDEX.encode("utf-8"),
            destination,
            self._members(
                ("alpha", "user-stories/alpha.md", "core_wins"),
                ("beta", "user-stories/beta.md", "core_wins"),
            ),
        )
        assert collisions == [
            "collision: path user-stories/alpha.md; core wins",
            "collision: slug alpha; core wins",
        ]
        assert b"| `alpha` | Alpha | active | ep-a | `a` |" in merged
        assert b"| `alpha` | Alpha local edit |" not in merged
        assert b"| `dest-own` | Destination owned | active | local | `d` |" in merged
        assert merged.endswith(
            b"\n## Destination notes\n\n"
            b"Local trailing section that must survive byte-for-byte.\n"
        )

    def test_differing_non_core_wins_member_writes_nothing_and_reports_nothing(self) -> None:
        destination = (
            "# User Stories\n\n"
            "| Slug | Title | Status | Epic | Affected areas |\n"
            "|---|---|---|---|---|\n"
            "| `beta` | Beta local edit | active | ep-b | `b` |\n"
            "| `dest-own` | Destination owned | active | local | `d` |\n"
        ).encode("utf-8")
        merged, collisions = merge_story_index(
            STORY_CORE_INDEX.encode("utf-8"),
            destination,
            self._members(("beta", "user-stories/beta.md", None)),
        )
        assert merged == destination, "a non-core_wins member must not be written"
        assert collisions == []

    def test_core_index_missing_member_row_is_invalid_mapping(self) -> None:
        core_without_alpha = STORY_CORE_INDEX.replace(
            "| `alpha` | Alpha | active | ep-a | `a` |\n", ""
        )
        with pytest.raises(SyncError) as caught:
            merge_story_index(
                core_without_alpha.encode("utf-8"),
                STORY_DESTINATION_INDEX.encode("utf-8"),
                self._members(
                    ("alpha", "user-stories/alpha.md", "core_wins"),
                    ("beta", "user-stories/beta.md", "core_wins"),
                ),
            )
        assert caught.value.code == "invalid_mapping", caught.value.message
        self.init_repo(self.upstream)
        self.write(self.upstream, "user-stories/index.md", core_without_alpha)
        commit = self.commit(self.upstream, "core index without alpha")
        self.init_repo(self.adopter)
        self.write(self.adopter, "user-stories/index.md", STORY_DESTINATION_INDEX)
        adopter_rev = self.commit(self.adopter, "destination index")
        catalog_unit = yaml.safe_load(STORY_CATALOG)["units"][0]
        declaration_unit = yaml.safe_load(STORY_DECLARATION)["units"][0]
        with pytest.raises(SyncError) as caught:
            _story_index_collisions(
                "portable-stories-always",
                catalog_unit,
                declaration_unit,
                _GitRepo(str(self.upstream)),
                commit,
                _RevisionSnapshot(_GitRepo(str(self.adopter)), adopter_rev),
            )
        assert caught.value.code == "invalid_mapping", caught.value.message

    def test_check_reports_exactly_one_core_wins_collision_pair(self) -> None:
        fixture = self.build_stories(STORY_DESTINATION_INDEX)
        index_path = fixture["adopter"] / "user-stories/index.md"
        index_before = index_path.read_bytes()
        proc = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision", fixture["adopter_rev"],
            "--format", "json",
        )
        self.assert_exit(proc, 0)
        report = json.loads(proc.stdout)
        assert report["collisions"] == [
            "collision: path user-stories/alpha.md; core wins",
            "collision: slug alpha; core wins",
        ]
        assert all(unit["disposition"] == "current" for unit in report["units"]), report["units"]
        assert index_path.read_bytes() == index_before

    def test_propose_lock_prints_collisions_to_stderr_only(self) -> None:
        fixture = self.build_stories(STORY_DESTINATION_INDEX)
        fixture["review"].write_text(
            review_with_transition(
                EMPTY_REVIEW,
                self.rev(fixture["upstream"]),
                fixture["declaration"].read_text(encoding="utf-8"),
                _raw_file_digest(str(fixture["lock"])),
            ),
            encoding="utf-8",
        )
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "fresh transition")
        proc = self.run_cli(
            "propose-lock",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--lock", str(fixture["lock"]),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(proc, 0)
        candidate = yaml.safe_load(proc.stdout)
        assert candidate["schema_version"] == 2
        assert "collision" not in proc.stdout
        assert proc.stderr.splitlines() == [
            "collision: path user-stories/alpha.md; core wins",
            "collision: slug alpha; core wins",
        ]

    def test_inapplicable_story_units_are_never_projected(self) -> None:
        destination_index = STORY_DESTINATION_INDEX.replace(
            "| `gamma` | Gamma | active | ep-g | `g` |",
            "| `gamma` | Gamma local edit | active | ep-g | `g` |",
        )
        fixture = self.build_stories(destination_index, ticket=False)
        proc = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision", fixture["adopter_rev"],
            "--format", "json",
        )
        self.assert_exit(proc, 0)
        collisions = json.loads(proc.stdout)["collisions"]
        assert collisions == [
            "collision: path user-stories/alpha.md; core wins",
            "collision: slug alpha; core wins",
        ]
        assert not any("gamma" in line for line in collisions)


class StoryIndexWorkflowTests(EngineTestCase):
    """Owner story-index edits stay reviewed ordinary-tool changes."""

    def test_owner_edited_story_index_survives_prepared_acceptance(self) -> None:
        fixture = self.build_stories(STORY_DESTINATION_INDEX)
        adopter = fixture["adopter"]
        index_path = adopter / "user-stories/index.md"

        edited = STORY_DESTINATION_INDEX.replace(
            "| `dest-own` | Destination owned |",
            "| `dest-own` | Destination owned, owner-reviewed edit |",
        )
        index_path.write_text(edited, encoding="utf-8")
        fixture["adopter_rev"] = self.commit(adopter, "owner-reviewed index edit")
        fixture["review"].write_text(
            review_with_transition(
                EMPTY_REVIEW,
                self.rev(fixture["upstream"]),
                fixture["declaration"].read_text(encoding="utf-8"),
                _raw_file_digest(str(fixture["lock"])),
            ),
            encoding="utf-8",
        )
        fixture["adopter_rev"] = self.commit(adopter, "fresh transition")

        proposal = self.run_cli(
            "propose-lock",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--lock", str(fixture["lock"]),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(proposal, 0)
        assert "collision" not in proposal.stdout

        self.write(adopter, ".aicore/adoption.lock.yaml", proposal.stdout)
        fixture["adopter_rev"] = self.commit(
            adopter, "accept candidate lock", allow_empty=True
        )
        check = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision", fixture["adopter_rev"],
            "--format", "json",
        )
        self.assert_exit(check, 0)

        final_index = index_path.read_text(encoding="utf-8")
        assert "| `dest-own` | Destination owned, owner-reviewed edit |" in final_index
        assert "Local trailing section that must survive byte-for-byte." in final_index
