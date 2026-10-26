# PR evidence format

> Canonical body format for every pull request: findings, test evidence, open debt, and the closing verdict. `git-pr` writes the initial draft; the designated post-review evidence writer (Inquisitor 🔎 (PR Reviewer) when the roster is installed) alone updates these sections. The presentation never varies per PR.

## Assembly order

1. `## Summary` — why the change exists.
2. `## Breaking changes` — only when the skill's breaking-change trigger applies, before the test plan.
3. `## Test plan` — what will be checked, as checkboxes.
4. `## Findings / blockers` — review dispositions.
5. `## Test evidence` — post-review only; present when at least one item is checked.
6. `## Open debt` — only when an authorized follow-up exists.
7. Verdict line — post-review only, last line of the body.

Each fact appears once. Summary explains why; Test plan states what will be checked; Findings records dispositions; Test evidence records observations; Open debt records authorized follow-ups; the verdict states release readiness. Never restate a table in prose.

## Initial draft

```markdown
## Summary
- what changed and why

## Test plan
- [ ] action and observable expected result
- [ ] edge case or regression and its expected result

## Findings / blockers
No review findings yet.
```

`No review findings yet.` is literal. It means review has not run; it is not a finding and not a verdict. Summary keeps at most three one-line bullets; the test plan keeps at least two executable items.

## Findings / blockers

After review, replace the placeholder with the mandatory table, or with the literal `No findings.` when the review produced no findings.

| ID | Severity | Status | Evidence | Owner / resolution |
|---|---|---|---|---|
| F1 | `BLOCK` | `OPEN` | path:line — short literal result | owner — next action |

Rules:

- One row per finding. IDs are `F1`, `F2`, ... in discovery order; stable across rounds; never renumbered or reused.
- Severity is `BLOCK` or `ADVISORY`; it records the assessed severity at review and does not change with status. An INFO observation is a note in the review round summary, not a finding: no row and no gate effect.
- Status is exactly `OPEN`, `IN PROGRESS`, `FIXED`, `DEFERRED`, or `REJECTED`. No other status exists; `IGNORE` is never a disposition.
- `OPEN`, `IN PROGRESS`, and `DEFERRED` are open. Any open row prevents `[PASS]`, regardless of severity.
- `OPEN` and `IN PROGRESS` name the owner and the next concrete action; no finding row is ownerless.
- `FIXED` names the remediation and the party that verified it, and its Evidence names the verified fix evidence, not only the original finding location. Fixed rows stay visible; never delete, hide, collapse, or downgrade a row.
- `DEFERRED` requires explicit user authority and names its destination in Owner / resolution; the same finding is listed under Open debt.
- `REJECTED` means not a defect and requires a mechanically decidable refutation; a judgment-dependent false finding goes to the user, not `REJECTED`. Keep the short literal refutation result in Evidence; the review round summary keeps the full literal output.
- A finding persists across rounds with its status until `FIXED` or `REJECTED`. A new finding invalidates a prior `[PASS]`.
- Evidence is concise: `path:line`, a short literal result, or a named evidence artifact. No dumps, logs, or multi-paragraph cells.

When the review produced no findings:

```markdown
## Findings / blockers
No findings.
```

## Test plan

- Use `- [ ]` checkboxes; prose test plans are forbidden.
- Keep at least two concrete, executable items. The section is mandatory and never empty; an empty test plan blocks the PR.
- Each item names the exact action and its observable expected result.
- Keep `- [ ]` until the matching evidence row and tick are persisted together at the reviewed head. Never write `- [x]`, a result, or a claim that something ran in the initial draft.
- A checked item's text is its evidence key. Never reword a checked item; rewording invalidates its row and requires re-verification.

## Test evidence

Post-review only, at the current immutable head. Omit the section until at least one item is checked.

Header, in this order:

```markdown
## Test evidence
- PR: `#<number>`
- Immutable head SHA: `<headRefOid>`
- Base: `<base-ref>`
- Scope command: `git diff "<base-ref>"...<head-sha>`
```

Then the mandatory table:

| Test-plan item | Literal action/input | Observed result | Executor |
|---|---|---|---|
| exact checkbox text | exact executed command, or exact manual action/input | verdict-only observed result | actual person or agent |

Rules:

- The header block is part of every row's evidence: each row is bound to that PR number, immutable head, base, and scope command. Never repeat those values per row, and never accept a row without that binding.
- Every checked item has exactly one row. No checked item lacks a row, and no item has two rows. Re-running an item at the same head updates its one row.
- Copy the test-plan item verbatim. Never paraphrase or renumber it.
- Literal action/input is the exact command that ran. When a command consumed input, record the command and the input in that cell. When no command ran, record the exact manual action or input. Never invent a command, and never add a command field for a manual check.
- Observed result is the human-readable verdict only: for a test run, the pass/fail summary line and the exit code where relevant. Never progress bars, per-test dots, stack traces, raw dumps, or source bodies. Full logs stay outside the body.
- Executor is the actual person or agent that performed the check, never the body writer by default. CI records its workflow or run identifier.
- Record literal values: the base ref, the head SHA, and the scope command with that base and head. Never write the `$BASE` token.
- One head only. A changed head invalidates every row and tick; replace the block, re-verify every required item at the new head, and never mix heads or carry a stale row forward.
- A checked item's row records a passing verdict. A failed or unresolved check stays `- [ ]` and is recorded as a finding; it never appears as a passing row.
- Only author-evidenced N/A may exclude a required item. `manual` or `optional` alone never omits, ticks, or satisfies an item.

## Open debt

Only when a finding is `DEFERRED` or an authorized follow-up exists.

```markdown
## Open debt
- F2 — destination register entry, authorized by user on date
```

Every entry names its destination and the authority that permitted deferral. Open debt never replaces or hides the finding row. Omit the section when there is none; never write `None.`

## Verdict

The completed body ends with exactly one line:

```text
[PASS] — one-sentence basis
```

The same `[<VERDICT>] — basis` shape applies to all three tokens; an `[ADVISORY]` line also names the accepting user and date.

- `[PASS]` — zero open findings: `No findings.`, or every finding row is `FIXED` or `REJECTED`; every required (non-N/A) test-plan item is checked with a passing row; no required verification is unresolved.
- `[ADVISORY]` — every open finding is nonblocking `ADVISORY` severity (including a `DEFERRED` row the user accepted for release), the user's documented acceptance is named in the line, and all required verification is resolved.
- `[BLOCK]` — any open `BLOCK` severity finding; any unresolved required verification; any missing, invalid, or stale evidence; any unchecked required item; or an open nonblocking finding whose required user acceptance is not yet documented (the body is not release-ready until then).

Rules:

- The verdict line is absent from the initial draft. It is written only by the designated evidence writer at the atomic join, and only after any required user acceptance is documented.
- It states release readiness. It does not replace the reviewer's gate signal to the coordinator.
- Any new finding, changed head, or changed evidence invalidates a prior `[PASS]`; re-establish the body at the current head.

## Readability

- Keep every cell to one short phrase or literal; never a paragraph or nested list.
- Use inline code for commands, paths, SHAs, and status tokens.
- Escape a literal pipe in a cell as `\|`.
- Keep the mandated columns and order; do not add columns or HTML layout.
- Put detail in a named local audit artifact and cite it by path; never paste it into the body.
