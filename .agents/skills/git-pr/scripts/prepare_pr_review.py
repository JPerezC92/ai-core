"""Compose PR review content preparation commands from local files."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

from pr_content.application.validate_final_body import execute as validate
from pr_content.domain.body_validation import extract_body
from pr_content.domain.records import ReviewPreparationError
from pr_content.infrastructure.filesystem import create_text, read_text


def main(argv: list[str] | None = None) -> int:
    """Decode supplied files, invoke operations and serialize results at delivery."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    initialize = commands.add_parser("initialize")
    initialize.add_argument("--draft", required=True)
    initialize.add_argument("--working-body", required=True)
    validate_command = commands.add_parser("validate")
    validate_command.add_argument("--baseline", required=True)
    validate_command.add_argument("--current", required=True)
    validate_command.add_argument("--working-body", required=True)
    validate_command.add_argument("--decisions")
    args = parser.parse_args(argv)
    try:
        if args.command == "initialize":
            body = extract_body(read_text(args.draft))
            if isinstance(body, ReviewPreparationError):
                print(json.dumps(asdict(body)))
                return 1
            create_text(args.working_body, body)
        else:
            baseline = json.loads(read_text(args.baseline))
            current = json.loads(read_text(args.current))
            candidate = read_text(args.working_body)
            outcome = validate(baseline=baseline, current=current, body=candidate,
                               decisions=json.loads(read_text(args.decisions)) if args.decisions else None)
            if isinstance(outcome, ReviewPreparationError):
                print(json.dumps(asdict(outcome)))
                return 1
        print(json.dumps({"status": "prepared", "command": args.command}))
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        print(f"input/output failure: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
