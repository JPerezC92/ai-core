"""Shared constants and fixture helpers for the split core_sync behavior tests.

The former monolith `test_core_sync.py` was split by behavior; every constant
and helper shared by more than one behavior module lives here instead.
"""

from __future__ import annotations

import sys
from pathlib import Path

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

RAW_SOURCE_BYTES = b'{\n  "theme": "dark",\n  "model": "sample"\n}\n'

ROOT_TEXT = "# Root runtime\n\nIntro paragraph.\n\nLast line.\n"

EXPECTED_RECONCILE_BODY = (
    "> **⚠️ ACTION REQUIRED — core reconciliation. This project is not current "
    "until this is done.**\n"
    ">\n"
    "> You (the assistant working in THIS project) must reconcile some files, "
    "and adopt one permanent rule. This block is self-contained; no other "
    "context is required.\n"
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
    "> 2. If `.aicore/reconciliation/init.yaml` exists, read it. It records the "
    "core revision and each affected destination path, source, and action as "
    "metadata; it does not contain the displaced content. Use that metadata to "
    "locate and review each destination file, then inspect the displaced "
    "content there, in its `<!-- project:begin -->` … `<!-- project:end -->` "
    "region.\n"
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


def _write_file(base: Path, relative: str, content: str) -> Path:
    """Write a fixture file under a base directory, creating parents."""
    path = base / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _write_bytes_file(base: Path, relative: str, content: bytes) -> Path:
    """Write a raw-byte fixture file under a base directory, creating parents."""
    path = base / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def _binding_entry(
    source: str, destinations: list[str], mode: uc.BindingMode = "region"
) -> uc.BindingEntry:
    """Build one bindings entry with an explicit mode."""
    return {"source": source, "destinations": list(destinations), "mode": mode}


def _bindings_with_entries(
    revision: str,
    entries: list[uc.BindingEntry],
    pending: list[str] | None = None,
    root: str | None = None,
) -> uc.Bindings:
    """Build a valid bindings document from explicit binding entries."""
    return {
        "schema": 1,
        "core_revision": revision,
        "bindings": list(entries),
        "pending": list(pending) if pending else [],
        "root": root,
    }


def _bindings_document(
    revision: str,
    source: str,
    destinations: list[str],
    pending: list[str] | None = None,
    root: str | None = None,
    mode: uc.BindingMode = "region",
) -> uc.Bindings:
    """Build a valid single-entry bindings document for a fixture."""
    return _bindings_with_entries(
        revision,
        [_binding_entry(source, destinations, mode)],
        pending,
        root,
    )


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


def _raw_setup(
    tmp_path: Path,
    *,
    source_content: bytes = RAW_SOURCE_BYTES,
    destination_content: bytes | None = RAW_SOURCE_BYTES,
    pinned: str = REV_A,
    pending: list[str] | None = None,
) -> tuple[Path, Path, Path]:
    """Build a raw-mode source/destination fixture plus a raw bindings file."""
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    _write_bytes_file(source, "opencode.jsonc", source_content)
    if destination_content is None:
        destination.mkdir(parents=True, exist_ok=True)
    else:
        _write_bytes_file(destination, "opencode.jsonc", destination_content)
    bindings_path = tmp_path / "bindings.yaml"
    uc.save_bindings(
        bindings_path,
        _bindings_with_entries(
            pinned,
            [_binding_entry("opencode.jsonc", ["opencode.jsonc"], "raw")],
            pending,
        ),
    )
    return source, destination, bindings_path
