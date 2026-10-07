"""Tests for core_sync.py — marker validation, the check/apply exit contract,
outside-byte preservation for one source across multiple destinations, and the
destination reconciliation blocker (add, refresh, remove, idempotency).

Run: uv run --frozen --group dev pytest .opencode/skills/core-sync/scripts/test_core_sync.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent))
import core_sync as uc  # noqa: E402

REV_A = "a" * 40
REV_B = "b" * 40

SOURCE_MARKED = (
    "---\n"
    "name: sample\n"
    "---\n"
    "<!-- core:begin -->\n"
    "\n"
    "Core body line one\n"
    "Core body line two\n"
    "<!-- core:end -->\n"
)

DEST_MARKED = (
    "---\n"
    "name: sample\n"
    "---\n"
    "<!-- core:begin -->\n"
    "\n"
    "Destination old body\n"
    "<!-- core:end -->\n"
    "\n"
    "Destination project region\n"
)

SOURCE_NO_MARKERS = (
    "---\n"
    "name: src\n"
    "---\n"
    "\n"
    "Core body one\n"
    "Core body two\n"
)

DEST_PLAIN = (
    "---\n"
    "name: dest\n"
    "---\n"
    "\n"
    "# Old title\n"
    "\n"
    "Old body line\n"
)


def _write_file(base: Path, relative: str, content: str) -> Path:
    """Write a fixture file under a base directory, creating parents."""
    path = base / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _bindings_document(
    revision: str,
    source: str,
    destinations: list[str],
    pending: list[str] | None = None,
    root: str | None = None,
) -> uc.Bindings:
    """Build a valid bindings document for a fixture."""
    return {
        "schema": 1,
        "core_revision": revision,
        "bindings": [{"source": source, "destinations": list(destinations)}],
        "pending": list(pending) if pending else [],
        "root": root,
    }


def _check_args(
    source: Path, destination: Path, bindings: Path, revision: str
) -> list[str]:
    """Build the `check` CLI arguments for a fixture."""
    return [
        "check",
        "--source",
        str(source),
        "--destination",
        str(destination),
        "--bindings",
        str(bindings),
        "--source-revision",
        revision,
    ]


def _apply_args(
    source: Path, destination: Path, bindings: Path, revision: str
) -> list[str]:
    """Build the `apply` CLI arguments for a fixture."""
    return [
        "apply",
        "--source",
        str(source),
        "--destination",
        str(destination),
        "--bindings",
        str(bindings),
        "--source-revision",
        revision,
    ]


def _init_args(
    source: Path, destination: Path, bindings: Path, revision: str
) -> list[str]:
    """Build the `init` CLI arguments for a fixture."""
    return [
        "init",
        "--source",
        str(source),
        "--destination",
        str(destination),
        "--bindings",
        str(bindings),
        "--source-revision",
        revision,
    ]


class MarkerValidationTests:
    def test_missing_markers_returns_none(self) -> None:
        assert uc.find_markers("no markers here\n") is None

    def test_inline_marker_is_ignored(self) -> None:
        assert uc.find_markers("prefix <!-- core:begin --> suffix\n") is None

    def test_fenced_marker_is_ignored(self) -> None:
        content = "```\n<!-- core:begin -->\n<!-- core:end -->\n```\n"
        assert uc.find_markers(content) is None

    def test_duplicate_begin_returns_none(self) -> None:
        content = (
            "a\n<!-- core:begin -->\nb\n<!-- core:begin -->\nc\n<!-- core:end -->\n"
        )
        assert uc.find_markers(content) is None

    def test_reversed_markers_returns_none(self) -> None:
        assert uc.find_markers("<!-- core:end -->\nbody\n<!-- core:begin -->\n") is None

    def test_valid_markers_split_region_and_outside(self) -> None:
        content = "head\n<!-- core:begin -->\nbody\n<!-- core:end -->\ntail\n"
        split = uc.split_regions(content)
        assert split is not None
        assert split["before"] == "head\n"
        assert split["region"] == "body\n"
        assert split["after"] == "tail\n"
        assert (
            uc.outside_bytes(split)
            == "head\n<!-- core:begin -->\n<!-- core:end -->\ntail\n"
        )


class CheckContractTests:
    def _setup(
        self,
        tmp_path: Path,
        *,
        source_content: str = SOURCE_MARKED,
        destination_content: str = SOURCE_MARKED,
        pinned: str = REV_A,
        pending: list[str] | None = None,
    ) -> tuple[Path, Path, Path]:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", source_content)
        _write_file(destination, "agent.md", destination_content)
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(pinned, "agent.md", ["agent.md"], pending),
        )
        return source, destination, bindings_path

    def test_current_returns_zero_and_prints_current(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        source, destination, bindings_path = self._setup(tmp_path)
        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 0
        assert capsys.readouterr().out == "current\n"

    def test_region_drift_returns_one(self, tmp_path: Path) -> None:
        source, destination, bindings_path = self._setup(
            tmp_path, destination_content=DEST_MARKED
        )
        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 1

    def test_revision_mismatch_returns_one(self, tmp_path: Path) -> None:
        source, destination, bindings_path = self._setup(tmp_path, pinned=REV_B)
        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 1

    def test_nonempty_pending_returns_one(self, tmp_path: Path) -> None:
        source, destination, bindings_path = self._setup(
            tmp_path, pending=["agent.md"]
        )
        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 1

    def test_malformed_bindings_returns_two(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        source.mkdir()
        destination.mkdir()
        bindings_path = tmp_path / "bindings.yaml"
        bindings_path.write_text(
            "schema: 2\nbindings: []\npending: []\n", encoding="utf-8"
        )
        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 2

    def test_missing_destination_returns_one(self, tmp_path: Path) -> None:
        source, destination, bindings_path = self._setup(tmp_path)
        (destination / "agent.md").unlink()
        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 1

    def test_invalid_destination_markers_return_two(self, tmp_path: Path) -> None:
        source, destination, bindings_path = self._setup(tmp_path)
        _write_file(destination, "agent.md", "no markers\n")
        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 2

    def test_markerless_source_uses_whole_body_and_drifts(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = self._setup(tmp_path)
        _write_file(source, "agent.md", "no markers\n")
        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 1


class ApplyContractTests:
    def _setup(
        self,
        tmp_path: Path,
        *,
        destination_content: str = DEST_MARKED,
        pinned: str = REV_B,
    ) -> tuple[Path, Path, Path]:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        _write_file(destination, "agent.md", destination_content)
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(pinned, "agent.md", ["agent.md"]),
        )
        return source, destination, bindings_path

    def test_apply_heals_region_and_preserves_outside(self, tmp_path: Path) -> None:
        source, destination, bindings_path = self._setup(tmp_path)
        destination_path = destination / "agent.md"

        assert uc.main(_apply_args(source, destination, bindings_path, REV_A)) == 0

        source_split = uc.split_regions(SOURCE_MARKED)
        destination_split = uc.split_regions(DEST_MARKED)
        healed_split = uc.split_regions(destination_path.read_text(encoding="utf-8"))
        assert source_split is not None
        assert destination_split is not None
        assert healed_split is not None
        assert healed_split["region"] == source_split["region"]
        assert uc.outside_bytes(healed_split) == uc.outside_bytes(destination_split)
        assert destination_path.read_text(encoding="utf-8").endswith(
            "Destination project region\n"
        )

    def test_apply_pins_core_revision(self, tmp_path: Path) -> None:
        source, destination, bindings_path = self._setup(tmp_path)
        assert uc.main(_apply_args(source, destination, bindings_path, REV_A)) == 0
        updated = uc.load_bindings(bindings_path)
        assert updated is not None
        assert updated["core_revision"] == REV_A

    def test_apply_invalid_destination_markers_returns_two_without_writing(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = self._setup(
            tmp_path, destination_content="no markers\n"
        )
        destination_path = destination / "agent.md"
        assert uc.main(_apply_args(source, destination, bindings_path, REV_A)) == 2
        assert destination_path.read_text(encoding="utf-8") == "no markers\n"

    def test_apply_missing_destination_returns_one_and_writes_nothing(
        self, tmp_path: Path
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        present = _write_file(destination, "present.md", DEST_MARKED)
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(REV_B, "agent.md", ["present.md", "absent.md"]),
        )

        assert uc.main(_apply_args(source, destination, bindings_path, REV_A)) == 1
        assert present.read_text(encoding="utf-8") == DEST_MARKED
        assert not (destination / "absent.md").exists()
        updated = uc.load_bindings(bindings_path)
        assert updated is not None
        assert updated["core_revision"] == REV_B

    def test_apply_malformed_bindings_returns_two(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        source.mkdir()
        destination.mkdir()
        bindings_path = tmp_path / "bindings.yaml"
        bindings_path.write_text("schema: 1\nbindings: nope\n", encoding="utf-8")
        assert uc.main(_apply_args(source, destination, bindings_path, REV_A)) == 2


class MultiDestinationTests:
    def test_one_source_two_destinations_both_healed(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        first = _write_file(destination, "one.md", DEST_MARKED)
        second = _write_file(
            destination,
            "two.md",
            DEST_MARKED.replace("Destination old body", "Second old body").replace(
                "Destination project region", "Second project region"
            ),
        )
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(REV_B, "agent.md", ["one.md", "two.md"]),
        )

        assert uc.main(_apply_args(source, destination, bindings_path, REV_A)) == 0
        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 0

        source_split = uc.split_regions(SOURCE_MARKED)
        assert source_split is not None
        for path in (first, second):
            split = uc.split_regions(path.read_text(encoding="utf-8"))
            assert split is not None
            assert split["region"] == source_split["region"]


class SourceCoreTests:
    def test_markerless_source_uses_body_after_frontmatter(self) -> None:
        content = "---\nname: sample\n---\n\nBody line one\nBody line two\n"
        assert uc.extract_source_core(content) == "\nBody line one\nBody line two\n"

    def test_markerless_source_without_frontmatter_uses_whole_body(self) -> None:
        assert uc.extract_source_core("plain body\n") == "plain body\n"

    def test_marked_source_uses_region(self) -> None:
        assert uc.extract_source_core(SOURCE_MARKED) == (
            "\nCore body line one\nCore body line two\n"
        )


class InitContractTests:
    def _setup(
        self,
        tmp_path: Path,
        *,
        source_content: str = SOURCE_NO_MARKERS,
        destination_content: str = DEST_PLAIN,
        pinned: str = REV_B,
    ) -> tuple[Path, Path, Path]:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", source_content)
        _write_file(destination, "agent.md", destination_content)
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(pinned, "agent.md", ["agent.md"]),
        )
        return source, destination, bindings_path

    def test_init_generates_both_regions_and_wraps_old_body(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = self._setup(tmp_path)

        assert uc.main(_init_args(source, destination, bindings_path, REV_A)) == 0

        content = (destination / "agent.md").read_text(encoding="utf-8")
        assert content.startswith("---\nname: dest\n---\n<!-- core:begin -->\n")
        split = uc.split_regions(content)
        assert split is not None
        assert split["region"] == "\nCore body one\nCore body two\n"
        assert "<!-- project:begin -->\n" in content
        project_body = content.split("<!-- project:begin -->\n", 1)[1].split(
            "<!-- project:end -->", 1
        )[0]
        assert project_body == "\n# Old title\n\nOld body line\n"
        assert content.endswith("<!-- project:end -->\n")

    def test_init_separates_core_end_and_project_begin_with_one_blank_line(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = self._setup(tmp_path)

        assert uc.main(_init_args(source, destination, bindings_path, REV_A)) == 0

        content = (destination / "agent.md").read_text(encoding="utf-8")
        lines = content.splitlines()
        end_index = lines.index(uc.END)
        begin_index = lines.index(uc.PROJECT_BEGIN)
        assert lines[end_index + 1] == ""
        assert begin_index == end_index + 2
        assert "<!-- core:end -->\n\n<!-- project:begin -->" in content
        assert "<!-- core:end -->\n\n\n<!-- project:begin -->" not in content

        split = uc.split_regions(content)
        assert split is not None
        assert split["region"] == "\nCore body one\nCore body two\n"
        assert split["after"].startswith("\n<!-- project:begin -->\n")
        project_body = content.split("<!-- project:begin -->\n", 1)[1].split(
            "<!-- project:end -->", 1
        )[0]
        assert project_body == "\n# Old title\n\nOld body line\n"

    def test_init_is_idempotent_when_rerun(self, tmp_path: Path) -> None:
        source, destination, bindings_path = self._setup(tmp_path)
        destination_path = destination / "agent.md"

        assert uc.main(_init_args(source, destination, bindings_path, REV_A)) == 0
        after_first = destination_path.read_text(encoding="utf-8")
        assert uc.main(_apply_args(source, destination, bindings_path, REV_A)) == 0
        after_refresh = destination_path.read_text(encoding="utf-8")
        assert uc.main(_init_args(source, destination, bindings_path, REV_A)) == 0
        after_second = destination_path.read_text(encoding="utf-8")

        assert after_first == after_refresh == after_second

    def test_init_records_report_and_pending(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        source, destination, bindings_path = self._setup(tmp_path)

        assert uc.main(_init_args(source, destination, bindings_path, REV_A)) == 0
        assert capsys.readouterr().out == "initialized\n"

        updated = uc.load_bindings(bindings_path)
        assert updated is not None
        assert updated["pending"] == ["agent.md"]

        report_path = bindings_path.parent / "reconciliation" / "init.yaml"
        assert report_path.is_file()
        report = yaml.safe_load(report_path.read_text(encoding="utf-8"))
        assert report["core_revision"] == REV_A
        assert report["entries"] == [
            {"destination": "agent.md", "source": "agent.md", "action": "initialized"}
        ]

    def test_init_then_check_current_after_pending_cleared(self, tmp_path: Path) -> None:
        source, destination, bindings_path = self._setup(tmp_path)

        assert uc.main(_init_args(source, destination, bindings_path, REV_A)) == 0
        updated = uc.load_bindings(bindings_path)
        assert updated is not None
        updated["pending"] = []
        uc.save_bindings(bindings_path, updated)

        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 0


ROOT_TEXT = "# Root runtime\n\nIntro paragraph.\n\nLast line.\n"

EXPECTED_RECONCILE_BODY = (
    "> **⚠️ ACTION REQUIRED — core reconciliation. This project is not current "
    "until this is done.**\n"
    ">\n"
    "> You (the assistant working in THIS project) must reconcile some files, "
    "and adopt one permanent rule. These instructions are self-contained — no "
    "other context is needed.\n"
    ">\n"
    "> **Permanent rule — adopt it now, in every future session.** Files here "
    "are split into two marked regions:\n"
    "> - `<!-- core:begin -->` … `<!-- core:end -->` — the **core region**, "
    "owned by an upstream core project. **Never edit, move, or delete anything "
    "between these two markers.**\n"
    "> - `<!-- project:begin -->` … `<!-- project:end -->` — the "
    "**project region**, owned by THIS project. All edits go here.\n"
    "> If this rule is not already in this project's root instructions "
    "(`CLAUDE.md` / `AGENTS.md`), add it there permanently. This blocker "
    "block is temporary and gets deleted at the end; the rule is permanent.\n"
    ">\n"
    "> **What happened.** A core update replaced each file's core region with "
    "new shared content. The old content that used to sit there was moved into "
    "the project region, so the project region now holds BOTH this project's "
    "own rules AND an old copy of the core rules that the new core region "
    "already supersedes.\n"
    ">\n"
    "> **Do this for every file listed in `.aicore/core.yaml` under "
    "`pending:` (paths are relative to this project root):**\n"
    "> 1. Open the file.\n"
    "> 2. If a report exists under `.aicore/reconciliation/`, read it — it "
    "lists the displaced content.\n"
    "> 3. Edit ONLY inside `<!-- project:begin -->` … `<!-- project:end -->`: "
    "remove anything that merely duplicates or contradicts the core region "
    "(it is the superseded old copy), and keep this project's genuine, "
    "project-specific rules and facts.\n"
    "> 4. Never touch the core region and never move or delete the markers.\n"
    "> 5. Delete that file's entry from the `pending:` list in "
    "`.aicore/core.yaml`.\n"
    ">\n"
    "> **To finish.** When `pending:` is empty, **delete this entire blocker "
    "block** (from `<!-- core:reconcile:begin -->` to "
    "`<!-- core:reconcile:end -->`). Change nothing outside the project regions."
)


def _exact_marker_line_count(text: str, marker: str) -> int:
    """Count lines whose stripped content equals the marker exactly."""
    return sum(1 for line in text.splitlines() if line.strip() == marker)


class ReconcileBlockerTests:
    def test_block_body_is_the_self_contained_action_required_text(self) -> None:
        assert uc.RECONCILE_BODY == EXPECTED_RECONCILE_BODY

    def test_block_body_is_step_by_step_and_self_contained(self) -> None:
        body = uc.RECONCILE_BODY
        assert "ACTION REQUIRED" in body
        assert "self-contained" in body
        assert "project region" in body
        assert "core region" in body
        for step in ("1. Open the file.", "2. If a report exists", "5. Delete that file's entry"):
            assert step in body
        assert "delete this entire blocker block" in body

    def test_block_appended_when_pending_nonempty(self) -> None:
        result = uc.sync_reconciliation_blocker(ROOT_TEXT, ["a.md"])
        assert result == (
            ROOT_TEXT
            + "\n"
            + uc.RECONCILE_BEGIN
            + "\n"
            + uc.RECONCILE_BODY
            + "\n"
            + uc.RECONCILE_END
            + "\n"
        )
        assert _exact_marker_line_count(result, uc.RECONCILE_BEGIN) == 1
        assert _exact_marker_line_count(result, uc.RECONCILE_END) == 1
        assert uc.find_reconcile_block(result.splitlines(keepends=True)) is not None

    def test_fenced_reconcile_block_is_ignored(self) -> None:
        fenced = (
            "# Root\n\n```markdown\n"
            + uc.RECONCILE_BEGIN
            + "\n> STALE FENCED BODY\n"
            + uc.RECONCILE_END
            + "\n```\n"
        )

        assert uc.find_reconcile_block(fenced.splitlines(keepends=True)) is None
        assert uc.sync_reconciliation_blocker(fenced, []) == fenced

        appended = uc.sync_reconciliation_blocker(fenced, ["a.md"])
        assert appended.startswith(fenced)
        assert "STALE FENCED BODY" in appended
        assert appended.count(uc.RECONCILE_BODY) == 1
        assert uc.find_reconcile_block(appended.splitlines(keepends=True)) is not None

    def test_block_updated_in_place_on_rerun(self) -> None:
        first = uc.sync_reconciliation_blocker(ROOT_TEXT, ["a.md"])
        stale = first.replace(uc.RECONCILE_BODY, "STALE BODY")
        assert "STALE BODY" in stale

        repaired = uc.sync_reconciliation_blocker(stale, ["a.md", "b.md"])

        assert repaired == first
        assert "STALE BODY" not in repaired
        assert _exact_marker_line_count(repaired, uc.RECONCILE_BEGIN) == 1
        assert _exact_marker_line_count(repaired, uc.RECONCILE_END) == 1

    def test_block_removed_when_pending_empty(self) -> None:
        blocked = uc.sync_reconciliation_blocker(ROOT_TEXT, ["a.md"])
        assert uc.sync_reconciliation_blocker(blocked, []) == ROOT_TEXT

    def test_removal_is_noop_without_block(self) -> None:
        assert uc.sync_reconciliation_blocker(ROOT_TEXT, []) == ROOT_TEXT

    def test_idempotent_add_and_remove(self) -> None:
        once = uc.sync_reconciliation_blocker(ROOT_TEXT, ["a.md"])
        assert uc.sync_reconciliation_blocker(once, ["a.md"]) == once
        second = uc.sync_reconciliation_blocker(
            uc.sync_reconciliation_blocker(once, []), []
        )
        assert second == ROOT_TEXT

    def test_other_root_content_preserved(self) -> None:
        blocked = uc.sync_reconciliation_blocker(ROOT_TEXT, ["a.md"])
        removed = uc.sync_reconciliation_blocker(blocked, [])
        assert removed == ROOT_TEXT
        assert "# Root runtime" in removed
        assert "Last line." in removed

    def test_empty_root_text_gets_block_without_leading_blank(self) -> None:
        result = uc.sync_reconciliation_blocker("", ["a.md"])
        assert result == (
            uc.RECONCILE_BEGIN
            + "\n"
            + uc.RECONCILE_BODY
            + "\n"
            + uc.RECONCILE_END
            + "\n"
        )

    def test_root_without_trailing_newline_gains_separator(self) -> None:
        result = uc.sync_reconciliation_blocker("no newline", ["a.md"])
        assert result.startswith("no newline\n\n" + uc.RECONCILE_BEGIN)


def _region_fixture(
    tmp_path: Path,
    *,
    pending: list[str] | None,
    root: str | None,
    root_file: str | None,
    preexisting_block: bool = False,
) -> tuple[Path, Path, Path]:
    """Build a matching source/destination region fixture plus a root file."""
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    _write_file(source, "agent.md", SOURCE_MARKED)
    _write_file(destination, "agent.md", SOURCE_MARKED)
    if root_file is not None:
        root_text = "# Root\n\nContent.\n"
        if preexisting_block:
            root_text = uc.sync_reconciliation_blocker(root_text, ["agent.md"])
        _write_file(destination, root_file, root_text)
    bindings_path = tmp_path / "bindings.yaml"
    uc.save_bindings(
        bindings_path,
        _bindings_document(REV_A, "agent.md", ["agent.md"], pending, root),
    )
    return source, destination, bindings_path


class BlockerWiringTests:
    def test_check_writes_block_and_returns_one_when_pending(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = _region_fixture(
            tmp_path, pending=["agent.md"], root="CLAUDE.md", root_file="CLAUDE.md"
        )
        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 1
        text = (destination / "CLAUDE.md").read_text(encoding="utf-8")
        assert uc.RECONCILE_BEGIN in text
        assert uc.RECONCILE_BODY in text

    def test_check_removes_block_and_returns_zero_when_pending_cleared(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = _region_fixture(
            tmp_path,
            pending=[],
            root="CLAUDE.md",
            root_file="CLAUDE.md",
            preexisting_block=True,
        )
        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 0
        text = (destination / "CLAUDE.md").read_text(encoding="utf-8")
        assert uc.RECONCILE_BEGIN not in text
        assert text == "# Root\n\nContent.\n"

    def test_check_defaults_to_agents_md_when_present(self, tmp_path: Path) -> None:
        source, destination, bindings_path = _region_fixture(
            tmp_path, pending=["agent.md"], root=None, root_file="CLAUDE.md"
        )
        (destination / "CLAUDE.md").unlink()
        _write_file(destination, "AGENTS.md", "# Agents\n\nBody.\n")

        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 1
        assert uc.RECONCILE_BEGIN in (destination / "AGENTS.md").read_text(
            encoding="utf-8"
        )
        assert not (destination / "CLAUDE.md").exists()

    def test_apply_writes_block_when_pending(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        _write_file(destination, "agent.md", DEST_MARKED)
        _write_file(destination, "CLAUDE.md", "# Root\n\nContent.\n")
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(
                REV_B, "agent.md", ["agent.md"], ["agent.md"], "CLAUDE.md"
            ),
        )
        assert uc.main(_apply_args(source, destination, bindings_path, REV_A)) == 0
        text = (destination / "CLAUDE.md").read_text(encoding="utf-8")
        assert uc.RECONCILE_BEGIN in text

    def test_init_writes_block_when_pending_set(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_NO_MARKERS)
        _write_file(destination, "agent.md", DEST_PLAIN)
        _write_file(destination, "CLAUDE.md", "# Root\n\nContent.\n")
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(REV_B, "agent.md", ["agent.md"], None, "CLAUDE.md"),
        )
        assert uc.main(_init_args(source, destination, bindings_path, REV_A)) == 0
        text = (destination / "CLAUDE.md").read_text(encoding="utf-8")
        assert uc.RECONCILE_BEGIN in text

    def test_bindings_round_trip_preserves_root(self, tmp_path: Path) -> None:
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(REV_A, "agent.md", ["agent.md"], [], "CLAUDE.md"),
        )
        loaded = uc.load_bindings(bindings_path)
        assert loaded is not None
        assert loaded["root"] == "CLAUDE.md"

    def test_invalid_root_escapes_are_rejected(self) -> None:
        text = (
            "schema: 1\n"
            "core_revision: " + REV_A + "\n"
            "root: ../escape.md\n"
            "bindings:\n"
            "  - source: agent.md\n"
            "    destinations:\n"
            "      - agent.md\n"
            "pending: []\n"
        )
        assert uc.parse_bindings(text) is None
