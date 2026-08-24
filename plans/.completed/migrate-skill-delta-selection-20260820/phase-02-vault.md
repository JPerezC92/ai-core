# Phase 2 — Vault 🔐 (Catalog Steward): selectable list + idempotent copy + merge adapts

> **Owner:** Vault 🔐 (Catalog Steward)
> **Pre:** Phase 1 gate passed (structured manifest + inventory step in place).
> **Reads:** `.opencode/skills/migrate-core-to-project/SKILL.md` (current steps 2-4)
> **Writes:** `.opencode/skills/migrate-core-to-project/SKILL.md` (edited — steps 2-4)

## Steps

1. Rewrite `### 2. Preview manifest (confirm before write)` → `### 2. Select items`. New content:
   - Present a multi-select list (the `question` tool, `multiple: true`) of ONLY the `missing` eligible items from step 1, grouped by Kind (skills / agents / infra). Config merge targets are NOT listed (they are always handled in step 4).
   - The first option is "Migrate all missing eligible items" (default).
   - Each listed option's label is the manifest Item name; the description cites its Destination path (read from the manifest, not re-invented).
   - The selection maps 1:1 to manifest entries → derive the exact write manifest from the selection. Never invent an item not in the manifest.

2. Rewrite `### 3. Copy` → `### 3. Copy (idempotent)`. New content:
   - Copy only the selected items.
   - `present` items are NEVER touched; re-copying an already-present item requires the user to explicitly override (never silent).
   - Agents always copy as pairs: `.opencode/agents/<name>.md` + `agents/<name>/profile.md`. `investigator` copies spec only; `cipher` copies CV only.
   - Infra copies the specific file (or `.gitkeep`).

3. Rewrite `### 4. Adapt` → `### 4. Merge adapts`. New content:
   - `AGENTS.md` — if `<target>/AGENTS.md` exists, MERGE new roster lines into the existing file (append lines for newly selected agents; do NOT regenerate from scratch). If absent, write fresh.
   - `opencode.jsonc` — append only the missing permission gates (grep for an existing gate before adding; never duplicate).
   - `.gitignore` — append-if-missing entries `commit.txt`, `pr-draft.md`, `output/`, `plans/.completed/`.
   - Build approvals unchanged (pnpm ≥ 11 check).

## Output

- **Artifact:** `.opencode/skills/migrate-core-to-project/SKILL.md` (edited)
- **Schema / shape:** step 2 = multi-select of missing items with "migrate all missing" default; step 3 = idempotent copy (present never touched, pairs enforced); step 4 = merge adapts (append-if-missing, never regenerate).

## Gate

- ⬜ `grep -c 'Select items' .opencode/skills/migrate-core-to-project/SKILL.md` → 1.
- ⬜ `grep -c 'multiple: true' .opencode/skills/migrate-core-to-project/SKILL.md` → >=1.
- ⬜ `grep -c 'Migrate all missing eligible items' .opencode/skills/migrate-core-to-project/SKILL.md` → 1.
- ⬜ `grep -c 'Copy (idempotent)' .opencode/skills/migrate-core-to-project/SKILL.md` → 1.
- ⬜ `grep -c 'Merge adapts' .opencode/skills/migrate-core-to-project/SKILL.md` → 1.
- ⬜ `grep -cE 'append-if-missing|append only the missing|never duplicate' .opencode/skills/migrate-core-to-project/SKILL.md` → >=1.
- ⬜ Old section headers gone: `grep -c 'Preview manifest (confirm before write)' .opencode/skills/migrate-core-to-project/SKILL.md` → 0.

## Abort conditions

- Halt if the selection step would list config merge targets as selectable items (they are always handled in step 4, not selectable).
- Halt if any step would overwrite an already-present file without an explicit user override.

## Tool whitelist / blacklist

- Whitelist: read tools; edit on `.opencode/skills/migrate-core-to-project/SKILL.md`.
- Blacklist: edits to any other skill, agent spec, CV, or `knowledge/` file in this phase.
