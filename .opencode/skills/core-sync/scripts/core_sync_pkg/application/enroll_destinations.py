"""Use case: enroll markerless destinations and refresh already-marked destinations."""

from __future__ import annotations

from pathlib import Path

from core_sync_pkg.domain.ports import (
    BindingsStore,
    ClearanceRecord,
    DestinationWriter,
    FilesystemPaths,
    RootRuntimeFile,
    SourceCoreReader,
    UseCaseResult,
)
from core_sync_pkg.domain.bindings import (
    _merge_init_binding_options,
    _normalize_pending,
    _raw_destination_paths,
    uncleared_sources,
)
from core_sync_pkg.domain.constants import CLEARANCE_REL, MODE_RAW
from core_sync_pkg.domain.errors import (
    CODE_DRIFT,
    CODE_INVALID,
    DomainError,
    MalformedSourceMarkers,
)
from core_sync_pkg.domain.markers import _has_exact_core_marker_lines
from core_sync_pkg.domain.reconciliation import ReconciliationEntry
from core_sync_pkg.domain.regions import (
    outside_bytes,
    render_init_file,
    render_with_region,
    split_regions,
)


class EnrollDestinations:
    """Enroll markerless destinations and refresh already-marked destinations."""

    def __init__(
        self,
        bindings_store: BindingsStore,
        source_reader: SourceCoreReader,
        destination_writer: DestinationWriter,
        clearance: ClearanceRecord,
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
        region_specs: list[str],
        raw_specs: list[str],
    ) -> UseCaseResult | DomainError:
        bindings = self._bindings_store.load(bindings_path)
        if bindings is None:
            return DomainError(CODE_INVALID, f"invalid bindings: {bindings_path}")

        declaration_error, new_raw_destinations = _merge_init_binding_options(
            bindings, region_specs, raw_specs
        )
        if declaration_error is not None:
            return DomainError(
                CODE_INVALID, f"invalid init binding: {declaration_error}"
            )

        cleared, clearance_exists = self._clearance.load(source_dir)
        preflight_error = self._paths.preflight_write_targets(
            "init",
            source_dir,
            destination_dir,
            bindings_path,
            bindings,
            new_raw_destinations,
        )
        if preflight_error is not None:
            return DomainError(
                CODE_INVALID, f"invalid write target: {preflight_error}"
            )

        if not clearance_exists:
            return DomainError(
                CODE_DRIFT, f"missing clearance file: {source_dir / CLEARANCE_REL}"
            )
        if cleared is None:
            return DomainError(
                CODE_INVALID,
                f"invalid clearance file: {source_dir / CLEARANCE_REL}",
            )
        names = uncleared_sources(bindings, cleared)
        if names:
            return DomainError(
                CODE_DRIFT,
                f"source not cleared for distribution: {', '.join(names)}",
            )

        writes: list[tuple[Path, str]] = []
        raw_writes: list[tuple[Path, bytes]] = []
        entries: list[ReconciliationEntry] = []
        pending = _normalize_pending(
            bindings["pending"], _raw_destination_paths(bindings)
        )

        for entry in bindings["bindings"]:
            source_path = source_dir / entry["source"]
            if entry["mode"] == MODE_RAW:
                source_bytes = self._source_reader.read_raw(source_path)
                if source_bytes is None:
                    return DomainError(
                        CODE_DRIFT, f"missing source: {source_path}"
                    )
                for destination in entry["destinations"]:
                    destination_path = destination_dir / destination
                    destination_bytes = self._destination_writer.read_bytes(
                        destination_path
                    )
                    if destination_bytes is None:
                        if (
                            destination in new_raw_destinations
                            and not self._paths.exists(destination_path)
                            and not self._paths.is_symlink(destination_path)
                        ):
                            if not self._paths.is_dir(destination_path.parent):
                                return DomainError(
                                    CODE_DRIFT,
                                    "missing destination parent: "
                                    f"{destination_path.parent}",
                                )
                            raw_writes.append((destination_path, source_bytes))
                            continue
                        return DomainError(
                            CODE_DRIFT,
                            f"missing destination: {destination_path}",
                        )
                    if destination_bytes == source_bytes:
                        continue
                    raw_writes.append((destination_path, source_bytes))
                continue
            try:
                source_core = self._source_reader.read_core(source_path)
            except MalformedSourceMarkers:
                return DomainError(
                    CODE_INVALID, f"invalid source markers: {source_path}"
                )
            if source_core is None:
                return DomainError(CODE_DRIFT, f"missing source: {source_path}")
            for destination in entry["destinations"]:
                destination_path = destination_dir / destination
                destination_content = self._destination_writer.read_text(
                    destination_path
                )
                if destination_content is None:
                    return DomainError(
                        CODE_DRIFT, f"missing destination: {destination_path}"
                    )
                destination_split = split_regions(destination_content)
                if destination_split is None:
                    if _has_exact_core_marker_lines(destination_content):
                        return DomainError(
                            CODE_INVALID,
                            f"invalid destination markers: {destination_path}",
                        )
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
                    return DomainError(
                        CODE_INVALID,
                        f"outside-marker mismatch: {destination_path}",
                    )
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
            self._destination_writer.write_text(destination_path, new_content)
        for destination_path, raw_content in raw_writes:
            self._destination_writer.write_bytes(destination_path, raw_content)

        if entries:
            self._bindings_store.write_report(
                bindings_path, entries, source_revision
            )

        bindings["core_revision"] = source_revision
        bindings["pending"] = pending
        self._bindings_store.save(bindings_path, bindings)
        self._root_runtime.write_blocker(
            self._root_runtime.resolve(destination_dir, bindings),
            bindings["pending"],
        )
        return UseCaseResult("initialized")
