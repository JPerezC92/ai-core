---
name: op-skill-creator
description: Create, revise, rename, or migrate an OpenCode skill by collecting its inputs, validating portable metadata, and writing SKILL.md under the project's skills directory. Optionally names a caller-supplied Markdown text-integrity checker; skill writing remains the core intent. Use when the user wants to create a new OpenCode skill, rewrite an existing skill, rename a skill, migrate a skill into `.agents/skills/`, or add a prefix to a skill name.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 2.1.0
  source: opencode-docs-skills
---

## ODD preflight

The project's `.aicore/core/knowledge/agent-workflow.md` is the governing workflow when present. If it is absent, note the gap in the final report and continue with the embedded discipline below; absence is not a blocker.

When that file is present, apply `.aicore/core/knowledge/agent-workflow.md` `### ODD protocol` before any write; do not restate that protocol here.

For authorized non-small work, read the governing `odd/tasks/<YYYY-MM-DD>-<feature-name>.md` through `## Log`, report the `S#` specs covered, and record compact per-task evidence in that existing Log: exact input/commit identity, relevant dependencies, executor, literal command or manual action, expected/observed result, and exit status when applicable. No second tracker, no execution transcript, never an invented test. This preflight grants no new authority.

## Inputs

- **Operation** — create, modify, migrate, or rename/prefix. Infer it only when the request and the existing files make it unambiguous; otherwise request it.
- **Name** — the skill's directory ID.
- **Description** — what the skill does and when to use it.
- **Body intent** — the actions, decisions, guards and outputs the skill must carry.
- **Optional metadata** — only values the requester or the project actually supplies.

Read what the project already answers, and request only the decisions still unresolved. Route those requests through the coordinator: never invoke the user-facing question tool from a delegated run.

## Steps

Run `## ODD preflight` before these steps. The operation class below is not the ODD size test.

1. Classify the operation. `create` has no prior file; `modify` edits an existing skill in place; `migrate` copies a skill from another harness's skills root; `rename`/`prefix` creates the skill at a new ID. Rename and migration have separate delete, archive or keep-source choices; choosing the operation never implies source removal.
2. Read before writing — the existing `SKILL.md` for a modify, the source skill and its supporting directories for a migrate or rename/prefix, and applicable project authoring references (migration notes, inventory, catalog checklist, conventions). Reuse content already in context when its identity and applicability are established. Note missing optional references in the final report; do not copy owner rulebooks, feature records, or legacy story surfaces into the skill. On a modify, preserve tone and structure unless the request changes them; apply the rewrite accounting below.
3. Validate the name against the portable rule: 1-64 characters, `^[a-z0-9]+(-[a-z0-9]+)*$`, no leading or trailing hyphen, no consecutive hyphens, and equal to the target directory name. Separately, apply the local catalog policy that the name is unique among the project's skills — checking the skill directories on disk when no inventory exists. This check cannot see global or external paths: report that boundary explicitly and leave uniqueness across all locations to the user.
4. Validate the description against the portable rule: 1-1024 characters, non-empty, stating what the skill does and when to use it. Then apply the project's declared description-wording policy — **this catalog's local convention** (not a portable requirement): no angle brackets, and a when-trigger clause such as `Use when …` naming the concrete situations that activate the skill. Validate inline so no optional reference is needed.
5. Handle frontmatter. Under the portable specification, `license` and `compatibility` must be strings, `compatibility` is 1–500 characters when present, and optional `metadata` is a mapping with string keys and values; reject lists and numeric values. Values come from the requester or an actually declared project convention, never a hardcoded default. Preserve supplied or existing typed values, including author/version/domain/source attribution; an absent convention never overwrites preserved values or blocks by itself. Apply declared defaults only where they exist; report enforced-convention conflicts for a decision rather than overwriting. Request missing required values. `metadata.author` and `metadata.version` must be non-empty when present or required; on modify, advance the preserved version for the actual change. Never invent optional metadata or delivery evidence.
6. Build the body under `## Generated body requirements` — that section is the single format authority; do not create a competing layout — then check consistency: every capability the body declares appears in the description.
7. Run `## Pre-write checks`, fixing safe defects. A decision that changes contract, metadata, or scope is a required input, not something to guess.
8. Resolve any existing-target collision before writing; never overwrite an unrelated skill. The first write is permitted only after `## ODD preflight`. Write the file under `.agents/skills/<name>/SKILL.md`, then re-read it to confirm valid frontmatter, a matching directory name, and the intended body. For rename/migration, complete the approved helper and reference work below before any source cleanup.

## Generated body requirements

This section is the single format authority for a generated skill. Do not create a competing layout.

- Plain Markdown with H2 subsections and no skipped heading level; no H1 title and no `> **Rule layout:**` marker.
- A shared or region-bound skill carries exactly one ordered `<!-- core:begin -->` … `<!-- core:end -->` pair immediately after the frontmatter closing `---`, plus a `<!-- project:begin -->` … `<!-- project:end -->` pair only for evidenced local content. When there is no evidenced local content, omit the project pair and end the core at EOF. A destination-local or raw-bound skill may be markerless only when its approved binding says so. Do not require a pair without that binding. A marker counts only as an exact line outside a fenced code block.
- Necessary steps, decisions, safeguards and outputs only — no restated anatomy, no redundant mandatory section names, no copied owner policy, no command recipe where an outcome states the requirement.
- Required inputs and missing-input handling explicit. When the skill takes arguments, state how they are collected — the field set (name, type, description, validation, options), when each is required, the fallback when one is missing, and the collection-form schema a consumer relies on. Do not assume Claude-style argument interpolation; declare inputs the skill needs.
- Examples or failure guidance only where they settle a decision or an expected use. Cause and remedy stay where an operator can act on them, not only in an optional reference.
- Environment-dependent invocations use project-defined bindings; necessary Python uses the destination project's `<python>` binding, never a bare/global interpreter or a source-specific runner. Binding authority remains project-owned; this grants no shell authority or new exact-command exception.
- Keep external artifact schemas explicit when a consumer depends on them.
- Referenced support files are named explicitly with their applicability and the dependent action before which they must be read. Keep universal safeguards in `SKILL.md`; conditionally applicable procedures and static material may live in `references/`, executable code in `scripts/`. Reuse applicable content already in context.

## Pre-write checks

- File is `SKILL.md`; frontmatter `name` matches the directory basename and is kebab-case. This catalog's local policy, not a portable requirement: no `claude-` or `anthropic-` prefix, and no `README.md` in the skill directory.
- No unfilled `{...}` placeholders. Prefer a short main skill: under 5,000 tokens and 500 lines are upper guidance, not targets or portable limits. Assess cumulative content needed for each operation, not line count alone; extract only when applicability-based loading improves context use or ownership without hiding safeguards. Estimate tokens when practical; no tokenizer is required.
- `compatibility` present at the value the project's catalog convention declares when it declares one; otherwise the supplied or existing value is preserved rather than replaced or invented.
- Additional local quality checks: names carry no vendor-specific prefix; Mermaid diagrams appear only where three or more branches need them, use `flowchart TD` and correct node shapes, and reference real section headers; a code fence nesting another fence uses a longer outer fence. Diagnostic skills embedding SQL document schema deltas as numbered additions, verify primary-key and constraint claims against `CREATE TABLE`, and bound every `SELECT` with `LIMIT`, `WHERE`, a CTE filter or documented pagination. Query results intended as image evidence include their filter columns for readability (`.aicore/core/knowledge/agents.md`). For OpenCode skills in this catalog, `compatibility: opencode` is the local convention; another harness substitutes its own criteria.
- Every project command names its defined binding rather than a fixed runner.
- Naming and pattern-registry updates are checked against the project's catalog conventions before completion is claimed; cross-references are not left stale. Apply the applicable quality checks to the finished draft before use or publication; fix defects and report judgment calls rather than silently accepting them. This is the author's check, not a separate audit gate or review.
- After writing, re-run these checks against the target and against every edited reference file. If the skill does not load afterwards, check the cause before changing anything else: the file is named `SKILL.md`, the frontmatter carries `name` and `description`, the name is unique, and the project's skill or permission configuration has not disabled it.

## Portable, runtime and local layers

| Layer                               | Governs                           | Examples                                                                                                                                                                                                           |
| ----------------------------------- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Portable Agent Skills specification | Package and metadata requirements | A directory containing `SKILL.md`; `name` up to 64 kebab-case characters matching the directory; `description` 1-1024 characters; optional `license`, `compatibility`, `metadata`                                  |
| OpenCode V2 runtime                 | Discovery and loading             | Frontmatter optional at runtime; the file path derives the exact skill ID; `name` is a display label; `compatibility` is accepted but uninterpreted; supporting files are read on demand, not loaded automatically |
| Project catalog policy              | Stricter local conventions        | Exact `compatibility` value per the project's declared convention; metadata author/version/domain convention; catalog checklist item IDs                                                                           |

A local convention is reported as local, never as a portable or runtime requirement.

## Rewrite and specialized operations

- A modify in place changes only the named skill. It does not imply a rename, a deprecation, or cleanup of neighbouring skills.
- Where the operation modifies, renames, or migrates existing instructions, identify the full original and the candidate inputs. Account for every valid original obligation as retained, translated, or retired with authority and rationale. Never narrow a scope or ceiling silently, and never import superseded wording as precedent. Missing accounting blocks acceptance.
- Rename, prefix and migration never imply source cleanup; delete or archive requires separate explicit prior confirmation. Never overwrite unrelated targets, invent metadata, or expand tool authority. Before previewing or performing rename/prefix or migration, read `references/_specialized-operations.md` § Rename and migration; before any source cleanup, also apply that section's verification and approval requirements. Use a bounded section read where available.
- List all changed paths from observed outcomes. For a previewed operation (rename, prefix or migration) compare them against the approved preview; for a plain in-place modify, report the actual changed set directly. The preview is never the result; report what actually changed, including a recorded empty result.

## Rules

- Write only the skill path plus, for a confirmed rename or migration, the previewed set of files.
- No fabricated metadata, no invented history, no new tool, runner, shell or argument authority.
- A missing required input, conflicting authoritative behavior, or unresolved migration choice stops the operation and reports it; it is never guessed.
- No completion claim before the author has verified the delivered skill against the actual request and this skill's applicable checks, with zero open findings. An independent review may be requested by the user and is never required. Small or read-only work has no feature Specs; do not invent them.

## Optional Markdown text integrity

Optional only; not a pre-write check or completion gate. Before using the checker, read `references/_specialized-operations.md` § Optional Markdown text integrity; use a bounded section read where available. This grants no new tool or execution authority.
