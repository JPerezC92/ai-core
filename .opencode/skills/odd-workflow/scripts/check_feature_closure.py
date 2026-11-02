"""Report feature documents still claiming to be active after their branch is gone.

A feature whose branch no longer exists on the remote is delivered but unclosed:
the branch disappears only after its pull request merged and the branch was
cleaned up. The check reads documents and remote ref state and mutates nothing;
its only external interaction is one `git ls-remote` per checkable branch.

Exit status: 0 when nothing is reported, 1 when at least one document is
reported, and 2 for a usage, IO, or Git boundary failure. Reported documents go
to stdout; boundary diagnostics go to stderr. Exit 2 rather than 0 for an empty
document selection is deliberate: a check that read no document must never
present itself as a clean check.

Usage:
    uv run --frozen python3 .opencode/skills/odd-workflow/scripts/check_feature_closure.py
"""

from __future__ import annotations

import argparse
import sys

from feature_closure.application.check_feature_closure import execute
from feature_closure.domain.records import NoFeatureDocumentsError, UnclosedFeatureError
from feature_closure.infrastructure.filesystem import FilesystemFeatureSource
from feature_closure.infrastructure.git_remote import GitBoundaryError, GitRemoteBranchProbe

DEFAULT_FEATURES_DIR = "odd/tasks"
DEFAULT_REMOTE = "origin"


def _options(argv: list[str]) -> argparse.Namespace:
    """Parse the document-directory and remote overrides at the delivery edge."""
    parser = argparse.ArgumentParser(
        prog="check_feature_closure.py",
        description="Report active feature documents whose branch left the remote.",
    )
    parser.add_argument(
        "--features-dir",
        default=DEFAULT_FEATURES_DIR,
        help=f"feature-document directory to scan (default: {DEFAULT_FEATURES_DIR})",
    )
    parser.add_argument(
        "--remote",
        default=DEFAULT_REMOTE,
        help=f"remote whose branches are checked (default: {DEFAULT_REMOTE})",
    )
    return parser.parse_args(argv[1:])


def main(argv: list[str]) -> int:
    """Serialize reported documents and boundary failures into an exit status."""
    options = _options(argv)
    source = FilesystemFeatureSource()
    branches = GitRemoteBranchProbe()
    reported = False
    try:
        for result in execute(options.features_dir, options.remote, source, branches):
            if isinstance(result, UnclosedFeatureError):
                reported = True
                print(
                    f"UNCLOSED {result.path}: branch "
                    f"'{result.branch}' no longer exists on '{options.remote}'"
                )
            elif isinstance(result, NoFeatureDocumentsError):
                print(f"error: {result.message}", file=sys.stderr)
                return 2
    except (OSError, GitBoundaryError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 1 if reported else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
