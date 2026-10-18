---
name: op-skill-creator
description: Create, revise, rename, or migrate an OpenCode skill by collecting its inputs, validating portable metadata, and writing SKILL.md under the project's skills directory. Use when the user wants to create a new OpenCode skill, rewrite an existing skill, rename a skill, migrate a skill into `.opencode/skills/`, or add a prefix to a skill name.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.3.0
  source: opencode-docs-skills
---

## Inputs

- **Operation** — create, modify, migrate, or rename/prefix. Infer it only when the request and the existing files make it unambiguous; otherwise request it.
- **Name** — the skill's directory ID.
- **Description** — what the skill does and when to use it.
- **Body intent** — the actions, decisions, guards and outputs the skill must carry.
- **Optional metadata** — only values the requester or the project actually supplies.

Read what the project already answers, and request only the decisions still unresolved. Route those requests through the coordinator: never invoke the user-facing question tool from a delegated run.

## Steps

1. Classify the operation. `create` has no prior file; `modify` edits an existing skill in place; `migrate` copies a skill from another harness's skills root; `rename`/`prefix` creates the skill at a new ID. Rename and migration have separate delete, archive or keep-source choices; choosing the operation never implies source removal.
2. Read before writing — the existing `SKILL.md` for a modify, the source skill and its supporting directories for a migrate or rename/prefix, and the project's own authoring references when present (migration notes, skills inventory, catalog checklist, conventions). A missing optional reference is not a blocker: the embedded checks below stay coherent, and the gap is noted in the final report. Never silently skip a reference that does exist.
3. Validate the name against the portable rule: 1–64 characters, `^[a-z0-9]+(-[a-z0-9]+)*$`, no leading or trailing hyphen, no consecutive hyphens, and equal to the target directory name. Separately, apply the local catalog policy that the name is unique among the project's skills.
4. Validate the description against the portable rule: 1–1024 characters, non-empty, stating what the skill does and when to use it. Then apply this catalog's local wording policy inline, so validation needs no optional reference: no angle brackets, and a when-trigger clause such as `Use when …` naming the concrete situations that activate the skill.
5. Handle frontmatter. Under the portable specification, optional `metadata` must be a mapping with string keys and string values; reject lists and numeric values. Keep `license`, `compatibility` and `metadata` at this project's convention: `license: MIT`, `compatibility: opencode`, and non-empty `metadata.author` and `metadata.version`, alongside existing `domain`, `source` and attribution. Preserve supplied author/version/domain/source attribution across operations; on a modify, advance the preserved version for the actual change. Never invent optional metadata, fabricate delivery evidence, or leave empty author values.
6. Build the body under `## Generated body requirements`, then check consistency: every capability the body declares appears in the description.
7. Run `## Pre-write checks`, fixing safe defects. A decision that changes contract, metadata, or scope is a required input, not something to guess.
8. Resolve any existing-target collision before writing; never overwrite an unrelated skill. Write the file under `.opencode/skills/<name>/SKILL.md`, then re-read it to confirm valid frontmatter, a matching directory name, and the intended body. For rename/migration, complete the approved helper and reference work below before any source cleanup.

## Generated body requirements

- Plain Markdown with H2 subsections and no skipped heading level; no H1 title and no rule-layout marker.
- Necessary steps, decisions, safeguards and outputs only — no restated anatomy, no redundant mandatory section names, no command recipe where an outcome states the requirement.
- Required inputs and missing-input handling explicit. Do not assume Claude-style argument interpolation; declare inputs the skill needs.
- Examples or failure guidance only where they settle a decision or an expected use. Cause and remedy stay where an operator can act on them, not only in an optional reference.
- Environment-dependent invocations use project-defined bindings; necessary Python uses the destination project's `<python>` binding, never a bare/global interpreter or a source-specific runner. Binding authority remains project-owned; this grants no shell authority or new exact-command exception.
- Keep external artifact schemas explicit when a consumer depends on them.
- Referenced support files are named and read explicitly, since they are not loaded automatically; operational instructions stay in `SKILL.md`, static reference data in `references/`, executable code in `scripts/`.

## Pre-write checks

- File is `SKILL.md`; frontmatter `name` matches the directory basename and is kebab-case; no `claude-` or `anthropic-` prefix; no `README.md` in the skill directory.
- No unfilled `{...}` placeholders; body under 5,000 words and under 500 lines; static blocks over roughly 30 lines extracted to a named reference artifact with a read-pointer.
- `compatibility: opencode` present per local convention, and the body stays compact.
- Every project command names its defined binding rather than a fixed runner.
- Naming, pattern-registry and audit follow-up handed to the catalog owner; cross-references are not left stale.

## Portable, runtime and local layers

| Layer | Governs | Examples |
|---|---|---|
| Portable Agent Skills specification | Package and metadata requirements | A directory containing `SKILL.md`; `name` up to 64 kebab-case characters matching the directory; `description` 1–1024 characters; optional `license`, `compatibility`, `metadata` |
| OpenCode V2 runtime | Discovery and loading | Frontmatter optional at runtime; the file path derives the exact skill ID; `name` is a display label; `compatibility` is accepted but uninterpreted; supporting files are read on demand, not loaded automatically |
| Project catalog policy | Stricter local conventions | Exact `compatibility: opencode`; metadata author/version/domain convention; catalog checklist item IDs |

A local convention is reported as local, never as a portable or runtime requirement.

## Rewrite, rename and migration

- A modify in place changes only the named skill. It does not imply a rename, a deprecation, or cleanup of neighbouring skills.
- Before a rename/prefix or copy-based migration, preview every file to create, copy, move, edit or delete. Obtain explicit approval of the target, helper transfers, discovered-reference updates, and whether to preserve output/script paths or retarget them. Resolve target collisions rather than overwriting an unrelated skill.
- Offer source cleanup separately: delete, move to `_deprecated/`, or keep the old source as-is. Delete/archive requires explicit prior confirmation; declined cleanup leaves the source intact and does not prevent an otherwise approved copy. Neither the operation nor target approval implies cleanup approval.
- Copy required helpers and update target references for the approved paths. Search the project's inventories, agent specs, knowledge files, plans and stories for the old name or path; update the approved matches, preserving intentional source references when keeping the source. Record an empty result instead of skipping the search.
- Re-read the target, verify its required helpers and all target references, and re-read each edited reference before any approved source cleanup. Helpers may move only as part of explicitly confirmed cleanup after target verification; keep-source leaves the original skill and support tree intact.

## Rules

- Write only the skill path plus, for a confirmed rename or migration, the previewed set of files.
- No fabricated metadata, no invented history, no new tool, runner, shell or argument authority.
- A missing required input, conflicting authoritative behavior, or unresolved migration choice stops the operation and reports it; it is never guessed.
