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

        records, clearance_exists = self._clearance.load(source_dir)
        mode_of = (
            {} if records is None
            else {source: record.mode for source, record in records.items()}
        )
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
        if records is None:
            return DomainError(
                CODE_INVALID,
                f"invalid clearance file: {source_dir / CLEARANCE_REL}",
            )
        cleared = set(records)
        names = uncleared_sources(bindings, cleared)
        for entry in bindings["bindings"]:
            record = records.get(entry["source"])
            if (
                record is not None
                and entry["mode"] == MODE_RAW
                and record.mode != MODE_RAW
            ):
                return DomainError(
                    CODE_INVALID,
                    f"binding mode 'raw' conflicts with source clearance mode "
                    f"{record.mode!r} for {entry['source']}",
                )
        if names:
            return DomainError(
                CODE_DRIFT,
                f"source not cleared for distribution: {', '.join(names)}",
            )

        source_cores: dict[str, str] = {}
        for entry in bindings["bindings"]:
            if mode_of.get(entry["source"]) == MODE_RAW:
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

        raw_destinations = _raw_destination_paths(bindings, mode_of)
        stale_raw_pending = [
            path for path in bindings["pending"] if path in raw_destinations
        ]
        normalized_pending = _normalize_pending(
            bindings["pending"], raw_destinations
        )
        self._root_runtime.write_blocker(
            self._root_runtime.resolve(destination_dir, bindings),
            normalized_pending,
        )

        if stale_raw_pending:
            paths = ", ".join(stale_raw_pending)
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
