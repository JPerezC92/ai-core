"""Use case: splice each source core into its destinations, then pin the revision.

A region destination's core region is replaced and its frontmatter identity keys
are refreshed from the source; an unrefreshable frontmatter is left as it is and
named in the result message.
"""

from __future__ import annotations

from pathlib import Path

from core_sync_pkg.application.region_creation import (
    created_region_document,
    destination_is_absent,
    read_source_frontmatter,
)
from core_sync_pkg.domain.ports import (
    BindingsStore,
    ClearanceStore,
    DestinationWriter,
    FilesystemPaths,
    RootRuntimeFile,
    SourceCoreReader,
    UseCaseResult,
)
from core_sync_pkg.domain.bindings import (
    binding_mode_conflict,
    non_region_destination_paths,
    normalize_pending,
    uncleared_sources,
)
from core_sync_pkg.domain.clearance import expand_clearance
from core_sync_pkg.domain.constants import CLEARANCE_REL, MODE_MERGE, MODE_RAW
from core_sync_pkg.domain.errors import (
    CODE_DRIFT,
    CODE_INVALID,
    DomainError,
    MalformedJsonc,
    MalformedSourceMarkers,
)
from core_sync_pkg.domain.jsonc import parse_object
from core_sync_pkg.domain.merge import merge_top_level
from core_sync_pkg.domain.regions import (
    protected_bytes,
    render_with_region,
    split_regions,
)


class ApplyCoreRevision:
    """Splice each source core into its destinations, then pin the revision."""

    def __init__(
        self,
        bindings_store: BindingsStore,
        source_reader: SourceCoreReader,
        destination_writer: DestinationWriter,
        clearance: ClearanceStore,
        root_runtime: RootRuntimeFile,
        paths: FilesystemPaths,
    ) -> None:
        self._bindings_store = bindings_store
        self._source_reader = source_reader
        self._destination_writer = destination_writer
        self._clearance = clearance
        self._root_runtime = root_runtime
        self._paths = paths

    def execute(
        self,
        source_dir: Path,
        destination_dir: Path,
        bindings_path: Path,
        source_revision: str,
    ) -> UseCaseResult | DomainError:
        bindings = self._bindings_store.load(bindings_path)
        if bindings is None:
            return DomainError(CODE_INVALID, f"invalid bindings: {bindings_path}")

        entries, clearance_exists = self._clearance.load(source_dir)
        mode_of: dict[str, str] = {}
        if entries is not None:
            enumerated = {
                key: self._paths.enumerate_files_under(source_dir / key[:-1])
                for key in entries
                if key.endswith("/")
            }
            mode_of = expand_clearance(entries, enumerated)
        preflight_error = self._paths.preflight_write_targets(
            "apply",
            source_dir,
            destination_dir,
            bindings_path,
            bindings,
            mode_of=mode_of,
        )
        if preflight_error is not None:
            return DomainError(
                CODE_INVALID, f"invalid write target: {preflight_error}"
            )

        if not clearance_exists:
            return DomainError(
                CODE_DRIFT, f"missing clearance file: {source_dir / CLEARANCE_REL}"
            )
        if entries is None:
            return DomainError(
                CODE_INVALID,
                f"invalid clearance file: {source_dir / CLEARANCE_REL}",
            )
        cleared = set(mode_of)
        names = uncleared_sources(bindings, cleared)
        for entry in bindings["bindings"]:
            conflict = binding_mode_conflict(entry, mode_of)
            if conflict is not None:
                return conflict
        if names:
            return DomainError(
                CODE_DRIFT,
                f"source not cleared for distribution: {', '.join(names)}",
            )

        writes: list[tuple[Path, str]] = []
        raw_writes: list[tuple[Path, bytes]] = []
        created: list[str] = []
        notes: list[str] = []
        for entry in bindings["bindings"]:
            source_path = source_dir / entry["source"]
            if mode_of.get(entry["source"]) == MODE_RAW:
                source_bytes = self._source_reader.read_raw(source_path)
                if source_bytes is None:
                    return DomainError(
                        CODE_DRIFT, f"missing source: {source_path}"
                    )
                for destination in entry["destinations"]:
                    destination_path = destination_dir / destination
                    if not self._paths.is_file(destination_path):
                        if not destination_is_absent(
                            self._paths, destination_path
                        ):
                            return DomainError(
                                CODE_DRIFT,
                                f"missing destination: {destination_path}",
                            )
                        # A destination recorded in the bindings file but absent
                        # from disk is recreated with its parent directory, made
                        # immediately before the write.
                        created.append(destination)
                    raw_writes.append((destination_path, source_bytes))
                continue
            if mode_of.get(entry["source"]) == MODE_MERGE:
                source_text = self._source_reader.read_text(source_path)
                if source_text is None:
                    return DomainError(
                        CODE_DRIFT, f"missing source: {source_path}"
                    )
                try:
                    parse_object(source_text)
                except MalformedJsonc:
                    return DomainError(
                        CODE_INVALID, f"invalid JSONC: {source_path}"
                    )
                for destination in entry["destinations"]:
                    destination_path = destination_dir / destination
                    if not self._paths.is_file(destination_path):
                        return DomainError(
                            CODE_DRIFT,
                            f"missing destination: {destination_path} "
                            "(merge mode cannot create it; the destination must "
                            "exist)",
                        )
                    destination_text = self._destination_writer.read_text(
                        destination_path
                    )
                    if destination_text is None:
                        return DomainError(
                            CODE_DRIFT,
                            f"missing destination: {destination_path}",
                        )
                    try:
                        merged_text = merge_top_level(
                            source_text,
                            destination_text,
                            project_name=destination_dir.resolve().name,
                        )
                    except MalformedJsonc:
                        return DomainError(
                            CODE_INVALID, f"invalid JSONC: {destination_path}"
                        )
                    if merged_text != destination_text:
                        writes.append((destination_path, merged_text))
                continue
            try:
                source_core = self._source_reader.read_core(source_path)
            except MalformedSourceMarkers:
                return DomainError(
                    CODE_INVALID, f"invalid source markers: {source_path}"
                )
            if source_core is None:
                return DomainError(CODE_DRIFT, f"missing source: {source_path}")
            source_frontmatter = read_source_frontmatter(
                self._source_reader, source_path
            )
            for destination in entry["destinations"]:
                destination_path = destination_dir / destination
                if not self._paths.is_file(destination_path):
                    if not destination_is_absent(self._paths, destination_path):
                        return DomainError(
                            CODE_DRIFT,
                            f"missing destination: {destination_path}",
                        )
                    # A destination recorded in the bindings file but absent from
                    # disk is recreated, not drift: it gets exactly the content a
                    # fresh enrollment creates, so a declaration does not depend
                    # on when it was recorded.
                    writes.append(
                        (
                            destination_path,
                            created_region_document(
                                self._source_reader, source_path, source_core
                            ),
                        )
                    )
                    created.append(destination)
                    continue
                destination_content = self._destination_writer.read_text(
                    destination_path
                )
                destination_split = (
                    split_regions(destination_content)
                    if destination_content is not None
                    else None
                )
                if destination_split is None:
                    return DomainError(
                        CODE_INVALID,
                        f"invalid destination markers: {destination_path}",
                    )
                rendered = render_with_region(
                    destination_split, source_core, source_frontmatter
                )
                new_content = rendered["text"]
                if rendered["skipped"]:
                    notes.append(
                        f"frontmatter not refreshed: {destination_path} "
                        f"({rendered['skipped']})"
                    )
                new_split = split_regions(new_content)
                if new_split is None or protected_bytes(
                    new_split
                ) != protected_bytes(destination_split):
                    return DomainError(
                        CODE_INVALID,
                        f"outside-marker mismatch: {destination_path}",
                    )
                writes.append((destination_path, new_content))

        # Parent directories and writes happen only once every destination has
        # been classified, so a later refusal cannot leave a directory behind.
        for destination_path, new_content in writes:
            self._paths.ensure_dir(destination_path.parent)
            self._destination_writer.write_text(destination_path, new_content)
        for destination_path, raw_content in raw_writes:
            self._paths.ensure_dir(destination_path.parent)
            self._destination_writer.write_bytes(destination_path, raw_content)

        bindings["core_revision"] = source_revision
        bindings["pending"] = normalize_pending(
            bindings["pending"], non_region_destination_paths(bindings, mode_of)
        )
        self._bindings_store.save(bindings_path, bindings)
        self._root_runtime.write_blocker(
            self._root_runtime.resolve(destination_dir, bindings),
            bindings["pending"],
        )
        message = "applied"
        if notes:
            message = "; ".join([message, *notes])
        if created:
            message = f"{message}; created: {', '.join(created)}"
        return UseCaseResult(message)
