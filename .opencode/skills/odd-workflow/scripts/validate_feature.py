"""Validate ODD feature-document anatomy through the assembled CLI.

Mechanical checks do not establish semantic correctness or evidence truth.
The entry wires filesystem access and prints the operation's typed outcomes.
The pure validate_feature helper remains importable for existing consumers.

Usage:
    uv run --frozen python3 .opencode/skills/odd-workflow/scripts/validate_feature.py odd/tasks
"""

import sys

from feature_validation.application.validate_features import execute
from feature_validation.domain.records import InvalidFeatureError, NoFeatureDocumentsError
from feature_validation.domain.rules import validate_feature as validate_feature
from feature_validation.infrastructure.filesystem import FilesystemFeatureSource


def main(argv: list[str]) -> int:
    """Validate a target and serialize outcomes without catching boundary errors."""
    if len(argv) != 2:
        print("usage: validate_feature.py <file-or-directory>")
        return 2

    source = FilesystemFeatureSource()
    failed = False
    for result in execute(argv[1], source):
        if isinstance(result, NoFeatureDocumentsError):
            print(result.message)
            failed = True
        elif isinstance(result, InvalidFeatureError):
            failed = True
            print(f"FAIL {result.path}")
            for finding in result.findings:
                print(f"  - {finding}")
        else:
            print(f"ok {result.path}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
