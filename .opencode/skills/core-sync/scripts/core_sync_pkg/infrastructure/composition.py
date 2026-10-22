"""Composition root: parse the CLI, wire adapters to use cases, and map exit codes."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from core_sync_pkg.application.apply_core_revision import ApplyCoreRevision
from core_sync_pkg.application.enroll_destinations import EnrollDestinations
from core_sync_pkg.application.verify_destinations import VerifyDestinations
from core_sync_pkg.domain.constants import (
    EXIT_DRIFT,
    EXIT_INVALID,
    EXIT_OK,
    REVISION_RE,
    CommandName,
)
from core_sync_pkg.domain.errors import (
    CODE_DRIFT,
    CODE_INVALID,
    DomainError,
)
from core_sync_pkg.domain.ports import UseCaseResult
from core_sync_pkg.infrastructure.filesystem import (
    LocalDestinationWriter,
    LocalFilesystemPaths,
    LocalRootRuntimeFile,
    LocalSourceCoreReader,
)
from core_sync_pkg.infrastructure.stores import (
    JsonClearanceStore,
    YamlBindingsStore,
)

_EXIT_CODE_BY_ERROR_CODE = {
    CODE_DRIFT: EXIT_DRIFT,
    CODE_INVALID: EXIT_INVALID,
}


def _revision_arg(value: str) -> str:
    """Argparse type: require a 40-character lowercase hex revision string."""
    if not REVISION_RE.match(value):
        raise argparse.ArgumentTypeError("must be a 40-character lowercase hex string")
    return value


def _build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser with the shared flags for every subcommand."""
    parser = argparse.ArgumentParser(
        prog="core-sync",
        description="Region- or raw-mode core update for destination files.",
        epilog="Exit codes: 0 current/applied/initialized, 1 drift, 2 malformed input.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("check", "verify destination core regions against the source"),
        ("apply", "splice source core regions into the destinations"),
        ("init", "enroll markerless destinations and refresh marked ones"),
    ):
        subparser = subparsers.add_parser(name, help=help_text)
        subparser.add_argument("--source", required=True, help="source directory")
        subparser.add_argument(
            "--destination", required=True, help="destination directory"
        )
        subparser.add_argument("--bindings", required=True, help="bindings YAML file")
        subparser.add_argument(
            "--source-revision",
            required=True,
            type=_revision_arg,
            help="40-hex source revision to pin or compare",
        )
        if name == "init":
            subparser.add_argument(
                "--bind",
                action="append",
                default=[],
                metavar="SOURCE=DEST",
                help="add a region-mode source and destination mapping (repeatable)",
            )
            subparser.add_argument(
                "--bind-raw",
                action="append",
                default=[],
                metavar="SOURCE=DEST",
                help="add a raw-mode source and destination mapping (repeatable)",
            )
            subparser.add_argument(
                "--bind-cleared",
                action="store_true",
                help="enroll every cleared source not already bound",
            )
            subparser.add_argument(
                "--root",
                default=None,
                metavar="PATH",
                help="destination instruction-root path for the source root",
            )
    return parser


def _build_use_case(
    command: CommandName,
) -> VerifyDestinations | ApplyCoreRevision | EnrollDestinations:
    """Construct the requested use case with its local adapters wired in."""
    bindings_store = YamlBindingsStore()
    source_reader = LocalSourceCoreReader()
    destination_writer = LocalDestinationWriter()
    clearance = JsonClearanceStore()
    root_runtime = LocalRootRuntimeFile()
    paths = LocalFilesystemPaths()
    if command == "check":
        return VerifyDestinations(
            bindings_store,
            source_reader,
            destination_writer,
            clearance,
            root_runtime,
            paths,
        )
    if command == "apply":
        return ApplyCoreRevision(
            bindings_store,
            source_reader,
            destination_writer,
            clearance,
            root_runtime,
            paths,
        )
    return EnrollDestinations(
        bindings_store,
        source_reader,
        destination_writer,
        clearance,
        root_runtime,
        paths,
    )


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and dispatch to `check`, `apply`, or `init`."""
    args = _build_parser().parse_args(argv)
    source_dir = Path(args.source)
    destination_dir = Path(args.destination)
    bindings_path = Path(args.bindings)
    if args.command in ("apply", "init") and bindings_path.is_symlink():
        print(
            "invalid write target: bindings write target is a symbolic link: "
            f"{bindings_path}",
            file=sys.stderr,
        )
        return EXIT_INVALID
    outcome: UseCaseResult | DomainError
    try:
        use_case = _build_use_case(args.command)
        if args.command == "check":
            outcome = use_case.execute(
                source_dir, destination_dir, bindings_path, args.source_revision
            )
        elif args.command == "apply":
            outcome = use_case.execute(
                source_dir, destination_dir, bindings_path, args.source_revision
            )
        else:
            outcome = use_case.execute(
                source_dir,
                destination_dir,
                bindings_path,
                args.source_revision,
                getattr(args, "bind", []),
                getattr(args, "bind_raw", []),
                getattr(args, "bind_cleared", False),
                getattr(args, "root", None),
            )
    except OSError as error:
        print(f"core-sync I/O error: {error}", file=sys.stderr)
        return EXIT_DRIFT

    if isinstance(outcome, DomainError):
        print(outcome.message, file=sys.stderr)
        return _EXIT_CODE_BY_ERROR_CODE[outcome.code]
    print(outcome.message)
    return EXIT_OK
