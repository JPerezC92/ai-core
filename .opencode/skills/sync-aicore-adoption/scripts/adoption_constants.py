"""Protocol constants and fixed data for sync-aicore-adoption."""

from __future__ import annotations

import re

EXIT_FATAL = 2
PROFILE_MARKERS = ("backend_stack", "python_scripts", "ticket_system")
DECLARATION_MODES = ("mirror", "adapted", "replacement", "destination_owned", "not_applicable")
LOCK_MODES = DECLARATION_MODES
PROJECTIONS = ("file", "tree")
SYNC_PROJECTIONS = ("file", "guarded_file", "tree", "assertions")
DESTINATION_POLICIES = ("adopter_root_runtime", "adopter_root_rules")
REVIEW_DECISIONS = ("applied", "declined", "superseded")
COLLISION_POLICIES = ("core_wins",)

# ---------------------------------------------------------------------------
# protected rule-document layout contract
# ---------------------------------------------------------------------------

# A unit carrying ``rule_documents`` is a protected rule unit. Only these
# declaration modes are permitted: ordinary mirror/adapted mappings and a
# machine-valid ``not_applicable``. ``replacement`` and ``destination_owned``
# cannot avoid mandatory-core convergence.
PROTECTED_DECLARATION_MODES = ("mirror", "adapted", "not_applicable")
RULE_LAYOUT_VALUE = "two-section-v1"
RULE_LAYOUT_MARKER = f"> **Rule layout:** {RULE_LAYOUT_VALUE}"
RULE_LAYOUT_EXTENSIONS_HEADING = "## Project extensions"
RULE_LAYOUT_MANDATORY_HEADING = "## Mandatory core"
RULE_DOCUMENT_SUFFIX = ".md"
STORY_UNIT_KIND = "user-story"
STORY_INDEX_NAME = "index.md"
LOCK_DIGEST_FIELDS = (
    "accepted_catalog_digest",
    "declaration_digest",
    "review_digest",
    "accepted_snapshot_digest",
)
SCHEMA_UPGRADE_GUIDANCE = (
    "schema_version 1 is upgrade-only input. Re-declare the adopter under v2 (add the "
    "profile block, cover every catalog unit including former `none` config units), author "
    "the v2 review, and regenerate a fresh v2 lock at one revision. See "
    "references/protocol-v2.md §7 \"Errors and compatibility\"."
)

# ---------------------------------------------------------------------------
# check dispositions and review modes
# ---------------------------------------------------------------------------

_BLOCKING_DISPOSITIONS = frozenset(
    {
        "policy_violation",
        "update_available",
        "local_drift",
        "review_required",
        "conflict",
        "baseline_advance_required",
    }
)
_REVIEW_MODES = ("adapted", "replacement", "destination_owned")

# ---------------------------------------------------------------------------
# adopter-root runtime policy markers and reference data
# ---------------------------------------------------------------------------

_ADOPTER_ROOT_FORBIDDEN_REFERENCES = (
    "aicore",
    "ai-core",
    "migrate-core-to-project",
    "sync-aicore-adoption",
    ".aicore/",
    "upstream provenance",
    "upstream lineage",
    "reuse guide",
)
_ADOPTER_ROOT_REQUIRED_MARKERS = (
    (
        "Project identity",
        re.compile(r"^> \*\*Project identity:\*\* \S.*$", re.MULTILINE),
    ),
    (
        "Spec version",
        re.compile(r"^> \*\*Spec version:\*\* \d+\.\d+\.\d+\s*$", re.MULTILINE),
    ),
    (
        "Local version",
        re.compile(r"^> \*\*Local version:\*\* \d+\.\d+\.\d+\s*$", re.MULTILINE),
    ),
)

# ---------------------------------------------------------------------------
# test-runner metadata and runner-policy constants
# ---------------------------------------------------------------------------

AICORE_SUITE_COMMAND = "uv run --frozen --group dev pytest -q"
OPENCODE_CONFIG_BASENAME = "opencode.jsonc"
TEST_RUNNER_KEYS = ("no_tests", "commands", "executor", "scope", "reviewer", "evidence")
TEST_RUNNER_SCOPE = "whole_project"
