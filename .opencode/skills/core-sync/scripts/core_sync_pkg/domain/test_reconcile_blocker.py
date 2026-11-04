"""Behavior tests for static destination reconciliation blocker content.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/domain/test_reconcile_blocker.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import EXPECTED_RECONCILE_BODY  # noqa: E402
from core_sync_pkg.domain.constants import RECONCILE_BODY  # noqa: E402


class ReconcileBlockerContentTests:
    def test_block_body_is_the_self_contained_action_required_text(self) -> None:
        assert RECONCILE_BODY == EXPECTED_RECONCILE_BODY

    def test_block_body_is_step_by_step_and_self_contained(self) -> None:
        body = RECONCILE_BODY
        assert "ACTION REQUIRED" in body
        assert "self-contained" in body
        assert "This block is self-contained; no other context is required." in body
        assert "project region" in body
        assert "core region" in body
        assert (
            "> 2. If `.aicore/reconciliation/init.yaml` exists, read it. It records the "
            "core revision and each affected destination path, source, and action as "
            "metadata; it does not contain the displaced content. Use that metadata to "
            "locate and review each destination file, then inspect the displaced "
            "content there, in its `<!-- project:begin -->` … `<!-- project:end -->` "
            "region."
        ) in body
        for step in (
            "1. Open the file.",
            "5. Delete that file's entry",
        ):
            assert step in body
        assert "delete this entire blocker block" in body

    def test_block_body_carries_v2_migration_and_mcp_preservation_guidance(
        self,
    ) -> None:
        body = RECONCILE_BODY
        assert "`opencode.jsonc`" in body
        assert "OpenCode V1 layout" in body
        assert "migrate the file to the V2 layout" in body
        assert (
            "keeps this project's own MCP servers alongside the core-registered "
            "ones" in body
        )
        assert "same-named MCP server entry core-wins" in body
        assert "every other key is still replaced wholesale" in body
        assert "restore any MCP server" not in body
        assert "replaces the source-owned `mcp` key wholesale" not in body

    def test_block_body_requires_replacing_the_inherited_qmd_index_name(
        self,
    ) -> None:
        body = RECONCILE_BODY

        # Keep the RAW paragraph: the placeholder token checked below ends in
        # ">", which the normalization step also rewrites, so a
        # placeholder-absence check can never read normalized text.
        raw_paragraphs = [
            paragraph
            for paragraph in body.split(">\n")
            if "qmd" in paragraph.lower()
        ]
        assert len(raw_paragraphs) == 1, (
            "expected exactly one QMD index guidance paragraph in the blocker "
            f"body, found {len(raw_paragraphs)}"
        )
        raw_guidance = raw_paragraphs[0]
        # Control: the raw view still carries the blockquote prefix, so a later
        # refactor cannot silently route normalized text into the guard below.
        assert raw_guidance.startswith(">")

        paragraphs = [
            " ".join(paragraph.replace(">", " ").split()).lower()
            for paragraph in raw_paragraphs
        ]
        guidance = paragraphs[0]

        assert "replace" in guidance
        assert "own" in guidance or "your" in guidance or "this project" in guidance
        assert "index" in guidance
        assert "config" in guidance or "opencode.jsonc" in guidance
        assert "verify" in guidance
        assert "retrieval" in guidance

        # No placeholder index value ships, so the note must not claim one.
        # Checked on the constant itself, never on a derived view, because two
        # independent derivations defeat a view-based check: the
        # `paragraph.replace(">", " ")` normalization rewrites the closing ">"
        # of the placeholder, and the `body.split(">\n")` split above consumes
        # any ">" that ends a line — not only a blockquote terminator — so a
        # line-final token with no closing backtick is severed before the
        # assertion runs: the forbidden token ships while the check passes
        # vacuously (false green). The whole string has neither seam, so no
        # normalization or split can hide the token from this assertion.
        assert "<project-index>" not in RECONCILE_BODY.lower()

        assert "project region" in body
        assert "never touch the core region" in body.lower()
        if "core region" in guidance:
            assert "never" in guidance or "do not" in guidance
