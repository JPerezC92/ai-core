"""Test the LF-termination contract of the filesystem write boundary.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/infrastructure/test_filesystem.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core_sync_pkg.domain.constants import (  # noqa: E402
    RECONCILE_BEGIN,
    RECONCILE_BODY,
    RECONCILE_END,
)
from core_sync_pkg.infrastructure.filesystem import (  # noqa: E402
    read_bytes,
    write_bytes,
    write_reconciliation_blocker,
    write_text,
)


class TextWriteLineEndingTests:
    """`write_text` terminates LF only; `write_bytes` stays byte-exact."""

    def test_write_text_normalizes_crlf_and_lone_cr(self, tmp_path: Path) -> None:
        path = tmp_path / "out.md"

        write_text(path, "a\r\nb\rc\n")

        assert read_bytes(path) == b"a\nb\nc\n"

    def test_write_text_leaves_lf_content_byte_identical(self, tmp_path: Path) -> None:
        path = tmp_path / "out.md"

        write_text(path, "a\nb\nc\n")

        assert read_bytes(path) == b"a\nb\nc\n"

    def test_write_bytes_is_exempt_from_normalization(self, tmp_path: Path) -> None:
        path = tmp_path / "payload.bin"

        write_bytes(path, b"a\r\nb")

        assert read_bytes(path) == b"a\r\nb"

    def test_write_reconciliation_blocker_terminates_crlf_root_in_lf(
        self, tmp_path: Path
    ) -> None:
        root_path = tmp_path / "AGENTS.md"
        crlf_root = "# Root\r\n\r\nbody line\r\n"
        write_bytes(root_path, crlf_root.encode("utf-8"))

        assert write_reconciliation_blocker(root_path, ["agent.md"]) is True

        written = read_bytes(root_path)
        assert written is not None
        assert b"\r" not in written
        text = written.decode("utf-8")
        assert text.startswith("# Root\n\nbody line\n")
        lines = text.splitlines()
        assert RECONCILE_BEGIN in lines
        assert RECONCILE_END in lines
        assert "ACTION REQUIRED" in text
        assert RECONCILE_BODY in text
