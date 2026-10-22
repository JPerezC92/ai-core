"""Application tests for EnrollDestinations over in-memory port doubles.

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

from core_sync_pkg.application.enroll_destinations import (  # noqa: E402
    EnrollDestinations,
)
from core_sync_pkg.domain.bindings import BindingEntry, Bindings  # noqa: E402
from core_sync_pkg.domain.clearance import (  # noqa: E402
    ClearanceEntry,
    ClearanceRecord,
    SkillRootEntry,
)
from core_sync_pkg.domain.constants import BindingMode, CommandName  # noqa: E402
from core_sync_pkg.domain.errors import (  # noqa: E402
    CODE_DRIFT,
    CODE_INVALID,
    DomainError,
)
from core_sync_pkg.domain.jsonc import parse_object  # noqa: E402
from core_sync_pkg.domain.ports import UseCaseResult  # noqa: E402
from core_sync_pkg.domain.reconciliation import ReconciliationEntry  # noqa: E402
from core_sync_pkg.domain.regions import render_init_file  # noqa: E402

REV_A = "a" * 40
REV_B = "b" * 40
SOURCE_DIR = Path("/src")
DEST_DIR = Path("/dst")
BINDINGS_PATH = Path("/src/bindings.yaml")
ROOT = ".opencode/skills/foo/"
MERGE_SOURCE_TEXT = '{"theme": "dark", "shared": "source"}'
MERGE_DEST_TEXT = (
    '{\n  // keep\n  "shared": "destination",\n  "extra": 1\n}\n'
)
PLAIN_DEST = "---\nname: dest\n---\n\nOld body\n"
INIT_DEST = (
    "---\nname: dest\n---\n"
    "<!-- core:begin -->\nCORE\n<!-- core:end -->\n\n"
    "<!-- project:begin -->\n\nOld body\n<!-- project:end -->\n"
)
MARKED_DEST = (
    "---\nname: dest\n---\n"
    "<!-- core:begin -->\nOLD\n<!-- core:end -->\n\nProject\n"
)
REFRESHED_DEST = (
    "---\nname: dest\n---\n"
    "<!-- core:begin -->\nCORE\n<!-- core:end -->\n\nProject\n"
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
    """In-memory SourceCoreReader double recording every payload read."""

    def __init__(
        self,
        cores: dict[Path, str | Exception] | None = None,
        raws: dict[Path, bytes] | None = None,
        texts: dict[Path, str] | None = None,
    ) -> None:
        self.cores = cores or {}
        self.raws = raws or {}
        self.texts = texts or {}
        self.reads: list[str] = []

    def read_core(self, path: Path) -> str | None:
        self.reads.append(f"core:{path}")
        value = self.cores.get(path)
        if isinstance(value, Exception):
            raise value
        return value

    def read_raw(self, path: Path) -> bytes | None:
        self.reads.append(f"raw:{path}")
        return self.raws.get(path)

    def read_text(self, path: Path) -> str | None:
        self.reads.append(f"text:{path}")
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
    """In-memory ClearanceStore double returning configured clearance entries."""

    def __init__(
        self,
        cleared: set[str] | None,
        exists: bool = True,
        modes: dict[str, str] | None = None,
        roots: dict[str, SkillRootEntry] | None = None,
    ) -> None:
        self.cleared = cleared
        self.exists = exists
        self.modes = modes or {}
        self.roots = dict(roots or {})

    def load(
        self, source_dir: Path
    ) -> tuple[dict[str, ClearanceEntry] | None, bool]:
        if self.cleared is None:
            return (None, self.exists)
        entries: dict[str, ClearanceEntry] = {
            path: ClearanceRecord(mode=self.modes.get(path, "region"))
            for path in self.cleared
        }
        entries.update(self.roots)
        return (entries, self.exists)


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
        enumeration: dict[Path, list[str]] | None = None,
        detected_root: str | None = None,
    ) -> None:
        self.files = files or set()
        self.dirs = dirs or set()
        self.symlinks = symlinks or set()
        self.preflight_error = preflight_error
        self.enumeration = dict(enumeration or {})
        self.detected_root = detected_root

    def is_file(self, path: Path) -> bool:
        return path in self.files

    def is_dir(self, path: Path) -> bool:
        return path in self.dirs

    def exists(self, path: Path) -> bool:
        return path in self.files or path in self.dirs or path in self.symlinks

    def is_symlink(self, path: Path) -> bool:
        return path in self.symlinks

    def detect_root(self, destination_dir: Path) -> str | None:
        return self.detected_root

    def ensure_dir(self, path: Path) -> None:
        self.dirs.add(path)

    def enumerate_files_under(self, root: Path) -> list[str]:
        return list(self.enumeration.get(root, []))

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
    """A wired EnrollDestinations plus the doubles needed for assertions."""

    use_case: EnrollDestinations
    store: FakeBindingsStore
    writer: FakeDestinationWriter
    reader: FakeSourceCoreReader


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


def _skill_root(
    mode: BindingMode, region_files: tuple[str, ...] = ()
) -> SkillRootEntry:
    """Build one parsed skill-root entry with a region-file subset."""
    return SkillRootEntry(mode=mode, region_files=region_files)


def _enroll(
    bindings: Bindings | None,
    *,
    cores: dict[Path, str | Exception] | None = None,
    raws: dict[Path, bytes] | None = None,
    texts: dict[Path, str] | None = None,
    text: dict[Path, str] | None = None,
    binary: dict[Path, bytes] | None = None,
    cleared: set[str] | None = None,
    modes: dict[str, str] | None = None,
    roots: dict[str, SkillRootEntry] | None = None,
    clearance_exists: bool = True,
    files: set[Path] | None = None,
    dirs: set[Path] | None = None,
    preflight_error: str | None = None,
    enumeration: dict[Path, list[str]] | None = None,
    detected_root: str | None = None,
) -> _Fixture:
    """Build EnrollDestinations with in-memory doubles."""
    store = FakeBindingsStore(bindings)
    writer = FakeDestinationWriter(text=text, binary=binary)
    reader = FakeSourceCoreReader(cores=cores, raws=raws, texts=texts)
    use_case = EnrollDestinations(
        store,
        reader,
        writer,
        FakeClearanceStore(
            cleared=cleared,
            exists=clearance_exists,
            modes=modes,
            roots=roots,
        ),
        FakeRootRuntimeFile(),
        FakeFilesystemPaths(
            files=files,
            dirs=dirs,
            preflight_error=preflight_error,
            enumeration=enumeration,
            detected_root=detected_root,
        ),
    )
    return _Fixture(use_case=use_case, store=store, writer=writer, reader=reader)


class EnrollDestinationsTests:
    """EnrollDestinations decision paths over in-memory port doubles."""

    def test_enrolls_markerless_destination_from_region_spec(self) -> None:
        fixture = _enroll(
            _bindings(None, []),
            cores={SOURCE_DIR / "agent.md": "CORE\n"},
            text={DEST_DIR / "agent.md": PLAIN_DEST},
            cleared={"agent.md"},
        )
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_A, ["agent.md=agent.md"], []
        )
        assert isinstance(result, UseCaseResult)
        assert result.message == "initialized"
        assert fixture.writer.text_writes == [(DEST_DIR / "agent.md", INIT_DEST)]
        assert fixture.store.reports[-1][1] == [
            {"destination": "agent.md", "source": "agent.md", "action": "initialized"}
        ]
        assert fixture.store.saves[-1][1]["pending"] == ["agent.md"]
        assert fixture.store.saves[-1][1]["core_revision"] == REV_A

    def test_refreshes_marked_destination_and_pins_revision(self) -> None:
        fixture = _enroll(
            _bindings(REV_A, [_entry("agent.md", ["agent.md"])]),
            cores={SOURCE_DIR / "agent.md": "CORE\n"},
            text={DEST_DIR / "agent.md": MARKED_DEST},
            cleared={"agent.md"},
        )
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_B, [], []
        )
        assert isinstance(result, UseCaseResult)
        assert result.message == "initialized"
        assert fixture.writer.text_writes == [
            (DEST_DIR / "agent.md", REFRESHED_DEST)
        ]
        assert fixture.store.reports[-1][1] == [
            {"destination": "agent.md", "source": "agent.md", "action": "refreshed"}
        ]
        assert fixture.store.saves[-1][1]["pending"] == ["agent.md"]
        assert fixture.store.saves[-1][1]["core_revision"] == REV_B

    def test_reports_conflict_when_destination_bound_to_other_source(self) -> None:
        fixture = _enroll(
            _bindings(REV_A, [_entry("agent.md", ["agent.md"])]),
            cleared=set(),
        )
        result = fixture.use_case.execute(
            SOURCE_DIR,
            DEST_DIR,
            BINDINGS_PATH,
            REV_B,
            ["other.md=agent.md"],
            [],
        )
        assert isinstance(result, DomainError)
        assert result.code == CODE_INVALID
        assert "conflicts" in result.message

    def test_reports_conflict_when_destination_mode_differs(self) -> None:
        fixture = _enroll(
            _bindings(REV_A, [_entry("agent.md", ["agent.md"])]),
            cleared=set(),
        )
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_B, [], ["other.md=agent.md"]
        )
        assert isinstance(result, DomainError)
        assert result.code == CODE_INVALID
        assert "conflicts" in result.message

    def test_reports_invalid_when_spec_is_malformed(self) -> None:
        fixture = _enroll(_bindings(REV_A, []), cleared=set())
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_B, ["noseparator"], []
        )
        assert isinstance(result, DomainError)
        assert result.code == CODE_INVALID
        assert "malformed or unsafe binding declaration" in result.message

    def test_reports_missing_source_when_source_core_absent(self) -> None:
        fixture = _enroll(
            _bindings(REV_A, [_entry("agent.md", ["agent.md"])]),
            text={DEST_DIR / "agent.md": PLAIN_DEST},
            cleared={"agent.md"},
        )
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_B, [], []
        )
        assert isinstance(result, DomainError)
        assert result.code == CODE_DRIFT
        assert "missing source" in result.message

    def test_reports_missing_destination_when_region_target_absent(self) -> None:
        fixture = _enroll(
            _bindings(REV_A, [_entry("agent.md", ["agent.md"])]),
            cores={SOURCE_DIR / "agent.md": "CORE\n"},
            cleared={"agent.md"},
        )
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_B, [], []
        )
        assert isinstance(result, DomainError)
        assert result.code == CODE_DRIFT
        assert "missing destination" in result.message

    def test_reports_missing_clearance_when_clearance_file_absent(self) -> None:
        fixture = _enroll(
            _bindings(REV_A, [_entry("agent.md", ["agent.md"])]),
            cores={SOURCE_DIR / "agent.md": "CORE\n"},
            text={DEST_DIR / "agent.md": PLAIN_DEST},
            cleared=None,
            clearance_exists=False,
        )
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_B, [], []
        )
        assert isinstance(result, DomainError)
        assert result.code == CODE_DRIFT
        assert "missing clearance file" in result.message

    def test_returns_invalid_when_bindings_unreadable(self) -> None:
        fixture = _enroll(None)
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_B, [], []
        )
        assert isinstance(result, DomainError)
        assert result.code == CODE_INVALID
        assert "invalid bindings" in result.message

    def test_merges_existing_destination_without_report_or_pending(self) -> None:
        fixture = _enroll(
            _bindings(
                REV_B, [_entry("opencode.jsonc", ["opencode.jsonc"], "merge")]
            ),
            texts={SOURCE_DIR / "opencode.jsonc": MERGE_SOURCE_TEXT},
            text={DEST_DIR / "opencode.jsonc": MERGE_DEST_TEXT},
            cleared={"opencode.jsonc"},
            modes={"opencode.jsonc": "merge"},
            files={DEST_DIR / "opencode.jsonc"},
        )
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_A, [], []
        )
        assert isinstance(result, UseCaseResult)
        assert result.message == "initialized"
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
        assert fixture.store.reports == []
        assert fixture.store.saves[-1][1]["pending"] == []
        assert fixture.store.saves[-1][1]["core_revision"] == REV_A

    def test_merge_reports_missing_destination_and_creates_nothing(self) -> None:
        fixture = _enroll(
            _bindings(
                REV_B, [_entry("opencode.jsonc", ["opencode.jsonc"], "merge")]
            ),
            texts={SOURCE_DIR / "opencode.jsonc": MERGE_SOURCE_TEXT},
            cleared={"opencode.jsonc"},
            modes={"opencode.jsonc": "merge"},
        )
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_A, [], []
        )
        assert isinstance(result, DomainError)
        assert result.code == CODE_DRIFT
        assert "missing destination" in result.message
        assert fixture.writer.text_writes == []

    def test_merge_reports_invalid_when_destination_malformed(self) -> None:
        fixture = _enroll(
            _bindings(
                REV_B, [_entry("opencode.jsonc", ["opencode.jsonc"], "merge")]
            ),
            texts={SOURCE_DIR / "opencode.jsonc": MERGE_SOURCE_TEXT},
            text={DEST_DIR / "opencode.jsonc": '{"theme": }'},
            cleared={"opencode.jsonc"},
            modes={"opencode.jsonc": "merge"},
            files={DEST_DIR / "opencode.jsonc"},
        )
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_A, [], []
        )
        assert isinstance(result, DomainError)
        assert result.code == CODE_INVALID
        assert "invalid JSONC" in result.message

    def test_uncleared_source_is_rejected_before_any_payload_read(self) -> None:
        fixture = _enroll(
            _bindings(REV_A, [_entry("agent.md", ["agent.md"])]),
            cores={SOURCE_DIR / "agent.md": "CORE\n"},
            text={DEST_DIR / "agent.md": MARKED_DEST},
            cleared=set(),
        )
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_B, [], []
        )
        assert isinstance(result, DomainError)
        assert result.code == CODE_DRIFT
        assert "source not cleared for distribution: agent.md" in result.message
        assert fixture.reader.reads == []
        assert fixture.writer.text_writes == []
        assert fixture.writer.byte_writes == []

    def test_invalid_clearance_is_rejected_before_any_payload_read(self) -> None:
        fixture = _enroll(
            _bindings(REV_A, [_entry("agent.md", ["agent.md"])]),
            cores={SOURCE_DIR / "agent.md": "CORE\n"},
            text={DEST_DIR / "agent.md": MARKED_DEST},
            cleared=None,
        )
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_B, [], []
        )
        assert isinstance(result, DomainError)
        assert result.code == CODE_INVALID
        assert "invalid clearance file" in result.message
        assert fixture.reader.reads == []
        assert fixture.writer.text_writes == []
        assert fixture.writer.byte_writes == []

    def test_bind_cleared_enrolls_expanded_skill_root_files(self) -> None:
        fixture = _enroll(
            None,
            cores={SOURCE_DIR / (ROOT + "SKILL.md"): "CORE\n"},
            raws={
                SOURCE_DIR / (ROOT + "README.md"): b"# Readme\n",
                SOURCE_DIR / (ROOT + "data.json"): b"{}\n",
            },
            cleared=set(),
            roots={ROOT: _skill_root("raw", ("SKILL.md",))},
            enumeration={
                SOURCE_DIR / ROOT[:-1]: ["SKILL.md", "README.md", "data.json"]
            },
            dirs={DEST_DIR, DEST_DIR / ROOT[:-1]},
        )
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_A, [], [], bind_cleared=True
        )
        assert isinstance(result, UseCaseResult)
        assert result.message == "initialized"
        saved = fixture.store.saves[-1][1]
        assert [(e["source"], e["mode"]) for e in saved["bindings"]] == [
            (ROOT + "SKILL.md", "region"),
            (ROOT + "README.md", "raw"),
            (ROOT + "data.json", "raw"),
        ]
        assert fixture.writer.text_writes == [
            (DEST_DIR / (ROOT + "SKILL.md"), render_init_file("", "CORE\n"))
        ]
        assert fixture.writer.byte_writes == [
            (DEST_DIR / (ROOT + "README.md"), b"# Readme\n"),
            (DEST_DIR / (ROOT + "data.json"), b"{}\n"),
        ]

    def test_bind_cleared_enrolls_new_file_appearing_under_root(self) -> None:
        fixture = _enroll(
            _bindings(
                REV_A, [_entry(ROOT + "SKILL.md", [ROOT + "SKILL.md"])]
            ),
            cores={SOURCE_DIR / (ROOT + "SKILL.md"): "CORE\n"},
            raws={SOURCE_DIR / (ROOT + "new.md"): b"new\n"},
            cleared=set(),
            roots={ROOT: _skill_root("raw", ("SKILL.md",))},
            enumeration={
                SOURCE_DIR / ROOT[:-1]: ["SKILL.md", "new.md"]
            },
            dirs={DEST_DIR, DEST_DIR / ROOT[:-1]},
            text={DEST_DIR / (ROOT + "SKILL.md"): MARKED_DEST},
        )
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_A, [], [], bind_cleared=True
        )
        assert isinstance(result, UseCaseResult)
        saved = fixture.store.saves[-1][1]
        assert [(e["source"], e["mode"]) for e in saved["bindings"]] == [
            (ROOT + "SKILL.md", "region"),
            (ROOT + "new.md", "raw"),
        ]
        assert fixture.writer.byte_writes == [
            (DEST_DIR / (ROOT + "new.md"), b"new\n")
        ]

    def test_interpreter_caches_never_enroll_from_expanded_roots(self) -> None:
        fixture = _enroll(
            None,
            raws={SOURCE_DIR / (ROOT + "mod.py"): b"pass\n"},
            cleared=set(),
            roots={ROOT: _skill_root("raw")},
            enumeration={
                SOURCE_DIR / ROOT[:-1]: [
                    "mod.py",
                    "__pycache__/mod.cpython-313.pyc",
                    "pkg/__pycache__/x.py",
                    "pkg/old.pyc",
                ]
            },
            dirs={DEST_DIR, DEST_DIR / ROOT[:-1]},
        )
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_A, [], [], bind_cleared=True
        )
        assert isinstance(result, UseCaseResult)
        saved = fixture.store.saves[-1][1]
        assert [e["source"] for e in saved["bindings"]] == [ROOT + "mod.py"]

    def test_root_derived_mode_conflict_fails_before_payload_io(self) -> None:
        fixture = _enroll(
            _bindings(
                REV_A,
                [_entry(ROOT + "SKILL.md", [ROOT + "SKILL.md"], "raw")],
            ),
            cores={SOURCE_DIR / (ROOT + "SKILL.md"): "CORE\n"},
            cleared=set(),
            roots={ROOT: _skill_root("raw", ("SKILL.md",))},
            enumeration={SOURCE_DIR / ROOT[:-1]: ["SKILL.md"]},
            text={DEST_DIR / (ROOT + "SKILL.md"): MARKED_DEST},
        )
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_B, [], []
        )
        assert isinstance(result, DomainError)
        assert result.code == CODE_INVALID
        assert (
            "binding mode 'raw' conflicts with source clearance mode "
            f"'region' for {ROOT}SKILL.md"
        ) in result.message
        assert fixture.reader.reads == []
        assert fixture.writer.text_writes == []
        assert fixture.writer.byte_writes == []

    def test_returns_invalid_when_preflight_reports_symlinked_target(self) -> None:
        fixture = _enroll(
            _bindings(REV_A, [_entry("agent.md", ["agent.md"])]),
            cores={SOURCE_DIR / "agent.md": "CORE\n"},
            text={DEST_DIR / "agent.md": PLAIN_DEST},
            cleared={"agent.md"},
            preflight_error="symlinked target",
        )
        result = fixture.use_case.execute(
            SOURCE_DIR, DEST_DIR, BINDINGS_PATH, REV_B, [], []
        )
        assert isinstance(result, DomainError)
        assert result.code == CODE_INVALID
        assert "invalid write target" in result.message
        assert fixture.writer.text_writes == []
        assert fixture.writer.byte_writes == []
        assert fixture.store.saves == []
