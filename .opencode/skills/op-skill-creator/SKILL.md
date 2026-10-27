---
name: op-skill-creator
description: Create, revise, rename, or migrate an OpenCode skill by collecting its inputs, validating portable metadata, and writing SKILL.md under the project's skills directory. Optionally names a caller-supplied Markdown text-integrity checker; skill writing remains the core intent. Use when the user wants to create a new OpenCode skill, rewrite an existing skill, rename a skill, migrate a skill into `.opencode/skills/`, or add a prefix to a skill name.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.6.0
  source: opencode-docs-skills
---

## ODD preflight

The project's `knowledge/agent-workflow.md` is the governing workflow when present. If it is absent, note the gap in the final report and continue with the embedded discipline below; absence is not a blocker.

Classify with the ODD test before any write. Work is small only when it is understood, risk-contained, and resumable from the request plus diff. Counts of files, commands, tests, fixes, tasks, or requested todo lists never decide. Read-only work stays read-only. Small bounded authoring needs no feature artifact.

Non-small state-changing authoring requires the authorized `odd/tasks/<feature>.md` before the first write. Read it through `## Log`, report the `S#` specs covered, and record compact per-task evidence in that existing Log: exact input/commit identity, relevant dependencies, executor, literal command or manual action, expected/observed result, and exit status when applicable. No second tracker, no execution transcript, never an invented test. This preflight grants no new authority.

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
2. Read before writing — the existing `SKILL.md` for a modify, the source skill and its supporting directories for a migrate or rename/prefix, and the project's own authoring references when present (migration notes, skills inventory, catalog checklist, conventions). `knowledge/agent-workflow.md` is governed by `## ODD preflight`, not by this optional list. On a modify, preserve the existing tone and structure unless the request explicitly changes them, and apply the rewrite accounting in `## Rewrite, rename and migration`. A missing optional reference is not a blocker: the embedded checks below stay coherent, and the gap is noted in the final report. Never silently skip a reference that does exist. Do not copy owner rulebooks, feature records, or legacy story surfaces into the skill; name and read them.
3. Validate the name against the portable rule: 1-64 characters, `^[a-z0-9]+(-[a-z0-9]+)*$`, no leading or trailing hyphen, no consecutive hyphens, and equal to the target directory name. Separately, apply the local catalog policy that the name is unique among the project's skills — checking the skill directories on disk when no inventory exists. This check cannot see global or external paths: report that boundary explicitly and leave uniqueness across all locations to the user.
4. Validate the description against the portable rule: 1-1024 characters, non-empty, stating what the skill does and when to use it. Then apply the project's declared description-wording policy — **this catalog's local convention** (not a portable requirement): no angle brackets, and a when-trigger clause such as `Use when …` naming the concrete situations that activate the skill. Validate inline so no optional reference is needed.
5. Handle frontmatter. Under the portable specification, `license` and `compatibility` must be strings, and optional `metadata` must be a mapping with string keys and string values; reject lists and numeric values. `license`, `compatibility` and `metadata` values come from the requester's input or from a convention the project actually declares (see `## Portable, runtime and local layers`) — never from a literal hardcoded here. Preserve every supplied or already-present typed value across operations, including author/version/domain/source attribution. Apply a declared convention value or default only where one exists; an absent convention is not itself a blocker and must not overwrite preserved values. Where a supplied or existing value conflicts with a convention the project enforces as a catalog check, report the conflict and request a decision — do not silently overwrite either. When a genuinely required value is still missing, request that one value rather than inventing a default. `metadata.author` and `metadata.version` must be non-empty strings whenever present or required. On a modify, advance the preserved version for the actual change. Never invent optional metadata, fabricate delivery evidence, or leave empty author values.
6. Build the body under `## Generated body requirements` — that section is the single format authority; do not create a competing layout — then check consistency: every capability the body declares appears in the description.
7. Run `## Pre-write checks`, fixing safe defects. A decision that changes contract, metadata, or scope is a required input, not something to guess.
8. Resolve any existing-target collision before writing; never overwrite an unrelated skill. The first write is permitted only after `## ODD preflight`. Write the file under `.opencode/skills/<name>/SKILL.md`, then re-read it to confirm valid frontmatter, a matching directory name, and the intended body. For rename/migration, complete the approved helper and reference work below before any source cleanup.

## Generated body requirements

This section is the single format authority for a generated skill. Do not create a competing layout.

- Plain Markdown with H2 subsections and no skipped heading level; no H1 title and no `> **Rule layout:**` marker.
- A shared or region-bound skill carries exactly one ordered `<!-- core:begin -->` … `<!-- core:end -->` pair immediately after the frontmatter closing `---`, plus a `<!-- project:begin -->` … `<!-- project:end -->` pair only for evidenced local content. When there is no evidenced local content, omit the project pair and end the core at EOF. A destination-local or raw-bound skill may be markerless only when its approved binding says so. Do not require a pair without that binding. A marker counts only as an exact line outside a fenced code block.
- Necessary steps, decisions, safeguards and outputs only — no restated anatomy, no redundant mandatory section names, no copied owner policy, no command recipe where an outcome states the requirement.
- Required inputs and missing-input handling explicit. When the skill takes arguments, state how they are collected — the field set (name, type, description, validation, options), when each is required, the fallback when one is missing, and the collection-form schema a consumer relies on. Do not assume Claude-style argument interpolation; declare inputs the skill needs.
- Examples or failure guidance only where they settle a decision or an expected use. Cause and remedy stay where an operator can act on them, not only in an optional reference.
- Environment-dependent invocations use project-defined bindings; necessary Python uses the destination project's `<python>` binding, never a bare/global interpreter or a source-specific runner. Binding authority remains project-owned; this grants no shell authority or new exact-command exception.
- Keep external artifact schemas explicit when a consumer depends on them.
- Referenced support files are named and read explicitly, since they are not loaded automatically; operational instructions stay in `SKILL.md`, static reference data in `references/`, executable code in `scripts/`.

## Pre-write checks

- File is `SKILL.md`; frontmatter `name` matches the directory basename and is kebab-case. This catalog's local policy, not a portable requirement: no `claude-` or `anthropic-` prefix, and no `README.md` in the skill directory.
- No unfilled `{...}` placeholders; total under 5,000 words and `SKILL.md` under 500 lines — the whole file, not the body alone; static blocks over roughly 30 lines extracted to a named reference artifact with a read-pointer. Those ceilings are this catalog's **local** policy values, not portable requirements.
- `compatibility` present at the value the project's catalog convention declares when it declares one; otherwise the supplied or existing value is preserved rather than replaced or invented.
- Every project command names its defined binding rather than a fixed runner.
- Naming and pattern-registry updates are handed to the catalog owner with the audit; cross-references are not left stale. That audit is a completion-gate input under `## Rules`, not a follow-up that can remain pending after a completion claim.
- After writing, re-run these checks against the target and against every edited reference file. If the skill does not load afterwards, check the cause before changing anything else: the file is named `SKILL.md`, the frontmatter carries `name` and `description`, the name is unique, and the project's skill or permission configuration has not disabled it.

## Portable, runtime and local layers

| Layer | Governs | Examples |
|---|---|---|
| Portable Agent Skills specification | Package and metadata requirements | A directory containing `SKILL.md`; `name` up to 64 kebab-case characters matching the directory; `description` 1-1024 characters; optional `license`, `compatibility`, `metadata` |
| OpenCode V2 runtime | Discovery and loading | Frontmatter optional at runtime; the file path derives the exact skill ID; `name` is a display label; `compatibility` is accepted but uninterpreted; supporting files are read on demand, not loaded automatically |
| Project catalog policy | Stricter local conventions | Exact `compatibility` value per the project's declared convention; metadata author/version/domain convention; catalog checklist item IDs |

A local convention is reported as local, never as a portable or runtime requirement.

## Rewrite, rename and migration

- A modify in place changes only the named skill. It does not imply a rename, a deprecation, or cleanup of neighbouring skills.
- Where the operation modifies, renames, or migrates existing instructions, identify the full original and the candidate inputs. Account for every valid original obligation as retained, translated, or retired with authority and rationale. Never narrow a scope or ceiling silently, and never import superseded wording as precedent. Missing accounting blocks acceptance.
- Before a rename/prefix or copy-based migration, preview every file to create, copy, move, edit or delete. Obtain explicit approval of the target, helper transfers, discovered-reference updates, and whether to preserve output/script paths or retarget them. Resolve target collisions rather than overwriting an unrelated skill.
- Offer source cleanup separately: delete, move to `_deprecated/`, or keep the old source as-is. Delete/archive requires explicit prior confirmation; declined cleanup leaves the source intact and does not prevent an otherwise approved copy. Neither the operation nor target approval implies cleanup approval.
- Copy required helpers and update target references for the approved paths. Search the project's inventories, `odd/tasks/` feature records, knowledge files, agent specs, and any legacy plan or story surface that actually exists for the old name or path; update the approved matches, preserving intentional source references when keeping the source. Record an empty result instead of skipping the search.
- Re-read the target, verify its required helpers and all target references, and re-read each edited reference before any approved source cleanup. Helpers may move only as part of explicitly confirmed cleanup after target verification; keep-source leaves the original skill and support tree intact.
- List all changed paths from observed outcomes. For a previewed operation (rename, prefix or migration) compare them against the approved preview; for a plain in-place modify, report the actual changed set directly. The preview is never the result; report what actually changed, including a recorded empty result. That report is not a completion claim; completion is the independent gate in `## Rules`.

## Rules

- Write only the skill path plus, for a confirmed rename or migration, the previewed set of files.
- No fabricated metadata, no invented history, no new tool, runner, shell or argument authority.
- A missing required input, conflicting authoritative behavior, or unresolved migration choice stops the operation and reports it; it is never guessed.
- No completion claim before a reviewer who authored neither the change nor its evidence returns zero open findings after comparing the actual request, Specs, delivered content, accounting and evidence. The catalog-owner audit is part of that gate. A pending audit is not completion. Small or read-only work has no feature Specs; do not invent them.

## Optional Markdown text integrity

Optional only — not a pre-write check, completion gate, or mandatory every-task scan. Distinct from skill metadata, feature anatomy, and fenced-language validation.

- Read the project's Markdown text-integrity policy when present; absence is not a blocker and not a default path.
- The caller supplies `--policy PATH`. This skill does not hardcode a source-root policy file or imply destination synchronization.
- Read `scripts/check_markdown_text.py` explicitly; it is not loaded automatically.
- CLI shape via the project's `<python>` binding is a usage reference, not a shell grant or install: `<python> .opencode/skills/op-skill-creator/scripts/check_markdown_text.py --policy PATH [--check-editor PATH] PATH [PATH ...]`
- Required: `--policy PATH` and one or more explicit Markdown file or directory paths. Optional: `--check-editor PATH`. No implicit repository-root scan.
- Read-only: no formatting, Git, network, or runtime dependency installation.
- Exit 0: no errors (warnings may exist; they are not file defects). Exit 1: content errors or editor-projection drift. Exit 2: policy, input, or IO failure.
- No ASCII-only mode. En dashes, emoji, joiners, and ordinary Unicode prose are not errors merely because they are non-ASCII. Editor highlighting is not the checker's complete semantics.
