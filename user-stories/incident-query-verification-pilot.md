# User story — incident-query-verification-pilot

> **Created:** 2026-09-10
> **Title:** Incident query-verification pilot
> **Status:** active
> **Epic:** incident-diagnostics
> **Affected areas:** `.opencode/skills/query-verification/`, `.opencode/skills/ticket-runbook/`, `.opencode/agents/crucible.md`, `knowledge/`

## Persona

- An incident investigator who must establish whether a current ticket exhibits a known data symptom without guessing or exposing sensitive case data.

## Goal

- **G:** Validate a destination-owned, read-only diagnostic query definition and evaluate its trusted result without giving AICore database credentials or query-execution authority.
  - Done when: the pilot produces a redacted, digest-bound `verified`, `not_verified`, or `inconclusive` evidence record from a root-contained incident verifier and normalized adapter output.

## Scenario

- An incident ticket has a known symptom and a destination-owned SQL diagnostic query. The investigator validates its sidecar definition, obtains normalized output from the destination's trusted adapter, and records the three-state verdict as investigate-step evidence while consuming one existing query-budget slot.

## Acceptance criteria

- ✅ A sidecar verifier is accepted only when it is incident-owned, adjacent to its root-contained SQL source, read-only, bounded, and uses declared named bindings. Evidence: `test_query_verification.py` exits 0 with 73 tests, including `test_rejects_absolute_source`, `test_rejects_traversal_source`, and `test_rejects_mutating_source`; the closed contract is `references/protocol-v1.md` in the `query-verification` skill.
- ✅ Unsafe SQL, path escapes, malformed metadata, untrusted output mismatches, and ambiguous result shapes produce a rejection or `inconclusive` verdict without query execution. Evidence: `test_rejects_mutating_source`, `test_rejects_unknown_sidecar_field`, `test_rejects_malformed_yaml_sidecar`, and the `test_evaluate_*_is_inconclusive` cases in `test_query_verification.py`; the suite exits 0 with 73 tests.
- ✅ The evidence record redacts configured values, binds verifier/source/definition digests to the verdict, and does not retain raw adapter output or credentials. Evidence: `test_evaluate_verified_redacts_and_binds_digests` in `test_query_verification.py`; the redaction and digest rules are in `references/protocol-v1.md`.
- ✅ The optional investigate-step verifier path consumes one existing query-budget unit and never treats a verified symptom as automatic root-cause confirmation. Evidence: the implemented investigate-step verifier-evidence route is recorded in `knowledge/query-verification-design.md`, and `test_validate_runbook.py` exits 0.
- ✅ The skill, protocol, fixtures, and migration entry are available to ticket-enabled destination projects. Evidence: the `query-verification` skill ships `references/protocol-v1.md` and the valid fixture trio, and `knowledge/query-verification-design.md` records the skill and design document as `only if ticket marker` migration items.
- ✅ The shipped valid adapter-output fixture is independently protocol-valid and its source digest is guarded against fixture/source drift.

## Advisory dispositions

Recorded 2026-09-10. Every outcome is evidence-backed; no dependency, lockfile, register, protocol, or ticket behavior changed.

| Advisory | Disposition | Evidence |
|---|---|---|
| The shipped valid adapter fixture was not independently usable | **Resolved.** `source_digest` equals the SHA-256 of the unchanged `incident-check.sql` bytes (`sha256:1e098701a3d6952bf6bae5a05d899527051e40f384e344e607981f4ffb7a218a`); the fixture trio evaluates directly to `verified`. | The query-verification suite exits 0 with 73 tests and a drift assertion that fails on fixture/source digest divergence. |
| Vault 🔐 (Catalog Steward) extraction rule QC-27 required a literal `.md` path | **Resolved.** QC-27 accepts named, non-executable Markdown/YAML/JSON/other machine-readable reference artifacts when explicitly referenced; executable code stays in `scripts/`; opaque or unnamed artifacts are rejected. | Vault 🔐 (Catalog Steward) runtime spec `1.1.0`. |
| README register labels and skill count were stale | **Resolved.** Labels now match the register H1s (`Diagnostic Symptom Catalog`, `Known Problem Pattern Register`); a note explains the manifest's self-exclusion of `migrate-core-to-project` (9 skill rows vs 10 inventory). | `README.md`; migration selection unchanged. |
| A plan phase could name a verification command without a traceable executor | **Resolved.** `plan-enforce` `1.11.1` requires one canonical `Executor`/`Command` table per phase; the validator enforces table presence/shape (declared traceability only) and phase review audits executor authority. | 29 validator tests pass, including 8 executor-command table cases (7 rejection + 1 acceptance). |
| Python stdlib `unittest` test gating had no owner | **Resolved — superseded by the Crucible 🔥 (Test Architect) Python-audit branch (2026-09-10).** Bastion 🧱 (Backend & Scripts Architect) `1.1.0` originally owned the gate: a declared runnable `python3` command plus Bastion 🧱 (Backend & Scripts Architect) [PASS], with Crucible 🔥 (Test Architect) dispatched and its actual applicability verdict recorded without relabeling. `pytest` is not added. | Original gate: Bastion 🧱 (Backend & Scripts Architect) runtime spec `1.1.0`. Superseding gate: `.opencode/agents/crucible.md` `1.1.0` (`## PYTHON STDLIB UNITTEST TESTS`), `.opencode/agents/bastion.md` `1.2.0`, and `plan-enforce` `1.11.1`. |
| `__pycache__` bytecode and register title edits | **No action.** `__pycache__/` is gitignored; the `knowledge/symptoms.md` and `knowledge/problems.md` title edits belong to the completed `query-verification-naming-20260910` plan and were not modified here. | Root `.gitignore`; register H1s unchanged. |

**Recorded audit verdicts:** Vault 🔐 (Catalog Steward) ADVISORY (gate items pass, findings corrected); Sentinel 🛡️ (Quality Guardian) ADVISORY (mechanical naming fixes applied; no blocking defect); Bastion 🧱 (Backend & Scripts Architect) PASS; Crucible 🔥 (Test Architect) `[UNCERTAIN]` (TypeScript rules inapplicable, recorded as-is; superseded 2026-09-10 — see Resolved decisions).

## Change log

- 2026-09-10 - query-verification-pilot-20260910: created the feature definition for the incident-only safe pilot.
- 2026-09-10 - advisory-fixes-plan-enforce-20260910: added standalone-valid fixture and digest-drift acceptance coverage; recorded the completed fixture, QC-27, README, executor, and stdlib-test-gate advisory dispositions and the Bastion-owned stdlib unittest governance decision.
- 2026-09-10 - python-test-audit-governance-20260910: checked the five remaining acceptance criteria with evidence (the story remains active as the living feature registry); recorded the superseding Crucible 🔥 (Test Architect) Python-audit decision and dropped the unsupported fix-count claim.
- 2026-09-12 - refresh-git-pr-evidence-contract-20260912: refreshed the current plan-enforce requirement citations to the shipped 1.11.1; no feature behavior or acceptance criteria changed.
- 2026-09-12 - register-first-incident-identification-20260912: mapped the optional verifier route from Phase 04 wording to the investigate step; acceptance criteria unchanged.

## Resolved decisions

- 2026-09-10 - the pilot accepts normalized output from a destination-owned trusted adapter; AICore does not connect to databases or execute diagnostic queries.
- 2026-09-10 - the pilot is incident-only and sidecar-only; Dev workflow integration and centralized catalogs are deferred.
- 2026-09-10 - Python stdlib `unittest` test gating is owned by Bastion 🧱 (Backend & Scripts Architect); Crucible 🔥 (Test Architect) applicability results are recorded as-is and never relabeled PASS.
- 2026-09-10 - superseding decision: Python stdlib `unittest` test architecture is owned by Crucible 🔥 (Test Architect) via its additive `## PYTHON STDLIB UNITTEST TESTS` branch, which returns [PASS]/[FAIL] for exact active-plan Python test files; [UNCERTAIN] is not acceptable for that scope. The earlier Bastion-only gate and its recorded [UNCERTAIN] applicability verdict remain historical and are not relabeled.
- 2026-09-12 - register-first collision: this story keeps its completed verifier contract; ticket-runbook identification is redefined by `register-first-incident-identification`. The optional verifier remains symptom evidence only on the investigate step.
