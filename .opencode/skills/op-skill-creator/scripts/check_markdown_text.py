"""Read-only Markdown text-integrity checker.

Usage:
    python check_markdown_text.py --policy PATH [--check-editor PATH] PATH [PATH ...]

Exit codes:
    0 — no errors (warnings may exist)
    1 — content errors and/or EDITOR-DRIFT
    2 — policy, input, or IO failure (takes precedence)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).absolute().parent))

from markdown_text_pkg.infrastructure.composition import main

if __name__ == "__main__":
    raise SystemExit(main())
