"""Pure bindings parsing, serialization, pending normalization, and clearance policy."""

from __future__ import annotations

from typing import NotRequired, Optional, TypedDict

import yaml

from core_sync_pkg.domain.constants import (
    MODE_MERGE,
    MODE_RAW,
    MODE_REGION,
    REVISION_RE,
    SCHEMA_VERSION,
    VALID_MODES,
    BindingMode,
)
from core_sync_pkg.domain.markers import _is_safe_relative


class BindingEntry(TypedDict):
    """One source file and the destination files that mirror it.

    `mode` is an in-memory declaration hint, not persisted: the authoritative
    distribution mode is owned by the source `distribution-clearance.json`. It
    defaults to `region` and is dropped on serialization.
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
        destination: entry["source"]
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
        existing_source = destination_mappings.get(destination)
        if existing_source is not None:
            if existing_source != source:
                return (f"destination mapping conflicts for {destination!r}", set())
            continue

        matching_entry = next(
            (
                entry
                for entry in bindings["bindings"]
                if entry["source"] == source
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
        destination_mappings[destination] = source
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
    """Render one binding entry; the distribution mode lives in source clearance."""
    return {
        "source": entry["source"],
        "destinations": list(entry["destinations"]),
    }


def _non_region_destination_paths(
    bindings: Bindings, mode_of: dict[str, str]
) -> set[str]:
    """Return destinations whose source is declared raw or merge in clearance."""
    return {
        destination
        for entry in bindings["bindings"]
        if mode_of.get(entry["source"]) in (MODE_RAW, MODE_MERGE)
        for destination in entry["destinations"]
    }


def _normalize_pending(
    pending: list[str], non_region_destinations: set[str]
) -> list[str]:
    """Return pending paths that still have a region to reconcile."""
    return [path for path in pending if path not in non_region_destinations]


def uncleared_sources(bindings: Bindings, cleared: set[str]) -> list[str]:
    """Return distinct bound sources absent from clearance in bindings order."""
    uncleared: list[str] = []
    seen: set[str] = set()
    for entry in bindings["bindings"]:
        source = entry["source"]
        if source not in cleared and source not in seen:
            seen.add(source)
            uncleared.append(source)
    return uncleared
