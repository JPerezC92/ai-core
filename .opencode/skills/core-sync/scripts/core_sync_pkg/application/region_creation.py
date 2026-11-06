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


def created_region_document(
    source_reader: SourceCoreReader, source_path: Path, source_core: str
) -> str:
    """Build the document a created or recreated region target is written with.

    Shared by both write commands so the creation policy — the source document's
    frontmatter, the core region, and an empty project region — cannot be changed
    in one path and missed in the other. An unreadable source keeps empty
    frontmatter rather than inventing one.
    """
    source_content = source_reader.read_text(source_path)
    source_frontmatter = (
        "" if source_content is None else split_frontmatter(source_content)[0]
    )
    return render_init_file("", source_core, source_frontmatter)
