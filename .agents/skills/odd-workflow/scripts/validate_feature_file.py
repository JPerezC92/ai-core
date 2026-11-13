"""Validate durable feature-file anatomy through the assembled CLI.

Mechanical checks do not establish semantic correctness or evidence truth.
The entry wires filesystem access and prints the operation's typed outcomes.
Two pure helpers are re-exported for callers that do not need the CLI:
validate_feature_file returns the ordered findings alone, and
assess_feature_file returns those findings together with the status derived
from the ticks — the same status this CLI prints.

Usage:
    uv run --frozen python3 .agents/skills/odd-workflow/scripts/validate_feature_file.py .aicore/core/odd/features
"""

import sys

from feature_file_validation.application.validate_feature_files import execute
from feature_file_validation.domain.records import (
    InvalidFeatureFileError,
    NoFeatureFileDocumentsError,
)
from feature_file_validation.domain.rules import (
    assess_feature_file as assess_feature_file,
    validate_feature_file as validate_feature_file,
)
from feature_file_validation.infrastructure.filesystem import FilesystemFeatureFileSource


def main(argv: list[str]) -> int:
    """Validate a target and serialize outcomes without catching boundary errors."""
    if len(argv) != 2:
        print("usage: validate_feature_file.py <file-or-directory>")
        return 2

    source = FilesystemFeatureFileSource()
    failed = False
    for result in execute(argv[1], source):
        if isinstance(result, NoFeatureFileDocumentsError):
            print(result.message)
            failed = True
        elif isinstance(result, InvalidFeatureFileError):
            failed = True
            print(f"FAIL {result.path}")
            for finding in result.findings:
                print(f"  - {finding}")
        else:
            print(f"ok {result.path} — status: {result.status}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
