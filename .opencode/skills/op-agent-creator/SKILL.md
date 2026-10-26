---
name: op-agent-creator
description: Create or modify an OpenCode agent (primary, subagent, or dual-use all mode) by collecting mode, system prompt, and permission model; validating name, description, and frontmatter; and writing `.opencode/agents/{name}.md`. Use when the user wants to create, update, rename, or migrate a Claude Code agent to OpenCode.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.4.7
---

## Project extensions

### Knowledge hooks

This project's pre-flight knowledge hooks are the files `knowledge/agents.md`, `knowledge/agent-workflow.md`, `knowledge/skill-migration-reference.md`, `knowledge/skills.md`, and `.opencode/agents/vault.md` (Quality Checklist section). `knowledge/agents.md` and `knowledge/agent-workflow.md` are shared infrastructure; skip the workflow entry only when it is not present yet. `knowledge/skill-migration-reference.md` and `knowledge/skills.md` are destination-specific hooks and may be absent; the skill degrades gracefully when they are.

### Claude Code migration

An existing Claude Code agent spec lives at `.claude/agents/{name}.md`. Migrating it maps Claude Code fields to OpenCode fields:

| Claude Code | OpenCode |
|---|---|
| `name` | `name` (file name becomes agent name) |
| `description` | `description` |
| `team` | dropped (not an OpenCode concept) |
| `tools: Read, Write, Edit, ...` | `permission.read: allow` / `permission.edit: allow` / etc. |
| `model: sonnet/opus/haiku/inherit` | `model: provider/model-id` (map `sonnet` → `anthropic/claude-sonnet-4-20250514`, etc.) |
| `color` | `color` |
| (no mode field) | `mode: subagent` (this skill's migration-intent selection for child agents, not the OpenCode omission default) |

Source-harness cleanup is outside this skill's write scope: preserve `.claude/agents/{name}.md` and mark it read-only in the migration preview. Any later deletion or move is a separate owner-run operation. Persona-CV handling, preview, confirmation, execution, and prevalidation steps for this sub-flow are described in the Mandatory core migration workflow. The `op-agent-creator` does NOT modify `.claude/agents/*.md` (that is Marshal 🎖️ (HR Director) territory).

### Example model identifiers

Illustrative concrete model IDs used in this project's examples: `anthropic/claude-sonnet-4-20250514`.

## Mandatory core

### Pre-flight: Autoload guidelines

Load the guidelines below into the working context when they exist in the project. **Missing files degrade gracefully** — see Step 0.5. This skill is self-contained: the essential Quality Checklist is embedded in Step 6, so a project without the reference files can still scaffold valid agents.

#### Step 0.1 — Identify scenario

Classify the requested operation as exactly one of:

- `create` — new agent at `.opencode/agents/<name>.md` (no prior file exists)
- `modify` — existing OpenCode agent being edited; the current `<name>.md` exists at the path
- `migrate` — copying a Claude Code agent from `.claude/agents/<name>.md` to `.opencode/agents/<name>.md`
- `rename` / `add-prefix` — net effect is create + delete; treat as `modify` of the source plus `create` of the target

#### Step 0.2 — Read when present (regardless of scenario)

| File | Why | If absent |
|---|---|---|
| This project's shared-rules reference (see Project extensions) | Roster ownership table (per-agent rule boundaries) | Skip; use the roster in this project's docs |
| This project's agent-workflow entry (see Project extensions) | Authority map; keep files small; do not copy owner rulebooks | Skip; do not invent a competing workflow |
| This project's skill-migration reference (see Project extensions) | Field deltas, body renames, metadata defaults | Skip; use the embedded rules in this skill |
| This project's skills inventory (see Project extensions) | Inventory + uniqueness check + adjacent skill state | Skip; uniqueness checked against the agent directory on disk |
| The catalog steward agent's Quality Checklist section (see Project extensions) | QC-4 (WHAT + WHEN description) guidance; the agent-contract checks are embedded in Step 6 | Skip; the agent-contract checks are embedded in Step 6 |

#### Step 0.3 — Conditionally read

| Trigger | File | Why |
|---|---|---|
| Scenario = `modify` | `.opencode/agents/<name>.md` | Surface current spec before rewriting; preserve tone/structure unless explicitly changing |
| Scenario = `migrate` | The Claude Code agent's file (and `agents/<name>/profile.md`) | Source of truth for the conversion; persona CV preserved separately by Marshal 🎖️ |
| Agent will have specific permission keys | another existing agent as live reference (consulted at write-time) | Permission-key semantics reference |

#### Step 0.4 — Acknowledge each loaded file

After loading, the agent MUST emit one line per file:

```
guidelines loaded:
- shared-rules reference: loaded | skipped (not present)
- agent-workflow entry: loaded | skipped (not present)
- skill-migration reference: loaded | skipped (not present)
- skills inventory: loaded | skipped (not present)
- catalog steward Quality Checklist section: loaded | skipped (not present)
- <conditional file>: loaded | skipped (scenario=<X>, not applicable)
```

#### Step 0.5 — Missing-file handling (degraded mode)

If any Step 0.2 file is absent, proceed in **degraded mode**: rely on the embedded agent-contract checks (Step 6) and the rules in this skill. Note the gap in the post-edit audit section. Do NOT stop and block on a missing reference file — this skill must be usable in any project that ships it.

### What I do

Create a new OpenCode-native agent under `.opencode/agents/{name}.md`. The agent can be a **primary agent** (main session), a **subagent** (child session through the `subagent` tool), or **all** (either primary or child session). I collect the mode, system prompt body, permission model, and optional config (model, temperature, color, hidden flag, etc.); validate against OpenCode guidelines; and write the agent markdown file. A separate, non-default sub-flow migrates Claude Code agent specs to OpenCode.

### When to use me

- User wants to create a new OpenCode agent.
- User wants to define a custom subagent for a specific task.
- User wants to add a primary agent with a custom model or toolset.
- User wants a dual-use agent that supports both primary and child sessions (`mode: all`).
- User wants to set up an agent with restricted tool access (read-only, no bash, sandboxed, etc.).
- User wants to migrate a Claude Code agent spec to OpenCode format.
- Keywords: "agent", "subagent", "primary agent", "OpenCode agent", "custom agent", "@ mention", "Task tool", "permission model", "tool access", "restricted agent", "hidden agent".

### Steps

1. Take `name` from the request; if missing, report to Cipher 🔓 (Lead Orchestrator).
2. Validate `name` immediately:
   - 1–64 characters
   - Matches `^[a-z0-9]+(-[a-z0-9]+)*$`
   - Does not start or end with `-`
   - Does not contain `--`
   - Will become the file name (no `.md` extension in the YAML `name` field)
   - Is unique in `.opencode/agents/` (project-local check; the creator cannot check global paths — the user must ensure uniqueness across all locations)
   - If a file already exists at `.opencode/agents/{name}.md`, stop and report to Cipher 🔓 (Lead Orchestrator): overwrite, pick a different name, or abort. Never invoke the user-facing `question` tool from a delegated run.
     - **A.** Overwrite the existing file
     - **B.** Pick a different name
     - **C.** Abort
3. Require an explicit authored `mode`: `primary`, `subagent`, or `all`. If mode is missing, report to Cipher 🔓 (Lead Orchestrator); select **subagent** when the request already implies child-only intent, and write that value explicitly. This is the skill's intent-based selection, not the platform default: OpenCode V2 defaults a new custom agent to `primary` when mode is omitted ([Modes and Options / Mode](https://opencode.ai/v2/docs/agents)).
4. Branch to the matching sub-flow (primary, subagent, or all) — see sections below.
5. **Step 5 — Consistency check.** Verify the agent's `description` frontmatter field covers every major capability declared in the body (system prompt). A **subagent** description states WHAT it does and WHEN to dispatch it. A **primary** description is a brief behavioral summary, not a skill-style `Use when …` trigger. An **all** description satisfies both: a behavioral summary plus WHAT it does and WHEN to dispatch it as a child. For example:
   - If the body says "I review pull requests" but the description says "I write docs" → mismatch.
   - If the body is restricted to read-only tools but the description says "I edit and run tests" → mismatch.
   - If a capability is missing from the description, stop and report to Cipher 🔓 (Lead Orchestrator): auto-update, let the user edit, or abort. Never invoke the user-facing `question` tool from a delegated run.
     - **A.** Auto-update the description with a recommended addition
     - **B.** Let the user edit manually
      - **C.** Abort agent creation
6. **Step 6 — Pre-validation (agent-contract subset).** Generated specs must cite `knowledge/agents.md` `### Clean architecture (language-agnostic) (HARD RULE)` and must not tell a language section to suspend it. Before writing, run these checks against the fully built agent definition. The agent runtime-spec contract (Marshal 🎖️ (HR Director)'s Runtime Spec Format; Sentinel 🛡️ (Quality Guardian) rule SP-3) is authoritative; reference it for full text:

   ```
   - [ ] File is `.opencode/agents/<name>.md` — a single markdown file, not a folder — QC-1 (adapted)
   - [ ] Frontmatter `name` matches file basename — QC-2
   - [ ] Frontmatter `name` is kebab-case — QC-3
   - [ ] `description` 1-1024 chars, no `<`, `>`; subagent WHAT + WHEN to dispatch; primary behavioral summary, not a skill trigger; all satisfies both capability-based requirements - QC-4 (adapted for agents)
   - [ ] No `claude-` or `anthropic-` prefix — QC-5
   - [ ] No unfilled `{...}` placeholders — QC-13
   - [ ] Total under 5,000 words; body under 500 lines; static blocks >30 lines extracted — QC-14 / QC-27 (adapted)
   - [ ] Contract: frontmatter has `name`, `description`, and explicit `mode` (`primary` | `subagent` | `all`); all passes the relevant checks for both capabilities without expanding permissions or role authority
   - [ ] Contract: frontmatter has repository-metadata `version` in SemVer MAJOR.MINOR.PATCH form (`local-version` only on destination-derived specs)
    - [ ] Contract: technical framing present — H1 inside the core region and, for a governed roster spec, a persona reference line to agents/<name>/profile.md (no `> **Rule layout:**` marker)
   - [ ] Contract: if the Rulebook states language-specific rules, it opens with a language-agnostic subsection before the first language section, and no language section suspends the clean-architecture contract (SP-11, SP-12)
     - [ ] Contract: follow Marshal 🎖️ (HR Director)'s Runtime Spec Format and Sentinel 🛡️ (Quality Guardian) SP-3 — do not invent a competing layout. Exactly one `<!-- core:begin -->` … `<!-- core:end -->` pair immediately after the frontmatter closing `---`. Governed roster specs use all eight H3s in order under `## Mandatory core`: Your Role, Roster Context, Rulebook, Workflow, Tools and References, Output Format, Stop and Report, Hard Rules. Custom non-roster specs omit the persona line and `### Roster Context` explicitly and keep the other seven in core. Optional project markers only for evidenced local configuration, actual local grants, selected bindings, or local history. `### Hard Rules` is the last H3. A command named in the body is a reference form, not a grant; the frontmatter `permission` block is the configured grant.
   ```

   If any check FAILS, fix safe defects or report to Cipher 🔓 (Lead Orchestrator) before the write step (Step 10). Never invoke the user-facing `question` tool from a delegated run. Mandatory portable requirements, runtime validity, and shared/core agent-contract obligations cannot be waived by a generic override. A legitimate discretionary project-local exception must be explicitly permitted by its owning rule, approved by its authorized owner, and recorded with scope and rationale; it resolves that local choice, never a mandatory-check failure or a conflict with core. If the authority or applicability is unclear, stop and report rather than treating the check as optional.
7. If issues are found, stop and report to Cipher 🔓 (Lead Orchestrator) with a short recommendation: auto-fix if safe, request a corrected value, or abort.
   - **A.** Auto-fix the issue if safe
   - **B.** Let the user provide a corrected value
   - **C.** Abort agent creation
   - Include a short recommendation for each issue.
8. Apply the chosen fix and re-run the final prevalidation. Repeat until no issues remain or the user aborts.
9. Create the directory `.opencode/agents/` if it does not exist.
10. **Step 10 — Write file.** Write to `.opencode/agents/{name}.md` only after all mandatory checks pass and any permitted discretionary local exception is resolved and recorded under Step 6. Any unresolved or mandatory failed check halts the write and is reported to Cipher 🔓 (Lead Orchestrator); an override does not authorize a noncompliant spec.
11. Re-read the file to confirm it exists, frontmatter parses, and the file name matches the `name` field.

### Argument collection form

When the initial `name` or `mode` arguments are missing, invalid, or ambiguous, report to Cipher 🔓 (Lead Orchestrator) — never invoke the user-facing `question` tool from a delegated run.

#### Fields

| # | name | type | description | validation | options |
|---|---|---|---|---|---|
| 1 | `name` | `text` | Agent file name | `^[a-z0-9]+(-[a-z0-9]+)*$`, 1–64 chars | First option = parsed value with "(Recommended)" suffix |
| 2 | `mode` | `choice` | Main, child-only, or dual-use session agent | Explicit `primary`, `subagent`, or `all`; recommend subagent only for request-implied child-only intent | `[{ label: "primary", description: "Main session" }, { label: "subagent", description: "Child session through subagent tool" }, { label: "all", description: "Primary or child session" }]` |

#### Trigger conditions

| Trigger | Example |
|---|---|
| **Missing arg** | Name not provided, or mode not stated |
| **Validation failure** | Name fails regex (e.g., uppercase, underscores, double hyphens) |

Clean parse + clean validation = **no form** — agent proceeds directly. Later missing decisions are reported to Cipher 🔓 (Lead Orchestrator), not asked via the user-facing `question` tool on a delegated run.

### Sub-flow: primary agent

Take each field from the request; report missing required fields to Cipher 🔓 (Lead Orchestrator), then build the frontmatter:

| Field | Required? | Notes |
|---|---|---|
| `mode` | yes | must be `primary` |
| `description` | yes | 1–1024 chars; brief behavioral summary, NOT a usage trigger |
| `model` | optional | `provider/model-id` format; defaults to the globally configured model |
| `temperature` | optional | 0.0–1.0; lower is more focused, higher is more creative |
| `top_p` | optional | 0.0–1.0; alternative to temperature |
| `color` | optional | hex (`#FF5733`) or theme name (`primary`, `secondary`, `accent`, `success`, `warning`, `error`, `info`) |
| `steps` | optional | positive integer; max agentic iterations before forced summary |
| `disable` | optional | `true` to disable the agent |
| `prompt` | optional | external prompt file path; if unset, the markdown body IS the system prompt |
| `permission` | optional | take keys from the request; typical keys for a primary agent: `edit`, `bash`, `webfetch`, `websearch`, `skill`, `task`, `external_directory` |

> `hidden` controls visibility across modes, not security; do not reject it solely because mode is `primary`.

### Sub-flow: subagent (request-implied child-only intent)

Take each field from the request; report missing required fields to Cipher 🔓 (Lead Orchestrator), then build the frontmatter:

| Field | Required? | Notes |
|---|---|---|
| `mode` | yes | must be `subagent` |
| `description` | yes | 1–1024 chars; WHAT it does and WHEN to dispatch it |
| `model` | optional | defaults to the model of the invoking primary agent |
| `temperature` | optional | 0.0–1.0 |
| `top_p` | optional | 0.0–1.0 |
| `color` | optional | hex or theme name |
| `steps` | optional | positive integer |
| `disable` | optional | `true` to disable the agent |
| `hidden` | optional | controls visibility in normal listings, interactive discovery, and the subagent catalog; not a security boundary |
| `prompt` | optional | external prompt file path; if unset, the markdown body IS the system prompt |
| `permission` | optional | typically more restrictive than primary; typical keys: `read`, `edit`, `bash`, `webfetch`, `skill` |
| `permission.task` | optional | controls which other subagents this one can invoke via the Task tool; uses glob patterns with last-match-wins semantics |

### Sub-flow: all (primary or child session)

Require `mode: all` explicitly. Collect the shared fields from the primary and subagent sub-flows once; apply all relevant checks according to both capabilities. The description must summarize primary behavior and explain WHAT the agent does and WHEN to dispatch it as a child. For an omitted model, distinguish primary session model selection from child inheritance rather than assuming one context's default applies to both. `hidden` remains a visibility option across modes.

Use only the requested or evidenced permission configuration and existing role authority. Do not union permissive examples, inherit the most permissive branch, broaden grants, or add delegation rights because the agent is dual-use. Preserve applicable restrictions for both contexts; if requirements conflict or a required choice is unresolved, stop and report to Cipher 🔓 (Lead Orchestrator) before writing. Run the shared consistency and mandatory prevalidation checks once against the complete dual-use definition.

### Validation rules (centralized)

| Field | Rule |
|---|---|
| `name` | `^[a-z0-9]+(-[a-z0-9]+)*$`, 1–64 chars, no leading/trailing `-`, no `--` |
| `description` | 1–1024 chars |
| `mode` | Explicit `primary` \| `subagent` \| `all` required by this skill; platform omission default for a new custom agent is `primary`, not `all` |
| `temperature` | 0.0–1.0 (typical range) |
| `top_p` | 0.0–1.0 (typical range) |
| `color` | hex (`#RRGGBB`) or theme name |
| `steps` | positive integer |
| `hidden` | boolean, visibility option across all modes; not a permission grant |
| `disable` | boolean |
| `model` | `provider/model-id` format |
| `prompt` | string with `{file:./path}` syntax for external file, or omit to use the body |
| `permission` keys | see the table below |

#### Permission keys reference

| Key | Tools it gates |
|---|---|
| `read` | `read` |
| `edit` | `write`, `edit`, `apply_patch` |
| `glob` | `glob` |
| `grep` | `grep` |
| `list` | `list` |
| `bash` | `bash` |
| `task` | `task` |
| `external_directory` | any tool reading/writing outside the project worktree |
| `todowrite` | `todowrite`, `todoread` |
| `webfetch` | `webfetch` |
| `websearch` | `websearch` |
| `lsp` | `lsp` |
| `skill` | `skill` |
| `question` | `question` |
| `doom_loop` | recovery prompts when agent is stuck |

Each permission key accepts either a shorthand action (`"allow" | "ask" | "deny"`) or a pattern→action object for fine-grained control. **Last matching rule wins.**

This table names which keys gate which tools. It is a reference, not a grant. Example command strings elsewhere in this skill are reference forms. They do not authorize installing packages, changing permission config, selecting a runner, or executing a command. The grant that is actually configured is the `permission` block written into that agent's frontmatter (plus any evidenced local grant in a project region). Do not treat a reference command as permission to edit `opencode.json` / `opencode.jsonc`.

### Examples

Generated agent files follow the region-delimited eight-section contract in Marshal 🎖️ (HR Director)'s Runtime Spec Format (`.opencode/agents/marshal.md`) and Sentinel 🛡️ (Quality Guardian) SP-3. Cite those sources; do not treat this skill as a competing standard. No `> **Rule layout:**` marker is used.

Exactly one `<!-- core:begin -->` … `<!-- core:end -->` pair sits immediately after the frontmatter closing `---`. Technical framing is inside that core: an H1, and — for a governed roster spec only — the persona reference line `**Persona / personality:** see \`agents/<name>/profile.md\``. Then `## Mandatory core`. `### Hard Rules` is the last H3. When there is no evidenced local content, omit the project pair and end the core at EOF.

A **governed roster spec** (persona CV at `agents/<name>/profile.md`) uses the persona line and all eight H3s in order: `Your Role`, `Roster Context`, `Rulebook`, `Workflow`, `Tools and References`, `Output Format`, `Stop and Report`, `Hard Rules`. Persona content stays in the CV; the runtime spec does not duplicate it.

A **custom non-roster agent** (no CV) omits the persona reference line and `### Roster Context` explicitly, and still keeps `Your Role`, `Rulebook`, `Workflow`, `Tools and References`, `Output Format`, `Stop and Report`, and `Hard Rules` inside the core markers.

Reusable review, documentation, and diagnostic rules belong in core. Add `<!-- project:begin -->` … `<!-- project:end -->` only when the spec actually contains evidenced local configuration, actual local grants, selected operational bindings, or local history. A command named in the body is a reference form. The frontmatter `permission` block is the configured grant. Writing a reference command does not authorize installing packages, editing permission config, or running that command.

#### Governed roster spec (primary) — `code-reviewer`

See `references/governed-roster-code-reviewer.md` for the complete rendered `.opencode/agents/code-reviewer.md` example. It is illustrative; validate new specs against the current Runtime Spec Format and SP-3 rules.

#### Custom and hidden subagent examples

When creating custom or hidden subagents, read this skill's `references/custom-agent-examples.md` before rendering the agent spec. It contains the complete rendered `docs-writer` and `internal-helper` examples; validate new specs against the current Runtime Spec Format and SP-3 rules above.

### Migration: Claude Code → OpenCode

Use this when the user has an existing Claude Code agent spec and wants an OpenCode equivalent. **This sub-flow is never auto-applied** — the user must explicitly request the migration. The Claude Code field mapping and source-read-only rule live in Project extensions.

#### Steps

1. Read the existing Claude Code agent file (frontmatter + body).
2. Map its fields to OpenCode fields (see Project extensions for the concrete Claude Code mapping).
3. Keep the Claude Code agent file read-only. Report **Persona CV handling** to Cipher 🔓 (Lead Orchestrator) when `agents/{name}/profile.md` exists:
   - A. Keep the CV; OpenCode agent body references it via a single persona reference line.
   - B. Drop the CV; consolidate persona into the OpenCode agent body — **only for a custom (non-roster) agent**. When the target is a governed roster spec this option is unavailable: the CV/runtime split is mandatory — persona lives only in the persona CV and the runtime spec references it via the single line. Never duplicate persona content into a roster spec body.
   - C. Stop — migration requires human review of persona content.
4. Build a migration preview: list every OpenCode file to create or edit, and show the Claude Code source file as read-only/unchanged.
5. Report the preview to Cipher 🔓 (Lead Orchestrator) for confirmation. Never invoke the user-facing `question` tool from a delegated run.
6. Execute the migration: write `.opencode/agents/{name}.md` and update its body to reference the CV (if option A above); never move, edit, or delete the Claude Code source file.
7. Run a final prevalidation on the new agent and any edited reference files.
8. If issues are found, stop and report to Cipher 🔓 (Lead Orchestrator) with recommendations.
9. Apply the chosen fix and re-run prevalidation. Repeat until no issues remain or the user aborts.
10. Confirm completion and list all changed paths.

### Relationship to existing skills

| Skill | Scope | Distinction |
|---|---|---|
| `op-skill-creator` | Creates new OpenCode skills in `.opencode/skills/{name}/SKILL.md` | Different file shape (folder + SKILL.md vs single .md), different frontmatter fields, different body semantics (skill doc vs agent system prompt) |
| `customize-opencode` (built-in) | Edits or creates opencode config in `opencode.json` / `opencode.jsonc` and files under `.opencode/`, `~/.config/opencode/` | Broader config-ecosystem view; `op-agent-creator` is the focused, interactive, validated alternative for agent creation |
| `op-agent-creator` (this skill) | Creates new OpenCode agents in `.opencode/agents/{name}.md` with interactive validation | Focused on agents only; does not touch `opencode.jsonc` (markdown agents are auto-discovered) |

> The `op-agent-creator` does NOT modify `opencode.jsonc` (markdown agents in `.opencode/agents/` are auto-discovered, no registration needed).

### Troubleshooting

- **Pre-flight file autoload degraded:** the autoload step (Step 0) is conditional — reference files are loaded when present; if any are absent, proceed in degraded mode using the embedded Quality Checklist (Step 6) and note the gap in the post-edit audit section. Silent skip of a present-but-unread file is FORBIDDEN.
- **Agent does not show up after creation**: verify the file is at `.opencode/agents/{name}.md` (not `.opencode/agents/{name}/`), frontmatter has `description` and a valid `mode`, the file name matches the `name` convention, and `opencode.json` permissions are not set to `deny`.
- **Name rejected**: check for uppercase letters, underscores, leading/trailing hyphens, or double hyphens.
- **Description rejected**: ensure it is between 1 and 1024 characters.
- **`hidden: true` visibility confusion**: V2 hides agents from normal listings, interactive discovery, and the subagent catalog across modes. This is not a security boundary; use permissions to restrict behavior.
- **`task: deny` not preventing user invocation**: Task permissions gate which subagents an agent can invoke via the Task tool. Users can still invoke any subagent directly via the `@` autocomplete menu. This is by design.
- **Permission glob pattern not matching**: in `permission.bash` and `permission.task`, the **last matching rule wins**. Put the broad `*` wildcard first and the specific patterns after it, so a later specific rule overrides the wildcard.
- **`prompt` file not found**: when using `prompt: "{file:./prompts/foo.txt}"`, the path is relative to the directory containing `opencode.json` / `opencode.jsonc` (not the agent file). For project-local config, this is the project root.
- **Body not being used as system prompt**: if `prompt` is set to an external file, the body markdown is ignored. Remove `prompt` (or set it to empty) to use the body.
- **Mode missing or ambiguous**: write an explicit `primary`, `subagent`, or `all`; request-implied child-only intent selects `subagent`, not a platform default. Otherwise report the missing decision before writing. Do not reject `hidden` based solely on mode.
- **Missing core markers or eight-section contract**: the written file must match Marshal 🎖️ (HR Director)'s Runtime Spec Format and Sentinel 🛡️ (Quality Guardian) SP-3 (Step 6). A markerless body, optional heading layout, or reusable rules parked in a project region fails prevalidation. Fix the shape; do not treat a reference command in the body as permission to change grants.
