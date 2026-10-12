"""Data-only constants shared by the core-sync domain, application, and infrastructure."""

from __future__ import annotations

import re
from typing import Literal

BindingMode = Literal["region", "raw", "merge"]
CommandName = Literal["check", "apply", "init"]

MODE_REGION: BindingMode = "region"
MODE_RAW: BindingMode = "raw"
MODE_MERGE: BindingMode = "merge"
VALID_MODES: tuple[BindingMode, ...] = (MODE_REGION, MODE_RAW, MODE_MERGE)

ROLE_ROOT = "root"
VALID_ROLES: tuple[str, ...] = (ROLE_ROOT,)
CLEARANCE_SCHEMA = 2

BEGIN = "<!-- core:begin -->"
END = "<!-- core:end -->"
PROJECT_BEGIN = "<!-- project:begin -->"
PROJECT_END = "<!-- project:end -->"

FRONTMATTER_DELIMITER = "---"
REVISION_RE = re.compile(r"^[0-9a-f]{40}$")
FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
SCHEMA_VERSION = 1
RECONCILIATION_DIRNAME = "reconciliation"
RECONCILIATION_FILENAME = "init.yaml"
CLEARANCE_REL = "distribution-clearance.json"

RECONCILE_BEGIN = "<!-- core:reconcile:begin -->"
RECONCILE_END = "<!-- core:reconcile:end -->"
RECONCILE_BODY = (
    "> **⚠️ ACTION REQUIRED — core reconciliation. This project is not current "
    "until this is done.**\n"
    ">\n"
    "> You (the assistant working in THIS project) must reconcile some files, "
    "and adopt one permanent rule. This block is self-contained; no other "
    "context is required.\n"
    ">\n"
    "> **Permanent rule — adopt it now, in every future session.** Files here "
    "are split into two marked regions:\n"
    "> - `<!-- core:begin -->` … `<!-- core:end -->` — the **core region**, "
    "owned by an upstream core project. **Never edit, move, or delete anything "
    "between these two markers.**\n"
    "> - `<!-- project:begin -->` … `<!-- project:end -->` — the "
    "**project region**, owned by THIS project. All edits go here.\n"
    "> If this rule is not already in this project's root instructions "
    "(`CLAUDE.md` / `AGENTS.md`), add it there permanently. This blocker "
    "block is temporary and gets deleted at the end; the rule is permanent.\n"
    ">\n"
    "> **What happened.** A core update replaced each file's core region with "
    "new shared content. The old content that used to sit there was moved into "
    "the project region, so the project region now holds BOTH this project's "
    "own rules AND an old copy of the core rules that the new core region "
    "already supersedes.\n"
    ">\n"
    "> **Do this for every file listed in `.aicore/core.yaml` under "
    "`pending:` (paths are relative to this project root):**\n"
    "> 1. Open the file.\n"
    "> 2. If `.aicore/reconciliation/init.yaml` exists, read it. It records the "
    "core revision and each affected destination path, source, and action as "
    "metadata; it does not contain the displaced content. Use that metadata to "
    "locate and review each destination file, then inspect the displaced "
    "content there, in its `<!-- project:begin -->` … `<!-- project:end -->` "
    "region.\n"
    "> 3. Edit ONLY inside `<!-- project:begin -->` … `<!-- project:end -->`: "
    "remove anything that merely duplicates or contradicts the core region "
    "(it is the superseded old copy), and keep this project's genuine, "
    "project-specific rules and facts.\n"
    "> 4. Never touch the core region and never move or delete the markers.\n"
    "> 5. Delete that file's entry from the `pending:` list in "
    "`.aicore/core.yaml`.\n"
    ">\n"
    "> **To finish.** When `pending:` is empty, **delete this entire blocker "
    "block** (from `<!-- core:reconcile:begin -->` to "
    "`<!-- core:reconcile:end -->`). Change nothing outside the project regions."
)
DEFAULT_ROOT_CANDIDATES: tuple[str, ...] = (
    "AGENTS.md",
    "agents.md",
    "CLAUDE.md",
    "claude.md",
    "instructions.md",
)

EXIT_OK = 0
EXIT_DRIFT = 1
EXIT_INVALID = 2
