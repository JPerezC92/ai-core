---
name: git-pr
description: Draft a pull request title/body from branch commits and the base diff, then prepare one local review body and scanner snapshot for a single final publication by its existing owner. Use when opening a PR, drafting its description, preparing review evidence, or getting a branch ready to merge.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.10.0
  domain: git
---
<!-- core:begin -->

## Steps

1. Establish scope: the commits on the branch and the complete diff from the merge base with the project's configured base ref (`$BASE`, substituted with the project's actual base) to the current head, sampling the highest-signal files when the change set is large. That diff is the only scope evidence; a whitespace or staging diagnostic never is. An unresolvable or ambiguous configured base stops the draft and is reported as a blocker; never substitute a base of your own choosing.
2. Read `knowledge/agent-workflow.md` and apply `### ODD protocol` for classification; do not restate that protocol here. Establish authorized intent from the request/assignment, branch/task context, scoped commits and reconciled diff:
   - **Small work:** use the authorized request/assignment with the scoped commits and diff for intent and current state; require no artificial feature document.
   - **Non-small work:** identify the unique governing ODD feature document at `odd/tasks/<YYYY-MM-DD>-<feature-name>.md` from the task context and reconciled changed files, never merely by filename, date, or status; read its `## Specs`, relevant `## Tasks`, and `## Log` for intent and current state. A missing document or timing evidence is a blocker, not permission to document implementation retroactively.
   - **Explicit legacy migration** may consume its existing legacy input for intent; it is not an alternative workflow for new work and does not waive applicable ODD classification or timing requirements.
   Use ticket references from recent commit subjects where present. The Summary explains why, grounded in the applicable authorized intent rather than inferred from the diff alone. If classification, authority, intent, or the required document's applicability is ambiguous or missing, investigate accessible evidence, then stop and report unresolved gaps and inspected candidates to the coordinator/requester before drafting; never infer an answer.
3. Derive the title and body from the diff. When the current branch follows `type/scope/description` and its type or scope disagrees with the derived title, keep the diff-derived title and report both values explicitly: a branch is evidence of intent, not authority.
4. Before any draft or working-body write, obtain a read-only effective-ignore check for the exact intended path (`output/pr-draft.md` or `output/pr-working-body.md`) through the existing Git owner (Herald 📯 (Release Manager) when the roster is installed, otherwise the authorized requester). Confirm the actual path is ignored, including negation rules and whether it is already tracked; merely finding an ignore entry is not proof. Check a not-yet-created path prospectively. Not ignored, tracked, denied, failed, or inconclusive → stop and report the checked path and observed blocker to the coordinator/requester for separately authorized remediation by the existing ignore-configuration owner. This skill never edits `.gitignore` or other ignore configuration. While remediation is blocked, pending, or declined, create/overwrite neither draft, working body nor directory and do not hand off a stale file as ready. Resume only after a fresh successful check; this grants no new Git-command authority.
5. Write `output/pr-draft.md` in the shape below only after that check succeeds. Create `output/` if needed. Never write `pr-draft.md` at the repository root. It is the initial creation draft, not the post-review evidence document; the sole later working body is `output/pr-working-body.md`.
6. Hand off. When the roster is installed, report that `output/pr-draft.md` is ready for Herald 📯 (Release Manager) to create the PR, naming Inquisitor 🔎 (PR Reviewer) review at the immutable head as the completion condition, and print no publication command. Otherwise report the draft ready for the requester.

When the branch has no commits ahead of the base, report that there is nothing to draft; if uncommitted changes exist, point to `git-commit` first.

## Draft and body contract

### Title

`type(scope): concise summary under 70 characters`

- **type**: `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style`, or `test`; `style` means formatting, not CSS or UI design.
- **scope**: one lowercase kebab-case token — the affected module, feature, layer, package, app side (`<app>-api`, `<app>-web`), or the shared concern behind a cross-cutting change (`deps`, `ci`, `repo`).
- Imperative mood, lowercase after the colon, no trailing period.

### Body

Read `references/_pr-evidence-format.md` in full before drafting. It is the canonical format for the completed body, including the mandatory findings and test-evidence tables.

```markdown
## Summary
- <what changed and why — one line each, at most three>

## Test plan
- [ ] <action and the observable expected result>
- [ ] <edge case or regression and its expected result>

## Findings / blockers
No review findings yet.
```

- **Summary**: the motivation, not a restatement of the diff.
- **Test plan**: at least two concrete, executable steps, each naming the action and its expected result. Every item is an unchecked `- [ ]` checkbox in the draft — never `[x]`, a result, or a claim that something ran.
- **Findings / blockers**: the initial draft states `No review findings yet.` with no table. After review, this section follows `references/_pr-evidence-format.md`: the mandatory findings table, or `No findings.` when the review produced none.
- **Line budget**: keep the initial draft under 20 lines. After review, the findings and test-evidence tables extend the body only as required — one row per finding or checked item, no duplicated prose, no padding.

### Breaking changes

When a commit title carries `!` or the diff removes or renames a public interface, add before the test plan:

```markdown
## Breaking changes
- <what breaks>
- Migration: <one-line path>
```

### Output shape

```text
Title: <title>

---

<body>
```

### Post-PR evidence contract

Read `references/_pr-evidence-format.md` in full before writing post-review evidence. It is canonical for the findings, test-evidence, open-debt, and verdict sections.

After the PR exists, `output/pr-working-body.md` is the sole local body-only review document; the published PR body remains the sole published evidence surface — never comments, reviews, or parallel review documents. Local authored title/body stay authoritative; GitHub is the publication destination, not a source for repeatedly reconstructing prose. Before any checkbox changes from `- [ ]` to `- [x]`, the current-head evidence block and one row for that item must exist. The block records the PR number, immutable head SHA, base, and literal scope command once; the table maps every checked test-plan item to exactly one row with the exact item text, literal action/input, verdict-only observed result, and actual executor.

**Verdict-only observed output.** Record the human-readable verdict — for a test run, the pass/fail summary line and exit code where relevant. Never paste progress bars, per-test dots, stack traces, or raw dumps unless the requester explicitly asks.

**Manual actions.** A genuinely performed manual check records its literal action or input, observed result and actual executor. Include a command only when one actually ran; never invent one, and never let a bare tick directive or a manual/optional label stand in for a performed check.

**Atomic join.** The single designated evidence writer accumulates findings, evidence, open debt, verdict and matching ticks together locally, validates the complete current-head block, then publishes the completed review body in ONE final body update, with no intermediate review-body uploads. The same join owns every post-review findings, evidence, open-debt, and verdict write; no other post-review body writer updates them. Authenticate PR identity/head and check unexpected remote divergence immediately before publication, then live-reread the saved head and body. A changed head, divergent body, failed upload or failed reread blocks acceptance; missing or partial evidence leaves the item unchecked. Never blindly overwrite or retry publication. Fresh attribution scanning of the actual persisted body remains mandatory before a gate.

**Execution ownership.** An execution owner that runs an item but does not own the PR body never reports the PR complete. Only the designated writer joins its row and tick locally; publication completion requires their verified persistence at the final review join.

**Separate prose corrections.** A later authorized factual prose correction belongs to its own serialized writer, only after observed release of the evidence writer, and must preserve every findings/evidence/open-debt/verdict row, every tick, and unrelated prose.

## Offline review preparation

Read `references/_pr-evidence-format.md` in full, including its input schemas. Read `scripts/prepare_pr_review.py` and the relevant `scripts/pr_review/` production operations before invoking them. Commands below use the project's defined `<python>` binding; a missing binding or missing owner-supplied input stops preparation. These are usage shapes, not execution grants. This tool performs local file IO only, plus read-only Git reads for `prepare-local`; it makes no GitHub call and performs no remote collection, authentication, publication or evidence-truth verification.

1. After the working path's ignore preflight, initialize once: `<python> .opencode/skills/git-pr/scripts/prepare_pr_review.py initialize --draft output/pr-draft.md --working-body output/pr-working-body.md`. This removes only the creation wrapper and preserves body bytes. Never initialize over an existing working body. Resume that same file for the same review; a conflicting/stale file requires coordinator disposition, not a renamed competing body or silent deletion.
2. The existing authorized owners supply immutable commit/file inventory and exact diff paths from their existing reads; no broad remote collector or per-PR helper script is required — the reusable `prepare-local` route builds that inventory from read-only Git data. Keep the local title in the creation draft and review prose in the working body. Assemble scanner input from the local draft, the local working body and read-only Git reads with `<python> .opencode/skills/git-pr/scripts/prepare_pr_review.py prepare-local --pr <number> --base $BASE --draft output/pr-draft.md --working-body output/pr-working-body.md --output SNAPSHOT`; that route resolves HEAD and the base ref, computes their merge base, enumerates commit messages, reads changed paths with deletions retained and reads file bodies at the resolved head, and performs no GitHub call and fetches no persisted body. Where an owner supplies the inventory separately, `<python> .opencode/skills/git-pr/scripts/prepare_pr_review.py prepare-snapshot --draft output/pr-draft.md --working-body output/pr-working-body.md --input INVENTORY --paths PATHS --output SNAPSHOT` remains available; uppercase arguments are explicit supplied UTF-8 JSON file paths, not defaults, and that form reconciles paths and assembles local prose without collecting the inventory automatically. Reuse `scripts/scan_attribution.py` through its existing authorized route and policy, not a replacement matcher.
3. The designated writer accumulates the canonical review sections locally, preserving findings history and exact checked-item keys. Before final publication, run `<python> .opencode/skills/git-pr/scripts/prepare_pr_review.py validate --baseline BASELINE --current CURRENT --working-body output/pr-working-body.md` with `--decisions DECISIONS` when exclusions, acceptance or debt require it. Owner-authenticated baseline/current JSON captures publication context and divergence, not prose authority. The supplied metadata must match exactly; successful structural validation is not authenticated truth or a reviewer verdict. Completed PASS and accepted ADVISORY are supported, including explicit debt records for independently authorized follow-ups without artificial findings; BLOCK remains a canonical non-ready outcome, not a publishable success from this validator.
4. Hand off the unchanged validated working path to the existing designated publication owner; this skill never uploads it. After that owner's single final update, compare its authenticated persisted capture with `<python> .opencode/skills/git-pr/scripts/prepare_pr_review.py verify --baseline BASELINE --current PERSISTED --working-body output/pr-working-body.md`. Both JSON inputs require the full metadata schema in the reference: `number`, `headRefOid`, `baseRefName`, `headRefName`, `state`, `title`, `body`; a head/body-only capture is insufficient. Verify compares every baseline field except body, including identity/title/state, and requires persisted body to match the intended working-body bytes; it neither fetches nor repairs. The existing authorized executor must additionally scan the actual persisted body and complete the final live readback before any gate. Local pre-write scan/validation cannot replace either control.

`initialize`, snapshot and `prepare-local` outputs are exclusive-create; existing files produce IO failure without overwrite. Allocate distinct machine-evidence snapshot paths for actual input revisions through the coordinator; these are not extra Markdown bodies. Keep the single working body, do not silently delete/reuse an occupied output. Other commands do not write files. Exit 0 emits `status: prepared`; exit 1 reports a business rejection, including a Git-derived one; exit 2 reports IO/JSON failure or a Git boundary failure — git absent from `PATH`, a failing `rev-list`/`diff`/`show`/`log` read, a timeout, or non-UTF-8 Git output. None authorizes publication or acceptance.

## Rules

- Authoring writes are limited to `output/pr-draft.md`, the one `output/pr-working-body.md`, and their `output/` parent directory when absent. Explicit assigned machine-evidence outputs may be created by the preparation tool through the existing authorized owner; this is not permission to invent further PR-description files. Do not write the repository root or edit `.gitignore`. Never publish or mutate a PR — creation, title, body, merge, comments and reviews included — and never run a state-mutating Git command.
- Do not tick a checkbox, claim executed evidence, or record a result in the initial creation draft. The designated writer's local review body instead follows the evidence contract above; no fabricated results.
- Do not force the title to match the branch; report the mismatch and keep the diff-derived title.
<!-- core:end -->
