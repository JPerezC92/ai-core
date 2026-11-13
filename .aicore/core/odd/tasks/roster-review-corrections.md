# Roster review corrections

> **Status:** closed
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-10-25
> **Closed:** 2026-10-25

## Specs

- S1 — Preserve accepted small predecessors: the PR-intent correction in `.opencode/skills/git-pr/SKILL.md` 1.7.4 and the Forge ODD-routing correction in `.opencode/agents/forge.md` 1.6.7, with the aligned Forge version fixture. They use ODD classification; small work needs no artificial feature document, non-small work needs its unique governing feature, and legacy input is migration-only.
- S2 — Resolve audit finding 3 in `.opencode/agents/warden.md` and `.opencode/agents/herald.md`: a Critical/High dependency BLOCK is never cleared by an agent override; an ADVISORY is fixed first when a safe, in-scope correction exists, otherwise the user explicitly decides, and Cipher documents but does not accept the risk. Both specs must express one coherent policy.
- S3 — Define the review gate: `[PASS]` requires zero open findings at the reviewed head. Fixed findings stay in audit history but are closed; a deferred/ADVISORY finding remains open and cannot be PASS; BLOCK cannot be PASS; a new finding invalidates a prior PASS. An observation that requires no action is a note, not a finding.
- S4 — Define fix-first disposition for every real finding: if it is in scope, local/reversible, has one correct answer, changes no behavior/API/security/data/dependency/permission, and is verifiable now, fix it and record it without asking. Otherwise stop affected work and report exact evidence, impact, options, and recommendation. Never use “ignore” as a disposition; deferred work needs explicit authority.
- S5 — Resolve remaining roster findings 4–11 with their canonical owners: Lumen's output-versus-root write boundary; Quill/Ledger remote ticket-image references; Ledger ticket `created` provenance; Investigator `mitigated` structural matching; Augur/Warden Git-read routing; Lumen project-owned browser binding; Investigator's nonexistent heading; Sentinel naming consistency. Findings requiring a user choice stop for that choice; no silent policy selection.
- S6 — Scope is limited to the affected runtime specs, shared rules, PR-review guidance, and source-version fixture. No application implementation, dependency, permission, destination, legacy plan/story, or historical record change is authorized. DEBT-017 and DEBT-018 remain open and nonblocking; this feature neither resolves nor ignores them.
- S7 — Each edited runtime advances by the applicable SemVer and the source-version fixture aligns. Verification includes independent Sentinel review with zero open findings, ODD validation, and the whole suite when a test-file edit applies. No PASS or completion claim precedes those checks.

## Tasks

- T1 | S5, S6 | Cipher 🔓 (Lead Orchestrator): inventory and classify findings 4–11 with exact files, owners, and user-decision boundaries before further edits | done | commit: 4baaae41c6dbec9ae6db27e6f664567e7eb8a85e
- T2 | S2 | Marshal 🎖️ (HR Director): align Warden and Herald dependency-gate authority; Cipher documents, user decides | done | commit: 4baaae41c6dbec9ae6db27e6f664567e7eb8a85e
- T3 | S3, S4 | Marshal 🎖️ (HR Director): encode zero-open-findings PASS and fix-first disposition in shared review/report guidance and affected reviewer specs | done | commit: 4baaae41c6dbec9ae6db27e6f664567e7eb8a85e
- T4 | S5 | Marshal 🎖️ (HR Director): apply the bounded fixes or decision stops for findings 4–11 | done | commit: 4baaae41c6dbec9ae6db27e6f664567e7eb8a85e
- T5 | S1, S7 | Forge 🔨 (Implementer): align the source-version fixture after approved runtime versions; Crucible 🔥 (Test Architect) and Bastion 🧱 (Backend & Scripts Architect) review the test-file edit | done | commit: 4baaae41c6dbec9ae6db27e6f664567e7eb8a85e
- T6 | S3, S4, S7 | Sentinel 🛡️ (Quality Guardian): independent combined audit; require zero open findings | done | commit: 4baaae41c6dbec9ae6db27e6f664567e7eb8a85e
- T7 | S7 | Cipher 🔓 (Lead Orchestrator): validate, record evidence, and close only after T6 returns zero open findings | done | commit: 4baaae41c6dbec9ae6db27e6f664567e7eb8a85e

Allowed status: open, in progress, done. `pending` is valid for open or in-progress work. A task marked done must cite its completed work-unit commit. A feature closes only when every task is done and committed.

## Log

- L1 — "i think is time to amke a full review of all the agents"
- L2 — "ok start 1 by 1"
- L3 — "i agree with u but this is aligned with ODD workflow?"
- L4 — "wait there if any of these are detected maybe the finall result should not be PASS, can we define a PASS is a 0 findings?"
- L5 — "nice, i agreed, next steps?"
- L6 — "continue"
- L7 — Decision: fix-first does not bypass ODD. A real in-scope fix stays inside its authorized task; a new requirement or shared policy change is tracked under this feature; out-of-scope work stops and reports. Severity is a release gate, not a substitute for remediation.
- L8 — Decision: PASS is reserved for zero open findings. Fixed findings remain audit history; deferred findings produce ADVISORY, not PASS. Observations with no required action remain notes.
- L9 — Audit evidence accepted from full-roster-review/read-only-1: 11 defects, 3 decision/authority boundaries, all 16 runtime specs and 17 profiles reviewed. Findings 1–2 are accepted small predecessors; findings 3–11 are governed here. This document was created before the first non-small correction.
- L10 — Final independent audit returned zero open findings across the 15-file candidate and root runtime. Findings 1–11 are resolved; dependency BLOCK has no agent override, ADVISORY is fix-first with user authority, PASS requires zero open findings, and fix-first disposition is recorded in shared guidance. The root `AGENTS.md` naming corrections advanced it to `3.0.5`; no fixture entry applies to the root. The reviewed whole suite passed: `738 passed in 5.60s`.
- L11 — DEBT-017 and DEBT-018 remain open and nonblocking; this feature neither resolves nor ignores them. No application implementation, dependency, permission, destination, legacy plan/story, or historical record change is included. Publication remains separately authorized.
- L12 — Close: T1–T7 completed in work commit `4baaae41c6dbec9ae6db27e6f664567e7eb8a85e`. Final Sentinel audit reports zero open findings across the 15-file candidate and root runtime; Crucible test architecture passed; exact suite `uv run --frozen --group dev pytest -q` exited 0 with `738 passed in 5.60s`; ODD validation must be rerun on this closed record before publication. Root `AGENTS.md` is 3.0.5; 12 agent versions and the 16-entry fixture align. No push, PR, merge, or tag performed.
