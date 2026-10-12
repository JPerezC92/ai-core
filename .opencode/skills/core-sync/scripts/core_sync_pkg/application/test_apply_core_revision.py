"""Application tests for ApplyCoreRevision over in-memory port doubles.

Each test drives one decision path of the use case through fakes that implement
the six domain ports, with no real filesystem, no CLI, and no `core_sync`.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/application
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core_sync_pkg.application.apply_core_revision import (  # noqa: E402
    ApplyCoreRevision,
)
from core_sync_pkg.domain.bindings import BindingEntry, Bindings  # noqa: E402
from core_sync_pkg.domain.clearance import ClearanceRecord
from core_sync_pkg.domain.constants import BindingMode, CommandName  # noqa: E402
from core_sync_pkg.domain.errors import (  # noqa: E402
    CODE_DRIFT,
    CODE_INVALID,
    DomainError,
    MalformedSourceMarkers,
)
from core_sync_pkg.domain.jsonc import parse_object  # noqa: E402
from core_sync_pkg.domain.ports import UseCaseResult  # noqa: E402
from core_sync_pkg.domain.reconciliation import ReconciliationEntry  # noqa: E402

REV_A = "a" * 40
REV_B = "b" * 40
SOURCE_DIR = Path("/src")
DEST_DIR = Path("/dst")
BINDINGS_PATH = Path("/src/bindings.yaml")
OLD_DEST = "HEAD\n<!-- core:begin -->\nOLD\n<!-- core:end -->\nTAIL\n"
NEW_DEST = "HEAD\n<!-- core:begin -->\nCORE\n<!-- core:end -->\nTAIL\n"
RAW_SOURCE = b'{\n  "theme": "dark"\n}\n'
MERGE_SOURCE_TEXT = '{"theme": "dark", "shared": "source"}'
MERGE_DEST_TEXT = (
    '{\n  // keep\n  "shared": "destination",\n  "extra": 1\n}\n'
)
MERGE_DEST_ALREADY = (
    '{\n  "shared": "source",\n  "extra": 1,\n  "theme": "dark"\n}\n'
)


class FakeBindingsStore:
    """In-memory BindingsStore double recording saves and reports."""

    def __init__(self, bindings: Bindings | None) -> None:
        self.bindings = bindings
        self.saves: list[tuple[Path, Bindings]] = []
        self.reports: list[tuple[Path, list[ReconciliationEntry], str]] = []

    def load(self, path: Path) -> Bindings | None:
        return self.bindings

    def save(self, path: Path, bindings: Bindings) -> None:
        self.saves.append((path, bindings))
        self.bindings = bindings

    def write_report(
        self, bindings_path: Path, entries: list[ReconciliationEntry], revision: str
    ) -> None:
        self.reports.append((bindings_path, entries, revision))


class FakeSourceCoreReader:
    """In-memory SourceCoreReader double keyed by source path."""

    def __init__(
        self,
        cores: dict[Path, str | Exception] | None = None,
        raws: dict[Path, bytes] | None = None,
        texts: dict[Path, str] | None = None,
    ) -> None:
        self.cores = cores or {}
        self.raws = raws or {}
        self.texts = texts or {}

    def read_core(self, path: Path) -> str | None:
        value = self.cores.get(path)
        if isinstance(value, Exception):
            raise value
        return value

    def read_raw(self, path: Path) -> bytes | None:
        return self.raws.get(path)

    def read_text(self, path: Path) -> str | None:
        return self.texts.get(path)


class FakeDestinationWriter:
    """In-memory DestinationWriter double recording writes."""

    def __init__(
        self,
        text: dict[Path, str] | None = None,
        binary: dict[Path, bytes] | None = None,
    ) -> None:
        self.text = dict(text or {})
        self.binary = dict(binary or {})
        self.text_writes: list[tuple[Path, str]] = []
        self.byte_writes: list[tuple[Path, bytes]] = []

    def read_text(self, path: Path) -> str | None:
        return self.text.get(path)

    def read_bytes(self, path: Path) -> bytes | None:
        return self.binary.get(path)

    def write_text(self, path: Path, content: str) -> None:
        self.text[path] = content
        self.text_writes.append((path, content))

    def write_bytes(self, path: Path, content: bytes) -> None:
        self.binary[path] = content
        self.byte_writes.append((path, content))


class FakeClearanceStore:
    """In-memory ClearanceRecord double returning configured clearance state."""

    def __init__(
        self,
        cleared: set[str] | None,
        exists: bool = True,
        modes: dict[str, str] | None = None,
    ) -> None:
        self.cleared = cleared
        self.exists = exists
        self.modes = modes or {}

    def load(
        self, source_dir: Path
    ) -> tuple[dict[str, ClearanceRecord] | None, bool]:
        records = (
            None
            if self.cleared is None
            else {
                path: ClearanceRecord(mode=self.modes.get(path, "region"))
                for path in self.cleared
            }
        )
        return records, self.exists


class FakeRootRuntimeFile:
    """In-memory RootRuntimeFile double recording blocker syncs."""

    def __init__(self) -> None:
        self.blockers: list[tuple[Path, list[str]]] = []

    def resolve(self, destination_dir: Path, bindings: Bindings) -> Path:
        return Path("/root-runtime.md")

    def write_blocker(self, root_path: Path, pending: list[str]) -> bool:
        self.blockers.append((root_path, list(pending)))
        return True


class FakeFilesystemPaths:
    """In-memory FilesystemPaths double over supplied path sets."""

    def __init__(
        self,
        files: set[Path] | None = None,
        dirs: set[Path] | None = None,
        symlinks: set[Path] | None = None,
        preflight_error: str | None = None,
    ) -> None:
        self.files = files or set()
        self.dirs = dirs or set()
        self.symlinks = symlinks or set()
        self.preflight_error = preflight_error

    def is_file(self, path: Path) -> bool:
        return path in self.files

    def is_dir(self, path: Path) -> bool:
        return path in self.dirs

    def exists(self, path: Path) -> bool:
        return path in self.files or path in self.dirs or path in self.symlinks

    def is_symlink(self, path: Path) -> bool:
        return path in self.symlinks

    def preflight_write_targets(
        self,
        command: CommandName,
        source_dir: Path,
        destination_dir: Path,
        bindings_path: Path,
        bindings: Bindings,
        new_raw_destinations: set[str] | None = None,
        mode_of: dict[str, str] | None = None,
    ) -> str | None:
        return self.preflight_error


@dataclass
class _Fixture:
    """A wired ApplyCoreRevision plus the doubles needed for assertions."""

    use_case: ApplyCoreRevision
    store: FakeBindingsStore
    writer: FakeDestinationWriter


def _entry(
    source: str,
    destinations: list[str],
    mode: BindingMode = "region",
) -> BindingEntry:
    """Build one binding entry with an explicit mode."""
    return {"source": source, "destinations": list(destinations), "mode": mode}


def _bindings(
    revision: str | None,
    entries: list[BindingEntry],
    pending: list[str] | None = None,
) -> Bindings:
    """Build a valid bindings document from explicit entries."""
    return {
        "schema": 1,
        "core_revision": revision,
        "bindings": list(entries),
        "pending": list(pending or []),
        "root": None,
    }


def _apply(
    bindings: Bindings | None,
    *,
    cores: dict[Path, str | Exception] | None = None,
    raws: dict[Path, bytes] | None = None,
    texts: dict[Path, str] | None = None,
    text: dict[Path, str] | None = None,
    binary: dict[Path, bytes] | None = None,
    cleared: set[str] | None = None,
    modes: dict[str, str] | None = None,
    clearance_exists: bool = True,
    files: set[Path] | None = None,
    preflight_error: str | None = None,
) -> _Fixture:
    """Build ApplyCoreRevision with in-memory doubles."""
    store = FakeBindingsStore(bindings)
    writer = FakeDestinationWriter(text=text, binary=binary)
    use_case = ApplyCoreRevision(
        store,
        FakeSourceCoreReader(cores=cores, raws=raws, texts=texts),
        writer,
        FakeClearanceStore(cleared=cleared, exists=clearance_exists, modes=modes),
        FakeRootRuntimeFile(),
        FakeFilesystemPaths(files=files, preflight_error=preflight_error),
    )
    return _Fixture(use_case=use_case, store=store, writer=writer)


class ApplyCoreRevisionTests:
    """ApplyCoreRevision decision paths over in-memory port doubles."""

    def test_splices_region_core_and_pins_revision(self) -> None:
        fixture = _apply(
            _bindings(REV_A, [_entry("agent.md", ["agent.md"])]),
            cores={SOURCE_DIR / "agent.md": "CORE\n"},
            text={DEST_DIR / "agent.md": OLD_DEST},
            cleared={"agent.md"},
            files={DEST_DIR / "agent.md"},
        )
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_B
        )
        assert isinstance(result, UseCaseResult)
        assert result.message == "applied"
        assert fixture.writer.text_writes == [
            (DEST_DIR / "agent.md", NEW_DEST)
        ]
        assert fixture.store.saves[-1][1]["core_revision"] == REV_B

    def test_copies_raw_bytes_exact_and_pins_revision(self) -> None:
        fixture = _apply(
            _bindings(
                REV_A, [_entry("opencode.jsonc", ["opencode.jsonc"], "raw")]
            ),
            raws={SOURCE_DIR / "opencode.jsonc": RAW_SOURCE},
            cleared={"opencode.jsonc"},
            modes={"opencode.jsonc": "raw"},
            files={DEST_DIR / "opencode.jsonc"},
        )
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_B
        )
        assert isinstance(result, UseCaseResult)
        assert result.message == "applied"
        assert fixture.writer.byte_writes == [
            (DEST_DIR / "opencode.jsonc", RAW_SOURCE)
        ]
        assert fixture.store.saves[-1][1]["core_revision"] == REV_B

    def test_reports_missing_destination_when_region_target_absent(self) -> None:
        fixture = _apply(
            _bindings(REV_A, [_entry("agent.md", ["agent.md"])]),
            cores={SOURCE_DIR / "agent.md": "CORE\n"},
            cleared={"agent.md"},
        )
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_B
        )
        assert isinstance(result, DomainError)
        assert result.code == CODE_DRIFT
        assert "missing destination" in result.message

    def test_reports_invalid_markers_when_destination_unmarked(self) -> None:
        fixture = _apply(
            _bindings(REV_A, [_entry("agent.md", ["agent.md"])]),
            cores={SOURCE_DIR / "agent.md": "CORE\n"},
            text={DEST_DIR / "agent.md": "no markers here\n"},
            cleared={"agent.md"},
            files={DEST_DIR / "agent.md"},
        )
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_B
        )
        assert isinstance(result, DomainError)
        assert result.code == CODE_INVALID
        assert "invalid destination markers" in result.message

    def test_reports_missing_source_when_source_core_absent(self) -> None:
        fixture = _apply(
            _bindings(REV_A, [_entry("agent.md", ["agent.md"])]),
            cleared={"agent.md"},
            files={DEST_DIR / "agent.md"},
        )
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_B
        )
        assert isinstance(result, DomainError)
        assert result.code == CODE_DRIFT
        assert "missing source" in result.message

    def test_reports_invalid_when_source_markers_malformed(self) -> None:
        fixture = _apply(
            _bindings(REV_A, [_entry("agent.md", ["agent.md"])]),
            cores={SOURCE_DIR / "agent.md": MalformedSourceMarkers("bad")},
            text={DEST_DIR / "agent.md": OLD_DEST},
            cleared={"agent.md"},
            files={DEST_DIR / "agent.md"},
        )
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_B
        )
        assert isinstance(result, DomainError)
        assert result.code == CODE_INVALID
        assert "invalid source markers" in result.message

    def test_returns_invalid_when_bindings_unreadable(self) -> None:
        fixture = _apply(None)
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_B
        )
        assert isinstance(result, DomainError)
        assert result.code == CODE_INVALID
        assert "invalid bindings" in result.message

    def test_merge_writes_source_keys_into_destination(self) -> None:
        fixture = _apply(
            _bindings(
                REV_A, [_entry("opencode.jsonc", ["opencode.jsonc"], "merge")]
            ),
            texts={SOURCE_DIR / "opencode.jsonc": MERGE_SOURCE_TEXT},
            text={DEST_DIR / "opencode.jsonc": MERGE_DEST_TEXT},
            cleared={"opencode.jsonc"},
            modes={"opencode.jsonc": "merge"},
            files={DEST_DIR / "opencode.jsonc"},
        )
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_B
        )
        assert isinstance(result, UseCaseResult)
        assert result.message == "applied"
        assert len(fixture.writer.text_writes) == 1
        written_path, written = fixture.writer.text_writes[0]
        assert written_path == DEST_DIR / "opencode.jsonc"
        assert "// keep" in written
        assert parse_object(written) == {
            "shared": "source",
            "extra": 1,
            "theme": "dark",
        }
        assert fixture.writer.byte_writes == []
        assert fixture.store.saves[-1][1]["core_revision"] == REV_B

    def test_merge_writes_nothing_when_already_merged(self) -> None:
        fixture = _apply(
            _bindings(
                REV_A, [_entry("opencode.jsonc", ["opencode.jsonc"], "merge")]
            ),
            texts={SOURCE_DIR / "opencode.jsonc": MERGE_SOURCE_TEXT},
            text={DEST_DIR / "opencode.jsonc": MERGE_DEST_ALREADY},
            cleared={"opencode.jsonc"},
            modes={"opencode.jsonc": "merge"},
            files={DEST_DIR / "opencode.jsonc"},
        )
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_B
        )
        assert isinstance(result, UseCaseResult)
        assert fixture.writer.text_writes == []

    def test_merge_reports_missing_destination(self) -> None:
        fixture = _apply(
            _bindings(
                REV_A, [_entry("opencode.jsonc", ["opencode.jsonc"], "merge")]
            ),
            texts={SOURCE_DIR / "opencode.jsonc": MERGE_SOURCE_TEXT},
            cleared={"opencode.jsonc"},
            modes={"opencode.jsonc": "merge"},
        )
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_B
        )
        assert isinstance(result, DomainError)
        assert result.code == CODE_DRIFT
        assert "missing destination" in result.message

    def test_merge_reports_missing_source(self) -> None:
        fixture = _apply(
            _bindings(
                REV_A, [_entry("opencode.jsonc", ["opencode.jsonc"], "merge")]
            ),
            text={DEST_DIR / "opencode.jsonc": MERGE_DEST_TEXT},
            cleared={"opencode.jsonc"},
            modes={"opencode.jsonc": "merge"},
            files={DEST_DIR / "opencode.jsonc"},
        )
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_B
        )
        assert isinstance(result, DomainError)
        assert result.code == CODE_DRIFT
        assert "missing source" in result.message

    def test_merge_reports_invalid_when_destination_malformed(self) -> None:
        fixture = _apply(
            _bindings(
                REV_A, [_entry("opencode.jsonc", ["opencode.jsonc"], "merge")]
            ),
            texts={SOURCE_DIR / "opencode.jsonc": MERGE_SOURCE_TEXT},
            text={DEST_DIR / "opencode.jsonc": '{"theme": }'},
            cleared={"opencode.jsonc"},
            modes={"opencode.jsonc": "merge"},
            files={DEST_DIR / "opencode.jsonc"},
        )
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_B
        )
        assert isinstance(result, DomainError)
        assert result.code == CODE_INVALID
        assert "invalid JSONC" in result.message
