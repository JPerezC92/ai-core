"""Use case: verify every destination core region against the pinned source core."""

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
from core_sync_pkg.domain.merge import is_merged
from core_sync_pkg.domain.regions import split_regions


class VerifyDestinations:
    """Verify each destination core region against the pinned source revision."""

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
            "check",
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

        source_cores: dict[str, str] = {}
        for entry in bindings["bindings"]:
            if mode_of.get(entry["source"]) in (MODE_RAW, MODE_MERGE):
                continue
            source_path = source_dir / entry["source"]
            try:
                source_core = self._source_reader.read_core(source_path)
            except MalformedSourceMarkers:
                return DomainError(
                    CODE_INVALID, f"invalid source markers: {source_path}"
                )
            if source_core is None:
                return DomainError(CODE_DRIFT, f"missing source: {source_path}")
            source_cores[entry["source"]] = source_core

        non_region_destinations = non_region_destination_paths(bindings, mode_of)
        stale_non_region_pending = [
            path for path in bindings["pending"] if path in non_region_destinations
        ]
        normalized_pending = normalize_pending(
            bindings["pending"], non_region_destinations
        )
        self._root_runtime.write_blocker(
            self._root_runtime.resolve(destination_dir, bindings),
            normalized_pending,
        )

        if stale_non_region_pending:
            paths = ", ".join(stale_non_region_pending)
            return DomainError(
                CODE_DRIFT,
                "stale raw-bound pending paths cannot be reconciled: "
                f"{paths}; run apply or init to normalize the stale binding state",
            )

        if bindings["core_revision"] != source_revision:
            return DomainError(
                CODE_DRIFT,
                "revision drift: bindings revision does not match source",
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
                        return DomainError(
                            CODE_DRIFT,
                            f"missing destination: {destination_path}",
                        )
                    if destination_bytes != source_bytes:
                        return DomainError(
                            CODE_DRIFT, f"raw drift: {destination_path}"
                        )
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
                            f"missing destination: {destination_path}",
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
                        merged = is_merged(source_text, destination_text)
                    except MalformedJsonc:
                        return DomainError(
                            CODE_INVALID, f"invalid JSONC: {destination_path}"
                        )
                    if not merged:
                        return DomainError(
                            CODE_DRIFT, f"merge drift: {destination_path}"
                        )
                continue
            source_core = source_cores[entry["source"]]
            for destination in entry["destinations"]:
                destination_path = destination_dir / destination
                if not self._paths.is_file(destination_path):
                    return DomainError(
                        CODE_DRIFT, f"missing destination: {destination_path}"
                    )
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
                if destination_split["region"] != source_core:
                    return DomainError(
                        CODE_DRIFT, f"region drift: {destination_path}"
                    )

        if bindings["pending"]:
            return DomainError(
                CODE_DRIFT, "pending changes: destination is not current"
            )

        return UseCaseResult("current")
