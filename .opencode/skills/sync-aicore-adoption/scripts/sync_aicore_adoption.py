"""Core substrate for the ``sync-aicore-adoption`` protocol v2.

``check`` and ``propose-lock`` read existing repositories through the controlled
Git invocation and do not write those repositories, indexes, or worktrees;
``propose-lock`` writes only to stdout. ``verify-all`` reads a supplied checkout
unchanged and otherwise clones into a verifier-owned temporary directory that
it alone removes. Invoke this entry point with ``python3 -B``. This module does
not sandbox arbitrary importers or hosts.
"""

from __future__ import annotations

import sys

if __name__ == "__main__":
    sys.dont_write_bytecode = True

import argparse
from collections.abc import Sequence

from adoption_check import run_check
from adoption_constants import EXIT_FATAL, SCHEMA_UPGRADE_GUIDANCE
from adoption_contracts import SyncError
from adoption_propose import run_propose
from adoption_registry import run_verify


def _add_global_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--upstream-repo",
        default=".",
        help="upstream AICore repository (default: .)",
    )
    parser.add_argument(
        "--catalog",
        default=".aicore/core-catalog-v2.yaml",
        help="catalog path",
    )
    parser.add_argument("--declaration", help="adopter declaration path")
    parser.add_argument("--review", help="adopter review path")
    parser.add_argument("--lock", help="adopter lock path")
    parser.add_argument("--registry", help="adopter registry path")
    parser.add_argument(
        "--format",
        choices=("json", "human"),
        default="human",
        help="output format",
    )


def _add_snapshot_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--adopter-repo",
        help="adopter Git repository (default: inferred from --declaration)",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--adopter-revision",
        metavar="<sha>",
        help="explicit adopter commit tree",
    )
    group.add_argument(
        "--adopter-index",
        action="store_true",
        help="staged Git index only",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sync-aicore-adoption",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Read existing repositories for check and propose-lock.\n"
            "verify-all reads a supplied checkout unchanged, or clones into a\n"
            "verifier-owned temporary directory and removes only that directory.\n"
            "Invoke with python3 -B. This entry point does not sandbox importers."
        ),
    )
    _add_global_options(parser)
    subparsers = parser.add_subparsers(
        dest="command", metavar="{check,propose-lock,verify-all}"
    )
    subparsers.required = True
    check = subparsers.add_parser(
        "check",
        help="report adoption compliance from an existing repository",
    )
    _add_global_options(check)
    _add_snapshot_options(check)
    check.add_argument(
        "--diagnostic-revision",
        metavar="<sha>",
        help="diagnostic-only comparison revision",
    )
    check.set_defaults(func=run_check)
    propose = subparsers.add_parser(
        "propose-lock",
        help="emit a candidate lock to stdout without writing the repository",
    )
    _add_global_options(propose)
    _add_snapshot_options(propose)
    propose.set_defaults(func=run_propose)
    verify = subparsers.add_parser(
        "verify-all",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        help="read supplied checkouts or clone a verifier-owned temporary directory",
        description=(
            "Read each supplied checkout unchanged.\n"
            "A missing checkout is cloned into a verifier-owned temporary directory "
            "and only that directory is removed."
        ),
    )
    _add_global_options(verify)
    verify.add_argument("--checkouts-root", help="cached read-only checkout root")
    verify.set_defaults(func=run_verify)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except SyncError as exc:
        print(f"sync-aicore-adoption: {exc.code}: {exc.message}", file=sys.stderr)
        if exc.code == "schema_upgrade_required":
            print(SCHEMA_UPGRADE_GUIDANCE, file=sys.stderr)
        return EXIT_FATAL


if __name__ == "__main__":
    sys.exit(main())
