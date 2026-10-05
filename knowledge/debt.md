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

## Register

### DEBT-001 — PR test-evidence observed output is unstandardized

- **ID:** DEBT-001
- **Date:** 2026-09-27
- **Description:** `## Test evidence` Observed output has no human-readable contract. Agents paste full runner stdout (pytest `-q` progress dots, traces, dumps). The useful signal is the verdict line.
- **Direct evidence:** PR #44 Test evidence for pytest at `c89a6e6698a52948cfbf3f62c8eb41f04383482e` recorded `........................................................................ [ 97%]` / `.. [100%]` plus `74 passed in 0.11s`. User rejected the dots as unhelpful. `git-pr` SKILL.md Post-PR evidence contract requires `<literal observed output>` with no verdict-only rule. Inquisitor 🔎 (PR Reviewer) and Herald 📯 (Release Manager) persist that same shape.
- **Resolution criteria:** `git-pr`, Inquisitor 🔎 (PR Reviewer), and Herald 📯 (Release Manager) require Observed output to be the human-readable verdict only (for pytest: `N passed in Xs`). Progress bars, per-test dots, stack traces, and raw dumps are forbidden unless the user asks for them. Clearing PR UPDATES `user-stories/git-pr-drafting.md`; do not CREATE a new story. That PR deletes this entry.
- **Explicit deferral decision:** User, 2026-09-27 — strip the dots from PR #44 now; standardize the contract later. Non-blocking for #44 merge.

### DEBT-002 — No delegated owner can execute Python pytest

- **ID:** DEBT-002
- **Date:** 2026-09-28
- **Description:** Phase 3 lacked a delegated Python runner, so Cipher 🔓 (Lead Orchestrator) ran the file-scoped test. The whole-suite role, project-level grant, and restarted delegated run are now verified. This entry remains open only until the user-authorized completing PR retires it.
- **Direct evidence:** Phase 3 Forge 🔨 (Implementer) returned `Pytest: not run — Forge Bash permission excludes this command`; Cipher 🔓 (Lead Orchestrator) ran the earlier file-scoped command with `60 passed in 5.12s`. After restart, Crucible 🔥 (Test Architect) ran `uv run --frozen --group dev pytest -q` with exit 0 (`304 passed in 14.10s`), test architecture `[PASS]`. A historical `313 passed` figure recorded under a plan that was later superseded is retained as history only, not as current evidence.
- **Resolution criteria:** Crucible 🔥 (Test Architect) is the delegated test runner. Each project's root `opencode.jsonc` holds `agent.crucible.permission.bash` for that project's reviewed commands; Crucible's shared agent spec has no executable grant. AICore's own grant is its reviewed UV pytest command. After OpenCode restart, Crucible runs the declared command with exit 0 and persistent verdict-only evidence. Clearing PR UPDATES Crucible 🔥 (Test Architect), Warden 🔒 (Dependency Warden), Inquisitor 🔎 (PR Reviewer), `plan-enforce`, `python-pytest`, and the project config contract, then deletes this entry.
- **Explicit deferral decision:** User, 2026-09-28 — record now and continue the destination synchronization plan. Non-blocking for G3-G5.

### DEBT-003 — Cipher escalated internally decidable test-file scope

- **ID:** DEBT-003
- **Date:** 2026-10-01
- **Description:** Cipher 🔓 (Lead Orchestrator) asked the user whether two test files should move into Phase 2 after an audit assertion, pausing implementation. File ownership and actual defect scope should have been inspected and decided internally.
- **Direct evidence:** The user identified that Cipher's question stopped work while awaiting a response, although the phase assignments and affected files were available for inspection in the repository.
- **Resolution criteria:** Before escalating phase placement, Cipher 🔓 (Lead Orchestrator) verifies the file's ownership and actual defect scope from repository evidence. User-facing questions are reserved for decisions that cannot be resolved from available evidence. The clearing PR updates applicable orchestration guidance and deletes this entry.
- **Explicit deferral decision:** User, 2026-10-01 — record this process error and continue the work. Non-blocking for the adoption reconciliation goals.

### DEBT-004 — Evidence-bounded finding admission and scope control

- **ID:** DEBT-004
- **Date:** 2026-10-05
- **Description:** Deferred PROCESS improvement to `plan-enforce`: make finding admission evidence-bounded and prevent supplemental concerns or fixture-only fixes from silently expanding the confirmed scope. This is not a waiver of actual adoption safety blockers.
- **Direct evidence:** In the session described by the user, `OrderedBootstrapAcceptanceTests._preflight` in `.opencode/skills/sync-aicore-adoption/scripts/test_adoption_apply.py` was discussed as proof of production migration gating. That method is a test-driver helper; production `adoption_git._GitRepo` in the same scripts directory is a read-only Git object/snapshot reader, while the migration skill instructs destination mutation. Later static audit attributed missing `BISECT_START` handling to an unsaved-work `[BLOCK]`, although bisect can have a clean worktree and protocol-v2 §5 prohibits in-progress merge/rebase/cherry-pick/revert, not bisect. Repeated local fixes enlarged the test-only gate instead of finishing one end-to-end boundary. `.opencode/skills/plan-enforce/SKILL.md` **Simplicity discipline** and `references/_consistency-checklist.md` analysis rules constrain scope but lack an explicit actor/policy/goal/expected-versus-observed/production-versus-fixture finding-admission packet. These are source facts and user-reported session evidence, not evidence that adoption was executed or safety defects were fixed.
- **Resolution criteria:**
  - The `plan-enforce` skill, consistency checklist, and appropriate phase template require each admitted finding to identify its confirmed goal, normative clause, actual responsible actor and shipped path versus helper/fixture, expected versus observed behavior, affected scope, reproduction or precise static fact, severity and literal output, and an explicit keep/fix/reject-scope decision.
  - Review distinguishes an actual requirement defect, documentation drift, and a supplemental concern. No speculative blocker or implicit new goal, matrix, or compatibility obligation is admitted. Audits judge the complete flow once, rather than treating repeated helper-only fixes as end-to-end proof; unresolved source safety remains blocking. No semantic automated classifier is introduced.
  - The clearing PR UPDATES existing `user-stories/plan-enforce.md` (does not CREATE another story), applies reviewed applicable repository rule/template changes, and deletes this entry in that same PR. Its body and commit carry resolution evidence: criteria met, validation and audit results, per the register rules.
- **Explicit deferral decision:** User, 2026-10-05 — current request: 'add those errors as debt to improve the plan enforce skill and then upgrade the plan'. Defer only the skill/process upgrade, not current Git safety fixes or their approval gates. This process debt does not waive current G5/G8 obligations or unresolved adoption safety blockers; no release is authorized.

### DEBT-005 — Dispatch and completion evidence is incompletely enforced

- **ID:** DEBT-005
- **Date:** 2026-10-05
- **Description:** Deferred PROCESS improvement to `plan-enforce`: enforce the required verbatim dispatch packet and evaluate distinct, current completion evidence before reporting completion. Suite execution success and an audit's valid shape are not substitutes for applicable architecture verdicts or an evaluated completion audit.
- **Direct evidence:** `.opencode/skills/plan-enforce/SKILL.md` **Dispatch bundle contract** already requires verbatim Subject, all Goals, full phase runbook, and consumed prior-phase values. In the session described by the user, implementation prompts instead said 'read plan/file wins' with summarized bundles. After the last two fixes, Crucible 🔥 (Test Architect) explicitly reported 'No test files were submitted for rule audit ... Execution success is not an architecture pass', yet completion was reported from `503 passed`. The completed adoption plan's Audit retained 'planning readiness only/current interrupted' while its Status was completed: validator shape passed without an evaluated completion audit. Durable anchors are the skill's **Resume (completion)**, `references/_consistency-checklist.md` audit/acceptance-criterion sections, and `user-stories/plan-enforce.md`, whose current criteria include suite citations rather than establishing each actual layer. The checklist already requires execution exit 0 and a separate test-architecture `[PASS]`; it explicitly leaves audit quality and evidence-to-checkbox truth to analysis. The quoted session output is historical evidence of the process error, not a current suite run or proof of safety remediation.
- **Resolution criteria:**
  - Fail-closed orchestrator evaluation checks the complete required verbatim dispatch packet before dispatch; references to files or summarized bundles cannot substitute for it.
  - Completion separately evaluates current-snapshot applicable code architecture, test architecture, execution, and model/guidance reports, with their scopes and verdicts. Missing or adverse required evidence blocks completion; passing execution does not imply an architecture pass.
  - A current final completion audit evaluates the finished work and cannot reuse a planning-readiness audit. Adverse findings are adjudicated before goal/story checkmarks, Outcome, or archive; each acceptance claim must establish its actual applicable layer.
  - The clearing PR UPDATES existing `user-stories/plan-enforce.md`, applies reviewed applicable repository rule/template changes, and adds native mechanical tests only where true repetitive state can be validated. No evidence-framework expansion or prose-semantics enforcement in the validator. That same PR deletes this entry and carries resolution evidence (criteria met, validation and audit results) in its body and commit, per the register rules.
- **Explicit deferral decision:** User, 2026-10-05 — current request: 'add those errors as debt to improve the plan enforce skill and then upgrade the plan'. Defer only the skill/process upgrade, not current Git safety fixes or their approval gates. This process debt does not waive current G5/G8 obligations or unresolved adoption safety blockers; no release is authorized.
