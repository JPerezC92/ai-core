---
name: op-agent-creator
description: Scaffold a new OpenCode agent (primary or subagent) by collecting mode, system prompt, and permission model; validating name, description, and frontmatter against the OpenCode agent guidelines; and writing the agent markdown to .opencode/agents/{name}.md. Use when the user wants to create a new OpenCode agent, define a custom subagent, add a primary agent, set up an agent with restricted tool access, or migrate a Claude Code agent spec to OpenCode format.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.1.0
---

# op-agent-creator

> **Rule layout:** two-section-v1

## Project extensions

### Knowledge hooks

This project's pre-flight knowledge hooks are the files `knowledge/agents.md`, `knowledge/skill-migration-reference.md`, `knowledge/skills.md`, and `.opencode/agents/vault.md` (Quality Checklist section). `knowledge/skill-migration-reference.md` and `knowledge/skills.md` are destination-specific hooks and may be absent; the skill degrades gracefully when they are.

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
| (no mode field) | `mode: subagent` (default — Claude Code agents are all subagent-equivalent in OpenCode terms) |

Old-file cleanup for this harness: delete `.claude/agents/{name}.md`, move it to `.claude/agents/_deprecated/{name}.md`, or keep it as-is. Persona-CV handling, preview, confirmation, execution, and prevalidation steps for this sub-flow are described in the Mandatory core migration workflow. The `op-agent-creator` does NOT modify `.claude/agents/*.md` (that is Marshal 🎖️ (HR Director) territory).

### Example model identifiers

Illustrative concrete model IDs used in this project's examples: `anthropic/claude-sonnet-4-20250514`.

## Mandatory core

### Pre-flight: Autoload guidelines

Load the guidelines below into the working context when they exist in the project. **Missing files degrade gracefully** — see Step 0.5. This skill is self-contained: the essential Quality Checklist is embedded in Step 6, so a project without the reference files can still scaffold valid agents.

#### Step 0.1 — Identify scenario

Classify the requested operation as exactly one of:

- `create` — new agent at `.opencode/agents/<name>.md` (no prior file exists)
- `modify` — existing OpenCode agent being edited; the current `<name>.md` exists at the path
- `migrate` — copying an agent from another harness's agent directory to `.opencode/agents/<name>.md`
- `rename` / `add-prefix` — net effect is create + delete; treat as `modify` of the source plus `create` of the target

#### Step 0.2 — Read when present (regardless of scenario)

| File | Why | If absent |
|---|---|---|
| This project's shared-rules reference (see Project extensions) | Roster ownership table (per-agent rule boundaries) | Skip; use the roster in this project's docs |
| This project's skill-migration reference (see Project extensions) | Field deltas, body renames, metadata defaults | Skip; use the embedded rules in this skill |
| This project's skills inventory (see Project extensions) | Inventory + uniqueness check + adjacent skill state | Skip; uniqueness checked against the agent directory on disk |
| The catalog steward agent's Quality Checklist section (see Project extensions) | QC-4 (WHAT + WHEN description) guidance; the agent-contract checks are embedded in Step 6 | Skip; the agent-contract checks are embedded in Step 6 |

#### Step 0.3 — Conditionally read

| Trigger | File | Why |
|---|---|---|
| Scenario = `modify` | `.opencode/agents/<name>.md` | Surface current spec before rewriting; preserve tone/structure unless explicitly changing |
| Scenario = `migrate` | The source agent's file (and `agents/<name>/profile.md`) | Source of truth for the conversion; persona CV preserved separately by Marshal 🎖️ |
| Agent will have specific permission keys | another existing agent as live reference (consulted at write-time) | Permission-key semantics reference |

#### Step 0.4 — Acknowledge each loaded file

After loading, the agent MUST emit one line per file:

```
guidelines loaded:
- shared-rules reference: loaded | skipped (not present)
- skill-migration reference: loaded | skipped (not present)
- skills inventory: loaded | skipped (not present)
- catalog steward Quality Checklist section: loaded | skipped (not present)
- <conditional file>: loaded | skipped (scenario=<X>, not applicable)
```

#### Step 0.5 — Missing-file handling (degraded mode)

If any Step 0.2 file is absent, proceed in **degraded mode**: rely on the embedded agent-contract checks (Step 6) and the rules in this skill. Note the gap in the post-edit audit section. Do NOT stop and block on a missing reference file — this skill must be usable in any project that ships it.

### What I do

Create a new OpenCode-native agent under `.opencode/agents/{name}.md`. The agent can be a **primary agent** (user-switchable via the Tab key) or a **subagent** (invoked via `@mention` or by another agent's Task tool). I collect the mode, system prompt body, permission model, and optional config (model, temperature, color, hidden flag, etc.); validate everything against the OpenCode agent guidelines; and write the agent markdown file. I also cover migrating an existing agent spec from another harness to its OpenCode equivalent in a separate, non-default sub-flow.

### When to use me

- User wants to create a new OpenCode agent.
- User wants to define a custom subagent for a specific task.
- User wants to add a primary agent with a custom model or toolset.
- User wants to set up an agent with restricted tool access (read-only, no bash, sandboxed, etc.).
- User wants to migrate an agent spec from another harness to OpenCode format.
- Keywords: "agent", "subagent", "primary agent", "OpenCode agent", "custom agent", "@ mention", "Task tool", "permission model", "tool access", "restricted agent", "hidden agent".

### Steps

1. Ask for the new agent's `name` if not provided.
2. Validate `name` immediately:
   - 1–64 characters
   - Matches `^[a-z0-9]+(-[a-z0-9]+)*$`
   - Does not start or end with `-`
   - Does not contain `--`
   - Will become the file name (no `.md` extension in the YAML `name` field)
   - Is unique in `.opencode/agents/` (project-local check; the creator cannot check global paths — the user must ensure uniqueness across all locations)
   - If a file already exists at `.opencode/agents/{name}.md`, ask the user via multiple-choice question:
     - **A.** Overwrite the existing file
     - **B.** Pick a different name
     - **C.** Abort
3. Ask: "Is this a **primary agent** or a **subagent**?" (default: **subagent** — more common case for new agents).
4. Branch to the matching sub-flow (primary or subagent) — see sections below.
5. **Step 5 — Consistency check.** Verify the agent's `description` frontmatter field covers every major capability declared in the body (system prompt). Cross-reference the Vault 🔐 (Catalog Steward) Quality Checklist (file loaded in Step 0.2) — specifically item QC-4 (description has WHAT + WHEN + "Use when …" — adapted for agents: WHAT the agent does + WHEN to dispatch it) and the agent body completeness rules. For example:
   - If the body says "I review pull requests" but the description says "I write docs" → mismatch.
   - If the body is restricted to read-only tools but the description says "I edit and run tests" → mismatch.
   - If a capability is missing from the description, stop and ask the user via multiple-choice question:
     - **A.** Auto-update the description with a recommended addition
     - **B.** Let the user edit manually
     - **C.** Ignore the mismatch and continue
6. **Step 6 — Pre-validation (agent-contract subset).** Before writing, run these checks against the fully built agent definition. The agent runtime-spec contract (Marshal 🎖️ (HR Director)'s Runtime Spec Format; Sentinel 🛡️ (Quality Guardian) rule SP-3) is authoritative; reference it for full text:

   ```
   - [ ] File is `.opencode/agents/<name>.md` — a single markdown file, not a folder — QC-1 (adapted)
   - [ ] Frontmatter `name` matches file basename — QC-2
   - [ ] Frontmatter `name` is kebab-case — QC-3
   - [ ] `description` 1–1024 chars, no `<`, `>`, has WHAT + WHEN — QC-4 (adapted for agents)
   - [ ] No `claude-` or `anthropic-` prefix — QC-5
   - [ ] No unfilled `{...}` placeholders — QC-13
   - [ ] Total under 5,000 words; body under 500 lines; static blocks >30 lines extracted — QC-14 / QC-27 (adapted)
   - [ ] Contract: frontmatter has `name`, `description`, and `mode` (`primary` | `subagent`)
   - [ ] Contract: frontmatter has repository-metadata `version` in SemVer MAJOR.MINOR.PATCH form (`local-version` only on destination-derived specs)
   - [ ] Contract: technical framing present — H1, the visible marker line > **Rule layout:** two-section-v1, and, for a governed roster spec, a persona reference line to agents/<name>/profile.md
   - [ ] Contract: exactly two ownership H2 sections in order — ## Project extensions then ## Mandatory core — with no operational prose outside them
   - [ ] Contract: ### Hard Rules is the last subsection of ## Mandatory core
   ```

   If any check FAILS, fix or surface to user via the `question` tool before the write step (Step 10).
7. If issues are found, stop and ask the user via multiple-choice question:
   - **A.** Auto-fix the issue if safe
   - **B.** Let the user provide a corrected value
   - **C.** Abort agent creation
   - Include a short recommendation for each issue.
8. Apply the chosen fix and re-run the final prevalidation. Repeat until no issues remain or the user aborts.
9. Create the directory `.opencode/agents/` if it does not exist.
10. **Step 10 — Write file.** Write to `.opencode/agents/{name}.md`. If any Quality Checklist check failed in Step 6 and was not explicitly overridden by the user, halt here and ask.
11. Re-read the file to confirm it exists, frontmatter parses, and the file name matches the `name` field.

### Argument collection form

When the initial `name` or `mode` arguments are missing, invalid, or ambiguous, use the `question` tool to collect corrections — never re-ask in plain text. Full convention: this project's conventions reference § "Skill argument form-fill convention" (see Project extensions).

#### Fields

| # | name | type | description | validation | options |
|---|---|---|---|---|---|
| 1 | `name` | `text` | Agent file name | `^[a-z0-9]+(-[a-z0-9]+)*$`, 1–64 chars | First option = parsed value with "(Recommended)" suffix |
| 2 | `mode` | `choice` | Primary or subagent | — | `[{ label: "subagent (Recommended)", description: "Invoked via @mention or Task tool" }, { label: "primary", description: "User-switchable via Tab key" }]` |

#### Trigger conditions

| Trigger | Example |
|---|---|
| **Missing arg** | Name not provided, or mode not stated |
| **Validation failure** | Name fails regex (e.g., uppercase, underscores, double hyphens) |

Clean parse + clean validation = **no form** — agent proceeds directly. Steps 3–11 already use multi-choice questions for later fields (overwrite/pick-new, auto-fix/manual/abort) — those are fine as-is.

### Sub-flow: primary agent

Ask the user for each field, then build the frontmatter:

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
| `permission` | optional | ask which permission keys to set and what action; typical keys for a primary agent: `edit`, `bash`, `webfetch`, `websearch`, `skill`, `task`, `external_directory` |

> `hidden` is NOT applicable for primary agents. Reject if the user tries to set it.

### Sub-flow: subagent (default)

Ask the user for each field, then build the frontmatter:

| Field | Required? | Notes |
|---|---|---|
| `mode` | yes | must be `subagent` |
| `description` | yes | 1–1024 chars; brief behavioral summary |
| `model` | optional | defaults to the model of the invoking primary agent |
| `temperature` | optional | 0.0–1.0 |
| `top_p` | optional | 0.0–1.0 |
| `color` | optional | hex or theme name |
| `steps` | optional | positive integer |
| `disable` | optional | `true` to disable the agent |
| `hidden` | optional | `true` to hide from `@` autocomplete; can still be invoked by other agents via the Task tool |
| `prompt` | optional | external prompt file path; if unset, the markdown body IS the system prompt |
| `permission` | optional | typically more restrictive than primary; typical keys: `read`, `edit`, `bash`, `webfetch`, `skill` |
| `permission.task` | optional | controls which other subagents this one can invoke via the Task tool; uses glob patterns with last-match-wins semantics |

### Validation rules (centralized)

| Field | Rule |
|---|---|
| `name` | `^[a-z0-9]+(-[a-z0-9]+)*$`, 1–64 chars, no leading/trailing `-`, no `--` |
| `description` | 1–1024 chars |
| `mode` | `primary` \| `subagent` \| `all` (default `all` if omitted) |
| `temperature` | 0.0–1.0 (typical range) |
| `top_p` | 0.0–1.0 (typical range) |
| `color` | hex (`#RRGGBB`) or theme name |
| `steps` | positive integer |
| `hidden` | boolean, subagent only |
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

### Examples

Every generated agent uses the two-section ownership layout: H1, the visible `> **Rule layout:** two-section-v1` marker, then exactly two ownership H2 sections — `## Project extensions` then `## Mandatory core` — with `### Hard Rules` last. A **governed roster spec** (one backed by a persona CV at `agents/<name>/profile.md`) additionally carries the persona reference line; a custom agent without a CV omits it.

Only technical framing may precede `## Project extensions`: the H1, the marker, an optional `> **Spec version:**`/version line, and (for a governed spec) the persona reference line. A role description belongs in `### Your Role` under `## Mandatory core` — never as prose in the framing, which the layout checker rejects as operational prose outside the ownership sections.

#### Governed roster spec (primary) — `code-reviewer`

`.opencode/agents/code-reviewer.md`:

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices. Use when a diff needs a quality, bug, performance, or security review.
mode: primary
version: 1.0.0
model: provider/model-id
temperature: 0.1
permission:
  edit: deny
  bash:
    "*": ask
    "git diff": allow
    "git log*": allow
    "grep *": allow
---

# Code Reviewer — Quality Reviewer

> **Rule layout:** two-section-v1

**Persona / personality:** see `agents/code-reviewer/profile.md` (source of truth — do not duplicate here).

## Project extensions

### Review conventions
- Code quality and best practices
- Performance implications

## Mandatory core

### Your Role

Review diffs and return constructive feedback without making direct changes.

### Hard Rules

- Never edit source — report only.
- Never approve a change you have not read in full.
```

#### Custom subagent — `docs-writer`

`.opencode/agents/docs-writer.md`:

```markdown
---
name: docs-writer
description: Writes and maintains project documentation. Use when docs need to be created or updated.
mode: subagent
version: 1.0.0
permission:
  bash: deny
---

# Docs Writer

> **Rule layout:** two-section-v1

## Project extensions

### Documentation standards
- Clear explanations
- Proper structure
- Code examples

## Mandatory core

### Your Role

Create clear, comprehensive documentation.

### Hard Rules

- Never edit source code.
- Never publish without human review.
```

#### Hidden subagent — `internal-helper`

`.opencode/agents/internal-helper.md`:

```markdown
---
name: internal-helper
description: Internal subagent for system-level diagnostics. Use when another agent needs diagnostics via the Task tool.
mode: subagent
version: 1.0.0
hidden: true
permission:
  edit: deny
  bash: ask
---

# Internal Helper

> **Rule layout:** two-section-v1

## Project extensions

### Diagnostics scope
- System-level diagnostics

## Mandatory core

### Your Role

Run system-level diagnostics and return findings.

### Hard Rules

- Never edit files.
- Never run destructive commands.
```

### Migration: another harness → OpenCode

Use this when the user has an existing agent spec from another harness and wants an OpenCode equivalent. **This sub-flow is never auto-applied** — the user must explicitly request the migration. The concrete Claude Code field mapping and cleanup options live in Project extensions.

#### Steps

1. Read the existing source-harness file (frontmatter + body).
2. Map the source-harness fields to OpenCode fields (see Project extensions for the concrete Claude Code mapping).
3. Ask the user via multiple-choice question:
   - **Old file cleanup**
     - A. Delete the old source-harness agent file
     - B. Move the old file to the source harness's `_deprecated/` directory
     - C. Keep the old file as-is
   - **Persona CV handling** (if `agents/{name}/profile.md` exists)
     - A. Keep the CV; OpenCode agent body references it via a single persona reference line
     - B. Drop the CV; consolidate persona into the OpenCode agent body — **only for a custom (non-roster) agent**. When the target is a governed roster spec this option is unavailable: the CV/runtime split is mandatory — persona lives only in the persona CV and the runtime spec references it via the single line. Never duplicate persona content into a roster spec body.
     - C. Stop — migration requires human review of persona content
4. Build a migration preview: list every file to create, move, edit, or delete.
5. Ask the user to confirm the preview.
6. Execute the migration: write `.opencode/agents/{name}.md`, copy/move the old file as chosen, update the body to reference the CV (if option A above).
7. Run a final prevalidation on the new agent and any edited reference files.
8. If issues are found, stop and ask the user via multiple-choice question with recommendations.
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
- **`hidden: true` not hiding the agent**: `hidden` only affects `@` autocomplete; the agent can still be invoked by other agents via the Task tool, AND users can still invoke it directly via `@`. Task permissions only affect programmatic invocation.
- **`task: deny` not preventing user invocation**: Task permissions gate which subagents an agent can invoke via the Task tool. Users can still invoke any subagent directly via the `@` autocomplete menu. This is by design.
- **Permission glob pattern not matching**: in `permission.bash` and `permission.task`, the **last matching rule wins**. Put the broad `*` wildcard first and the specific patterns after it, so a later specific rule overrides the wildcard.
- **`prompt` file not found**: when using `prompt: "{file:./prompts/foo.txt}"`, the path is relative to the directory containing `opencode.json` / `opencode.jsonc` (not the agent file). For project-local config, this is the project root.
- **Body not being used as system prompt**: if `prompt` is set to an external file, the body markdown is ignored. Remove `prompt` (or set it to empty) to use the body.
- **Mode mismatch with hidden flag**: `hidden: true` is only valid with `mode: subagent`. The `op-agent-creator` rejects `hidden` set on primary agents.
