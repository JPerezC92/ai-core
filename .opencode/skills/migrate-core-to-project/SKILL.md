---
name: migrate-core-to-project
description: Migrate the AICore reusable core (skills, subagents, persona CVs, and shared infrastructure) into a target project, including the consistency pass that trims broken references and aligns roster lists. Use when the user wants to install or migrate the agent core into another project, copy agents or skills from AICore, or scaffold a project with the core tooling.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.0.0
  domain: opencode
---

## What I do

Migrate AICore's reusable, agnostic core into a target project. I analyze the target's stack, propose the applicable subset of skills/subagents/infra, preview the exact write manifest, then copy, adapt, and verify — ending with a consistency pass that removes broken references to agents that were not installed. I never run git; shipping (branch/commit/PR) happens separately.

## When to use me

- User wants to install or migrate the core into another project ("install AICore in X", "migrate the core to project X")
- User asks to copy agents, skills, or infrastructure from AICore into a target project
- User wants to scaffold a new project with the agent tooling
- Before a fresh project starts, to seed it with the git/planning/agent skills

Do NOT use me to create or edit skills or agents themselves — those are `op-skill-creator` and `op-agent-creator` territory.

## Arguments

From the user's request, extract:

- **target** — path to the destination project (required).
- **scope** — what to migrate. One of `skills-only`, `skills+infra`, `roster` (subagents + CVs), `named-agents` (specific agents), or `all` (default). If absent, default to `all`.
- **stack hints** — optional notes about the target (backend? incident/ticket system?) that influence what to include.

### Argument collection form

| name | type | validation | trigger |
|---|---|---|---|
| `target` | text | non-empty, points to a directory | not provided |
| `scope` | choice | one of skills-only / skills+infra / roster / named-agents / all | not provided |

Use one `question` call per missing argument. Do not add a manual "Other" option.

## Steps

### 1. Scope discovery (read-first)

Read the target project:
- Identify the stack (frontend-only, full-stack, etc.) from its manifest files
- Check for an existing `.opencode/` directory and any existing agents/skills
- Check whether the target has an incident/ticket system (ticket folders, support workflows)

Decide the applicable subset:

- **Skills** — always applicable: `git-branch-name`, `git-commit`, `git-pr`, `op-model`, `op-skill-creator`, `op-agent-creator`, `plan-enforce`. Skip `ticket-runbook` unless the target has an incident/ticket system.
- **Subagents + persona CVs** — pick by relevance:
  - Dev team (always relevant): `atrium`, `crucible`, `forge`, `herald`, `lumen`, `sentinel`, `warden`, `inquisitor`
  - Cross-cutting (relevant): `augur`, `marshal`
  - Backend: `bastion` — only if the target has backend code
  - Lead: Cipher — persona CV only, defined via `AGENTS.md` (no runtime spec)
  - Incident team (only with a ticket system): `investigator`, `ledger`, `quill`, `scribe`, `vault`
- **Infra** — always: `knowledge/agents.md`, `knowledge/debt.md`, `plans/`, `user-stories/`
- **Config** — `opencode.jsonc` permission gates (extract the permission block; do NOT copy model overrides), `AGENTS.md` (lead + installed roster)

### 2. Preview manifest (confirm before write)

Build the complete write manifest in memory: every file to copy, every file to edit. Present it to the user and confirm before any write. This is a mutation skill — never write without confirmation.

### 3. Copy

- Skills: copy `.opencode/skills/<name>` directories (only the selected set)
- Subagent specs: `.opencode/agents/<name>.md`
- Persona CVs: `agents/<name>/profile.md` — every spec references its CV with a single line; copy them as pairs
- Infra: `knowledge/agents.md`, `knowledge/debt.md`, `plans/.gitkeep`, `user-stories/.gitkeep`

### 4. Adapt

- **AGENTS.md** — write a lead-orchestrator form (Cipher identity → roster → shared rules → what's installed → conventions → reuse guide). List only the installed agents.
- **opencode.jsonc** — copy the permission safety gates only (destructive command denies, stash safety). Do NOT copy the source project's model overrides.
- **.gitignore** — add `commit.txt`, `pr-draft.md`, `output/`, `plans/.completed/`.
- **Build approvals** — if the target uses pnpm ≥ 11, approve native build scripts (`sharp`, `@swc/core`, `agent-browser`, `@parcel/watcher`, `unrs-resolver`) via `pnpm approve-builds`.

### 5. Consistency pass (mandatory)

After every copy, verify and fix cross-references. Verbatim copies are never internally consistent.

1. **Broken file pointers** — grep every copied spec for `.opencode/agents/<name>.md` and `agents/<name>/profile.md` references; any reference to an agent that was not installed must be removed or trimmed (e.g. `forge.md` reading `bastion.md` when bastion is not copied).
2. **Roster lists** — align every roster list (AGENTS.md, knowledge/agents.md ownership table, sentinel audit-scope lists, per-spec Roster Context) to the installed set. Stale lists are the most common bug.
3. **Non-installed team references** — de-reference the non-installed team from copied specs/CVs (e.g. incident-team mentions in `augur.md`/`marshal.md` roster context, Cipher CV delegation lines).
4. **Frontmatter** — every spec must have `name` (matching the filename), `description`, and `mode: subagent`. Missing `name` is a common verbatim-copy defect.
5. **CV ↔ spec reconciliation** — persona CVs and runtime specs must agree (e.g. if the spec forbids posting GitHub comments, the CV must not claim it posts them).
6. **Grammar/emoji** — persona CV H1 headings use `# Name Emoji — Role`; fix "a agent" → "an agent".

### 6. Verify

- **Pointer sweep** — loop `.opencode/agents/*.md` and `agents/*/profile.md` references; none may point to a non-installed agent.
- **Roster count** — AGENTS.md, knowledge/agents.md, and sentinel audit lists must name exactly the installed roster.
- **Frontmatter** — every spec has `name` = basename, `description`, `mode: subagent`.
- **Build** — run the target's build command (`pnpm build` or equivalent) — must pass.

## Core manifest (what AICore contains)

- **Skills to migrate** (8): `git-branch-name`, `git-commit`, `git-pr`, `op-agent-creator`, `op-model`, `op-skill-creator`, `plan-enforce`, `ticket-runbook`. The `migrate-core-to-project` skill itself stays in the source project — it is not copied into the target.
- **Subagent specs** (16): `atrium`, `augur`, `bastion`, `crucible`, `forge`, `herald`, `inquisitor`, `investigator`, `ledger`, `lumen`, `marshal`, `quill`, `scribe`, `sentinel`, `vault`, `warden`
- **Persona CVs** (16): the subagent set minus `investigator`, plus `cipher` (lead, CV-only)
- **Infra**: `knowledge/agents.md`, `knowledge/debt.md`, `plans/`, `user-stories/`
- **Config**: `AGENTS.md` (lead orchestrator), `opencode.jsonc` (permission gates)

## Examples

### Example 1 — frontend portfolio (dev team + cross-cutting + lead)

Target: a Next.js frontend project, no backend, no ticket system. Scope: `all`.

- Skills: all except `ticket-runbook`
- Agents: `atrium`, `crucible`, `forge`, `herald`, `lumen`, `sentinel`, `warden`, `inquisitor`, `augur`, `marshal`, `bastion` (deferred until a backend grows), plus Cipher lead
- Consistency pass removes: `bastion.md` reads in `forge.md`, incident-team references in `augur.md`/`marshal.md`/Cipher CV, sentinel audit lists trimmed to installed agents, missing `name:` frontmatter added

### Example 2 — skills-only install

Target: any project that wants the git/planning workflows without the agent roster. Scope: `skills+infra`.

- Copy the 7 applicable skills + `knowledge/agents.md`/`debt.md`, `plans/`, `user-stories/`
- Adapt `.gitignore` and `opencode.jsonc`; no AGENTS.md roster, no subagents

## Troubleshooting

- **Copied spec references an agent that was not installed** — e.g. `forge.md` reads `.opencode/agents/bastion.md`. Cause: verbatim copy of a spec written for the full roster. Fix: trim the reference (warmup read, gate, roster line) to the installed set.
- **Roster list names agents that were not installed after a later agent addition** — Cause: a trim became stale when the roster grew. Fix: re-run step 5, align every roster list to the current installed set.
- **Spec is missing `name:` frontmatter** — Cause: the source project shipped the spec without it. Fix: add lowercase `name` matching the filename, plus `description` and `mode: subagent`.
- **CV and runtime spec disagree** — e.g. the CV claims the agent posts GitHub comments, the spec forbids it. Cause: separate files drifting. Fix: align the CV to the spec's Hard Rules.
- **`pnpm build` fails after install** — Cause: native build scripts ignored by pnpm 11. Fix: run `pnpm approve-builds` and rebuild.
