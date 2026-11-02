<!-- core:begin -->
# Accepted Debt Register

Records of deferred technical or process debt that are **non-blocking** for release.

## Entry format

Each entry MUST include:

- **ID** — unique identifier (e.g. `DEBT-001`)
- **Date** — when the deferral decision was made
- **Description** — what is deferred
- **Direct evidence** — the evidence that justifies deferral
- **Resolution criteria** — what must be true for the debt to be cleared
- **Explicit deferral decision** — who decided, and when

## Rules

- An accepted debt is nonblocking only when its record here carries direct evidence, resolution criteria, and an explicit deferral decision (see Herald 📯 (Release Manager) spec).
- Disclose the ID and unresolved criteria in any operation report that touches it.
- Clear and retire a debt in the same PR: the PR that clears a debt deletes its entry from this register, and its body and commit carry the Resolution evidence (criteria met, validation and audit results). Git history is the permanent record for retired entries; this register holds open debts only. Never open a dedicated PR whose sole purpose is pruning cleared entries — each debt is retired by exactly one PR: its clearing PR.
- **ID allocation.** Each register owns an independent monotonic ID sequence; IDs are never shared across projects or registers. Allocate the next ID as the current high-water plus one, read from this register's own recorded next-ID value — never recomputed from the currently open entries, because retiring an entry erases the maximum and would reuse an issued ID. Gaps are valid history: never refill one, and never reuse a retired ID. If the register has no recorded next-ID, bootstrap it once from the highest identifier ever present in this register's verified history; when that history is unavailable, truncated, or renamed, stop and report the gap instead of guessing a starting value.

## Register
<!-- core:end -->

<!-- project:begin -->
**Open debts: 7.**

### DEBT-022 — ODD step-status reporting and continuation

- **ID:** DEBT-022
- **Date:** 2026-10-29
- **Description:** After finishing an ODD step, Cipher did not send a status message identifying the step, its state, the evidence, and the next step, and did not continue to the next step. Work stopped or jumped to another task without stating which step was skipped and why, so the user had to ask repeatedly where the work stood.
- **Direct evidence:** Conversation record 2026-10-29; user instruction "add taht as a debt when u finish a step u should send a message of the status and continue"; `odd/tasks/domain-use-case-conventions.md` L1–L7; the step-status table delivered only after the user asked.
- **Resolution criteria:** Every completed ODD step produces a concise status message with the step number, state, evidence pointer, and next step; work continues to the next step unless a required gate or blocker stops it; any skipped step is named with its reason. Demonstrate this across the remaining steps of the active feature and the next non-small feature.
- **Explicit deferral decision:** User instruction 2026-10-29: "add taht as a debt when u finish a step u should send a message of the status and continue". The user accepted the process debt and directed continuation.

### DEBT-024 — Unnecessary stop and self-created boundary

- **ID:** DEBT-024
- **Date:** 2026-10-29
- **Description:** Cipher stopped after completing a task and justified it with "the task was finished," although finishing a task is the point at which the workflow continues. The stop was a choice, not a rule; Cipher also expanded the user's "add the debt" instruction into closing and committing the feature, then used that self-created boundary as the reason to stop.
- **Direct evidence:** Conversation record 2026-10-29; user corrections "WHY U STOPPED AGAIN? WHY U ARE NTO CLEAR ABOUT WHAT U WANT", "IT DONT JUSTIFY WHY U STOPPED, DONT DODGE IT", and "add that error as a debt, then continue"; `odd/tasks/domain-use-case-conventions.md` L9–L11 and commits `f7b5417`, `f659dcb`, `b77f9b5`, `e1ea9af`.
- **Resolution criteria:** After each completed task or step, Cipher reports status and continues to the next ready task without using task completion as a stop; scope expansion requires explicit user direction; any genuine stop names a concrete blocker or gate, not a self-created boundary. Demonstrate on the current rename and the next task.
- **Explicit deferral decision:** User instruction 2026-10-29: "add that error as a debt, then continue". The user accepted the process debt and directed continuation.

### DEBT-025 — Core-sync write-target policy in the infrastructure adapter

- **ID:** DEBT-025
- **Date:** 2026-10-29
- **Description:** `core_sync_pkg/infrastructure/filesystem.py` → `preflight_write_targets` decides symbolic-link, non-regular-file, alias, root-escape, and source-tree inode-sharing policy inside an infrastructure adapter. C3/C4 require policy in the application or domain. Feature-sized remediation: extract a pure domain policy over typed target facts, leave the adapter to collect resolved paths/inodes, and return typed errors from the use cases.
- **Direct evidence:** Bastion 🧱 (Backend & Scripts Architect) review `implementation-review/task1/bastion1` finding 1; `filesystem.py:177-370`; `architecture/implementation/architecture.md` C3/C4.
- **Resolution criteria:** Write-target policy lives in domain/application; the adapter performs IO and mapping only; tests cover symlink, non-regular file, alias, root escape, and inode sharing; Bastion `[PASS]` and the whole suite pass.
- **Explicit deferral decision:** User instruction 2026-10-29: "if that requiere its own feature just add as a debt to do it later but dont left any broken". Accepted for later feature work; not started.

### DEBT-026 — Query-verification split and typed business errors

- **ID:** DEBT-026
- **Date:** 2026-10-29
- **Description:** `query_verification.py` is a ~1,002-line module with two operations (`validate`, `evaluate`) that mixes sidecar parsing, SQL safety, adapter evaluation, file IO, and CLI. `ValidationError(ValueError)` has no stable code and is raised for business failures. Feature-sized remediation: split domain/application/infrastructure/edge, one use case per module with a single `execute()`, and return typed domain errors.
- **Direct evidence:** Bastion review findings 2–3; `query_verification.py:196,813-931`; `architecture/implementation/architecture.md` C1/C2/C3/C5 and `architecture/implementation/shapes/scripts.md` P1/P2.
- **Resolution criteria:** One use-case module per operation; pure domain parsing/safety/evaluation; typed domain errors returned as values; no business failure escapes the operation; Bastion and Crucible `[PASS]`; suite passes.
- **Explicit deferral decision:** User instruction 2026-10-29: "if that requiere its own feature just add as a debt to do it later but dont left any broken". Accepted for later feature work; not started.

### DEBT-029 — Stop without a user-action requirement

- **ID:** DEBT-029
- **Date:** 2026-10-29
- **Description:** Cipher stopped without a user-action requirement and left informational text that named no decision or next step. The stop did not distinguish "all pending work is finished" from "work remains," so the user had to ask why the turn ended.
- **Direct evidence:** Conversation record 2026-10-29; user corrections "why u stopped now?", "stopo dodging, hey u should understand if u stop there should be a reason that require me to take an action, in other casu if u finalized all your pending why u dolnt senmt a clear message like ALL FINISHED, and next steps or ask about what to do next"; `AGENTS.md` project extension `### Stop and next-step reporting`; no code change.
- **Resolution criteria:** Every stop either names the exact user action required or says `ALL FINISHED`, lists the completed scope, and states the next steps; if work remains, continue to the next ready task; informational evidence alone is not a stop reason. Demonstrate on the current push/PR and future tasks.
- **Explicit deferral decision:** User instruction 2026-10-29: "add this error as a debt iun the workflow and then continue with the 5". The user accepted the process debt and directed the push/PR.

### DEBT-032 — Reviewer dispatched without prior coordinator self-verification

- **ID:** DEBT-032
- **Date:** 2026-10-31
- **Description:** On the same feature, Cipher 🔓 (Lead Orchestrator) dispatched the corpus auditor three times and re-gated an owner reviewer twice, each round verifying corrections that Cipher 🔓 (Lead Orchestrator) could and should have verified itself first. Findings raised by the audit were produced by Cipher's own bookkeeping — a `done` task without a commit reference, five specs missing acceptance clauses, a Log entry that merged a verbatim correction with its rationale, undated Log entries, a task ID in the `S#` column, an inaccurate line reference in a debt entry, and a delivery claim that predated the commits. Each round therefore measured the coordinator's proofreading rather than the reviewer's judgment, and the review loop went to its cap on a defect that a single self-check would have caught.
- **Direct evidence:** Conversation record 2026-10-31 including the user's correction "about sentinel stop just raising it without a double chek of the fixes i presume u were lefting issues and calling him again and again, verify for issues then when u are sure call him again"; Sentinel 🛡️ (Quality Guardian) audit rounds 1–3 for `odd/tasks/architecture-whole-file-distribution.md` (findings S1–S6, then the narrowed S2 plus missing acceptance clauses and merged Log entry, then F1–F2); Crucible 🔥 (Test Architect) rounds 1–2 (C1–C4, then C3/C4 verification). The failure recurred on the same day and is recorded here: a fourth audit round found five coordinator-authored defects, including that the project's own anatomy validator had not been run before the dispatch, which would have caught the bold spec/Log forms, the unlinked task spec, and the two-commit field in one pass.
- **Resolution criteria:** Before any owner-gate or audit dispatch, the coordinator runs its own mechanical verification of the candidate — document anatomy, acceptance-clause presence, Log separation and dating, evidence accuracy including file:line references, registry consistency, and the change's own observable predicates — and fixes what it finds. Reviewers are dispatched on a self-checked candidate, so their rounds judge substance rather than coordinator proofreading. Demonstrated on the next review dispatch of this feature and the next non-small feature.
- **Explicit deferral decision:** User instruction 2026-10-31: "about sentinel stop just raising it without a double chek of the fixes i presume u were lefting issues and calling him again and again, verify for issues then when u are sure call him again". The user accepted the process debt and directed self-verification before the next review dispatch.

### DEBT-036 — Herald's cleanup command form does not match the permission grant it relies on

- **ID:** DEBT-036
- **Date:** 2026-11-02
- **Description:** `herald.md` templates the post-merge remote deletion as `git push "$BASE_REMOTE" --delete "refs/heads/$BRANCH"`, with the refspec quoted, at `:111` and `:190`. The permission allow row is the literal `git push origin --delete refs/heads/*` at `opencode.jsonc:115`, which contains no quote character, so a quoted refspec cannot match it and instead satisfies the `git push origin * ?*` deny row at `:106`. On the PR #148 cleanup the quoted form was refused with a `permission.rejected` refusal and the identical unquoted command deleted the branch on its first attempt. The coordinator compounded this by reporting the cause as a missing multi-segment grant, an inference from a configuration comment that was never tested; the user rejected that diagnosis. The defect is command text, not permission coverage.
- **Direct evidence:** PR #148 merged as squash `53b1e6ea79a446388c2d70d9cfe097aaa39949eb`; cleanup preflight `verified_pr_cleanup.py 148 --base-remote origin --base-branch main` returned `SAFE_TO_CLEAN` with 35 of 35 checks; quoted attempt `git push origin --delete "refs/heads/docs/debt/cleanup-and-herald-push-grant"` returned `{"error":{"type":"permission.rejected","message":"Permission denied: shell"}}`; unquoted attempt `git push origin --delete refs/heads/docs/debt/cleanup-and-herald-push-grant` returned `- [deleted] docs/debt/cleanup-and-herald-push-grant`; `herald.md:111` and `:190`; `opencode.jsonc:106` and `:115`. Remote cleanups of multi-segment branches had succeeded earlier in the same session, which refutes the coverage theory.
- **Resolution criteria:** The documented cleanup command and the permission rows agree on one form, either by removing the quoting from the two `herald.md` templates or by an equivalent change that a later merged pull request's cleanup exercises without a permission refusal; the next post-merge cleanup deletes its remote branch on the first attempt in the documented form; no force, refspec or extra-argument capability is added; and a coordinator claim of a permission defect is backed by an executed test rather than by inference from configuration text.
- **Explicit deferral decision:** User instruction 2026-11-02, verbatim: "the problem is the documentation? add that as a debt". The user identified the documented command form as the defect and directed that it be registered as debt instead of fixed now.

**ID to use for the next new debt:** `DEBT-037`. This is an allocation counter, not an open debt.
<!-- project:end -->
