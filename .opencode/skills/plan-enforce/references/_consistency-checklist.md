# Plan / Phase / Story — consistency checklist

> Canonical contract for artifacts written by the `plan-enforce` skill. Applied at write-time by the skill's post-write self-verification loop (analysis) and mechanically by `scripts/validate_plan.py` (repetitive subset). Sentinel 🛡️ (Quality Guardian) audits `plans/` and `user-stories/` against this same checklist — keep the two in lockstep.

## plan.md

- `Status:` value is `active` or `completed` (no other values).
- When `Status: completed`, a `Completed: YYYY-MM-DD HH:MM` line is present in the metadata header.
- Metadata header has `Started` and `Subject` (and `Layout` for subfolder plans).
- Required sections present: `## Context`, `## Goals`, `## Critical files / tools`, `## Verification`, `## Out of scope` (or `## Out of scope / Do-not-touch`), plus `## Body` (base template) or `## Current state` + `## Behavior change` (programming template).
- `## Goals` checkboxes present and match the confirmed goal list; each goal lists Issue, How, and Files; programming goals each carry a `Done when:` criterion. `## Context` is the overall issue. Table-only goals without that per-goal prose are a violation.
- No unfilled placeholders: `<task subject>`, a literal `YYYY-MM-DD HH:MM`, or stray `<!-- -->` comment lines (the `## Pending` section may retain its example comments).
- Goal trace: every dispatch-table row names an existing `phase-NN-<owner>.md` runbook, every phase file appears in the dispatch table, and (when the table ends in a `Goals` column) every cited goal ID exists and every declared goal ID is cited by ≥1 row.
- Manifest equality: `## Write/delete manifest` is an `Action`/`Path` table using only `Modify`, `Add`, or `Delete`, and its normalized path set equals the union of every phase's `**Writes:**` paths (`none` contributes nothing).
- Verification parity: the count of `## Verification` `- ⬜` / `- ✅` bullets equals the number of phase files; each verification checkbox traces to a phase output.
- Audit gate: `## Audit` (when present) carries a `Verdict` in `[PENDING]`, `[PASS]`, `[FAIL]`; a `Status: completed` plan carries `[PASS]` with a non-empty `Auditor` and a set `Date`. An unknown verdict or an audit missing on a completed plan is a violation.

## Execution-review (analysis)

- After plan files are written, the last user-facing message is human-readable prose per goal in order Issue, Goal, How, Files. A recap file table may follow and must not replace that prose. Dense dumps and table-only briefs are a violation.
- Forge 🔨 (Implementer) is not dispatched in the plan-creation turn. `ExitPlanMode` is not authorization to implement.
- CREATE of a new story file requires an explicit UPDATE / rename / CREATE user choice after index-filtered candidate analysis. CREATE without that choice is a violation.

## Audit gate

- Shape on `plan.md`: `- Auditor:`, `- Verdict:`, `- Findings:`, `- Date:`.
- `Auditor` — the independent auditor name, or `not yet run` while the plan is active.
- `Verdict` — one of `[PENDING]`, `[PASS]`, `[FAIL]`.
- `Date` — set when the independent audit runs.
- A plan is not reported ready and Forge 🔨 (Implementer) is not dispatched until an independent auditor returns `[PASS]`. If no auditor can run, the plan stays not-ready; a substitute requires explicit user authorization recorded in `## Audit` (fail-closed).

## phase-NN-<owner>.md

- `Owner`, `Pre`, `Reads`, `Writes` blockquote labels populated.
- No `TBD` in `Steps`, `Output`, `Gate`, or `Abort conditions`.
- `## Writes` paths match the derived write/delete manifest.
- No unfilled `<...>` placeholder tokens.
- `## Verify commands` is a non-empty canonical table with exactly the `Executor` and `Command` columns; every row pairs one non-empty executor with one non-empty command.
- Executor authority is a phase-review item: the reviewer confirms the declared executor holds the role and tool authority to run the command. The validator checks declared traceability only and never inspects permission models.
- A phase editing a Python `test_*.py` file in reviewed discovery areas lists the destination's approved whole-suite command, assigns Crucible 🔥 (Test Architect) as its executor, and records Bastion 🧱 (Backend & Scripts Architect) `[PASS]`; the gate requires Crucible's test command exit 0 and a separate test-architecture `[PASS]`; `[FAIL]` or `[UNCERTAIN]` blocks completion.

## user-stories

- `user-stories/index.md` exists and lists every feature file.
- Each story's `Title` and `Status` mirror the corresponding `index.md` columns.
- No unfilled `<...>`, `TODO`, or `TBD` placeholders.
- A dated `## Change log` entry is present for every plan that touched the story.
- CREATE of a new story file is forbidden until Cipher 🔓 (Lead Orchestrator) has read `user-stories/index.md`, filtered by epic and affected areas, read candidate bodies, presented UPDATE / rename / CREATE with evidence, and received an explicit user choice.
- Acceptance-criterion reconciliation (fail-closed): a story touched by the plan carries no `⬜` or `❌` criteria when the plan completes — each is `✅` (evidence-established) or removed as out-of-scope; `❌` (explicitly unmet) blocks completion until satisfied or removed. Out-of-scope work is removed, never left unchecked. Release events (PR opened/reviewed/merged) are not acceptance criteria. This is semantic analysis (evidence-to-checkbox truth), never mechanical auto-checking.

## Loop rule

Analysis items (everything above) are the skill's responsibility — a value must match evidence, never be invented to satisfy a check. `scripts/validate_plan.py` enforces only the mechanical/repetitive subset: enum values, section presence, placeholder/TBD detection, goal trace, manifest equality, verification parity, the completed-plan audit gate, index mirroring, and the presence/shape of each phase's executor-command table. It is a helper, not the authority. Executor authority, goal wording, and audit quality are analysis items, never a mechanical pass.
