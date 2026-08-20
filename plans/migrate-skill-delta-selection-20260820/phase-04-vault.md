<!--
HARD RULE — fill every Step / Output / Gate / Abort. No `TBD` placeholders. Agent improvisation forbidden.
-->

# Phase 4 — Arguments + description rewrite

> **Owner:** Vault 🔐 (Catalog Steward)
> **Pre:** Phase 3 gate passed.
> **Reads:** `.opencode/skills/migrate-core-to-project/SKILL.md` (frontmatter description, Arguments section, Argument collection form)
> **Writes:** `.opencode/skills/migrate-core-to-project/SKILL.md` (edited — description + Arguments)

## Steps

1. Update the frontmatter `description` (line 3) to reflect incremental behavior. New text:
   `description: Migrate the AICore reusable core (skills, subagents, persona CVs, and shared infrastructure) into a target project — deterministically. Computes an installed-set inventory from a structured manifest, presents a selectable list of only the missing eligible items, copies idempotently, merges config, and runs a union consistency pass with a re-diff verification. Use when the user wants to install or migrate the agent core into another project, migrate just the remaining missing items incrementally, copy agents or skills from AICore, or scaffold a project with the core tooling.`

2. Rewrite the `## Arguments` section and `### Argument collection form`:
   - `target` — path to the destination project (required).
   - `scope` — coarse Kind-prefilter narrowing the selection step. One of `all` (default), `skills`, `agents`, `infra`, `config`. `all` = no prefilter; `skills`/`agents`/`infra`/`config` limit the multi-select to that Kind group. This is NOT the old `skills-only`/`roster`/`named-agents` enum — fine-grained selection now happens in step 2.
   - `stack hints` — optional notes about the target that assist marker detection (backend? ticket system?).
   - Update the collection-form table: `scope` validation becomes `one of all / skills / agents / infra / config`.
   - Keep "Use one `question` call per missing argument. Do not add a manual 'Other' option."

3. Do not touch the `## What I do` / `## When to use me` sections beyond what is already correct; if they mention the old scope enum, align them to the new prefilter wording.

## Output

- **Artifact:** `.opencode/skills/migrate-core-to-project/SKILL.md` (edited)
- **Schema / shape:** description mentions incremental + deterministic + selectable list; scope is a Kind-prefilter enum `all/skills/agents/infra/config`; old enum values (`skills-only`, `skills+infra`, `roster`, `named-agents`) gone.

## Gate

- ⬜ `grep -c 'Kind-prefilter' .opencode/skills/migrate-core-to-project/SKILL.md` → >=1.
- ⬜ `grep -c 'all / skills / agents / infra / config' .opencode/skills/migrate-core-to-project/SKILL.md` → >=1.
- ⬜ `grep -c 'selectable list' .opencode/skills/migrate-core-to-project/SKILL.md` → >=1 (description).
- ⬜ Old enum gone: `grep -cE 'skills-only|skills\+infra|named-agents|roster \(subagents' .opencode/skills/migrate-core-to-project/SKILL.md` → 0.

## Abort conditions

- Halt if any old scope value survives (`skills-only`, `skills+infra`, `roster`, `named-agents`) — the redesign must not leave a stale enum.
- Halt if the `target` argument or the "one question call per missing argument" rule is altered.

## Tool whitelist / blacklist

- Whitelist: read tools; edit on `.opencode/skills/migrate-core-to-project/SKILL.md`.
- Blacklist: edits to any other skill, agent spec, CV, or `knowledge/` file in this phase.
