---
name: git-pr
description: Author one JSON pull-request publication input and generate the validated body-only publication artifact from it. Use when opening a PR, drafting its description, or getting a branch ready to merge.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 4.0.0
  domain: git
---

<!-- core:begin -->

## Steps

1. Establish scope: the commits on the branch and the complete diff from the merge base with the project's configured base ref (`$BASE`, substituted with the project's actual base) to the current head, sampling the highest-signal files when the change set is large. That diff is the only scope evidence; a whitespace or staging diagnostic never is. An unresolvable or ambiguous configured base stops the draft and is reported as a blocker; never substitute a base of your own choosing. The scope evidence is supplied, never gathered: this skill runs no Git or GitHub command, so the caller passes the authenticated merge-base diff and the scoped commits it received from the Git owner — Herald 📯 (Release Manager), the sole executor of Git and GitHub commands. A supplied scope that names a base other than the configured one, or a diff that is not the complete merge-base diff, stops the draft and is reported as a blocker.
2. Read `.aicore/core/knowledge/agent-workflow.md` and apply `### ODD protocol` for classification; do not restate that protocol here. Establish authorized intent from the request/assignment, branch/task context, scoped commits and reconciled diff:
   - **Small work:** use the authorized request/assignment with the scoped commits and diff for intent and current state; require no artificial feature document.
   - **Non-small work:** identify the unique governing ODD feature document at `odd/tasks/<YYYY-MM-DD>-<feature-name>.md` from the task context and reconciled changed files, never merely by filename, date, or status; read its `## Specs`, relevant `## Tasks`, and `## Log` for intent and current state. A missing document or timing evidence is a blocker, not permission to document implementation retroactively.
   - **Explicit legacy migration** may consume its existing legacy input for intent; it is not an alternative workflow for new work and does not waive applicable ODD classification or timing requirements.
     Use ticket references from recent commit subjects where present. The Summary explains why, grounded in the applicable authorized intent rather than inferred from the diff alone. If classification, authority, intent, or the required document's applicability is ambiguous or missing, investigate accessible evidence, then stop and report unresolved gaps and inspected candidates to the coordinator/requester before drafting; never infer an answer.
3. Derive the publication content from the diff: the title, the summary bullets and the test-plan items become fields of the publication input. When the current branch follows `type/scope/description` and its type or scope disagrees with the derived title, keep the diff-derived title and report both values explicitly: a branch is evidence of intent, not authority.
4. Before any publication-input or generated-body write, obtain a read-only effective-ignore check for the exact intended path (`output/pr-publication.json` or the assigned generated-body path) through the existing Git owner (Herald 📯 (Release Manager) when the roster is installed, otherwise the authorized requester). Confirm the actual path is ignored, including negation rules and whether it is already tracked; merely finding an ignore entry is not proof. Check a not-yet-created path prospectively. Not ignored, tracked, denied, failed, or inconclusive → stop and report the checked path and observed blocker to the coordinator/requester for separately authorized remediation by the existing ignore-configuration owner. This skill never edits `.gitignore` or other ignore configuration. While remediation is blocked, pending, or declined, create/overwrite neither the publication input, the generated body nor the directory and do not hand off a stale file as ready. Resume only after a fresh successful check; this grants no new Git-command authority.
5. Write the assigned publication-input path — the single-context default is `output/pr-publication.json` — in the shape below only after that check succeeds. Create its parent directory if needed. Never write `pr-publication.json` at the repository root. The input is data, not prose: it never carries preformatted Markdown, a heading, a table, a checkbox, a findings row or an evidence section, and the generated Markdown is an artifact that is never an input. It is the initial creation input, not the post-delivery evidence record; the evidence-stage sections are assembled by the agent that prepared the change.
6. Generate the body and hand it off. Run `node .agents/skills/git-pr/scripts/prepare_pr_review.ts --input <publication input> --output <body path>`; the command validates the input, renders the canonical body and creates the body with its receipt. Report that the generated body and its receipt are ready for Herald 📯 (Release Manager) to publish, and print no publication command.

When the branch has no commits ahead of the base, report that there is nothing to draft; if uncommitted changes exist, point to `git-commit` first.

## Publication input contract

Read `references/_pr-publication-input.md` in full before writing the input. It is the canonical schema for the single JSON publication input, and this skill owns it.

### Title

`type(scope): concise summary under 70 characters`

- **type**: `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style`, or `test`; `style` means formatting, not CSS or UI design.
- **scope**: one lowercase kebab-case token — the affected module, feature, layer, package, app side (`<app>-api`, `<app>-web`), or the shared concern behind a cross-cutting change (`deps`, `ci`, `repo`).
- Imperative mood, lowercase after the colon, no trailing period.

The title is the input's `title` field. The utility validates it and copies it into the generation receipt; the generated body never repeats it.

### Summary

One to three single-line bullets stating why the change exists, in the input's `summary` array. The summary explains the motivation; it never restates the diff.

### Test plan

At least two unique items in the input's `testPlan` array. Each item names the action and its observable expected result in its `text` field and carries an explicit `status`. Every creation-stage item is `PENDING`; the preparing agent sets `PASSED`, `FAILED` or `NOT_APPLICABLE` later, with the evidence or decision each state requires.

### Breaking changes

When a commit title carries `!` or the diff removes or renames a public interface, add the input's `breakingChanges` object, with its `description` and `migration`, before the test plan.

### Generated body

The body is generated, never authored. `references/_pr-evidence-format.md` is the canonical format of the generated body, and the utility renders it from the validated input. Never write, extend or repair a body by hand, never paste Markdown into the input, and never treat a generated body as an input for a later stage.

## Publication and review

This skill owns the pull-request content only: the publication input, the generated body, the format and the content-specific validation. The publication, evidence, attribution and persistence procedure — the immutable-head identity, the evidence preparation, the single publication write, the attribution scan and the persisted-body consistency — is `.agents/skills/git-pr-workflow/SKILL.md`; read it before handing a publication input off.

The one command that belongs to this skill is `node .agents/skills/git-pr/scripts/prepare_pr_review.ts --input <publication.json> --output <body.md>`; it runs natively on Node.js `>=24.12.0` from this skill's own TypeScript source with no build step. It declares one runtime dependency, `zod`, which validates the input's shape, so a destination that adopts this skill must provision it: the skill's runtime must resolve `zod` from its own `node_modules` before the command is run. It validates the JSON input, renders the canonical body, creates the body exclusively at the given path, creates `<body.md>.receipt.json` beside it and prints that receipt. The receipt holds exactly `{"status":"prepared","title":"<title>"}`: the title binds the prepared body to the publication input it came from.

- Exit `0` prints the receipt and leaves the body and its receipt in place.
- Exit `1` prints `{"code","message"}` for a refused input and creates nothing.
- Exit `2` reports a command-line or input/output failure on stderr and leaves every existing file unchanged.

A review input's `baseRef` is rendered as `origin/<baseRef>` in the generated body, so `main` and `origin/main` produce the same base line.

The same command serves both stages: an input without `review` is a creation input, an input with `review` is a review update. The command never compares the generated body with an earlier body, a capture or a published state — the current JSON input is the only source of the body — and it keeps no prior-state snapshot, receipt digest or history record of its own. The generated body is checked against the canonical body format before it is created, so an invalid body is never written.

The publication input and the generated body are caller-supplied paths — distinct files in one preparation directory, which is what identifies the delivery context. `output/pr-publication.json` and `output/pr-working-body.md` are the single-context default, not a fixed location two contexts may share, and existing exclusive-create behavior never overwrites an occupied path. A stage that regenerates the body uses a fresh body path, because a generated body is never overwritten. This skill never publishes or mutates a pull request and never runs a Git or GitHub command.

## Rules

- Never run a Git or GitHub command: the workflow commands that read Git are executed by Herald 📯 (Release Manager) through `.agents/skills/git-pr-workflow/SKILL.md`, and this skill's own command reads supplied files only.
- Authoring writes are limited to the supplied publication-input path, the supplied generated-body path, the receipt beside it, and their parent directory when absent; the single-context defaults are `output/pr-publication.json` and `output/pr-working-body.md`. Explicit assigned machine-evidence outputs may be created by the preparation tool through the existing authorized owner; this is not permission to invent further PR-description files. Do not write the repository root or edit `.gitignore`. Never publish or mutate a PR — creation, title, body, merge, comments and reviews included — and never run a state-mutating Git command.
- Never author Markdown publication content: no description, heading, table, checkbox, findings row or evidence section is written by hand, and a generated body is never edited or reused as an input.
- Do not record a result, claim executed evidence, or set an evidence-stage status in the creation input. The preparing agent's own evidence record instead follows `.agents/skills/git-pr-workflow/SKILL.md` and `references/_pr-evidence-format.md`; no fabricated results.
- Do not force the title to match the branch; report the mismatch and keep the diff-derived title.
<!-- core:end -->
