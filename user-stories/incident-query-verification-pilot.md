# User story — incident-query-verification-pilot

> **Created:** 2026-09-10
> **Title:** Incident query-verification pilot
> **Status:** active
> **version:** 1.2.0
> **Epic:** incident-diagnostics
> **Affected areas:** `.opencode/skills/query-verification/`, `.opencode/skills/ticket-runbook/`, `.opencode/agents/crucible.md`, `knowledge/`
> **Contract approval:** 2026-10-14 — user approved the AC5 reword and the proof-surface corrections after the whole-catalogue review, collision report, and contract preview.

## Persona

- An incident investigator who must establish whether a current ticket exhibits a known data symptom without guessing or exposing sensitive case data.

## Goal

- **G:** Validate a destination-owned, read-only diagnostic query definition and evaluate its trusted result without giving AICore database credentials or query-execution authority.
  - Done when: the pilot produces a redacted, digest-bound `verified`, `not_verified`, or `inconclusive` evidence record from a root-contained incident verifier and normalized adapter output.

## Scenario

- An incident ticket has a known symptom and a destination-owned SQL diagnostic query. The investigator validates its sidecar definition, obtains normalized output from the destination's trusted adapter, and records the three-state verdict as investigate-step evidence while consuming one existing query-budget slot.

## Acceptance criteria

- ✅ **AC1:** A sidecar verifier is accepted only when it is incident-owned, adjacent to its root-contained SQL source, read-only, bounded, and uses declared named bindings.
- ✅ **AC2:** Unsafe SQL, path escapes, malformed metadata, untrusted output mismatches, and ambiguous result shapes produce a rejection or `inconclusive` verdict without query execution.
- ✅ **AC3:** The evidence record redacts configured values, binds verifier/source/definition digests to the verdict, and retains neither raw adapter output nor credentials.
- ✅ **AC4:** The optional investigate-step verifier path consumes one existing query-budget unit and never treats a verified symptom as automatic root-cause confirmation.
- ✅ **AC5:** The skill, protocol, fixtures, and the living design's shared contract are available to ticket-enabled destination projects.
- ✅ **AC6:** The shipped valid adapter-output fixture is independently protocol-valid and its source digest is guarded against fixture/source drift.
- ✅ **AC7:** Reusable verifier persistence is destination-selected: the destination chooses its query-storage location, the problem row's Evidence records a pointer to the sidecar, and a later structural match replays the pair with current-ticket parameters under the same protocol (schema unchanged, one query-budget slot).
- ✅ **AC8:** The diagnostic-query protocol remains the only sidecar contract — one read-only SELECT, one row, three-state verdict. Identification packs use a separate Evidence pointer and are not evaluated by the diagnostic evaluator.

## Proof

- AC1 → `.opencode/skills/query-verification/references/protocol-v1.md` closed contract · `test_query_verification_paths.py` path tests · `test_query_verification_sql_safety.py` unsafe-source rejection · `test_query_verification_sidecar_schema.py` closed-schema rejections
- AC2 → `test_query_verification_sql_safety.py` · `test_query_verification_paths.py` · `test_query_verification_sidecar_schema.py` · evaluator `test_evaluate_*_is_inconclusive` cases
- AC3 → `test_query_verification.py` redaction-and-digest evaluation case · `references/protocol-v1.md` redaction and digest rules
- AC4 → `.opencode/skills/ticket-runbook/SKILL.md` `### Optional verifier route (investigate step)` · `test_validate_runbook_step_mode.py` · `test_validate_runbook_header_budgets.py`
- AC5 → `.opencode/skills/query-verification/` ships `references/protocol-v1.md` plus the valid fixture trio · `knowledge/diagnostic-system-design.md` `## Purpose` · `distribution-clearance.json` living-design row
- AC6 → `test_query_verification.py` valid-fixture evaluation case · `_query_verification_testkit.py` static-adapter source-digest guard · `test_query_verification_fixtures.py` fixture-trio validation
- AC7 → `knowledge/diagnostic-system-design.md` `## Portability contract` · `knowledge/problems.md` `## Entry format` → Evidence
- AC8 → `references/protocol-v1.md` · `test_query_verification.py` suite · `.opencode/skills/ticket-runbook/SKILL.md` verifier-step guidance · `knowledge/problems.md` Evidence format

## Constraints

- AICore never connects to a database and never executes a diagnostic query — because the pilot must not acquire production credentials or query-execution authority.
- The protocol is sidecar-only and incident-only; Dev workflow integration and centralized catalogs are out of scope — because the pilot establishes one narrow, auditable route before any generalization.
- A verified symptom is never automatic root-cause confirmation — because symptom presence and cause are different claims.
- Identification packs use a separate Evidence pointer and are not evaluated by the diagnostic evaluator — because a multi-statement correlation is not a single-query protocol-v1 verdict.
- The shipped adapter-output fixture's source digest is asserted against its SQL fixture — because a drifted fixture silently proves nothing.

## Change log

- before 2026-09-16 — earlier history: see git history for this file
- 2026-09-16 — identification-pack-pointer-20260916 (PR #42): recorded that identification packs use `pack:`, not a protocol-v1 change.
- 2026-09-27 — python-pytest-20260927 (PR #43): moved Python skill tests to pytest under Crucible 🔥 (Test Architect); earlier unittest decisions remain historical.
- 2026-10-10 — aicore-all-files-pr-20261008 (PR #52): repointed path, SQL-safety, sidecar-schema, and runbook test evidence to concern-specific modules; added direct valid-fixture/source-digest evidence.
- 2026-10-12 — story revision (PR #59): split behavioural criteria from `## Proof`, retired `## Resolved decisions` in favour of `## Constraints`, and removed the advisory-dispositions audit history from the contract.
- 2026-10-14 — knowledge-distribution-20261014 (PR #63): delivered the clearance-shipped living-design shared contract and recorded the approved AC5 reword plus the AC4/AC5/AC7 proof-surface corrections.
