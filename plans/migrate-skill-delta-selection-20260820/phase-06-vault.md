<!--
HARD RULE — fill every Step / Output / Gate / Abort. No `TBD` placeholders. Agent improvisation forbidden.
-->

# Phase 6 — Derive scope from Kind

> **Owner:** Vault 🔐 (Catalog Steward)
> **Pre:** Phase 5 gate passed.
> **Reads:** `.opencode/skills/migrate-core-to-project/SKILL.md` (Arguments, `## Core manifest`, Kind column)
> **Writes:** `.opencode/skills/migrate-core-to-project/SKILL.md` (edited)

## Steps

1. Insert a `## Kind vocabulary` section immediately before `## Core manifest`:
   - Intro line: "Kind is a closed set of 4 values:"
   - Table `| Kind | Meaning | Selectable? |` with rows:
     - `skill` | a skill directory under `.opencode/skills/` | yes
     - `agent` | a roster member — `.opencode/agents/<name>.md` and/or `agents/<name>/profile.md` | yes
     - `infra` | a shared-infra file or dir (`knowledge/`, `plans/`, `user-stories/`) | yes
     - `config` | a merge target (`AGENTS.md`, `opencode.jsonc`, `.gitignore`) | no — merge-only, step 4
   - `Hard corollaries:` bullets:
     - File count lives in the **Source** column, never in a new Kind. `investigator` (spec-only) and `cipher` (CV-only) are Kind `agent`; their reduced file set is expressed by Source.
     - `config` has **no `scope` value** because it is not selectable.
     - **No 5th Kind.** Any future special case is encoded via Source + Include-rule, not a new Kind value.

2. In `## Arguments`, rewrite the `scope` bullet as a derivation:
   - `scope` = `all` (default), or the plural of any selectable Kind (`skill`→`skills`, `agent`→`agents`, `infra`→`infra`). Derived from the Kind column, never hand-written. `config` has no scope value — it is a merge target, never selectable. Fine-grained selection happens in step 2, not here.

3. In `### Argument collection form`, change the `scope` validation to:
   - `| \`scope\` | choice | all / skills / agents / infra (derived from selectable Kinds) | not provided |`

## Output

- **Artifact:** `.opencode/skills/migrate-core-to-project/SKILL.md` (edited)
- **Schema / shape:** `## Kind vocabulary` block (4 Kinds + 3 hard corollaries) before `## Core manifest`; `scope` argument and collection-form express the derivation; `config` excluded from scope; no invented Kind.

## Gate

- ⬜ `grep -c 'Kind vocabulary' .opencode/skills/migrate-core-to-project/SKILL.md` → 1.
- ⬜ `grep -cE 'derived from the Kind column|Derived from the Kind column|never hand-written' .opencode/skills/migrate-core-to-project/SKILL.md` → >=1.
- ⬜ `grep -c 'No 5th Kind' .opencode/skills/migrate-core-to-project/SKILL.md` → >=1.
- ⬜ `grep -c 'config.*no.*scope.*value\|config.*has no.*scope.*value' .opencode/skills/migrate-core-to-project/SKILL.md` → >=1.
- ⬜ `grep -c 'derived from selectable Kinds' .opencode/skills/migrate-core-to-project/SKILL.md` → >=1.
- ⬜ `grep -c '| cv |' .opencode/skills/migrate-core-to-project/SKILL.md` → 0 (no stray Kind remains).

## Abort conditions

- Halt if `scope` is re-enumerated as a hand-written literal instead of derived from Kind.
- Halt if a 5th Kind value appears anywhere in the manifest Kind column.

## Tool whitelist / blacklist

- Whitelist: read tools; edit on `.opencode/skills/migrate-core-to-project/SKILL.md`.
- Blacklist: edits to any other skill, agent spec, CV, or `knowledge/` file in this phase.
