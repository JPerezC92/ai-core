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
**Open debts: 6.** The DEBT-008/009/010 deletion made in clearing commit `5eed3317…` is recorded as **provisional**, not a settled retirement; see the standing-condition record in `user-stories/plan-lifecycle-governance.md`.

### DEBT-011

- **ID** — `DEBT-011`
- **Date** — 2026-10-19
- **Description** — Plan completion and its independent audits return a passing verdict while material requirement, evidence and ownership defects remain; a user-requested double check after completion repeatedly finds them. Interpretation, not an established cause: the completion gate appears to prove shape, presence and internal consistency more reliably than it proves original-obligation accounting completeness, evidence durability outside temporal surfaces, shared/project separation, and live test-plan evidence. Confirming or refuting that reading is part of resolving this debt.
- **Direct evidence** — Plan `debt-review-reliability-20261019` was marked `Status: completed` with `## Audit` `[PASS]` (completion audit `dr-sentinel-completion-1`, final-snapshot review `dr-sentinel-final-1`), and PR #72 review returned `[PASS]` at head `5eed331724756921e56bc9b91a8014855a1e2502`. The user then requested a double check; adversarial re-review of that same head found six open findings: (1) the AC37 accounting covered only original anchor excerpts, not the complete original (`user-stories/plan-lifecycle-governance.md:133` against `output/audits/debt-010-review-cases.md:152-168`); (2) the constructed case inputs and deterministic deltas survived only in gitignored `output/`, not in durable project evidence, although the phase runbook required them; (3) the "exact failed invocation" evidence names one command inside an unspecified compound request (`output/audits/debt-009-inventory.md:51`), below AC36's bar; (4) shared `## Proof` carried source-local run claims, violating the shared/project separation rule; (5) the source-neutrality conclusion was unsupported — the raw-shipped `op-skill-creator` mandated `license: MIT` and `compatibility: opencode` **at head `5eed331724756921e56bc9b91a8014855a1e2502`** (since corrected at source) while the report recorded no mandated local policy value; (6) the PR test plan carries five unchecked items and no `## Test evidence` section, which the PR-review rules state cannot yield `[PASS]`. The same pass surfaced a real unaccounted obligation narrowing: the original limits applied to total words and to `SKILL.md` lines, while the candidate applies both to the body only. **Interpretation, not an established cause:** this appears to follow the false-PASS pattern already recorded historically under DEBT-010, whose implementation repair did not establish process repair. Confirming or refuting that reading is part of resolving this debt. **Durability note:** the file and line references in this evidence entry were correct when written but point at mutable working content and at gitignored `output/` reports; the authoritative record is the reviewed content bound at PR #72 head `5eed331724756921e56bc9b91a8014855a1e2502`, and any reference that no longer resolves there must be re-derived before it is relied upon.
- **Resolution criteria** — (1) Record a bounded completion-verification procedure that, before a plan is reported complete, requires an adversarial pass over the actual original and candidate content and over the delivered evidence, checking original-obligation accounting completeness, evidence durability in a non-temporal surface, shared/project separation, source-neutrality under its stated boundary, and live test-plan evidence — not shape, presence, or self-attestation. (2) Exercise that procedure against at least the six failure classes named above and record expected and observed verdicts on identified inputs. (3) Obtain an independent review of the procedure and its evidence by a reviewer that authored neither. (4) Demonstrate on a later completed plan that a user-requested double check returns no requirement, evidence, ownership or test-evidence defect, or that the procedure caught the defect before completion was claimed. Correcting the individual findings from the 2026-10-19 double check does not by itself clear this debt.
- **Explicit deferral decision** — 2026-10-19 — user directed "add as a debt the next always when u complete a plan and i tell u to make a double check u found issues"; Cipher 🔓 (Lead Orchestrator) records the recurring false-completion process failure as a separate follow-up debt, nonblocking for the bounded rework of PR #72. No permission, roster, Git or release change is authorized by this record.

### DEBT-012

- **ID** — `DEBT-012`
- **Date** — 2026-10-21
- **Description** — The release tooling generates working artifacts at the repository root and leaves them there. `git-commit` writes `commit.txt`, `git-pr` writes `pr-draft.md`, and the PR-body correction workflow wrote `pr73-body.md` and `pr73-body-new.md`. These are transient tool artifacts, not repository content; they should not be created in the root of a working tree and should not require manual deletion after every release.
- **Direct evidence** — Observed 2026-10-21 at the end of the PR #73 post-merge cleanup: `commit.txt`, `pr-draft.md`, `pr73-body.md` and `pr73-body-new.md` were present at the repository root and had to be removed manually. `.gitignore:8` and `.gitignore:9` list `pr-draft.md` and `commit.txt`, which confirms they are recognized non-content artifacts whose root placement is already known to be undesirable. `.gitignore` has no entries for the body-edit artifacts, so those appeared as untracked files. The release reports themselves recorded writing these paths at the repo root.
- **Resolution criteria** — (1) The generated release artifacts are written outside the repository root, to a machine-local or per-session artifact location, and the owning skill or workflow text is updated to say so. (2) A complete release run leaves no generated artifact at the repository root without manual deletion. (3) The `.gitignore` entries are reconciled with the new location, and obsolete root entries are removed rather than left as dead config. (4) The change is independently reviewed, and a later release run confirms a clean root.
- **Explicit deferral decision** — 2026-10-21 — user directed "delete the pr files u generated then and add as a debt creating them, they should not exist on the root"; Cipher 🔓 (Lead Orchestrator) records this as tooling-debris debt, nonblocking for release work. No permission, roster, Git or release change is authorized by this record.

### DEBT-013

- **ID** — `DEBT-013`
- **Date** — 2026-10-22
- **Description** — Cipher 🔓 (Lead Orchestrator) treated “a second active plan is not allowed” as a hard rule and blocked creating a plan for approved AC40/AC41 because `plans/agent-workflow-foundation-20261021` was already `Status: active`. That prohibition is not in the skill.
- **Direct evidence** — `.opencode/skills/plan-enforce/SKILL.md` `### Check for active plan` items 4–5: if one active plan exists, read it before showing it or dispatching Forge 🔨 (Implementer); if none exists, create; if multiple exist, stop and ask the user to select one. No item forbids a second active plan. The 2026-10-22 question offered “Keep foundation; park AC40/41”, “Complete/cancel foundation first”, and “User authorizes two actives (not recommended; conflicts with plan-enforce)” as if two actives were forbidden.
- **Resolution criteria** — (1) Operator guidance no longer states that a second active plan is forbidden. (2) Creating a new plan while another is active is allowed when the user selected a distinct task; the multiple-active case still requires the user to select which plan to show or resume. (3) Independent review of the corrected reading against the skill text.
- **Explicit deferral decision** — 2026-10-22 — user: “this is wrong A second active plan is not allowed. add as a debt”; Cipher 🔓 (Lead Orchestrator) records the false prohibition as nonblocking debt. No permission, Git, or release change is authorized by this record.

### DEBT-014

- **ID** — `DEBT-014`
- **Date** — 2026-10-22
- **Description** — After authorized delivery work, Cipher 🔓 (Lead Orchestrator) stops and waits (commit without close-out, close-out without the release PR, or a “not done / say when”) instead of continuing the remaining lifecycle: completion audit → Outcome → goal marks → archive → filesystem verify → release PR. The skip is recurrent.
- **Direct evidence** — 2026-10-22 on `close-out-before-done-claim-20261022`: (1) after phase 1, Cipher asked for release authorization while the plan was still active; (2) after user “u can commit”, Cipher reported SHA `4f2187f086d89caa49a140be0c9fcdeaf9614eb6` and stopped without close-out; (3) after user “hey what are u waiting for?”, Cipher archived then stopped again without opening the release PR. User: “AGAIN WHAT ARE U WAITING FOR? WHY U DONT CONTINUE THE WORKFLOW? U ARE MAKING THIS ERROR RECURTRENTLY ADD AS a DEBT”.
- **Resolution criteria** — (1) After user-authorized implementation, Cipher runs the remaining applicable lifecycle events in order without a new prompt to continue. (2) Archive-before-release still holds; a PR is opened only after archive, not instead of it. (3) Independent review of one later delivery that close-out and the release PR both happen without a “what are you waiting for” prompt.
- **Explicit deferral decision** — 2026-10-22 — user directed add as a debt; Cipher 🔓 (Lead Orchestrator) records the recurrent stop as nonblocking. This record does not replace continuing the current release PR.

### DEBT-015

- **ID** — `DEBT-015`
- **Date** — 2026-10-23
- **Description** — Cipher 🔓 (Lead Orchestrator) recommended merging PR #81 before PR #80 based on stale session context that said PR #80 was still open, without first checking live PR states or comparing the feature branch with current `main`. This gave the user an incorrect merge order and delayed identifying that PR #80 had already merged and PR #81 needed reconciliation.
- **Direct evidence** — In the conversation on 2026-10-23, Cipher 🔓 (Lead Orchestrator) said “merge #81 first” and described PR #80 as still open. Herald's subsequent live `gh pr view` evidence showed PR #80 `MERGED` at commit `06e3aff022abf67084cfb0c9e02ace97912d7364`; live `main` was at that same commit. PR #81 remained `OPEN`, based on `3fda46693831a1fcce60a7eec6ad34bb28907341`; GitHub reported `mergeable=CONFLICTING` and `mergeStateStatus=DIRTY`. The compare endpoint reported PR #81 one commit behind live `main`; `.opencode/agents/inquisitor.md` was the overlapping path.
- **Resolution criteria** — Before giving merge-order or readiness advice, inspect live metadata for every involved PR (state, base, head, merge commit, and mergeability) and the current base-branch SHA; compare each PR head against that live base, identify overlapping paths, and disclose whether the advice relies on current state. An independent review of a later merge-order recommendation must confirm it matches the captured live metadata.
- **Explicit deferral decision** — 2026-10-23 — user directed “and add as a debt the error u maded”; Cipher 🔓 (Lead Orchestrator) records the stale-state recommendation as a nonblocking process debt. This record does not authorize merging PR #81 or bypassing its refresh, validation, or review gates.

### DEBT-016

- **ID** — `DEBT-016`
- **Date** — 2026-10-24
- **Description** — Repository-authored Markdown uses curly quotation marks (U+201C/U+201D) and em dashes (U+2014), including inside verbatim user quotations and feature Log entries. The Gremlins VS Code extension flags these as dangerous characters, creating warning noise on otherwise valid documentation. The project has no approved Unicode policy for distinguishing legitimate punctuation from unsafe invisible/confusable characters.
- **Direct evidence** — In `odd/tasks/odd-classification-and-feature-scope.md` entry `L10`, the Gremlins extension flagged the curly quotes around the user's policy direction. A UTF-8 codepoint inspection of that entry returned `U+2014` and four `U+201C`/`U+201D` characters. The same punctuation style appears throughout existing project documentation and `knowledge/debt.md`.
- **Resolution criteria** — (1) Define the allowed character set for repository-authored prose, including curly quotes, em dashes, and verbatim user quotations. (2) Configure or document the Gremlins policy so legitimate punctuation is not reported as unsafe while genuinely dangerous invisible/confusable characters remain flagged. (3) Apply the policy to active documentation without altering the meaning or verbatim provenance of historical quotations. (4) Independently verify that editor/CI checks and repository content agree.
- **Explicit deferral decision** — 2026-10-24 — user: "i have a vscode plugin called gremlins, its telling me u are introducing dangerous characters ... add that as a debt"; Cipher 🔓 (Lead Orchestrator) records the policy/tooling mismatch as nonblocking documentation debt. This record does not authorize changing quoted user text, editor settings, or repository content.

**ID to use for the next new debt:** `DEBT-017`. This is an allocation counter, not an open debt.
<!-- project:end -->
