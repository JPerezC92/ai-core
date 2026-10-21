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
**Open debts: 2.** The DEBT-008/009/010 deletion made in clearing commit `5eed3317…` is recorded as **provisional**, not a settled retirement; see the standing-condition record in `user-stories/plan-lifecycle-governance.md`.

### DEBT-007

- **ID** — `DEBT-007`
- **Date** — 2026-10-18
- **Description** — The forbidden-AI-attribution matcher's literal token set is not recorded in any repository-readable surface, so the exact-token attribution scan cannot be reproduced from the checkout; PR reviews fall back to a conventional attribution-token scan.
- **Direct evidence** — PR #70 review at head `b82cdcad04c51eb0b5c3eeae78f2db651b75f88c` (finding 1): the matcher's tokens are defined outside every readable repo surface (`inquisitor.md` keeps them external; `herald.md` carries policy prose only); the conventional scan over both commit subjects and full message bodies, the PR title and body, and all four changed-file bodies returned zero matches.
- **Resolution criteria** — The approved matcher's literal token set is recorded in a repository surface the reviewing role can read, and the exact-token scan runs and is documented at a PR head.
- **Explicit deferral decision** — 2026-10-18 — user directed "add them as debts"; deferred at the PR #70 review by Inquisitor 🔎 (PR Reviewer), adjudicated `defer-to-debt` by Cipher 🔓 (Lead Orchestrator).

### DEBT-011

- **ID** — `DEBT-011`
- **Date** — 2026-10-19
- **Description** — Plan completion and its independent audits return a passing verdict while material requirement, evidence and ownership defects remain; a user-requested double check after completion repeatedly finds them. Interpretation, not an established cause: the completion gate appears to prove shape, presence and internal consistency more reliably than it proves original-obligation accounting completeness, evidence durability outside temporal surfaces, shared/project separation, and live test-plan evidence. Confirming or refuting that reading is part of resolving this debt.
- **Direct evidence** — Plan `debt-review-reliability-20261019` was marked `Status: completed` with `## Audit` `[PASS]` (completion audit `dr-sentinel-completion-1`, final-snapshot review `dr-sentinel-final-1`), and PR #72 review returned `[PASS]` at head `5eed331724756921e56bc9b91a8014855a1e2502`. The user then requested a double check; adversarial re-review of that same head found six open findings: (1) the AC37 accounting covered only original anchor excerpts, not the complete original (`user-stories/plan-lifecycle-governance.md:133` against `output/audits/debt-010-review-cases.md:152-168`); (2) the constructed case inputs and deterministic deltas survived only in gitignored `output/`, not in durable project evidence, although the phase runbook required them; (3) the "exact failed invocation" evidence names one command inside an unspecified compound request (`output/audits/debt-009-inventory.md:51`), below AC36's bar; (4) shared `## Proof` carried source-local run claims, violating the shared/project separation rule; (5) the source-neutrality conclusion was unsupported — the raw-shipped `op-skill-creator` mandated `license: MIT` and `compatibility: opencode` **at head `5eed331724756921e56bc9b91a8014855a1e2502`** (since corrected at source) while the report recorded no mandated local policy value; (6) the PR test plan carries five unchecked items and no `## Test evidence` section, which the PR-review rules state cannot yield `[PASS]`. The same pass surfaced a real unaccounted obligation narrowing: the original limits applied to total words and to `SKILL.md` lines, while the candidate applies both to the body only. **Interpretation, not an established cause:** this appears to follow the false-PASS pattern already recorded historically under DEBT-010, whose implementation repair did not establish process repair. Confirming or refuting that reading is part of resolving this debt. **Durability note:** the file and line references in this evidence entry were correct when written but point at mutable working content and at gitignored `output/` reports; the authoritative record is the reviewed content bound at PR #72 head `5eed331724756921e56bc9b91a8014855a1e2502`, and any reference that no longer resolves there must be re-derived before it is relied upon.
- **Resolution criteria** — (1) Record a bounded completion-verification procedure that, before a plan is reported complete, requires an adversarial pass over the actual original and candidate content and over the delivered evidence, checking original-obligation accounting completeness, evidence durability in a non-temporal surface, shared/project separation, source-neutrality under its stated boundary, and live test-plan evidence — not shape, presence, or self-attestation. (2) Exercise that procedure against at least the six failure classes named above and record expected and observed verdicts on identified inputs. (3) Obtain an independent review of the procedure and its evidence by a reviewer that authored neither. (4) Demonstrate on a later completed plan that a user-requested double check returns no requirement, evidence, ownership or test-evidence defect, or that the procedure caught the defect before completion was claimed. Correcting the individual findings from the 2026-10-19 double check does not by itself clear this debt.
- **Explicit deferral decision** — 2026-10-19 — user directed "add as a debt the next always when u complete a plan and i tell u to make a double check u found issues"; Cipher 🔓 (Lead Orchestrator) records the recurring false-completion process failure as a separate follow-up debt, nonblocking for the bounded rework of PR #72. No permission, roster, Git or release change is authorized by this record.

**ID to use for the next new debt:** `DEBT-012`. This is an allocation counter, not an open debt.
<!-- project:end -->
