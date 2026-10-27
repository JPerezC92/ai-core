# 02 — ODD: the core workflow (Organic Driven Development)

> Part of the [Gentleman Programming / ODD research set](README.md). Research date: 2026-10-22. All claims carry `S#` citations ([sources.md](sources.md)); inferences are labeled `infer:`. All quotes in this chapter are from `docs/usage.md` pinned at tag **v4.2.0** unless noted (S4).

## 1. Default-on, read-only-first

"ODD runs by default on every request, in every configured runtime, without you asking for a workflow, a plan, or task tracking." "Explanation, investigation, and proposal-only requests remain read-only." (S4)

Intended-usage reinforces the boundary: "Explanations and investigations stay read-only… findings do not silently expand authorization." (S5)

Small work stays small: "Small, understood work creates no durable task artifacts." (S4, S5)

## 2. The seven protocol steps

From usage.md, "The ODD protocol" (S4); gentle-shell's README summarizes the same seven steps ("Authorize, Explore, Resolve uncertainty, Classify, Track, Implement, Close") (S21):

1. **Authorize** — does the request authorize a change? read-only work stays read-only.
2. **Explore** — explore existing code and requirements first, proportionately.
3. **Resolve uncertainty** — optional research for a named uncertainty, **one focused question for a real product decision**, at most one assumption challenge for a high-consequence unproven premise.
4. **Classify** — small "when understood, risk is contained, and the work could be resumed from the request plus `git diff`"; large only when that resume test fails. "Counts of files, commands, tests, fixes, or a requested todo list never decide it." gentle-shell restates it as "work becomes large only when it can't be resumed from the diff" (S21).
5. **Track before the first write** — for substantial work, create the feature document **and its Engram mirror before the first source write**, announced in one line.
6. **Implement task by task** — smallest useful topology, test-first policy, checks; **work units committed in reviewable slices of about 400 authored changed lines** on the feature branch (branch first when on the default branch), tests and docs alongside, Conventional Commit message; "a unit whose Risk line names a high-risk item gets its own commit so native review can take it alone".
7. **Close** — report the verified outcome, every failed or pending check, and the next step. "The native review candidate is a work-unit commit or a PR slice, never a TODO checkbox and never the accumulated feature branch."

**Research depth without a new phase** (usage.md section title): "Depth adapts to uncertainty and consequence: no fixed questionnaire or mandatory rounds… Research stays read-only and introduces no new runtime command or persistence gate." (S4)

## 3. The one feature document — `odd/tasks/<feature-name>.md`

Verbatim structure (S4):

- a short header;
- `## Specs` with numbered `S#` that **quote your exact strings, error messages, and examples verbatim**, plus acceptance criteria and checks;
- `## Tasks` with one line per task (**stable ID, linked `S#`, route, commit**);
- `## Log` last, where **`L1` is your original request verbatim** and later corrections, evidence, and rationale are appended.

> **Naming caution:** the document's own spec IDs (`S#`) and this research set's citation IDs (`S#`) are different namespaces. Inside a feature document, `S#` means the document's numbered specs; in this research set, `S#` means the citation IDs in [sources.md](sources.md). `infer:` the collision is incidental — ODD's spec IDs are quoted from usage.md's own terminology.

**Requirement-change rule:** "A requirement change rewrites only the affected spec and reopens only its task." (S4)

**Engram mirror:** project-scoped **Engram topic `odd/<feature-name>/tasks` mirrors the full current document and file locator.** (S4)

**Handoffs:** "workers receive a reference to the document, their task, and its `S#`, never a paraphrase of your request; they read until `## Log` and report which specs they covered." Verify "returns a verdict per spec"; "A failure you report is reproduced before anyone decides it already works." (S4)

## 4. Small work, resumability, and the ~400-line heuristic

- **Small work stays small** — "Small, understood work creates no durable task artifacts." (S4, S5)
- **Classification is by resumability, not size** — small when "understood, risk is contained, and the work could be resumed from the request plus `git diff`"; "Counts of files, commands, tests, fixes, or a requested todo list never decide it." (S4)
- **The ~400-line figure is explicitly a disclaimer, not a gate:** task size ~400 authored changed lines is "only a planning heuristic, not a task acceptance criterion, hard cap, counter-trigger, automatic stop, forced split, or RDD trigger" (S4). The same 400-line figure appears as the `LargeChangeLines` threshold in the review-integration surface (S14) and as the "~400-line delivery budget" bounding PR-slice review (S13).

## 5. Test-first policy

From usage.md "Tests" (S4):

- test-first by default "when a relevant runnable deterministic test and a clear expected outcome exist: observed RED before implementation → GREEN → REFACTOR";
- one RED test per requested rule; one regression test per touched existing command/option;
- compare against `git stash`/HEAD behavior;
- "never invent a runner."

`infer:` the "Strict TDD" flag was retired in v4.0.0 because test-first became the default posture (S10, S11); see [`05-comparison-and-assessment.md`](05-comparison-and-assessment.md).

## 6. Work-unit commits and review boundaries

- Work units are committed **in reviewable slices of about 400 authored changed lines** on the feature branch (branch first when on the default branch), with tests and docs alongside, Conventional Commit message (S4).
- "a unit whose Risk line names a high-risk item gets its own commit so native review can take it alone" (S4).
- **Per-commit / per-PR-slice review arrived in gentle-ai v3.1.0 (2026-09-17)** — release title "ODD closes each task with a work-unit commit and reviews per commit or slice" (S12; devbrief.dev summary of the release, S13). After each work-unit commit with RDD on: `gentle-ai review assess --base-ref <last reviewed boundary> --committed-only`; passive/low silent (boundary advances), **high → the commit itself is the candidate**, **medium → defers to the PR slice** bounded by the ~400-line delivery budget (S4, S13).
- **Close:** "The native review candidate is a work-unit commit or a PR slice, never a TODO checkbox and never the accumulated feature branch." (S4)

## 7. Delivery strategies

One delivery strategy per feature in v4.x (S4):

| Strategy | Behavior (as documented) |
|---|---|
| `ask-on-risk` | **Default** — asks when risk warrants |
| `auto-chain` | Chains delivery automatically |
| `single-pr` | One PR for the feature |
| `exception-ok` | Exceptions permitted |

Forecast authored lines at document creation; slice boundaries recorded in the feature document (S4).

## 8. Resume semantics

Resume: the parent reads the full Engram observation and the actual task file, and reconciles code + evidence (S4):

- "Read back both writes: they are not atomic" — the feature file write and the Engram mirror write are not atomic (non-atomic-write caveat) (S4);
- if Engram is unavailable: "keep local progress and report the pending mirror; preserve conflicting versions rather than silently overwriting one." (S4)

`infer:` the non-atomic mirror and the preserve-conflicts rule make the local file authoritative and the Engram topic a recoverable mirror, not a transactional co-owner of state.

## 9. Human-owned delivery boundary

"Commit, push, PR, release, and archive follow ordinary repository policy and require their own explicit authorization" (S14); "Commit, push and release stay your call" (S9, README). RDD approval "never commits, pushes, opens a PR, or overrides repository policy" (S6). See [`03-rdd-receipt-driven-development.md`](03-rdd-receipt-driven-development.md).

Next: [`03-rdd-receipt-driven-development.md`](03-rdd-receipt-driven-development.md) — RDD, the review discipline that consumes ODD's output.
