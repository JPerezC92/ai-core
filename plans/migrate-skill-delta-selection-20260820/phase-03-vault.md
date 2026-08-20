<!--
HARD RULE — fill every Step / Output / Gate / Abort. No `TBD` placeholders. Agent improvisation forbidden.
-->

# Phase 3 — Union consistency pass + re-diff verify + examples

> **Owner:** Vault 🔐 (Catalog Steward)
> **Pre:** Phase 2 gate passed (selection + copy + merge steps in place).
> **Reads:** `.opencode/skills/migrate-core-to-project/SKILL.md` (current steps 5-6 + examples + troubleshooting)
> **Writes:** `.opencode/skills/migrate-core-to-project/SKILL.md` (edited — steps 5-6, examples, troubleshooting)

## Steps

1. Rewrite `### 5. Consistency pass (mandatory)` → `### 5. Consistency pass (union)`. Add to the opening line: run against the UNION = already-present set + newly selected. Keep the 6 existing checks but amend:
   - Check 1 (Broken file pointers): trim references only to agents that are NEITHER `present` NOR `selected` this run. A reference to an already-installed agent is valid and must NOT be trimmed.
   - Check 2 (Roster lists): align to the union (existing + new), merging not regenerating.
   - Checks 3-6 unchanged (non-installed team refs, frontmatter, CV↔spec, grammar).

2. Rewrite `### 6. Verify` → `### 6. Verify (re-diff)`. New content:
   - Re-run the step-1 inventory diff.
   - Every selected item must now be `present`; present-count = previous-present + selected-count.
   - If any selected item is still `missing`, or any item is now `partial`, **FAIL** — do not report success.
   - Keep the existing verify checks (pointer sweep, roster count, frontmatter, build).

3. Add a new example after Example 2, `### Example 3 — incremental migration`:
   - Target already has 12 agents + 6 skills (from a prior migration). User runs the skill.
   - Inventory shows 2 missing eligible items (e.g. `op-model` skill, `warden` agent) and 1 `partial` (spec present, CV missing).
   - The partial is reported and blocked. User selects only `op-model`.
   - Result: only `op-model` copies; AGENTS.md/appends unchanged (no new agent); consistency pass runs on the union; re-diff shows present-count +1 and `op-model` now present → PASS. The remaining 1 missing item stays missing (deferred).

4. Add troubleshooting entries:
   - **"Item present but partial"** — spec exists, CV missing (or vice versa). Cause: interrupted or manual prior copy. Fix: fail closed; ask the user whether to re-copy the pair or leave it; never auto-repair.
   - **"Item present but from an older core"** — destination copy is stale vs current AICore. Cause: prior migration of an earlier core. Fix: offer explicit re-copy (user override), never silent overwrite.
   - **"Target has a custom item with a core name"** — destination has its own `SKILL.md`/spec under a manifest name but it is not a core item. Cause: name collision. Fix: the manifest whitelist governs; the target's file is treated as `present` and skipped, reported to the user.

## Output

- **Artifact:** `.opencode/skills/migrate-core-to-project/SKILL.md` (edited)
- **Schema / shape:** step 5 = union consistency pass (trim only neither-present-nor-selected); step 6 = re-diff verify with fail-closed on still-missing/partial; Example 3 incremental added; 3 new troubleshooting entries.

## Gate

- ⬜ `grep -c 'Consistency pass (union)' .opencode/skills/migrate-core-to-project/SKILL.md` → 1.
- ⬜ `grep -c 'Verify (re-diff)' .opencode/skills/migrate-core-to-project/SKILL.md` → 1.
- ⬜ `grep -cE 'NEITHER.*present.*NOR.*selected|neither.*present.*nor.*selected' .opencode/skills/migrate-core-to-project/SKILL.md` → >=1.
- ⬜ `grep -c 'FAIL' .opencode/skills/migrate-core-to-project/SKILL.md` → >=1 (re-diff fail-closed).
- ⬜ `grep -c 'Example 3 — incremental migration' .opencode/skills/migrate-core-to-project/SKILL.md` → 1.
- ⬜ Old header gone: `grep -c 'Consistency pass (mandatory)' .opencode/skills/migrate-core-to-project/SKILL.md` → 0.

## Abort conditions

- Halt if the consistency pass would trim a reference to an already-present (valid) agent.
- Halt if the verify step could report success while any selected item is still missing.

## Tool whitelist / blacklist

- Whitelist: read tools; edit on `.opencode/skills/migrate-core-to-project/SKILL.md`.
- Blacklist: edits to any other skill, agent spec, CV, or `knowledge/` file in this phase.
