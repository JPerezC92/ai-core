"""Use case: enroll markerless destinations and refresh already-marked destinations."""

from __future__ import annotations

from pathlib import Path

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
    _merge_init_binding_options,
    _non_region_destination_paths,
    _normalize_pending,
    _parse_init_binding_spec,
    binding_mode_conflict,
    uncleared_sources,
)
from core_sync_pkg.domain.clearance import ClearanceRecord, expand_clearance
from core_sync_pkg.domain.constants import (
    CLEARANCE_REL,
    MODE_MERGE,
    MODE_RAW,
    MODE_REGION,
    ROLE_ROOT,
)
from core_sync_pkg.domain.errors import (
    CODE_DRIFT,
    CODE_INVALID,
    DomainError,
    MalformedJsonc,
    MalformedSourceMarkers,
)
from core_sync_pkg.domain.jsonc import parse_object
from core_sync_pkg.domain.markers import _has_exact_core_marker_lines
from core_sync_pkg.domain.merge import merge_top_level
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
        region_specs: list[str],
        raw_specs: list[str],
        bind_cleared: bool = False,
        root_override: str | None = None,
    ) -> UseCaseResult | DomainError:
        bindings = self._bindings_store.load(bindings_path)
        if bindings is None:
            if not bind_cleared:
                return DomainError(CODE_INVALID, f"invalid bindings: {bindings_path}")
            bindings = {
                "schema": 1,
                "core_revision": source_revision,
                "bindings": [],
                "pending": [],
                "root": None,
            }

        declaration_error, explicit_new_raw = _merge_init_binding_options(
            bindings, region_specs, raw_specs
        )
        if declaration_error is not None:
            return DomainError(
                CODE_INVALID, f"invalid init binding: {declaration_error}"
            )

        entries, clearance_exists = self._clearance.load(source_dir)
        mode_of: dict[str, str] = {}
        if entries is not None:
            enumerated = {
                key: self._paths.enumerate_files_under(source_dir / key[:-1])
                for key in entries
                if key.endswith("/")
            }
            mode_of = expand_clearance(entries, enumerated)

        bulk_new_region: set[str] = set()
        bulk_new_raw: set[str] = set()
        if bind_cleared and entries is not None:
            bound = {entry["source"] for entry in bindings["bindings"]}
            root_destination: str | None = bindings.get("root")
            root_source: str | None = None
            for source, entry in entries.items():
                if not (
                    isinstance(entry, ClearanceRecord) and entry.role == ROLE_ROOT
                ):
                    continue
                root_source = source
                existing = next(
                    (e for e in bindings["bindings"] if e["source"] == source),
                    None,
                )
                if existing is not None:
                    root_destination = existing["destinations"][0]
                elif root_override is not None:
                    root_destination = root_override
                else:
                    root_destination = self._paths.detect_root(destination_dir)
                if root_destination is None:
                    return DomainError(
                        CODE_DRIFT,
                        "destination instruction root not found; pass --root",
                    )
            for source, mode in mode_of.items():
                if source in bound:
                    continue
                destination = (
                    root_destination if source == root_source else source
                )
                bindings["bindings"].append(
                    {
                        "source": source,
                        "destinations": [destination],
                        "mode": mode,
                    }
                )
                bound.add(source)
                if not self._paths.exists(destination_dir / destination):
                    if mode == MODE_RAW:
                        bulk_new_raw.add(destination)
                    elif mode == MODE_REGION:
                        bulk_new_region.add(destination)
            if root_destination is not None:
                bindings["root"] = root_destination

        new_raw_destinations = set(explicit_new_raw) | bulk_new_raw

        preflight_error = self._paths.preflight_write_targets(
            "init",
            source_dir,
            destination_dir,
            bindings_path,
            bindings,
            new_raw_destinations,
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
        for spec, declared in (
            [(s, MODE_RAW) for s in raw_specs]
            + [(s, MODE_REGION) for s in region_specs]
        ):
            parsed = _parse_init_binding_spec(spec, declared)
            if parsed is None:
                continue
            declared_source, _declared_destination, declared_mode = parsed
            actual_mode = mode_of.get(declared_source)
            if actual_mode is not None and actual_mode != declared_mode:
                return DomainError(
                    CODE_INVALID,
                    f"declared {declared_mode} for {declared_source!r} conflicts "
                    f"with source clearance mode {actual_mode!r}",
                )
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
        entries: list[ReconciliationEntry] = []
        pending = _normalize_pending(
            bindings["pending"], _non_region_destination_paths(bindings, mode_of)
        )

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
                    destination_text = self._destination_writer.read_text(
                        destination_path
                    )
                    if destination_text is None:
                        return DomainError(
                            CODE_DRIFT,
                            f"missing destination: {destination_path}",
                        )
                    try:
                        merged_text = merge_top_level(source_text, destination_text)
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
            for destination in entry["destinations"]:
                destination_path = destination_dir / destination
                destination_content = self._destination_writer.read_text(
                    destination_path
                )
                if destination_content is None:
                    if destination in bulk_new_region:
                        init_content = render_init_file("", source_core)
                        self._paths.ensure_dir(destination_path.parent)
                        writes.append((destination_path, init_content))
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
