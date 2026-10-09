"""Core update tool with two per-binding modes: `region` and `raw`.

In `region` mode (the default), `check` verifies that each destination file's
`core` region byte-matches the pinned source core; `apply` splices the source
core into each destination between its markers; `init` enrolls markerless
destinations (frontmatter kept verbatim, source core pasted between the core
markers, the previous body moved into a new project region) and refreshes
already-marked destinations. In `raw` mode, the binding has no markers: `init`
and `apply` write the source file to the destination byte-for-byte, and `check`
verifies byte-equality. Raw destinations carry no project region, no `pending`
entry, and no reconciliation report.

The source tree is read-only; the only writes are the destination files, a
reconciliation report, the bindings file, and the destination root runtime
file's reconciliation blocker.

While the bindings `pending` list contains region-mode paths, `check`/`apply`/
`init` keep a marker-delimited blocker block in the destination root runtime file
(the `root` bindings field, else `AGENTS.md` when present, else `CLAUDE.md`)
telling the destination project to reconcile its `project` region and clear
`pending`. `apply` and `init` remove raw-mode paths from persisted `pending`;
`check` excludes them from the blocker and rejects stale raw entries without
changing bindings.

Usage:
    uv run --frozen python3 .opencode/skills/core-sync/scripts/core_sync.py check --source DIR --destination DIR \
        --bindings FILE --source-revision <40-hex>
    uv run --frozen python3 .opencode/skills/core-sync/scripts/core_sync.py apply --source DIR --destination DIR \
        --bindings FILE --source-revision <40-hex>
    uv run --frozen python3 .opencode/skills/core-sync/scripts/core_sync.py init --source DIR --destination DIR \
        --bindings FILE --source-revision <40-hex>

Exit codes:
    0 — current (check), applied (apply), or initialized (init)
    1 — drift (stale revision, region mismatch, missing destination)
    2 — malformed input (bad bindings, invalid markers)
"""

from __future__ import annotations

import argparse
import os
import re
import stat
import sys
from pathlib import Path, PureWindowsPath
from typing import Literal, NotRequired, Optional, TypedDict

import yaml

BindingMode = Literal["region", "raw"]

MODE_REGION: BindingMode = "region"
MODE_RAW: BindingMode = "raw"
VALID_MODES: tuple[BindingMode, ...] = (MODE_REGION, MODE_RAW)

BEGIN = "<!-- core:begin -->"
END = "<!-- core:end -->"
PROJECT_BEGIN = "<!-- project:begin -->"
PROJECT_END = "<!-- project:end -->"

FRONTMATTER_DELIMITER = "---"
REVISION_RE = re.compile(r"^[0-9a-f]{40}$")
FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
SCHEMA_VERSION = 1
RECONCILIATION_DIRNAME = "reconciliation"
RECONCILIATION_FILENAME = "init.yaml"

RECONCILE_BEGIN = "<!-- core:reconcile:begin -->"
RECONCILE_END = "<!-- core:reconcile:end -->"
RECONCILE_BODY = (
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
DEFAULT_ROOT_CANDIDATES = ("AGENTS.md", "CLAUDE.md")

EXIT_OK = 0
EXIT_DRIFT = 1
EXIT_INVALID = 2


class BindingEntry(TypedDict):
    """One source file and the destination files that mirror it.

    `mode` selects the binding behavior: `region` (the default) mirrors the
    source core region between the destination markers, while `raw` copies the
    whole source file byte-for-byte and ignores markers.
    """

    source: str
    destinations: list[str]
    mode: BindingMode


class Bindings(TypedDict):
    """The bindings document: schema version, pinned revision, and mappings."""

    schema: int
    core_revision: Optional[str]
    bindings: list[BindingEntry]
    pending: list[str]
    root: NotRequired[Optional[str]]


class RegionSplit(TypedDict):
    """A marked file split into the bytes before, inside, and after its region."""

    before: str
    begin_line: str
    region: str
    end_line: str
    after: str


class MalformedSourceMarkers(ValueError):
    """A region-mode source contains core marker lines without one valid pair."""


class ReconciliationEntry(TypedDict):
    """One destination that `init` generated or refreshed for review."""

    destination: str
    source: str
    action: str


def _is_safe_relative(path: str) -> bool:
    """Return True when a bindings path is a canonical safe relative POSIX path."""
    if not path or "\x00" in path or "\\" in path:
        return False
    if any(part in ("", ".", "..") for part in path.split("/")):
        return False
    windows_path = PureWindowsPath(path)
    return not windows_path.drive and not windows_path.root


def _exact_marker_line_indices(lines: list[str], marker: str) -> list[int]:
    """Return the indices of exact stripped `marker` lines outside code fences.

    Markdown fences use at least three matching backticks or tildes. A closer
    must use the opening character at least as many times, have at most three
    leading spaces, and contain no trailing content beyond horizontal
    whitespace; marker-looking lines inside a fence are skipped.
    """
    active_fence: Optional[tuple[str, int]] = None
    matches: list[int] = []
    for index, line in enumerate(lines):
        line_without_terminator = line.rstrip("\r\n")
        stripped = line_without_terminator.strip()
        if active_fence is not None:
            fence_char, fence_length = active_fence
            closing_pattern = (
                rf" {{0,3}}{re.escape(fence_char)}{{{fence_length},}}[ \t]*"
            )
            if re.fullmatch(closing_pattern, line_without_terminator):
                active_fence = None
            continue

        opening = FENCE_OPEN_RE.match(line)
        if opening is not None:
            fence = opening.group(1)
            info = opening.group(2)
            if fence[0] != "`" or "`" not in info:
                active_fence = (fence[0], len(fence))
                continue

        if active_fence is not None:
            continue
        if stripped == marker:
            matches.append(index)
    return matches


def find_markers(content: str) -> Optional[tuple[int, int]]:
    """Return the (begin, end) line indices of the single valid marker pair.

    A marker counts only as an exact stripped line outside a fenced code block.
    Returns None when the BEGIN/END markers are missing, duplicated, or reversed.
    """
    lines = content.splitlines()
    begins = _exact_marker_line_indices(lines, BEGIN)
    ends = _exact_marker_line_indices(lines, END)
    if len(begins) != 1 or len(ends) != 1:
        return None
    if begins[0] > ends[0]:
        return None
    return (begins[0], ends[0])


def _has_exact_core_marker_lines(content: str) -> bool:
    """Return whether either exact core marker occurs outside a code fence."""
    lines = content.splitlines()
    return bool(
        _exact_marker_line_indices(lines, BEGIN)
        or _exact_marker_line_indices(lines, END)
    )


def split_regions(content: str) -> Optional[RegionSplit]:
    """Split content into the bytes around and inside its single core region."""
    markers = find_markers(content)
    if markers is None:
        return None
    begin_index, end_index = markers
    lines = content.splitlines(keepends=True)
    return {
        "before": "".join(lines[:begin_index]),
        "begin_line": lines[begin_index],
        "region": "".join(lines[begin_index + 1 : end_index]),
        "end_line": lines[end_index],
        "after": "".join(lines[end_index + 1 :]),
    }


def outside_bytes(region_split: RegionSplit) -> str:
    """Return the bytes that are not the core region, the markers included."""
    return (
        region_split["before"]
        + region_split["begin_line"]
        + region_split["end_line"]
        + region_split["after"]
    )


def split_frontmatter(content: str) -> tuple[str, str]:
    """Split leading YAML frontmatter from the body, preserving both verbatim.

    Returns `("", content)` when the content does not open with a `---` line or
    has no closing delimiter.
    """
    lines = content.splitlines(keepends=True)
    if not lines or lines[0].strip() != FRONTMATTER_DELIMITER:
        return ("", content)
    for index in range(1, len(lines)):
        if lines[index].strip() == FRONTMATTER_DELIMITER:
            return ("".join(lines[: index + 1]), "".join(lines[index + 1 :]))
    return ("", content)


def extract_source_core(content: str) -> str:
    """Return a source file's core bytes.

    A valid marker pair yields its region. A markerless source uses its whole
    post-frontmatter body; any malformed exact core marker set raises
    `MalformedSourceMarkers` instead of falling back to markerless behavior.
    """
    region_split = split_regions(content)
    if region_split is not None:
        return region_split["region"]
    if _has_exact_core_marker_lines(content):
        raise MalformedSourceMarkers("source core markers are malformed")
    _, body = split_frontmatter(content)
    return body


def ensure_trailing_newline(text: str) -> str:
    """Return `text` with a trailing newline, adding one only when missing."""
    if not text or text.endswith("\n"):
        return text
    return text + "\n"


def render_with_region(destination: RegionSplit, source_region: str) -> str:
    """Rebuild a destination file with the source core region spliced in."""
    return (
        destination["before"]
        + destination["begin_line"]
        + source_region
        + destination["end_line"]
        + destination["after"]
    )


def render_init_file(destination_content: str, source_core: str) -> str:
    """Rebuild a markerless destination as a core region plus a project region.

    The destination frontmatter is kept verbatim; the source core fills the new
    core region; everything after the destination frontmatter is moved verbatim
    into the new project region.
    """
    frontmatter, body = split_frontmatter(destination_content)
    return (
        frontmatter
        + BEGIN
        + "\n"
        + ensure_trailing_newline(source_core)
        + END
        + "\n\n"
        + PROJECT_BEGIN
        + "\n"
        + ensure_trailing_newline(body)
        + PROJECT_END
        + "\n"
    )


def render_reconciliation_report(
    entries: list[ReconciliationEntry], revision: str
) -> str:
    """Render the reconciliation report for an `init` run to YAML."""
    data = {
        "schema": SCHEMA_VERSION,
        "core_revision": revision,
        "entries": [
            {
                "destination": entry["destination"],
                "source": entry["source"],
                "action": entry["action"],
            }
            for entry in entries
        ],
    }
    return yaml.safe_dump(data, sort_keys=False, default_flow_style=False)


def _reconcile_block_lines() -> list[str]:
    """Return the reconciliation blocker block as newline-terminated lines."""
    return [
        RECONCILE_BEGIN + "\n",
        RECONCILE_BODY + "\n",
        RECONCILE_END + "\n",
    ]


def find_reconcile_block(lines: list[str]) -> Optional[tuple[int, int]]:
    """Return the (begin, end) line indices of the single reconcile marker pair.

    A marker counts only as an exact stripped line outside a fenced code block.
    Returns None when the markers are missing, duplicated, or reversed.
    """
    begins = _exact_marker_line_indices(lines, RECONCILE_BEGIN)
    ends = _exact_marker_line_indices(lines, RECONCILE_END)
    if len(begins) != 1 or len(ends) != 1:
        return None
    if begins[0] > ends[0]:
        return None
    return (begins[0], ends[0])


def _append_reconcile_block(root_text: str, block_lines: list[str]) -> str:
    """Append the blocker block after a single blank separator line."""
    base = root_text
    if base and not base.endswith("\n"):
        base += "\n"
    separator = "\n" if base else ""
    return base + separator + "".join(block_lines)


def sync_reconciliation_blocker(root_text: str, pending: list[str]) -> str:
    """Add, refresh, or remove the reconciliation blocker block in root text.

    Pure transform. A non-empty `pending` ensures the marker-delimited blocker
    block exists — its body is replaced in place when present, otherwise the block
    is appended after one blank line. An empty `pending` removes the block and its
    one-line blank separator. The transform is idempotent.
    """
    lines = root_text.splitlines(keepends=True)
    block = find_reconcile_block(lines)
    if pending:
        block_lines = _reconcile_block_lines()
        if block is not None:
            begin_index, end_index = block
            return "".join(lines[:begin_index] + block_lines + lines[end_index + 1 :])
        return _append_reconcile_block(root_text, block_lines)
    if block is None:
        return root_text
    begin_index, end_index = block
    start = begin_index
    if start > 0 and lines[start - 1].strip() == "":
        start -= 1
    stop = end_index + 1
    if stop < len(lines) and lines[stop].strip() == "":
        stop += 1
    return "".join(lines[:start] + lines[stop:])


def _parse_binding_entry(
    raw_entry: object, seen_destinations: set[str]
) -> Optional[BindingEntry]:
    """Validate one `{source, destinations, mode?}` mapping and its destinations."""
    if not isinstance(raw_entry, dict):
        return None
    source = raw_entry.get("source")
    destinations = raw_entry.get("destinations")
    mode = raw_entry.get("mode", MODE_REGION)
    if not isinstance(source, str) or not _is_safe_relative(source):
        return None
    if not isinstance(destinations, list) or not destinations:
        return None
    if mode not in VALID_MODES:
        return None
    resolved: list[str] = []
    for destination in destinations:
        if not isinstance(destination, str) or not _is_safe_relative(destination):
            return None
        if destination in seen_destinations:
            return None
        seen_destinations.add(destination)
        resolved.append(destination)
    return {"source": source, "destinations": resolved, "mode": mode}


def _parse_init_binding_spec(
    spec: str, mode: BindingMode
) -> Optional[tuple[str, str, BindingMode]]:
    """Parse one exact `SOURCE=DEST` init declaration with safe paths."""
    if spec.count("=") != 1:
        return None
    source, destination = spec.split("=")
    if (
        "\x00" in source
        or "\x00" in destination
        or not _is_safe_relative(source)
        or not _is_safe_relative(destination)
    ):
        return None
    return (source, destination, mode)


def _merge_init_binding_options(
    bindings: Bindings, region_specs: list[str], raw_specs: list[str]
) -> tuple[Optional[str], set[str]]:
    """Merge CLI declarations and report raw destinations newly registered here."""
    destination_mappings = {
        destination: (entry["source"], entry["mode"])
        for entry in bindings["bindings"]
        for destination in entry["destinations"]
    }
    new_raw_destinations: set[str] = set()
    declarations = [
        *((spec, MODE_REGION) for spec in region_specs),
        *((spec, MODE_RAW) for spec in raw_specs),
    ]
    for spec, mode in declarations:
        declaration = _parse_init_binding_spec(spec, mode)
        if declaration is None:
            return (f"malformed or unsafe binding declaration: {spec!r}", set())
        source, destination, declaration_mode = declaration
        existing_mapping = destination_mappings.get(destination)
        if existing_mapping is not None:
            if existing_mapping != (source, declaration_mode):
                return (f"destination mapping conflicts for {destination!r}", set())
            continue

        matching_entry = next(
            (
                entry
                for entry in bindings["bindings"]
                if entry["source"] == source and entry["mode"] == declaration_mode
            ),
            None,
        )
        if matching_entry is None:
            bindings["bindings"].append(
                {
                    "source": source,
                    "destinations": [destination],
                    "mode": declaration_mode,
                }
            )
        else:
            matching_entry["destinations"].append(destination)
        destination_mappings[destination] = (source, declaration_mode)
        if declaration_mode == MODE_RAW:
            new_raw_destinations.add(destination)
    return (None, new_raw_destinations)


def parse_bindings(text: str) -> Optional[Bindings]:
    """Parse and validate a bindings document, returning None when malformed."""
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError:
        return None
    if not isinstance(data, dict) or data.get("schema") != SCHEMA_VERSION:
        return None

    revision = data.get("core_revision")
    if revision is not None:
        if not isinstance(revision, str) or not REVISION_RE.match(revision):
            return None

    raw_bindings = data.get("bindings")
    if not isinstance(raw_bindings, list):
        return None

    entries: list[BindingEntry] = []
    seen_destinations: set[str] = set()
    for raw_entry in raw_bindings:
        entry = _parse_binding_entry(raw_entry, seen_destinations)
        if entry is None:
            return None
        entries.append(entry)

    raw_root = data.get("root")
    if raw_root is not None:
        if not isinstance(raw_root, str) or not _is_safe_relative(raw_root):
            return None

    raw_pending = data.get("pending", [])
    if not isinstance(raw_pending, list):
        return None
    if not all(isinstance(item, str) for item in raw_pending):
        return None

    return {
        "schema": SCHEMA_VERSION,
        "core_revision": revision,
        "bindings": entries,
        "pending": list(raw_pending),
        "root": raw_root,
    }


def serialize_bindings(bindings: Bindings) -> str:
    """Render a bindings document to YAML without reordering its fields."""
    data: dict[str, object] = {
        "schema": bindings["schema"],
        "core_revision": bindings["core_revision"],
    }
    root = bindings.get("root")
    if root is not None:
        data["root"] = root
    data["bindings"] = [
        _serialize_binding_entry(entry) for entry in bindings["bindings"]
    ]
    data["pending"] = list(bindings["pending"])
    return yaml.safe_dump(data, sort_keys=False, default_flow_style=False)


def _serialize_binding_entry(entry: BindingEntry) -> dict[str, object]:
    """Render one binding entry, emitting `mode` only when it is not the default."""
    item: dict[str, object] = {
        "source": entry["source"],
        "destinations": list(entry["destinations"]),
    }
    if entry["mode"] != MODE_REGION:
        item["mode"] = entry["mode"]
    return item


def _raw_destination_paths(bindings: Bindings) -> set[str]:
    """Return every destination currently bound in raw mode."""
    return {
        destination
        for entry in bindings["bindings"]
        if entry["mode"] == MODE_RAW
        for destination in entry["destinations"]
    }


def _normalize_pending(pending: list[str], raw_destinations: set[str]) -> list[str]:
    """Return pending paths that still have a region to reconcile."""
    return [path for path in pending if path not in raw_destinations]


def read_text(path: Path) -> Optional[str]:
    """Read UTF-8 text from a path at the IO boundary."""
    try:
        with path.open("r", encoding="utf-8", newline="") as file:
            return file.read()
    except (OSError, UnicodeError):
        return None


def load_bindings(path: Path) -> Optional[Bindings]:
    """Read and parse the bindings file at the IO boundary."""
    text = read_text(path)
    if text is None:
        return None
    return parse_bindings(text)


def write_text(path: Path, content: str) -> None:
    """Write UTF-8 text to a path at the IO boundary."""
    with path.open("w", encoding="utf-8", newline="") as file:
        file.write(content)


def read_bytes(path: Path) -> Optional[bytes]:
    """Read raw bytes from a path at the IO boundary, or None when unreadable."""
    try:
        return path.read_bytes()
    except OSError:
        return None


def write_bytes(path: Path, content: bytes) -> None:
    """Write raw bytes to a path at the IO boundary."""
    path.write_bytes(content)


def read_source_raw(path: Path) -> Optional[bytes]:
    """Read a source file's bytes verbatim at the IO boundary (raw mode)."""
    return read_bytes(path)


def save_bindings(path: Path, bindings: Bindings) -> None:
    """Serialize and write the bindings file at the IO boundary."""
    write_text(path, serialize_bindings(bindings))


def reconciliation_report_path(bindings_path: Path) -> Path:
    """Return the reconciliation report path derived from the bindings file."""
    return (
        bindings_path.parent / RECONCILIATION_DIRNAME / RECONCILIATION_FILENAME
    )


def write_reconciliation_report(
    path: Path, entries: list[ReconciliationEntry], revision: str
) -> None:
    """Write the reconciliation report at the IO boundary."""
    path.parent.mkdir(parents=True, exist_ok=True)
    write_text(path, render_reconciliation_report(entries, revision))


def resolve_root_path(destination_dir: Path, bindings: Bindings) -> Path:
    """Resolve the destination root runtime file at the IO boundary.

    Uses the explicit `root` bindings field when present; otherwise defaults to
    `AGENTS.md` when it exists in the destination, else `CLAUDE.md`.
    """
    root = bindings.get("root")
    if root is not None:
        return destination_dir / root
    for candidate in DEFAULT_ROOT_CANDIDATES:
        path = destination_dir / candidate
        if path.is_file():
            return path
    return destination_dir / DEFAULT_ROOT_CANDIDATES[-1]


def _path_is_within(path: Path, root: Path) -> bool:
    """Return whether a resolved path is equal to or nested under a root."""
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _source_regular_file_inodes(source_dir: Path) -> set[tuple[int, int]]:
    """Collect regular-file device/inode identities reachable under the source root."""
    try:
        root_stat = source_dir.stat()
    except FileNotFoundError:
        return set()
    if stat.S_ISREG(root_stat.st_mode):
        return {(root_stat.st_dev, root_stat.st_ino)}
    if not stat.S_ISDIR(root_stat.st_mode):
        return set()

    inodes: set[tuple[int, int]] = set()
    visited_directories = {(root_stat.st_dev, root_stat.st_ino)}
    directories = [source_dir]
    while directories:
        directory = directories.pop()
        with os.scandir(directory) as entries:
            for entry in entries:
                try:
                    entry_stat = entry.stat(follow_symlinks=True)
                except FileNotFoundError:
                    if entry.is_symlink():
                        continue
                    raise
                identity = (entry_stat.st_dev, entry_stat.st_ino)
                if stat.S_ISDIR(entry_stat.st_mode):
                    if identity not in visited_directories:
                        visited_directories.add(identity)
                        directories.append(Path(entry.path))
                elif stat.S_ISREG(entry_stat.st_mode):
                    inodes.add(identity)
    return inodes


def _preflight_write_targets(
    command: Literal["check", "apply", "init"],
    source_dir: Path,
    destination_dir: Path,
    bindings_path: Path,
    bindings: Bindings,
    new_raw_destinations: Optional[set[str]] = None,
) -> Optional[str]:
    """Reject unsafe, aliased, or source-inode write targets before mutation."""
    try:
        resolved_source = source_dir.resolve()
        resolved_destination = destination_dir.resolve()
    except (OSError, RuntimeError) as error:
        return f"could not resolve source or destination root: {error}"

    if _path_is_within(resolved_source, resolved_destination) or _path_is_within(
        resolved_destination, resolved_source
    ):
        return "source and destination roots overlap"

    try:
        source_file_inodes = _source_regular_file_inodes(source_dir)
    except OSError as error:
        return f"could not inspect source tree for write protection: {error}"

    root_path = resolve_root_path(destination_dir, bindings)
    raw_destination_paths = [
        destination_dir / destination
        for entry in bindings["bindings"]
        if entry["mode"] == MODE_RAW
        for destination in entry["destinations"]
    ]
    targets: list[tuple[Path, str]] = [(root_path, "root")]
    if command in ("apply", "init"):
        targets.extend(
            (destination_dir / destination, "destination payload")
            for entry in bindings["bindings"]
            for destination in entry["destinations"]
        )
        targets.append((bindings_path, "bindings"))
    if command == "init":
        targets.append((reconciliation_report_path(bindings_path), "report"))

    resolved_root: Optional[Path] = None
    resolved_targets: dict[Path, tuple[Path, Path, str]] = {}
    target_inodes: dict[tuple[int, int], tuple[Path, Path, str]] = {}
    for target, target_kind in targets:
        try:
            resolved_target = target.resolve()
        except (OSError, RuntimeError) as error:
            return (
                f"could not resolve {target_kind} write target {target}: {error}"
            )
        lexical_target = Path(os.path.abspath(target))
        previous_target = resolved_targets.get(resolved_target)
        if previous_target is not None:
            previous_path, previous_lexical, previous_kind = previous_target
            if (
                previous_kind == "root"
                and target_kind == "destination payload"
                and target in raw_destination_paths
            ):
                return f"root write target aliases raw destination: {target}"
            same_root_region_target = (
                lexical_target == previous_lexical
                and {target_kind, previous_kind} == {"root", "destination payload"}
                and target not in raw_destination_paths
            )
            if not same_root_region_target:
                return (
                    "distinct write targets alias after resolution: "
                    f"{previous_path} and {target}"
                )
        else:
            resolved_targets[resolved_target] = (
                target,
                lexical_target,
                target_kind,
            )
        if _path_is_within(resolved_target, resolved_source):
            return f"{target_kind} write target resolves inside source tree: {target}"
        if target_kind in ("root", "destination payload") and not _path_is_within(
            resolved_target, resolved_destination
        ):
            return f"{target_kind} write target escapes destination root: {target}"
        try:
            target_stat = target.stat()
        except FileNotFoundError:
            target_stat = None
        except OSError as error:
            return f"could not inspect {target_kind} write target {target}: {error}"
        if target_stat is not None and stat.S_ISREG(target_stat.st_mode):
            target_inode = (target_stat.st_dev, target_stat.st_ino)
            if target_inode in source_file_inodes:
                return (
                    f"{target_kind} write target shares a source-tree file inode: "
                    f"{target}"
                )
            previous_inode_target = target_inodes.get(target_inode)
            if previous_inode_target is not None:
                previous_path, previous_lexical, previous_kind = previous_inode_target
                same_root_region_target = (
                    lexical_target == previous_lexical
                    and {target_kind, previous_kind}
                    == {"root", "destination payload"}
                )
                if not same_root_region_target:
                    return (
                        "distinct write targets share a filesystem inode: "
                        f"{previous_path} and {target}"
                    )
            else:
                target_inodes[target_inode] = (
                    target,
                    lexical_target,
                    target_kind,
                )
        if target_kind == "root":
            resolved_root = resolved_target

    for raw_destination_path in raw_destination_paths:
        try:
            resolved_raw_destination = raw_destination_path.resolve()
        except (OSError, RuntimeError) as error:
            return (
                "could not resolve raw destination write target "
                f"{raw_destination_path}: {error}"
            )
        if resolved_root == resolved_raw_destination:
            return (
                "root write target aliases raw destination: "
                f"{raw_destination_path}"
            )
        try:
            root_stat = root_path.stat()
            raw_stat = raw_destination_path.stat()
        except FileNotFoundError:
            continue
        except OSError as error:
            return (
                "could not inspect root/raw destination alias targets: "
                f"{error}"
            )
        if (
            stat.S_ISREG(root_stat.st_mode)
            and stat.S_ISREG(raw_stat.st_mode)
            and (root_stat.st_dev, root_stat.st_ino)
            == (raw_stat.st_dev, raw_stat.st_ino)
        ):
            return (
                "root write target aliases raw destination: "
                f"{raw_destination_path}"
            )

    if command == "init" and bindings.get("root") is None:
        agents_path = destination_dir / DEFAULT_ROOT_CANDIDATES[0]
        if not agents_path.is_file():
            try:
                resolved_agents_path = agents_path.resolve()
            except (OSError, RuntimeError) as error:
                return f"could not resolve default root candidate {agents_path}: {error}"
            for destination in new_raw_destinations or set():
                raw_path = destination_dir / destination
                if (
                    raw_path.exists()
                    or raw_path.is_symlink()
                    or not raw_path.parent.is_dir()
                ):
                    continue
                try:
                    resolved_raw_path = raw_path.resolve()
                except (OSError, RuntimeError) as error:
                    return (
                        "could not resolve planned raw destination "
                        f"{raw_path}: {error}"
                    )
                if resolved_raw_path == resolved_agents_path:
                    return (
                        "default root would alias newly created raw destination: "
                        f"{raw_path}"
                    )

    return None


def write_reconciliation_blocker(root_path: Path, pending: list[str]) -> bool:
    """Sync the reconciliation blocker block into the root file at the IO boundary.

    Reads the root file, applies `sync_reconciliation_blocker`, and writes it back
    only when the text changed. Returns False when the root file is missing or
    unreadable so the caller can skip it silently.
    """
    root_text = read_text(root_path)
    if root_text is None:
        return False
    new_text = sync_reconciliation_blocker(root_text, pending)
    if new_text != root_text:
        write_text(root_path, new_text)
    return True


def read_region_split(path: Path) -> Optional[RegionSplit]:
    """Read a file and split its core region at the IO boundary."""
    content = read_text(path)
    if content is None:
        return None
    return split_regions(content)


def read_source_core(path: Path) -> Optional[str]:
    """Read a source file's core at the IO boundary.

    Raises `MalformedSourceMarkers` when the source has exact core marker lines
    outside fences but no single ordered pair.
    """
    content = read_text(path)
    if content is None:
        return None
    return extract_source_core(content)


def run_check(args: argparse.Namespace) -> int:
    """Verify every destination core region against the pinned source core."""
    bindings = load_bindings(Path(args.bindings))
    if bindings is None:
        print(f"invalid bindings: {args.bindings}", file=sys.stderr)
        return EXIT_INVALID

    source_dir = Path(args.source)
    destination_dir = Path(args.destination)
    preflight_error = _preflight_write_targets(
        "check", source_dir, destination_dir, Path(args.bindings), bindings
    )
    if preflight_error is not None:
        print(f"invalid write target: {preflight_error}", file=sys.stderr)
        return EXIT_INVALID

    source_cores: dict[str, str] = {}
    for entry in bindings["bindings"]:
        if entry["mode"] == MODE_RAW:
            continue
        source_path = source_dir / entry["source"]
        try:
            source_core = read_source_core(source_path)
        except MalformedSourceMarkers:
            print(f"invalid source markers: {source_path}", file=sys.stderr)
            return EXIT_INVALID
        if source_core is None:
            print(f"missing source: {source_path}", file=sys.stderr)
            return EXIT_DRIFT
        source_cores[entry["source"]] = source_core

    raw_destinations = _raw_destination_paths(bindings)
    stale_raw_pending = [
        path for path in bindings["pending"] if path in raw_destinations
    ]
    normalized_pending = _normalize_pending(bindings["pending"], raw_destinations)
    write_reconciliation_blocker(
        resolve_root_path(destination_dir, bindings), normalized_pending
    )

    if stale_raw_pending:
        paths = ", ".join(stale_raw_pending)
        print(
            "stale raw-bound pending paths cannot be reconciled: "
            f"{paths}; run apply or init to normalize the stale binding state",
            file=sys.stderr,
        )
        return EXIT_DRIFT

    if bindings["core_revision"] != args.source_revision:
        print("revision drift: bindings revision does not match source", file=sys.stderr)
        return EXIT_DRIFT

    for entry in bindings["bindings"]:
        source_path = source_dir / entry["source"]
        if entry["mode"] == MODE_RAW:
            source_bytes = read_source_raw(source_path)
            if source_bytes is None:
                print(f"missing source: {source_path}", file=sys.stderr)
                return EXIT_DRIFT
            for destination in entry["destinations"]:
                destination_path = destination_dir / destination
                destination_bytes = read_bytes(destination_path)
                if destination_bytes is None:
                    print(f"missing destination: {destination_path}", file=sys.stderr)
                    return EXIT_DRIFT
                if destination_bytes != source_bytes:
                    print(f"raw drift: {destination_path}", file=sys.stderr)
                    return EXIT_DRIFT
            continue
        source_core = source_cores[entry["source"]]
        for destination in entry["destinations"]:
            destination_path = destination_dir / destination
            if not destination_path.is_file():
                print(f"missing destination: {destination_path}", file=sys.stderr)
                return EXIT_DRIFT
            destination_split = read_region_split(destination_path)
            if destination_split is None:
                print(f"invalid destination markers: {destination_path}", file=sys.stderr)
                return EXIT_INVALID
            if destination_split["region"] != source_core:
                print(f"region drift: {destination_path}", file=sys.stderr)
                return EXIT_DRIFT

    if bindings["pending"]:
        print("pending changes: destination is not current", file=sys.stderr)
        return EXIT_DRIFT

    print("current")
    return EXIT_OK


def run_apply(args: argparse.Namespace) -> int:
    """Splice each source core into its destinations, then pin the revision."""
    bindings = load_bindings(Path(args.bindings))
    if bindings is None:
        print(f"invalid bindings: {args.bindings}", file=sys.stderr)
        return EXIT_INVALID

    source_dir = Path(args.source)
    destination_dir = Path(args.destination)
    bindings_path = Path(args.bindings)
    preflight_error = _preflight_write_targets(
        "apply", source_dir, destination_dir, bindings_path, bindings
    )
    if preflight_error is not None:
        print(f"invalid write target: {preflight_error}", file=sys.stderr)
        return EXIT_INVALID

    writes: list[tuple[Path, str]] = []
    raw_writes: list[tuple[Path, bytes]] = []
    for entry in bindings["bindings"]:
        source_path = source_dir / entry["source"]
        if entry["mode"] == MODE_RAW:
            source_bytes = read_source_raw(source_path)
            if source_bytes is None:
                print(f"missing source: {source_path}", file=sys.stderr)
                return EXIT_DRIFT
            for destination in entry["destinations"]:
                destination_path = destination_dir / destination
                if not destination_path.is_file():
                    print(f"missing destination: {destination_path}", file=sys.stderr)
                    return EXIT_DRIFT
                raw_writes.append((destination_path, source_bytes))
            continue
        try:
            source_core = read_source_core(source_path)
        except MalformedSourceMarkers:
            print(f"invalid source markers: {source_path}", file=sys.stderr)
            return EXIT_INVALID
        if source_core is None:
            print(f"missing source: {source_path}", file=sys.stderr)
            return EXIT_DRIFT
        for destination in entry["destinations"]:
            destination_path = destination_dir / destination
            if not destination_path.is_file():
                print(f"missing destination: {destination_path}", file=sys.stderr)
                return EXIT_DRIFT
            destination_split = read_region_split(destination_path)
            if destination_split is None:
                print(f"invalid destination markers: {destination_path}", file=sys.stderr)
                return EXIT_INVALID
            new_content = render_with_region(destination_split, source_core)
            new_split = split_regions(new_content)
            if new_split is None or outside_bytes(new_split) != outside_bytes(
                destination_split
            ):
                print(f"outside-marker mismatch: {destination_path}", file=sys.stderr)
                return EXIT_INVALID
            writes.append((destination_path, new_content))

    for destination_path, new_content in writes:
        write_text(destination_path, new_content)
    for destination_path, raw_content in raw_writes:
        write_bytes(destination_path, raw_content)

    bindings["core_revision"] = args.source_revision
    bindings["pending"] = _normalize_pending(
        bindings["pending"], _raw_destination_paths(bindings)
    )
    save_bindings(bindings_path, bindings)
    write_reconciliation_blocker(
        resolve_root_path(destination_dir, bindings), bindings["pending"]
    )
    print("applied")
    return EXIT_OK


def run_init(args: argparse.Namespace) -> int:
    """Enroll markerless destinations and refresh already-marked destinations."""
    bindings = load_bindings(Path(args.bindings))
    if bindings is None:
        print(f"invalid bindings: {args.bindings}", file=sys.stderr)
        return EXIT_INVALID

    declaration_error, new_raw_destinations = _merge_init_binding_options(
        bindings, getattr(args, "bind", []), getattr(args, "bind_raw", [])
    )
    if declaration_error is not None:
        print(f"invalid init binding: {declaration_error}", file=sys.stderr)
        return EXIT_INVALID

    source_dir = Path(args.source)
    destination_dir = Path(args.destination)
    bindings_path = Path(args.bindings)
    preflight_error = _preflight_write_targets(
        "init",
        source_dir,
        destination_dir,
        bindings_path,
        bindings,
        new_raw_destinations,
    )
    if preflight_error is not None:
        print(f"invalid write target: {preflight_error}", file=sys.stderr)
        return EXIT_INVALID

    writes: list[tuple[Path, str]] = []
    raw_writes: list[tuple[Path, bytes]] = []
    entries: list[ReconciliationEntry] = []
    pending = _normalize_pending(
        bindings["pending"], _raw_destination_paths(bindings)
    )

    for entry in bindings["bindings"]:
        source_path = source_dir / entry["source"]
        if entry["mode"] == MODE_RAW:
            source_bytes = read_source_raw(source_path)
            if source_bytes is None:
                print(f"missing source: {source_path}", file=sys.stderr)
                return EXIT_DRIFT
            for destination in entry["destinations"]:
                destination_path = destination_dir / destination
                destination_bytes = read_bytes(destination_path)
                if destination_bytes is None:
                    if (
                        destination in new_raw_destinations
                        and not destination_path.exists()
                        and not destination_path.is_symlink()
                    ):
                        if not destination_path.parent.is_dir():
                            print(
                                "missing destination parent: "
                                f"{destination_path.parent}",
                                file=sys.stderr,
                            )
                            return EXIT_DRIFT
                        raw_writes.append((destination_path, source_bytes))
                        continue
                    print(f"missing destination: {destination_path}", file=sys.stderr)
                    return EXIT_DRIFT
                if destination_bytes == source_bytes:
                    continue
                raw_writes.append((destination_path, source_bytes))
            continue
        try:
            source_core = read_source_core(source_path)
        except MalformedSourceMarkers:
            print(f"invalid source markers: {source_path}", file=sys.stderr)
            return EXIT_INVALID
        if source_core is None:
            print(f"missing source: {source_path}", file=sys.stderr)
            return EXIT_DRIFT
        for destination in entry["destinations"]:
            destination_path = destination_dir / destination
            destination_content = read_text(destination_path)
            if destination_content is None:
                print(f"missing destination: {destination_path}", file=sys.stderr)
                return EXIT_DRIFT
            destination_split = split_regions(destination_content)
            if destination_split is None:
                if _has_exact_core_marker_lines(destination_content):
                    print(
                        f"invalid destination markers: {destination_path}",
                        file=sys.stderr,
                    )
                    return EXIT_INVALID
                new_content = render_init_file(destination_content, source_core)
                writes.append((destination_path, new_content))
                entries.append(
                    {
                        "destination": destination,
                        "source": entry["source"],
                        "action": "initialized",
                    }
                )
                if destination not in pending:
                    pending.append(destination)
                continue
            new_content = render_with_region(destination_split, source_core)
            new_split = split_regions(new_content)
            if new_split is None or outside_bytes(new_split) != outside_bytes(
                destination_split
            ):
                print(f"outside-marker mismatch: {destination_path}", file=sys.stderr)
                return EXIT_INVALID
            if new_split["region"] == destination_split["region"]:
                continue
            writes.append((destination_path, new_content))
            entries.append(
                {
                    "destination": destination,
                    "source": entry["source"],
                    "action": "refreshed",
                }
            )
            if destination not in pending:
                pending.append(destination)

    for destination_path, new_content in writes:
        write_text(destination_path, new_content)
    for destination_path, raw_content in raw_writes:
        write_bytes(destination_path, raw_content)

    if entries:
        write_reconciliation_report(
            reconciliation_report_path(bindings_path),
            entries,
            args.source_revision,
        )

    bindings["core_revision"] = args.source_revision
    bindings["pending"] = pending
    save_bindings(bindings_path, bindings)
    write_reconciliation_blocker(
        resolve_root_path(destination_dir, bindings), bindings["pending"]
    )
    print("initialized")
    return EXIT_OK


def _revision_arg(value: str) -> str:
    """Argparse type: require a 40-character lowercase hex revision string."""
    if not REVISION_RE.match(value):
        raise argparse.ArgumentTypeError("must be a 40-character lowercase hex string")
    return value


def _build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser with the shared flags for every subcommand."""
    parser = argparse.ArgumentParser(
        prog="core-sync",
        description="Region- or raw-mode core update for destination files.",
        epilog="Exit codes: 0 current/applied/initialized, 1 drift, 2 malformed input.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("check", "verify destination core regions against the source"),
        ("apply", "splice source core regions into the destinations"),
        ("init", "enroll markerless destinations and refresh marked ones"),
    ):
        subparser = subparsers.add_parser(name, help=help_text)
        subparser.add_argument("--source", required=True, help="source directory")
        subparser.add_argument(
            "--destination", required=True, help="destination directory"
        )
        subparser.add_argument("--bindings", required=True, help="bindings YAML file")
        subparser.add_argument(
            "--source-revision",
            required=True,
            type=_revision_arg,
            help="40-hex source revision to pin or compare",
        )
        if name == "init":
            subparser.add_argument(
                "--bind",
                action="append",
                default=[],
                metavar="SOURCE=DEST",
                help="add a region-mode source and destination mapping (repeatable)",
            )
            subparser.add_argument(
                "--bind-raw",
                action="append",
                default=[],
                metavar="SOURCE=DEST",
                help="add a raw-mode source and destination mapping (repeatable)",
            )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """Parse arguments and dispatch to `check`, `apply`, or `init`."""
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "check":
            return run_check(args)
        if args.command == "apply":
            return run_apply(args)
        return run_init(args)
    except OSError as error:
        print(f"core-sync I/O error: {error}", file=sys.stderr)
        return EXIT_DRIFT


if __name__ == "__main__":
    sys.exit(main())
