<!--
HARD RULE — fill every Step / Output / Gate / Abort. No `TBD` placeholders. Agent improvisation forbidden.
-->

# Phase 5 — Update migrate-core-to-project infra lists

> **Owner:** Vault 🔐 (Catalog Steward)
> **Pre:** Phases 1-4 gates passed.
> **Reads:** `.opencode/skills/migrate-core-to-project/SKILL.md` (all Infra references)
> **Writes:** `.opencode/skills/migrate-core-to-project/SKILL.md` (edited)

## Steps

1. In `.opencode/skills/migrate-core-to-project/SKILL.md`, add `knowledge/symptoms.md` + `knowledge/problems.md` to every Infra list:
   - Step 1 Scope discovery, Infra bullet: `**Infra** — always: \`knowledge/agents.md\`, \`knowledge/debt.md\`, \`knowledge/symptoms.md\`, \`knowledge/problems.md\`, \`plans/\`, \`user-stories/\``
   - Step 3 Copy, infra bullet: add `knowledge/symptoms.md`, `knowledge/problems.md` to the copied infra files.
   - Core manifest, Infra line: `**Infra**: \`knowledge/agents.md\`, \`knowledge/debt.md\`, \`knowledge/symptoms.md\`, \`knowledge/problems.md\`, \`plans/\`, \`user-stories/\``
   - Example 2 (skills+infra install): add the two knowledge files to the copy description.
2. Do not change the count claims ("Skills to migrate (8)", "Subagent specs (16)", "Persona CVs (16)") — the counts are unchanged; only the Infra lists grow.

## Output

- **Artifact:** `.opencode/skills/migrate-core-to-project/SKILL.md` (edited)
- **Schema / shape:** every Infra list names all four knowledge files; no count claim altered.

## Gate

- ⬜ `grep -c 'knowledge/symptoms.md' .opencode/skills/migrate-core-to-project/SKILL.md` → >=4.
- ⬜ `grep -c 'knowledge/problems.md' .opencode/skills/migrate-core-to-project/SKILL.md` → >=4.
- ⬜ `grep -cE '\(8\)|\(16\)' .opencode/skills/migrate-core-to-project/SKILL.md` → count claims still present.

## Abort conditions

- Halt if an Infra list is missed (skill consistency bug) — every list must name both files.
- Halt if a count claim (8 skills / 16 subagents / 16 CVs) is altered.

## Tool whitelist / blacklist

- Whitelist: read tools; edit on `.opencode/skills/migrate-core-to-project/SKILL.md`.
- Blacklist: edits to `AGENTS.md`, `knowledge/*.md`, or other skills in this phase.
