<!--
HARD RULE — fill every Step / Output / Gate / Abort. No `TBD` placeholders. Agent improvisation forbidden.
-->

# Phase 5 — Merge symptom pair into atomic item

> **Owner:** Vault 🔐 (Catalog Steward)
> **Pre:** Phase 4 gate passed.
> **Reads:** `.opencode/skills/migrate-core-to-project/SKILL.md` (manifest table, step 1, step 2, step 3, Example 2)
> **Writes:** `.opencode/skills/migrate-core-to-project/SKILL.md` (edited)

## Steps

1. In the `## Core manifest` table, replace the two separate infra rows with one atomic row:
   - From (two rows):
     ```
     | `knowledge/symptoms.md` | infra | `knowledge/symptoms.md` | `<target>/knowledge/symptoms.md` | always |
     | `knowledge/problems.md` | infra | `knowledge/problems.md` | `<target>/knowledge/problems.md` | always |
     ```
   - To (one row):
     ```
     | `symptom-problem-register` | infra | `knowledge/symptoms.md` + `knowledge/problems.md` | `<target>/knowledge/symptoms.md` + `<target>/knowledge/problems.md` | always |
     ```
   - No `Requires` column. The pair is inseparable because it is one row.

2. In `### 1. Inventory (deterministic)`, generalize the infra presence rule to cover multi-file items. Change the `infra` bullet from:
   - `infra → <target>/knowledge/<file> (or the .gitkeep) exists?`
   - To: `infra → each file in the item's Source exists? A multi-file item (e.g. symptom-problem-register) is present when ALL its files exist, partial when exactly one does, missing when none do.`
   - Keep the existing `partial` FAILS CLOSED paragraph unchanged (it already covers this).

3. In `### 2. Select items`, note the atomic item lists as ONE option. Under the infra grouping bullet, add:
   - `- a multi-file infra item (symptom-problem-register) is listed as ONE option, not one per file.`
   - The option's description must cite both destination paths.

4. In `### 3. Copy (idempotent)`, the infra copy bullet already says "copy the specific file (or .gitkeep)". Amend to:
   - `- **Infra:** copy every file in the item's Source (a multi-file item copies all its files as one unit).`

5. In `### Example 2 — skills and infra install`, update the copy description line:
   - From: `- Copy the 7 applicable skills + \`knowledge/agents.md\`, \`knowledge/debt.md\`, \`knowledge/symptoms.md\`, \`knowledge/problems.md\`, \`plans/\`, \`user-stories/\``
   - To: `- Copy the 7 applicable skills + \`knowledge/agents.md\`, \`knowledge/debt.md\`, the \`symptom-problem-register\` item (\`knowledge/symptoms.md\` + \`knowledge/problems.md\`), \`plans/\`, \`user-stories/\``

## Output

- **Artifact:** `.opencode/skills/migrate-core-to-project/SKILL.md` (edited)
- **Schema / shape:** manifest has one `symptom-problem-register` infra row (Source/Destination list both files); step 1 documents the multi-file presence rule; step 2 lists the atomic item as one option; step 3 copies all files of the item as a unit; Example 2 prose updated. No `Requires` column anywhere.

## Gate

- ⬜ `grep -c 'symptom-problem-register' .opencode/skills/migrate-core-to-project/SKILL.md` → >=2 (manifest row + step 2 note + example).
- ⬜ `grep -c 'knowledge/symptoms.md.*knowledge/problems.md' .opencode/skills/migrate-core-to-project/SKILL.md` → >=1 (merged Source lists both files).
- ⬜ Old separate rows gone: `grep -c '^| \`knowledge/symptoms.md\` | infra' .opencode/skills/migrate-core-to-project/SKILL.md` → 0.
- ⬜ Old separate rows gone: `grep -c '^| \`knowledge/problems.md\` | infra' .opencode/skills/migrate-core-to-project/SKILL.md` → 0.
- ⬜ Multi-file presence rule present: `grep -cE 'multi-file|when ALL its files|when exactly one' .opencode/skills/migrate-core-to-project/SKILL.md` → >=1.
- ⬜ No `Requires` column: `grep -c 'Requires' .opencode/skills/migrate-core-to-project/SKILL.md` → 0.

## Abort conditions

- Halt if a `Requires` column or any dependency mechanism is introduced — the design is atomic-item, not dependency-graph.
- Halt if the two files can still be selected separately (i.e. any place still lists them as two independent infra options).

## Tool whitelist / blacklist

- Whitelist: read tools; edit on `.opencode/skills/migrate-core-to-project/SKILL.md`.
- Blacklist: edits to any other skill, agent spec, CV, or `knowledge/` file in this phase.
