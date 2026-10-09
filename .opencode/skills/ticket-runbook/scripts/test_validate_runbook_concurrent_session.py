"""Tests for the runbook concurrent-session warning."""

from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import validate_runbook as vr  # noqa: E402
from _ticket_runbook_testkit import (  # noqa: E402
    _make_analysis,
    _patch_header,
)


class ValidateRunbookConcurrentSessionTests:
    def test_concurrent_session_warning(self, tmp_path: Path) -> None:
        analysis_dir = _make_analysis(tmp_path)
        updated = (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M")
        _patch_header(analysis_dir, {"Updated": updated})
        header = vr.load_state_header(analysis_dir / "state.md")
        warning = vr.check_concurrent_session(header)
        assert warning is not None
        assert "CONCURRENT" in warning
