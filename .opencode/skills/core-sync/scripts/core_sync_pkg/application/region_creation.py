"""Creation policy shared by both write commands: absent targets and their content."""

from __future__ import annotations

from pathlib import Path

from core_sync_pkg.domain.ports import FilesystemPaths, SourceCoreReader
from core_sync_pkg.domain.regions import render_init_file, split_frontmatter


def destination_is_absent(
    paths: FilesystemPaths, destination_path: Path
) -> bool:
    """Return whether a declared destination is absent from disk.

    The write-target preflight already rejects a symlink or a non-regular
    destination target for both write commands before the loop, so this predicate
    only has to answer "is it there": that state keeps one contract, and the
    preflight owns it.
    """
    return not paths.exists(destination_path)


def read_source_frontmatter(
    source_reader: SourceCoreReader, source_path: Path
) -> str:
    """Return a source document's leading YAML frontmatter, or nothing.

    One definition for both write commands: a created region target takes its
    frontmatter from the source document because the destination text does not
    exist yet, and an existing destination is refreshed from it. The core read
    already proved the source readable, so an unreadable source here keeps the
    empty frontmatter of a markerless document rather than inventing one.
    """
    source_content = source_reader.read_text(source_path)
    if source_content is None:
        return ""
    return split_frontmatter(source_content)[0]


def created_region_document(
    source_reader: SourceCoreReader, source_path: Path, source_core: str
) -> str:
    """Build the document a created or recreated region target is written with.

    Shared by both write commands so the creation policy — the source document's
    frontmatter, the core region, and an empty project region — cannot be changed
    in one path and missed in the other. An unreadable source keeps empty
    frontmatter rather than inventing one.

    A created target needs no frontmatter refresh: it is written with the source
    document's own frontmatter, so no destination key can be stale and no key the
    source does not define exists to preserve.
    """
    return render_init_file(
        "", source_core, read_source_frontmatter(source_reader, source_path)
    )["text"]
