"""Behavior tests for refreshing marked region files with `init`."""

from __future__ import annotations

from pathlib import Path

import yaml

from _core_sync_testkit import (
    DEST_MARKED,
    REV_A,
    REV_B,
    SOURCE_MARKED,
    _bindings_document,
    _init_args,
    _write_file,
    uc,
)


class InitRefreshTests:
    """Verify init refreshes a marked core and records reconciliation work."""

    def test_init_refreshes_marked_core_preserving_outside_and_records_pending(
        self, tmp_path: Path
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        destination_path = _write_file(destination, "agent.md", DEST_MARKED)
        root_path = _write_file(
            destination, "CLAUDE.md", "# Root\n\nContent.\n"
        )
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(
                REV_B, "agent.md", ["agent.md"], root="CLAUDE.md"
            ),
        )
        source_split = uc.split_regions(SOURCE_MARKED)
        before_content = destination_path.read_bytes().decode("utf-8")
        before_split = uc.split_regions(before_content)
        assert source_split is not None
        assert before_split is not None
        before_outside = uc.outside_bytes(before_split).encode("utf-8")

        assert uc.main(_init_args(source, destination, bindings_path, REV_A)) == 0

        after_content = destination_path.read_bytes()
        after_split = uc.split_regions(after_content.decode("utf-8"))
        assert after_split is not None
        assert after_split["region"] == source_split["region"]
        assert uc.outside_bytes(after_split).encode("utf-8") == before_outside

        updated = uc.load_bindings(bindings_path)
        assert updated is not None
        assert updated["core_revision"] == REV_A
        assert updated["pending"] == ["agent.md"]

        report_path = uc.reconciliation_report_path(bindings_path)
        report = yaml.safe_load(report_path.read_text(encoding="utf-8"))
        assert report["core_revision"] == REV_A
        assert report["entries"] == [
            {
                "destination": "agent.md",
                "source": "agent.md",
                "action": "refreshed",
            }
        ]

        root_text = root_path.read_text(encoding="utf-8")
        assert uc.RECONCILE_BEGIN in root_text
        assert uc.RECONCILE_END in root_text
