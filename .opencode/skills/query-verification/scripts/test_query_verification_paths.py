"""Tests for query-root paths, adjacency, and source-layout safety."""

from __future__ import annotations

import contextlib
import io
import sys
from pathlib import Path
from unittest.mock import patch

import yaml

sys.path.insert(0, str(Path(__file__).parent))
import query_verification as qv  # noqa: E402
from _query_verification_testkit import (  # noqa: E402
    SidecarVariant,
    VALID_SIDECAR_NAME,
    _base_sidecar,
    _read_source_text,
    _sidecar_variant,
    _write_root,
)


class QueryVerificationPathTests:
    def _assert_rejected(
        self, root: Path, sidecar_path: Path, fragment: str
    ) -> None:
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            result = qv.run_validate(str(root), str(sidecar_path))
        assert result == 1, stderr.getvalue()
        assert fragment in stderr.getvalue()

    def _assert_sidecar_rejected(
        self, tmp_path: Path, sidecar: SidecarVariant, fragment: str
    ) -> None:
        root = _write_root(tmp_path, _read_source_text(), sidecar)
        self._assert_rejected(root, root / VALID_SIDECAR_NAME, fragment)

    def test_rejects_absolute_source(self, tmp_path: Path) -> None:
        sidecar = _sidecar_variant()
        sidecar["source"] = "/etc/incident-check.sql"
        self._assert_sidecar_rejected(tmp_path, sidecar, "relative to the query root")

    def test_rejects_traversal_source(self, tmp_path: Path) -> None:
        sidecar = _sidecar_variant()
        sidecar["source"] = "../incident-check.sql"
        self._assert_sidecar_rejected(tmp_path, sidecar, "normalized path")

    def test_rejects_non_sql_source(self, tmp_path: Path) -> None:
        sidecar = _sidecar_variant()
        sidecar["source"] = "incident-check.txt"
        self._assert_sidecar_rejected(tmp_path, sidecar, "end with '.sql'")

    def test_rejects_absent_sidecar(self, tmp_path: Path) -> None:
        root = _write_root(tmp_path, _read_source_text(), _base_sidecar())
        self._assert_rejected(
            root, root / "missing.verifier.yaml", "sidecar not found"
        )

    def test_rejects_absent_source(self, tmp_path: Path) -> None:
        root = _write_root(tmp_path, _read_source_text(), _base_sidecar())
        (root / "incident-check.sql").unlink()
        self._assert_rejected(root, root / VALID_SIDECAR_NAME, "source not found")

    def test_rejects_non_adjacent_sidecar(self, tmp_path: Path) -> None:
        root = _write_root(
            tmp_path,
            _read_source_text(),
            _base_sidecar(),
            sidecar_name="other.verifier.yaml",
        )
        self._assert_rejected(root, root / "other.verifier.yaml", "not adjacent")

    def test_rejects_sidecar_outside_query_root(self, tmp_path: Path) -> None:
        root = _write_root(tmp_path, _read_source_text(), _base_sidecar())
        outside = tmp_path / "outside"
        outside.mkdir()
        outside_sidecar = outside / VALID_SIDECAR_NAME
        outside_sidecar.write_text(
            yaml.safe_dump(dict(_base_sidecar())), encoding="utf-8"
        )
        self._assert_rejected(root, outside_sidecar, "outside the query root")

    def test_rejects_resolved_source_escape(self, tmp_path: Path) -> None:
        root = _write_root(tmp_path, _read_source_text(), _base_sidecar())
        source_path = root / "incident-check.sql"
        escaped = tmp_path / "outside-source.sql"
        original = Path.resolve

        def stub_resolve(self: Path) -> Path:
            if self == source_path:
                return escaped
            return original(self)

        with patch.object(Path, "resolve", stub_resolve):
            self._assert_rejected(
                root,
                root / VALID_SIDECAR_NAME,
                "path resolves outside the query root",
            )
