"""Compose the attribution scan CLI from input decoding, the operation, and output."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from attribution_scan.application.scan_attribution import execute
from attribution_scan.domain.records import (
    Artifact,
    AttributionPolicy,
    ChangedFile,
    Exclusion,
    Match,
    PolicyValidationError,
    ScanInput,
    ScanResult,
    Snapshot,
    SnapshotValidationError,
)

# Explicit re-export surface preserved for `from scan_attribution import ...`
# consumers: the module keeps every typed record reachable by name.
__all__ = [
    "Artifact",
    "AttributionPolicy",
    "ChangedFile",
    "Exclusion",
    "Match",
    "ScanResult",
    "Snapshot",
    "main",
]


def main(argv: list[str] | None = None) -> int:
    """Read CLI inputs, serialize the scan, and return the documented status."""
    parser = argparse.ArgumentParser(description="Scan a complete PR snapshot for approved attribution lines.")
    parser.add_argument("--policy", required=True, help="path to the approved attribution policy JSON")
    parser.add_argument("--snapshot", required=True, help="path to the immutable PR snapshot JSON")
    arguments = parser.parse_args(argv)
    try:
        policy_value = json.loads(Path(arguments.policy).read_text(encoding="utf-8"))
        snapshot_value = json.loads(Path(arguments.snapshot).read_text(encoding="utf-8"))
    except OSError:
        print(json.dumps({"error": "unable to read input file"}, sort_keys=True))
        return 2
    except UnicodeError:
        print(json.dumps({"error": "input is not valid UTF-8"}, sort_keys=True))
        return 2
    except json.JSONDecodeError:
        print(json.dumps({"error": "input is not valid JSON"}, sort_keys=True))
        return 2
    result = execute(ScanInput(snapshot_value=snapshot_value, policy_value=policy_value))
    if isinstance(result, (PolicyValidationError, SnapshotValidationError)):
        print(json.dumps({"error": result.message}, sort_keys=True))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if result["matches"] else 0


if __name__ == "__main__":
    sys.exit(main())
