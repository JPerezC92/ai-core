# User story — consistency checklist

> Canonical format and hygiene contract for files at `user-stories/*.md`. Owned by the
> `user-story` skill. Applied at write-time by that skill's post-write self-verification
> loop and executed as semantic review by Sentinel 🛡️ (Quality Guardian). The mechanical
> subset (`index mirroring`) is enforced by `plan-enforce`'s `scripts/validate_plan.py`,
> which validates its own story inputs and does not own this contract.
>
> Plan, phase, audit, and completion artifacts are governed by
> `.opencode/skills/plan-enforce/references/_consistency-checklist.md`.
> Ticket working artifacts are governed by
> `.opencode/skills/ticket-runbook/references/_consistency-checklist.md`.

## Catalogue

- `user-stories/index.md` exists and lists every feature file.
- Every story file appears in the index and every index row resolves to a file.
- Each story's `Title`, `Status`, `Epic`, and `Affected areas` mirror the corresponding `index.md` columns.
- No unfilled `<...>`, `TODO`, or `TBD` placeholders.
- A dated `## Change log` entry is present for every plan that touched the story.

## Ownership

- Story creation and ownership decisions belong to the `user-story` skill: CREATE of a new story file is forbidden until that skill has reconciled `user-stories/index.md` with the files, read every candidate body, presented grounded UPDATE / rename / CREATE / supersession choices, and received an explicit user choice. `plan-enforce` consumes an approved story and never renegotiates the story choice.
- Approved vs draft: only an approved (`active`) story is a planning contract; a `draft` is in-progress discussion and is not consumed by `plan-enforce`. Approval establishes feature behavior only — it is not implementation evidence, a permission grant, or execution authorization.

## Behaviour / proof separation

- **Churn test (mandatory for every criterion a plan writes or materially changes):** if a criterion would need rewording when the implementation changes, it is rewritten as observable behaviour or moved to `## Constraints`. Internal symbols, module paths, function signatures, test class names, and file inventories never appear in `## Acceptance criteria`. Criteria untouched by a plan are grandfathered until that story is next revised.
- Each criterion is self-contained and observable at a boundary (CLI output, file bytes, API response, screen, ops log) without reading code or internal state.
- **AC-id resolution:** every criterion carries a resolvable `AC<n>` id in positional order, and every `AC<n>` referenced in `## Proof` resolves to exactly one criterion. The count of `## Proof` lines equals the count of criteria. A proof reference with no matching criterion is a finding.
- `## Proof` is present and records where each criterion is demonstrated (`<AC-id> → <section or symbol> · <command/verdict>`). Proof never states a requirement and never sets a criterion's status. Proof may go stale without invalidating the contract; a rename updates `## Proof` only.
- A `file:line` citation is resolved to a section or symbol name and lives in `## Proof`, never in the criterion text.

## Constraints

- `## Constraints` holds only currently governing pre-decided restrictions the plan must RESPECT, never deliver. Each entry carries its rationale in the form `— because <reason>`.
- Plan-execution, scheduling, and superseded constraints are absent; git history retains them.
- `## Resolved decisions` is retired — it is not written. Governing restrictions and their rationale live in `## Constraints`.

## Story hygiene (auditor checks, Sentinel-executed; the validator does not parse a checklist)

- An acceptance criterion or Goal `Done when:` must not depend on a plan-only goal or a temporal `plans/`/`output/` path (a genuine feature-input path is allowed).
- It must not pin a volatile test count (`N passed`, `N tests`) or cite a superseded spec version, and must not number a surface unless that version is the requirement (including a surface whose version the touching plan itself bumps).

## Approved-criteria completion scope (fail-closed)

- A plan that touches a story reconciles only the acceptance criteria it committed to deliver, the criteria it materially changed, and any regression it introduced.
- Each reconciled criterion is `✅` (evidence-established **as resolved through the story's `## Proof` section**) or removed as out-of-scope with a change-log entry; `❌` (explicitly unmet) blocks completion until satisfied or removed.
- Remaining legitimate story commitments the plan did not select stay `⬜` and do not block completion.
- Release events (PR opened/reviewed/merged) are not acceptance criteria; actual events live in the change log and PR history.
- Completion confirms the plan **respected** every `## Constraints` entry. Constraints are never delivered and never ticked.
- This is semantic analysis (evidence-to-checkbox truth), never mechanical auto-checking.

## Bounded change log

- `## Change log` has at most 5 one-line entries (`<date> — <plan-slug>: <what changed about this feature>`) plus at most one rollup line (`before <date> — earlier history: see git history for this file`).
- A story-only revision records `story revision` in place of a plan slug; a plan slug is never invented.
- No planning-only or execution narration.

## Authority

Analysis items (everything above) are the `user-story` skill's responsibility — a value must match evidence, never be invented to satisfy a check. `plan-enforce`'s `scripts/validate_plan.py` enforces only index mirroring here; it is a helper, not the authority. Criterion wording, proof quality, and constraint judgement are semantic, never mechanical.
