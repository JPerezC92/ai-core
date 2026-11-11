# PR evidence format

> Canonical body format for every pull request: findings, test evidence, open debt, and the closing verdict. `git-pr` writes the initial creation draft; the designated post-review evidence writer (Inquisitor 🔎 (PR Reviewer) when the roster is installed) alone accumulates these sections in `output/pr-working-body.md` and publishes the completed review body once. The presentation never varies per PR.

The creation draft retains its `Title:` wrapper; the single working body has no wrapper. Local title/body are authoritative preparation inputs. Published evidence belongs only in the PR body, never comments/reviews or competing documents. Required scanner snapshots are machine evidence, not alternative working bodies. Initial-draft bans on ticks/results do not prohibit the designated writer's evidence-backed local review assembly.

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
- Keep `- [ ]` until the designated writer joins the matching evidence row and tick together locally at the reviewed head. Publish the complete joined body in one final update; local assembly alone is not verified publication. Never write `- [x]`, a result, or a claim that something ran in the initial draft.
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

- The header block is part of every row's evidence: each row is applicable to that authenticated PR number, current immutable head, base, and scope command. It does not assert that every run executed at that head. Never repeat those current review values per row, and never accept a row without that binding.
- Every checked item has exactly one row. No checked item lacks a row, and no item has two rows. Re-running an item at the same head updates its one row.
- Copy the test-plan item verbatim. Never paraphrase or renumber it.
- Literal action/input is the exact command that ran. When a command consumed input, record the command and the input in that cell. When no command ran, record the exact manual action or input. Never invent a command, and never add a command field for a manual check.
- Observed result is the human-readable verdict only: for a test run, the pass/fail summary line and the exit code where relevant. Never progress bars, per-test dots, stack traces, raw dumps, or source bodies. Full logs stay outside the body.
- Executor is the actual person or agent that performed the check, never the body writer by default. CI records its workflow or run identifier.
- Record literal values: the base ref, the head SHA, and the scope command with that base and head. Never write the `$BASE` token.
- One current review head only. Authenticate the latest live PR head and exact diff, update the header, and reclassify every required item's evidence before the atomic row/tick join. A changed head alone, PR creation or body-only edit does not invalidate unaffected code-test evidence. Reuse sufficient task-time evidence across commits only when actual tested inputs and relevant dependencies, configuration and environment are unchanged or have an explicit proven equivalent-input mapping. Unknown equivalence fails closed; relevant changes, incomplete provenance, missing coverage or a genuinely required final combined check require an impact-scoped rerun with its stated reason. Never carry stale evidence forward or omit final combined review.
- For reused evidence, keep the original literal command/action and consumed inputs in Literal action/input, the original observed verdict/exit status in Observed result, and actual executor plus original run identity in Executor. Include the original tested content/commit and a concise current-input applicability/equivalence proof mapping or durable proof citation in Literal action/input. Never present an old run as newly executed at the header head. Keep the existing header/columns; no extra tracker or parallel evidence section.
- Every PR-body/prose change requires a fresh attribution scan covering the actual persisted body, through the existing authorized executor route, and final live-body reread before any gate. Immediately before the single publication, the final local working body must also be scanned over the exact bytes being uploaded, assembled by the `prepare-local` route described in `SKILL.md`; an attribution match blocks that upload. A pre-write scan is insufficient alone: it never replaces the persisted-body scan, and the pre-upload scan does not replace it either — both are required. This requirement is independent of unchanged code-test evidence and adds no command or mutation authority; preserve the exclusive single writer and atomic row/tick join.
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

## Preparation inputs and publication boundary

Read `scripts/prepare_pr_review.py` and the relevant `scripts/pr_review/` production operations relative to the skill root before use. Inputs are supplied UTF-8 files, not automatically authenticated observations. Missing provenance or inputs block the affected operation; never fabricate them or rebuild local prose from GitHub. Existing owners supply immutable inventory and exact paths using their authorized reads, or the `prepare-local` route derives them through read-only Git reads by that same authorized executor; this offline tool grants no collection or Git authority and makes no GitHub call.

- `initialize`: `--draft` is the creation text (`Title: …`, blank line, `---`, blank line, body starting `## Summary`); `--working-body` is the sole body-only destination. Creation is exclusive, never overwrite.
- `prepare-snapshot`: requires `--draft`, `--working-body`, `--input`, `--paths`, `--output`. Inventory JSON has exactly `schema` (integer `1`), `pr_number` (positive integer), `head_sha` (7–64 hex characters), `base` (nonblank string), `commit_messages` (nonempty array), and `changed_files` (nonempty array). Each commit entry has `surface: "commit-message"`, nonblank string `source`, and string `content`; each file entry has nonempty root-relative `path` without parent traversal and string `content`. `--paths` is a JSON array of unique exact diff-path strings, equal to the unique file-entry paths. Preserve deleted-file entries and owner-evidenced content; do not omit paths. The output is the existing scanner schema with one local title artifact, one local working-body artifact, the supplied commits and files. No remote prose is fetched.
- `snapshot`: lower-level compatibility path with `--input`, `--paths`, `--output`; input is already scanner-shaped (`schema`, `pr_number`, `head_sha`, `base`, `artifacts`, `changed_files`), with exactly one `pr-title`, one `pr-body` and at least one `commit-message` artifact, each carrying `surface`, `source`, `content`. Prefer `prepare-local`, then `prepare-snapshot`, for local authoring; neither path invents collection provenance.
- `validate`: requires `--baseline`, `--current`, `--working-body`; optional `--decisions` is required when decision-backed exceptions apply. Metadata JSON fields are `number` (positive integer), `headRefOid` (7–64 hex characters), and string fields `baseRefName`, `headRefName`, `state`, `title`, `body`; state is `OPEN`, base/head names and title nonblank. Baseline and current must be equal, including the remote body, to detect divergence; they are authenticated by the existing owner, not the tool. They do not replace the locally authored candidate. Summary, breaking changes, test-plan text and finding history are preserved; checked items retain their exact keys. The tool structurally supports completed PASS and accepted ADVISORY, not a successful BLOCK publication.
- Decisions JSON has exactly `pr_number`, `head_sha` (matching metadata), `not_applicable`, `acceptance`, `debt` (arrays). Every entry has exactly six string fields: `target`, `actor`, `date`, `statement`, `evidence`, `destination`; all except destination are nonblank, date is ISO date, targets are unique within each array. N/A targets are exact unchecked item texts; acceptance targets are exactly the unresolved finding IDs. Debt targets include every DEFERRED finding ID and may additionally name independently authorized follow-ups without artificial findings; each requires nonblank destination. Each accepting actor/date appears in the ADVISORY verdict. Owners establish actual author/user authority from cited evidence; schema acceptance proves none. Each debt record produces exactly one Open debt line, in supplied order: `- target — destination, authorized by actor on date`, substituting supplied literal values. For each DEFERRED finding, Owner / resolution starts with the exact destination followed by ` — ` and its resolution text; the validator compares the prefix before the first ` — ` exactly. Independent follow-ups retain their destination and explicit authority under Open debt above.
- `verify`: requires `--baseline`, `--current`, `--working-body`; both JSON files require the full metadata schema described for `validate`: `number`, `headRefOid`, `baseRefName`, `headRefName`, `state`, `title`, `body`, with the same types and validation. Current is the owner's authenticated persisted capture, not a head/body-only object. Every baseline field except body must remain equal, including title and OPEN state, and persisted body must equal the intended working-body bytes. The tool compares supplied data; it does not authenticate, fetch, publish, scan or repair.

All output creation is exclusive; occupied paths require explicit lifecycle disposition, never hidden overwrite or competing working-body names. Machine snapshots may use coordinator-assigned distinct paths per input revision. Validation success is structural only: retain independent evidence review, N/A authority, user acceptance, debt and final combined checks. The exclusive designated writer checks live freshness immediately before its ONE final publication, then verifies saved identity/body, obtains the mandatory fresh attribution scan of the actual persisted body and completes final live reread. The writer owns every row, tick, open-debt entry and the verdict; Herald 📯 (Release Manager) — the sole Git and GitHub executor — performs the single publication against the writer's exact validated body file and returns the persisted capture, and the writer — not Herald 📯 (Release Manager) — verifies it. Stale head/body, failed upload or divergent readback blocks acceptance; no blind overwrite or automatic retry. Later separately authorized factual prose corrections remain serialized after observed release of evidence ownership and preserve all rows/ticks/unrelated prose; every such change still needs its fresh persisted-body scan and readback.

## Readability

- Keep every cell to one short phrase or literal; never a paragraph or nested list.
- Use inline code for commands, paths, SHAs, and status tokens.
- Escape a literal pipe in a cell as `\|`.
- Keep the mandated columns and order; do not add columns or HTML layout.
- Put detail in a named local audit artifact and cite it by path; never paste it into the body.
