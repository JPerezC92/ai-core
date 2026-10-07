"""Region-based core update tool.

`check` verifies that each destination file's `core` region byte-matches the
pinned source core; `apply` splices the source core into each destination
between its markers; `init` enrolls markerless destinations (frontmatter kept
verbatim, source core pasted between the core markers, the previous body moved
into a new project region) and refreshes already-marked destinations. The source
tree is read-only; the only writes are the destination files, a reconciliation
report, the bindings file, and the destination root runtime file's reconciliation
blocker.

While the bindings `pending` list is non-empty, `check`/`apply`/`init` keep a
marker-delimited blocker block in the destination root runtime file (the `root`
bindings field, else `AGENTS.md` when present, else `CLAUDE.md`) telling the
destination project to reconcile its `project` region and clear `pending`. Once
`pending` is empty, `check` removes the block.

Usage:
    python3 core_sync.py check --source DIR --destination DIR \
        --bindings FILE --source-revision <40-hex>
    python3 core_sync.py apply --source DIR --destination DIR \
        --bindings FILE --source-revision <40-hex>
    python3 core_sync.py init --source DIR --destination DIR \
        --bindings FILE --source-revision <40-hex>

Exit codes:
    0 — current (check), applied (apply), or initialized (init)
    1 — drift (stale revision, region mismatch, missing destination)
    2 — malformed input (bad bindings, invalid markers)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NotRequired, Optional, TypedDict

import yaml

BEGIN = "<!-- core:begin -->"
END = "<!-- core:end -->"
PROJECT_BEGIN = "<!-- project:begin -->"
PROJECT_END = "<!-- project:end -->"

FRONTMATTER_DELIMITER = "---"
REVISION_RE = re.compile(r"^[0-9a-f]{40}$")
FENCE_PREFIX = "```"
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
DEFAULT_ROOT_CANDIDATES = ("AGENTS.md", "CLAUDE.md")

EXIT_OK = 0
EXIT_DRIFT = 1
EXIT_INVALID = 2


class BindingEntry(TypedDict):
    """One source file and the destination files that mirror its core region."""

    source: str
    destinations: list[str]


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


class ReconciliationEntry(TypedDict):
    """One destination that `init` generated or refreshed for review."""

    destination: str
    source: str
    action: str


def _is_safe_relative(path: str) -> bool:
    """Return True when a bindings path is relative and cannot escape upward."""
    if not path or path.startswith("/"):
        return False
    return ".." not in Path(path).parts


def _exact_marker_line_indices(lines: list[str], marker: str) -> list[int]:
    """Return the indices of exact stripped `marker` lines outside code fences.

    A line opens or closes a fence when its stripped form starts with the fence
    prefix; marker-looking lines inside a fence are skipped.
    """
    in_fence = False
    matches: list[int] = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(FENCE_PREFIX):
            in_fence = not in_fence
            continue
        if in_fence:
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

    A valid marker pair yields its region; otherwise the whole body after the
    frontmatter is the core — the source file itself is the core.
    """
    region_split = split_regions(content)
    if region_split is not None:
        return region_split["region"]
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
    """Validate one `{source, destinations}` mapping and its unique destinations."""
    if not isinstance(raw_entry, dict):
        return None
    source = raw_entry.get("source")
    destinations = raw_entry.get("destinations")
    if not isinstance(source, str) or not _is_safe_relative(source):
        return None
    if not isinstance(destinations, list) or not destinations:
        return None
    resolved: list[str] = []
    for destination in destinations:
        if not isinstance(destination, str) or not _is_safe_relative(destination):
            return None
        if destination in seen_destinations:
            return None
        seen_destinations.add(destination)
        resolved.append(destination)
    return {"source": source, "destinations": resolved}


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
        {
            "source": entry["source"],
            "destinations": list(entry["destinations"]),
        }
        for entry in bindings["bindings"]
    ]
    data["pending"] = list(bindings["pending"])
    return yaml.safe_dump(data, sort_keys=False, default_flow_style=False)


def read_text(path: Path) -> Optional[str]:
    """Read UTF-8 text from a path at the IO boundary."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def load_bindings(path: Path) -> Optional[Bindings]:
    """Read and parse the bindings file at the IO boundary."""
    text = read_text(path)
    if text is None:
        return None
    return parse_bindings(text)


def write_text(path: Path, content: str) -> None:
    """Write UTF-8 text to a path at the IO boundary."""
    path.write_text(content, encoding="utf-8")


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
    """Read a source file and return its core bytes at the IO boundary."""
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
    write_reconciliation_blocker(
        resolve_root_path(destination_dir, bindings), bindings["pending"]
    )

    if bindings["core_revision"] != args.source_revision:
        print("revision drift: bindings revision does not match source", file=sys.stderr)
        return EXIT_DRIFT

    for entry in bindings["bindings"]:
        source_path = source_dir / entry["source"]
        source_core = read_source_core(source_path)
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

    writes: list[tuple[Path, str]] = []
    for entry in bindings["bindings"]:
        source_path = source_dir / entry["source"]
        source_core = read_source_core(source_path)
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

    bindings["core_revision"] = args.source_revision
    save_bindings(Path(args.bindings), bindings)
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

    source_dir = Path(args.source)
    destination_dir = Path(args.destination)

    writes: list[tuple[Path, str]] = []
    entries: list[ReconciliationEntry] = []
    pending: list[str] = list(bindings["pending"])

    for entry in bindings["bindings"]:
        source_path = source_dir / entry["source"]
        source_core = read_source_core(source_path)
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

    if entries:
        write_reconciliation_report(
            reconciliation_report_path(Path(args.bindings)),
            entries,
            args.source_revision,
        )

    bindings["core_revision"] = args.source_revision
    bindings["pending"] = pending
    save_bindings(Path(args.bindings), bindings)
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
        description="Region-based core update for marked destination files.",
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
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """Parse arguments and dispatch to `check`, `apply`, or `init`."""
    args = _build_parser().parse_args(argv)
    if args.command == "check":
        return run_check(args)
    if args.command == "apply":
        return run_apply(args)
    return run_init(args)


if __name__ == "__main__":
    sys.exit(main())
