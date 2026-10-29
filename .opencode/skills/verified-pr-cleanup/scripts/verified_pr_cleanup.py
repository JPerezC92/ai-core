"""Read-only CLI entrypoint for merged-branch cleanup preflight."""

from __future__ import annotations

from verified_pr_cleanup_pkg.entry import main


if __name__ == "__main__":
    raise SystemExit(main())
