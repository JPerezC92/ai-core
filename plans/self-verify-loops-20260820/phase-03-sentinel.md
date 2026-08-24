# Phase 3 — Sentinel 🛡️ (Quality Guardian): sentinel pointer + scope

> **Owner:** Sentinel 🛡️ (Quality Guardian)
> **Pre:** phase 1 complete (`_consistency-checklist.md` exists).
> **Reads:** `.opencode/agents/sentinel.md`; `.opencode/skills/plan-enforce/references/_consistency-checklist.md`
> **Writes:** `.opencode/agents/sentinel.md` (edit)

## Steps

1. Replace sentinel rule 7 (plan consistency) with a pointer: files at `plans/**` must satisfy `.opencode/skills/plan-enforce/references/_consistency-checklist.md`.
2. Replace sentinel rule 8 (story consistency) with a pointer to the same checklist's story/index section.
3. Widen the plan scope in the default-in list from `plans/*.md` to `plans/**` so subfolder plans + phase files are covered.
4. Keep the mechanical auto-fix note (Status casing) aligned with the checklist; drop the duplicated criteria text now owned by the checklist.

## Output

- **Artifact:** `.opencode/agents/sentinel.md` (rules 7/8 → pointer, scope widened)
- **Schema / shape:** rules 7/8 reference the checklist path; no duplicated plan/story criteria text remains in sentinel.md.

## Verify commands

- ⬜ `grep -n "plans/\*\*" .opencode/agents/sentinel.md` → matches the default-in list and rule 7

## Gate

- ⬜ Rules 7/8 are pointers (no duplicated criteria)
- ⬜ Scope `plans/**` present in the default-in list and rule 7
- ⬜ Checklist path resolves to an existing file

## Abort conditions

- Checklist file missing (phase 1 not complete) → halt; phase 3 depends on phase 1.
