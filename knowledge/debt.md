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
**Open debts: 4.**

### DEBT-007

- **ID** — `DEBT-007`
- **Date** — 2026-10-18
- **Description** — The forbidden-AI-attribution matcher's literal token set is not recorded in any repository-readable surface, so the exact-token attribution scan cannot be reproduced from the checkout; PR reviews fall back to a conventional attribution-token scan.
- **Direct evidence** — PR #70 review at head `b82cdcad04c51eb0b5c3eeae78f2db651b75f88c` (finding 1): the matcher's tokens are defined outside every readable repo surface (`inquisitor.md` keeps them external; `herald.md` carries policy prose only); the conventional scan over both commit subjects and full message bodies, the PR title and body, and all four changed-file bodies returned zero matches.
- **Resolution criteria** — The approved matcher's literal token set is recorded in a repository surface the reviewing role can read, and the exact-token scan runs and is documented at a PR head.
- **Explicit deferral decision** — 2026-10-18 — user directed "add them as debts"; deferred at the PR #70 review by Inquisitor 🔎 (PR Reviewer), adjudicated `defer-to-debt` by Cipher 🔓 (Lead Orchestrator).

### DEBT-008

- **ID** — `DEBT-008`
- **Date** — 2026-10-18
- **Description** — `user-stories/core-sync.md`'s 2026-10-18 revision entry states "AC24's promise, mark, and Proof unchanged" beside the documented form-only Proof correction (verdict date removed from the Proof line); the wording could distinguish value stability from the recorded form change.
- **Direct evidence** — PR #70 review at head `b82cdcad04c51eb0b5c3eeae78f2db651b75f88c` (finding 2): the form-only correction is documented in the adjacent entry; no criterion, promise, mark, or verdict value changed.
- **Resolution criteria** — The wording is aligned at the next `core-sync` story revision so the entry distinguishes promise/mark/verdict-value stability from the recorded form correction.
- **Explicit deferral decision** — 2026-10-18 — user directed "add them as debts"; deferred at the PR #70 review by Inquisitor 🔎 (PR Reviewer), adjudicated `defer-to-debt` by Cipher 🔓 (Lead Orchestrator).

### DEBT-009

- **ID** — `DEBT-009`
- **Date** — 2026-10-18
- **Description** — The read-only Git inventory request included a command variant incompatible with configured allow/deny rules; the initial blocker report omitted the command/rule analysis, and the coordinator unnecessarily escalated to the user instead of investigating accessible configuration evidence. Process remediation is deferred.
- **Direct evidence** — In session `ses_eaf5afdb2ffeZ02v46nXo4cMVG`, a compound shell request including `git stash list --format='%gd%x09%H%x09%gs'` returned `permission.rejected: Permission denied: shell`. `opencode.jsonc:123` denies `git stash *`; line 140 allows only exact `git stash list`; the broad shell allow at line 55 does not override the later matching deny. The corrected, explicitly allowed `git stash list` returned exit 0 with empty output, and refreshed safety inventory/collision checks passed without configuration edits. The tool did not identify the exact denied scanner resource. hipótesis: the formatted stash variant explains the aggregate rejection based on the configured rules and corrected run; this is not an independently logged scanner verdict.
- **Resolution criteria** — (1) Read-only Git dispatches verify exact command variants against effective available permission rules before execution. (2) Blockers report the exact failed invocation, literal error, and matching rule, or explicitly state that the rule is unknown. (3) The coordinator investigates accessible evidence before requesting new permissions or user intervention. (4) Recorded verification demonstrates that permitted bare stash inventory succeeds and disallowed variants remain blocked, without weakening permissions.
- **Explicit deferral decision** — 2026-10-18 — user instructed "add that as a debt"; Cipher 🔓 (Lead Orchestrator) accepted process remediation as deferred/nonblocking for the current skill-authoring scope. No permission or configuration change was authorized.

### DEBT-010

- **ID** — `DEBT-010`
- **Date** — 2026-10-18
- **Description** — The concise-skill-authoring reviews and coordinator acceptance returned a false PASS: they claimed behavior preservation and environment neutrality while the creator rewrite narrowed source-retention choices, omitted helper-transfer safeguards and metadata type validation, and introduced a source-specific Python runner. Fixing these implementation defects does not establish that the review process itself has been repaired.
- **Direct evidence** — Skill review `csa-skills-reviewer-2` (session `ses_eaf19dd8dffedsmEhILrLWNABY`) and final audit `sentinel-final-1` (session `ses_eaf168309ffeB90vpw49s4e9cC`) returned `[PASS]` on creator SHA256 `4aa439786cc1e30537f03477a322c04c21c6e87cdcfd8e744deba66f5200350c`; Cipher 🔓 (Lead Orchestrator) reported fully verified execution. Fresh review `vault-recheck-2` (session `ses_eaef823f6ffeny9xtUFWtkkTFf`) returned `[FAIL]` with four introduced defects after `herald-recheck-1` (session `ses_eaef8241dffeonMfFgUqx5iGUe`) compared the complete original at `af36e6cddd37079abdf043c8835df6d154f260d5` with that candidate. The original creator permitted delete/archive/keep cleanup, explicitly transferred helpers and validated string-valued metadata; it did not contain the added UV binding. The separate archived-plan discovery omission predates this rewrite and is not one of the four introduced defects. These returns establish the missed defects, not an independently proven cause of the review failure.
- **Resolution criteria** — (1) Agree and record a bounded correction to the review/acceptance process requiring original-to-candidate obligation accounting and source-neutrality checks for instruction rewrites. (2) Exercise that correction against cases covering retention choices, helper assets, invalid metadata types and source runner leakage; record expected and observed review verdicts on identified inputs. (3) Obtain an independent review of the process correction and its evidence before retiring this debt. Implementation repair alone does not clear it.
- **Explicit deferral decision** — 2026-10-18 — user instructed "addctthat error as a debt then fix" after the fresh failed double-check. Cipher 🔓 (Lead Orchestrator) records the false-PASS process failure as separate follow-up debt, nonblocking for the bounded implementation repair. The four implementation defects themselves remain blocking until fixed and independently verified. No permission, roster, Git or release change is authorized by this record.

**ID to use for the next new debt:** `DEBT-011`. This is an allocation counter, not an open debt.
<!-- project:end -->
