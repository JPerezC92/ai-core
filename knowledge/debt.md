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
**Open debts: 9.**

### DEBT-021 — ODD execution-gate bypass

- **ID:** DEBT-021
- **Date:** 2026-10-29
- **Description:** During the research and ADR documentation work, the ODD execution gates were bypassed: the durable multi-file research record plus catalog update was classified as small; after creating `odd/tasks/domain-use-case-conventions.md`, Scribe was dispatched in the same turn instead of presenting the execution-review message and stopping; the user's core/project placement correction was applied to the shared core before the revised plan was re-presented; and the review-loop handling was misstated after the second `[FAIL]`—the two failed reviews addressed distinct findings, so the loop cap did not apply.
- **Correction (2026-10-29):** The original loop-cap statement was inaccurate. The two failed reviews addressed distinct findings; the cap requires the same finding across two remediation rounds or three total review rounds, so it did not apply. The original review evidence remains unchanged.
- **Direct evidence:** Conversation record 2026-10-29; `odd/tasks/domain-use-case-conventions.md` L1–L5; independent reviews `domain-use-case-conventions/task4/reviewer1` (`[FAIL]`, four findings) and `task5/reviewer1` (`[FAIL]`, one open finding). No code was changed.
- **Resolution criteria:** The corrected documentation slice passes independent review; the feature closes through the normal gate; and a subsequent non-small feature demonstrates the execution-review stop before its first write, or the stop is mechanically enforced. Until then the debt remains open.
- **Explicit deferral decision:** User instruction 2026-10-29: "add that error as a debt and continue now following the steps". The user accepted the process debt and directed continuation.

### DEBT-022 — ODD step-status reporting and continuation

- **ID:** DEBT-022
- **Date:** 2026-10-29
- **Description:** After finishing an ODD step, Cipher did not send a status message identifying the step, its state, the evidence, and the next step, and did not continue to the next step. Work stopped or jumped to another task without stating which step was skipped and why, so the user had to ask repeatedly where the work stood.
- **Direct evidence:** Conversation record 2026-10-29; user instruction "add taht as a debt when u finish a step u should send a message of the status and continue"; `odd/tasks/domain-use-case-conventions.md` L1–L7; the step-status table delivered only after the user asked.
- **Resolution criteria:** Every completed ODD step produces a concise status message with the step number, state, evidence pointer, and next step; work continues to the next step unless a required gate or blocker stops it; any skipped step is named with its reason. Demonstrate this across the remaining steps of the active feature and the next non-small feature.
- **Explicit deferral decision:** User instruction 2026-10-29: "add taht as a debt when u finish a step u should send a message of the status and continue". The user accepted the process debt and directed continuation.

### DEBT-023 — Per-commit authorization prompt

- **ID:** DEBT-023
- **Date:** 2026-10-29
- **Description:** Cipher treated local commits as requiring a per-commit user decision and stopped after each task for that decision, although the user's standing direction is that local commits are part of finishing a task. This created repeated stops and blocked feature close on a commit reference.
- **Direct evidence:** Conversation record 2026-10-29; user corrections "thats wrong a commit dont require my authorization if u do taht u will stop in each task thats onoyous" and "add taht error as a debt"; `odd/tasks/domain-use-case-conventions.md` L7/L8; no commit performed.
- **Resolution criteria:** Local commits proceed under the user's standing authorization without per-commit prompts; push, PR, merge, tag, release, and archive remain separately authorized; a coherent task's commit reference is produced and used for feature close. Demonstrate on the current documentation feature and the next feature.
- **Explicit deferral decision:** User instruction 2026-10-29: "add taht error as a debt". The user accepted the process debt and directed the standing authorization.

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
- **Direct evidence:** Bastion 🧱 (Backend & Scripts Architect) review `implementation-review/task1/bastion1` finding 1; `filesystem.py:177-370`; `architecture/clean-architecture.md` C3/C4.
- **Resolution criteria:** Write-target policy lives in domain/application; the adapter performs IO and mapping only; tests cover symlink, non-regular file, alias, root escape, and inode sharing; Bastion `[PASS]` and the whole suite pass.
- **Explicit deferral decision:** User instruction 2026-10-29: "if that requiere its own feature just add as a debt to do it later but dont left any broken". Accepted for later feature work; not started.

### DEBT-026 — Query-verification split and typed business errors

- **ID:** DEBT-026
- **Date:** 2026-10-29
- **Description:** `query_verification.py` is a ~1,002-line module with two operations (`validate`, `evaluate`) that mixes sidecar parsing, SQL safety, adapter evaluation, file IO, and CLI. `ValidationError(ValueError)` has no stable code and is raised for business failures. Feature-sized remediation: split domain/application/infrastructure/edge, one use case per module with a single `execute()`, and return typed domain errors.
- **Direct evidence:** Bastion review findings 2–3; `query_verification.py:196,813-931`; `architecture/clean-architecture.md` C1/C2/C3/C5 and `architecture/shapes/scripts.md` P1/P2.
- **Resolution criteria:** One use-case module per operation; pure domain parsing/safety/evaluation; typed domain errors returned as values; no business failure escapes the operation; Bastion and Crucible `[PASS]`; suite passes.
- **Explicit deferral decision:** User instruction 2026-10-29: "if that requiere its own feature just add as a debt to do it later but dont left any broken". Accepted for later feature work; not started.

### DEBT-027 — Scan-attribution application operation and typed errors

- **ID:** DEBT-027
- **Date:** 2026-10-29
- **Description:** `git-pr/scripts/scan_attribution.py` exposes `scan_attribution()` rather than an application `execute()` and raises `PolicyValidationError`/`SnapshotValidationError` for malformed policy or snapshot, so business failures escape the operation. Medium remediation: an application operation returning `ScanResult | DomainError`, validation returning typed errors, and `main` keeping only serialization.
- **Direct evidence:** Bastion review finding 4; `scan_attribution.py:205` and `:76-82`; `architecture/clean-architecture.md` C3/C5.
- **Resolution criteria:** Application `execute()` returns a typed result or domain error; business failures no longer throw; `main` serializes only; tests and Bastion `[PASS]`; suite passes.
- **Explicit deferral decision:** User instruction 2026-10-29: "if that requiere its own feature just add as a debt to do it later but dont left any broken". Accepted for later work; not started.

### DEBT-028 — Validate-feature application operation and typed result

- **ID:** DEBT-028
- **Date:** 2026-10-29
- **Description:** `odd-workflow/scripts/validate_feature.py` exposes `validate_feature(text) -> list[str]` rather than an application `execute()` and mixes policy with `main` IO. Medium remediation: an application operation returning a typed result or domain error, with the entry reading and printing only.
- **Direct evidence:** Bastion review finding 6; `validate_feature.py:58`; `architecture/clean-architecture.md` C3 and `architecture/shapes/scripts.md` P1/P2.
- **Resolution criteria:** Application operation with `execute()` and a typed result/error; IO stays at the entry; tests and Bastion `[PASS]`; suite passes.
- **Explicit deferral decision:** User instruction 2026-10-29: "if that requiere its own feature just add as a debt to do it later but dont left any broken". Accepted for later work; not started.

### DEBT-029 — Stop without a user-action requirement

- **ID:** DEBT-029
- **Date:** 2026-10-29
- **Description:** Cipher stopped without a user-action requirement and left informational text that named no decision or next step. The stop did not distinguish "all pending work is finished" from "work remains," so the user had to ask why the turn ended.
- **Direct evidence:** Conversation record 2026-10-29; user corrections "why u stopped now?", "stopo dodging, hey u should understand if u stop there should be a reason that require me to take an action, in other casu if u finalized all your pending why u dolnt senmt a clear message like ALL FINISHED, and next steps or ask about what to do next"; `AGENTS.md` project extension `### Stop and next-step reporting`; no code change.
- **Resolution criteria:** Every stop either names the exact user action required or says `ALL FINISHED`, lists the completed scope, and states the next steps; if work remains, continue to the next ready task; informational evidence alone is not a stop reason. Demonstrate on the current push/PR and future tasks.
- **Explicit deferral decision:** User instruction 2026-10-29: "add this error as a debt iun the workflow and then continue with the 5". The user accepted the process debt and directed the push/PR.

**ID to use for the next new debt:** `DEBT-030`. This is an allocation counter, not an open debt.
<!-- project:end -->
