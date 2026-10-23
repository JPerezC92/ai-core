# Feature-document validator

> **Status:** closed
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-10-23
> **Closed:** 2026-10-23

## Specs

- S1 — A validator checks every `odd/tasks/*.md` except `_template.md` for the header, `## Specs`, `## Tasks`, `## Log`, numbered `S#`, task IDs with status and commit, and an `L1` entry.
- S2 — The validation logic is a pure function; file IO stays at the CLI edge; no external dependency is added.
- S3 — Tests cover a valid document and each required failure: missing section, missing L1, missing Spec, missing Task status, and an unfilled template placeholder.
- S4 — `uv run --frozen --group dev pytest -q` passes for the new tests and the existing suite.
- S5 — The `odd-workflow` skill and checklist point to the validator, so future agents run it instead of re-deriving the format.
- S6 — No second tracker, context injection, plugin, or dependency is introduced.
- S7 — The validator rejects an invalid Status value, a closed document without a Closed date or a Close entry, and an active document with a Close entry.
- S8 — A closed feature has every task `done`; an `open` or `in progress` task is a finding.

## Tasks

- T1 | S1, S2 | Write `.opencode/skills/odd-workflow/scripts/validate_feature.py` | done | commit: pending
- T2 | S3 | Write `test_validate_feature.py` with valid and invalid cases | done | commit: pending
- T3 | S5 | Point the skill and checklist to the validator | done | commit: pending
- T4 | S4 | Run the new tests and the whole suite | done | commit: pending
- T5 | S1, S3 | Fix audit-10 advisories: per-entry validation, status vocabulary, directory/template-exclusion test, fenced-code handling | done | commit: pending
- T6 | S7 | Add status/close consistency checks and tests | done | commit: pending
- T7 | S8 | Add closed-task completion check and tests | done | commit: pending

## Log

- L1 — "continue"
- L2 — Scope: mechanical validation of feature-document anatomy only; no content rewrite, no new dependency, no second tracker.
- L3 — Implemented the validator and 12 tests; `pytest -q .opencode/skills/odd-workflow/scripts/test_validate_feature.py` → 12 passed; the validator returns `ok` for all three feature documents.
- L4 — Whole suite: `uv run --frozen --group dev pytest -q` → 679 passed, exit 0. The `odd-workflow` skill version advanced to 1.1.0.
- L5 — Close: verified outcome; no failed checks. Pending: independent audit. Next step: the next legacy feature migration.
- L6 — Scope boundary: the validator is mechanical anatomy only (headings, S#/T#/L1, task status, placeholders). Semantic correctness — meaningful specs, complete tasks, true evidence — remains Cipher's review.
- L7 — Audit-10 advisories fixed: per-entry validation, documented status vocabulary, directory/template-exclusion and exit-code tests, fenced-code placeholder handling. The mechanical boundary is unchanged.
- L8 — Verification after the advisories: feature tests 18 passed; whole suite 685 passed, exit 0; validator `ok` for all three feature documents.
- L9 — Close: status/close consistency rule added; 23 feature tests and 690-test suite pass; validator `ok` for all three documents.
- L10 — Close: closed-task completion rule added; 25 feature tests and 692-test suite pass; validator `ok` for all three documents.
