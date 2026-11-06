"""Shared constants and fixture helpers for the split core_sync behavior tests.

The former monolith `test_core_sync.py` was split by behavior; every constant
and helper shared by more than one behavior module lives here instead.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import TypedDict, cast

sys.path.insert(0, str(Path(__file__).parent))

from core_sync_pkg.domain.bindings import BindingEntry, Bindings  # noqa: E402
from core_sync_pkg.domain.constants import (  # noqa: E402
    CLEARANCE_REL,
    CLEARANCE_SCHEMA,
    MODE_MERGE,
    MODE_RAW,
    MODE_REGION,
    ROLE_ROOT,
    SCHEMA_VERSION,
    BindingMode,
)
from core_sync_pkg.domain.jsonc import parse_object  # noqa: E402
from core_sync_pkg.domain.reconciliation import (  # noqa: E402
    sync_reconciliation_blocker,
)
from core_sync_pkg.domain.regions import ensure_trailing_newline  # noqa: E402
from core_sync_pkg.infrastructure.stores import save_bindings  # noqa: E402

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

CRLF_SOURCE_MARKED = (
    "---\r\n"
    "name: sample\r\n"
    "---\r\n"
    "<!-- core:begin -->\r\n"
    "\r\n"
    "Core body line one\r\n"
    "Core body line two\r\n"
    "<!-- core:end -->\r\n"
)

CRLF_DEST_MARKED = (
    "---\r\n"
    "name: sample\r\n"
    "---\r\n"
    "<!-- core:begin -->\r\n"
    "\r\n"
    "Destination old body\r\n"
    "<!-- core:end -->\r\n"
    "\r\n"
    "Destination project region\r\n"
)

CRLF_SOURCE_NO_MARKERS = (
    "---\r\n"
    "name: src\r\n"
    "---\r\n"
    "\r\n"
    "Core body one\r\n"
    "Core body two\r\n"
)

CRLF_DEST_PLAIN = (
    "---\r\n"
    "name: dest\r\n"
    "---\r\n"
    "\r\n"
    "# Old title\r\n"
    "\r\n"
    "Old body line\r\n"
)

RAW_SOURCE_BYTES = b'{\n  "theme": "dark",\n  "model": "sample"\n}\n'

RAW_CRLF_PAYLOAD_BYTES = b'{\r\n  "payload": "raw"\r\n}\r\n\xff\x00'

MERGE_SOURCE = '{\n  "theme": "dark",\n  "shared": "source"\n}\n'

MERGE_DESTINATION = (
    "{\n"
    "  // destination-only comment\n"
    '  "shared": "destination",\n'
    '  "custom": 42\n'
    "}\n"
)

CRLF_MERGE_SOURCE = '{\r\n  "theme": "dark",\r\n  "shared": "source"\r\n}\r\n'

CRLF_MERGE_DESTINATION = (
    "{\r\n"
    "  // destination-only comment\r\n"
    '  "shared": "destination",\r\n'
    '  "custom": 42\r\n'
    "}\r\n"
)

MERGE_DESTINATION_MERGED = (
    "{\n"
    "  // user comment\n"
    '  "shared": "source",\n'
    '  "custom": 42,\n'
    '  "theme": "dark"\n'
    "}\n"
)

MERGE_MCP_SOURCE = (
    "{\n"
    '  "mcp": {\n'
    '    "servers": {\n'
    '      "core": {\n'
    '        "command": "core"\n'
    "      },\n"
    '      "shared": {\n'
    '        "command": "source-shared"\n'
    "      }\n"
    "    }\n"
    "  }\n"
    "}\n"
)

MERGE_MCP_DESTINATION = (
    "{\n"
    "  // keep this comment\n"
    '  "mcp": {\n'
    '    "enabled": true,\n'
    '    "servers": {\n'
    '      "shared": {\n'
    '        "command": "destination-shared"\n'
    "      },\n"
    '      "local": {\n'
    '        "command": "local"\n'
    "      }\n"
    "    }\n"
    "  }\n"
    "}\n"
)

MERGE_MCP_DESTINATION_CURRENT = (
    "{\n"
    '  "mcp": {\n'
    '    "enabled": true,\n'
    '    "servers": {\n'
    '      "core": {\n'
    '        "command": "core"\n'
    "      },\n"
    '      "shared": {\n'
    '        "command": "source-shared"\n'
    "      },\n"
    '      "local": {\n'
    '        "command": "local"\n'
    "      }\n"
    "    }\n"
    "  }\n"
    "}\n"
)

MERGE_MCP_RESULT: dict[str, object] = {
    "mcp": {
        "enabled": True,
        "servers": {
            "core": {"command": "core"},
            "shared": {"command": "source-shared"},
            "local": {"command": "local"},
        },
    }
}

MERGE_MCP_DESTINATION_MISSING_CORE = (
    "{\n"
    '  "mcp": {\n'
    '    "servers": {\n'
    '      "local": {\n'
    '        "command": "local"\n'
    "      }\n"
    "    }\n"
    "  }\n"
    "}\n"
)

MERGE_MCP_DESTINATION_STALE_SHARED = (
    "{\n"
    '  "mcp": {\n'
    '    "servers": {\n'
    '      "core": {\n'
    '        "command": "core"\n'
    "      },\n"
    '      "shared": {\n'
    '        "command": "stale"\n'
    "      }\n"
    "    }\n"
    "  }\n"
    "}\n"
)


def created_region(frontmatter: str, core_body: str) -> str:
    """Return the exact document a freshly created region target contains.

    The markers are spelled literally here, and the empty project region holds no
    blank line, so an expectation built from this helper cannot drift with the
    production renderer it exists to check. Both parts receive the same
    trailing-newline rule the renderer applies.
    """
    return (
        ensure_trailing_newline(frontmatter)
        + "<!-- core:begin -->\n"
        + ensure_trailing_newline(core_body)
        + "<!-- core:end -->\n"
        + "\n"
        + "<!-- project:begin -->\n"
        + "<!-- project:end -->\n"
    )


# The QMD fixtures are built by `_qmd_document` before the constants that use
# it, so the source and any retargeted destination differ only in the index.
QMD_CORE_INDEX = "ai-core"
QMD_DESTINATION_FOLDER = "example-destination"


def _qmd_document(index_name: str) -> str:
    """Build a one-server JSONC document whose qmd command carries `index_name`."""
    return (
        "{\n"
        '  "mcp": {\n'
        '    "servers": {\n'
        '      "qmd": {\n'
        '        "type": "local",\n'
        '        "command": [\n'
        '          "npx", "-y", "@tobilu/qmd@2.8.3",\n'
        f'          "--index", "{index_name}", "mcp"\n'
        "        ],\n"
        '        "codemode": false\n'
        "      }\n"
        "    }\n"
        "  }\n"
        "}\n"
    )


QMD_SOURCE = _qmd_document(QMD_CORE_INDEX)

QMD_DESTINATION = (
    "{\n"
    '  "mcp": {\n'
    '    "servers": {\n'
    '      "memories": {\n'
    '        "command": ["npx", "-y", "@memories.sh/cli@0.7.9", "serve"]\n'
    "      }\n"
    "    }\n"
    "  }\n"
    "}\n"
)


def _qmd_index(document_text: str) -> object:
    """Return the argument following `--index` in a document's qmd command."""
    mcp = parse_object(document_text)["mcp"]
    assert isinstance(mcp, dict), "document has no mcp object"
    servers = mcp["servers"]
    assert isinstance(servers, dict), "document has no mcp.servers object"
    qmd = servers["qmd"]
    assert isinstance(qmd, dict), "document has no mcp.servers.qmd object"
    command = qmd["command"]
    assert isinstance(command, list), "qmd server has no command array"
    return command[command.index("--index") + 1]


ROOT_TEXT = "# Root runtime\n\nIntro paragraph.\n\nLast line.\n"

AGENT_SOURCE = ".opencode/agents/atrium.md"
ROOT_SOURCE = "AGENTS.md"

AGENT_MARKED = (
    "---\nname: atrium\nversion: 1.0.0\n---\n"
    "<!-- core:begin -->\nAgent core\n<!-- core:end -->\n"
)

ROOT_MARKED = (
    "---\nname: agents\n---\n"
    "<!-- core:begin -->\nRoot core\n<!-- core:end -->\n"
)

CLEARED_AGENT_AND_ROOT: dict[str, dict[str, str]] = {
    AGENT_SOURCE: {"mode": MODE_REGION},
    ROOT_SOURCE: {"mode": MODE_REGION, "role": ROLE_ROOT},
}


class _FixtureClearance(TypedDict):
    """Valid schema-1 clearance metadata maintained by source fixtures."""

    schema: int
    cleared: dict[str, dict[str, str]]

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
    "> **Config file (`opencode.jsonc`) — finish the migration.** A core "
    "update merges the core's top-level keys into this project's "
    "`opencode.jsonc`. If this project is still on the OpenCode V1 layout, "
    "migrate the file to the V2 layout. The merge keeps this project's own "
    "MCP servers alongside the core-registered ones, with a same-named MCP "
    "server entry core-wins; every other key is still replaced wholesale.\n"
    ">\n"
    "> **QMD index (`mcp.servers.qmd`).** The merge registers THIS project's "
    "own folder name as the QMD index, so no manual edit is needed after a "
    "synchronization. To use a different index name, declare that QMD server "
    "in this project's own `.opencode/opencode.jsonc`, which overrides the "
    "shipped entry; the shipped `opencode.jsonc` is merged core, so a "
    "same-named edit there is restored on the next synchronization. Then "
    "verify retrieval works. An empty result under this project's own index "
    "name may mean this project has never built that index, so populate it "
    "with this project's own retrieval tooling before treating the empty "
    "result as a synchronization defect. Never edit the core region to "
    "change the index.\n"
    ">\n"
    "> **Legacy incident knowledge — only if present.** If this project has "
    "legacy `knowledge/patterns.md` or `knowledge/escalation.md`, its own "
    "authorized agents must review that content before reconciling it. "
    "Preserve case links, verbatim executed queries, diagnostic evidence, "
    "local skill references and catalog entries. Reconcile failure-pattern "
    "evidence into the existing project-owned symptom/problem registers "
    "under diagnostics' `S-xx` to `Team: incident` `P-NNN` policy and existing "
    "admission/approval gates; do not create a competing identification "
    "authority or infer a verdict from legacy patterns. Assess live catalog "
    "consumers separately: skill references are not incident verdicts. Keep "
    "genuine organization routing and required-ticket-field mappings, "
    "including evidenced values/IDs, teams and tools, in the project content "
    "of `knowledge/escalation.md`, not its shared core. Never invent values "
    "or IDs; report missing evidence or mappings and block the affected "
    "action. Update live consumers before legacy retirement, and verify "
    "replacement evidence and references before any separately authorized "
    "retirement; this is not an instruction to delete every legacy file. "
    "Never edit the core region. This guidance grants no new mutation scope "
    "and no edit authority over this project to the synchronization operator; retain "
    "the complete applicable core set, existing pending/check lifecycle "
    "and destination-owned reconciliation boundary.\n"
    ">\n"
    "> **To finish.** When `pending:` is empty, **delete this entire blocker "
    "block** (from `<!-- core:reconcile:begin -->` to "
    "`<!-- core:reconcile:end -->`). Change nothing outside the project regions."
)


def _destination_root() -> str:
    """Build one destination instruction-root file body."""
    return "---\nname: dest\n---\n# Dest\n"


def _write_clearance(
    source: Path, cleared: dict[str, dict[str, str]]
) -> Path:
    """Write one fixture source's version-1 clearance document verbatim."""
    path = source / CLEARANCE_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"schema": CLEARANCE_SCHEMA, "cleared": cleared}) + "\n",
        encoding="utf-8",
    )
    return path


def _ensure_fixture_clearance(
    source_dir: Path, relative_path: str, mode: str = "region"
) -> None:
    """Pre-clear a written source fixture without repairing malformed metadata."""
    if relative_path == CLEARANCE_REL:
        return

    clearance_path = source_dir / CLEARANCE_REL
    clearance: _FixtureClearance
    if clearance_path.exists():
        try:
            data: object = json.loads(
                clearance_path.read_text(encoding="utf-8")
            )
        except (OSError, UnicodeError, json.JSONDecodeError):
            return
        if (
            not isinstance(data, dict)
            or type(data.get("schema")) is not int
            or data.get("schema") != CLEARANCE_SCHEMA
            or not isinstance(data.get("cleared"), dict)
            or not all(isinstance(item, dict) for item in data["cleared"].values())
        ):
            return
        clearance = cast(_FixtureClearance, data)
    else:
        clearance = {"schema": CLEARANCE_SCHEMA, "cleared": {}}

    source_path = Path(relative_path).as_posix()
    if source_path not in clearance["cleared"]:
        clearance["cleared"][source_path] = {"mode": mode}
        clearance_path.write_text(
            json.dumps(clearance, indent=2) + "\n", encoding="utf-8"
        )


def _write_file(base: Path, relative: str, content: str) -> Path:
    """Write a fixture file under a base directory, creating parents."""
    path = base / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    if base.name == "source":
        _ensure_fixture_clearance(base, relative)
    return path


def _write_bytes_file(
    base: Path, relative: str, content: bytes, mode: str = MODE_RAW
) -> Path:
    """Write a raw-byte fixture file under a base directory, creating parents."""
    path = base / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    if base.name == "source":
        _ensure_fixture_clearance(base, relative, mode=mode)
    return path


def _cleared_source(
    tmp_path: Path,
    *,
    raw_payloads: dict[str, bytes] | None = None,
) -> Path:
    """Build a cleared source tree: agent and root regions plus a clearance record.

    `raw_payloads` are written as byte copies and cleared `raw`, which is what the
    bulk-enrollment fixtures need beyond the two region sources.
    """
    source = tmp_path / "source"
    _write_file(source, AGENT_SOURCE, AGENT_MARKED)
    _write_file(source, ROOT_SOURCE, ROOT_MARKED)
    records = dict(CLEARED_AGENT_AND_ROOT)
    for relative, content in (raw_payloads or {}).items():
        _write_bytes_file(source, relative, content)
        records[relative] = {"mode": MODE_RAW}
    _write_clearance(source, records)
    return source


def _binding_entry(
    source: str, destinations: list[str], mode: BindingMode = "region"
) -> BindingEntry:
    """Build one bindings entry with an explicit mode."""
    return {"source": source, "destinations": list(destinations), "mode": mode}


def _bindings_with_entries(
    revision: str,
    entries: list[BindingEntry],
    pending: list[str] | None = None,
    root: str | None = None,
) -> Bindings:
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
    mode: BindingMode = "region",
) -> Bindings:
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
            root_text = sync_reconciliation_blocker(root_text, ["agent.md"])
        _write_file(destination, root_file, root_text)
    bindings_path = tmp_path / "bindings.yaml"
    save_bindings(
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
    save_bindings(
        bindings_path,
        _bindings_with_entries(
            pinned,
            [_binding_entry("opencode.jsonc", ["opencode.jsonc"], "raw")],
            pending,
        ),
    )
    return source, destination, bindings_path


def _merge_setup(
    tmp_path: Path,
    *,
    source_content: str = MERGE_SOURCE,
    destination_content: str | None = MERGE_DESTINATION,
    destination_name: str = "destination",
    pinned: str = REV_A,
    pending: list[str] | None = None,
) -> tuple[Path, Path, Path]:
    """Build a merge-mode source/destination JSONC fixture plus a merge bindings file.

    The source is cleared with mode `merge`; both documents are written verbatim
    so merge behavior is exercised without production parsing in the fixture.
    `destination_name` sets the destination directory's folder name, which merge
    mode reads as the destination project name.
    """
    source = tmp_path / "source"
    destination = tmp_path / destination_name
    _write_bytes_file(
        source, "opencode.jsonc", source_content.encode("utf-8"), mode=MODE_MERGE
    )
    if destination_content is None:
        destination.mkdir(parents=True, exist_ok=True)
    else:
        _write_file(destination, "opencode.jsonc", destination_content)
    bindings_path = tmp_path / "bindings.yaml"
    save_bindings(
        bindings_path,
        _bindings_with_entries(
            pinned,
            [_binding_entry("opencode.jsonc", ["opencode.jsonc"], "merge")],
            pending,
        ),
    )
    return source, destination, bindings_path
