"""Compose offline PR review preparation commands without GitHub or subprocess IO."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

from pr_review.application.assemble_review_snapshot import execute as assemble
from pr_review.application.validate_final_body import execute as validate
from pr_review.application.verify_persisted_body import execute as verify
from pr_review.application.prepare_local_snapshot import execute as prepare_local
from pr_review.domain.body_validation import extract_body
from pr_review.domain.records import ReviewPreparationError
from pr_review.infrastructure.filesystem import create_text, read_text


def main(argv: list[str] | None = None) -> int:
    """Decode supplied files, invoke operations and serialize results at delivery."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    initialize = commands.add_parser("initialize")
    initialize.add_argument("--draft", required=True)
    initialize.add_argument("--working-body", required=True)
    snapshot = commands.add_parser("snapshot")
    snapshot.add_argument("--input", required=True)
    snapshot.add_argument("--paths", required=True)
    snapshot.add_argument("--output", required=True)
    local = commands.add_parser("prepare-snapshot")
    for option in ("draft", "working-body", "input", "paths", "output"):
        local.add_argument(f"--{option}", required=True)
    for name in ("validate", "verify"):
        command = commands.add_parser(name)
        command.add_argument("--baseline", required=True)
        command.add_argument("--current", required=True)
        command.add_argument("--working-body", required=True)
        if name == "validate":
            command.add_argument("--decisions")
    args = parser.parse_args(argv)
    try:
        if args.command == "initialize":
            body = extract_body(read_text(args.draft))
            if isinstance(body, ReviewPreparationError):
                print(json.dumps(asdict(body)))
                return 1
            create_text(args.working_body, body)
        elif args.command in ("snapshot", "prepare-snapshot"):
            inventory = json.loads(read_text(args.input))
            paths = json.loads(read_text(args.paths))
            result = (prepare_local(draft=read_text(args.draft), body=read_text(args.working_body), inventory=inventory, exact_paths=paths)
                      if args.command == "prepare-snapshot" else assemble(collected=inventory, exact_paths=paths))
            if isinstance(result, ReviewPreparationError):
                print(json.dumps(asdict(result)))
                return 1
            create_text(args.output, json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        else:
            baseline = json.loads(read_text(args.baseline))
            current = json.loads(read_text(args.current))
            candidate = read_text(args.working_body)
            outcome = (validate(baseline=baseline, current=current, body=candidate,
                                decisions=json.loads(read_text(args.decisions)) if args.decisions else None)
                       if args.command == "validate" else verify(expected=baseline, persisted=current, body=candidate))
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
