<!--
HARD RULE — fill every Step / Output / Gate / Abort. No `TBD` placeholders. Agent improvisation forbidden.
-->

# Phase 4 — Wire ticket-runbook prior-art phase

> **Owner:** Vault 🔐 (Catalog Steward)
> **Pre:** `knowledge/symptoms.md` + `knowledge/problems.md` exist; Phase 3 gate passed.
> **Reads:** `.opencode/skills/ticket-runbook/SKILL.md` (prior-art phase steps), `knowledge/symptoms.md`, `knowledge/problems.md`
> **Writes:** `.opencode/skills/ticket-runbook/SKILL.md` (edited)

## Steps

1. In `.opencode/skills/ticket-runbook/SKILL.md`, in the `### 2. Prior-art search` step list, add a new step 0 before the current step 1:
   - `0. **Symptom-first diagnostic** — match the ticket's error signature against \`knowledge/symptoms.md\`; if a class matches, note the S-xx and its canonical diagnostic, then use the S-xx as a filter over \`knowledge/problems.md\` in the next step.`
   - Re-number the existing steps 1-5 → 2-6.
2. Rewrite the current step 1 (now step 2), renaming `**Problem catalog**` → `**Problem records**` and aligning the compared fields to the `knowledge/problems.md` schema:
   - From: `1. **Problem catalog** — Glob the problem records for the domain. For each record, compare symptom + module from the ticket against the record's \`module\` field, \`titulo\` field, description section, and reproduction section. Match criterion: ≥2 of (system, module, issue_type, symptom keywords) align. Note the file path and matched fields.`
   - To: `2. **Problem records** — read \`knowledge/problems.md\`. For each record, compare the ticket's symptom + module against the record's \`Symptom\` (S-xx), \`Domain\`, \`Problem\`, and \`Evidence\` fields. Match criterion: ≥2 of (system, module, issue_type, symptom keywords) align AND the record's \`Team\` field is \`incident\`. Note the record ID (P-NNN) and matched fields.`
3. Rename the worked example `Prior-art: problem catalog — no match` (≈line 107) to `Prior-art: problem records — no match`.

## Output

- **Artifact:** `.opencode/skills/ticket-runbook/SKILL.md` (edited)
- **Schema / shape:** prior-art search opens with a symptom-first diagnostic (step 0) referencing `knowledge/symptoms.md`; step 2 is `Problem records` reading `knowledge/problems.md` with the Team filter and `knowledge/problems.md` schema fields; steps 2-6 renumbered.

## Gate

- ⬜ `grep -c 'knowledge/problems.md' .opencode/skills/ticket-runbook/SKILL.md` → >=1; `grep -c 'knowledge/symptoms.md' .opencode/skills/ticket-runbook/SKILL.md` → >=1.
- ⬜ `grep -c 'Problem records' .opencode/skills/ticket-runbook/SKILL.md` → >=1; `grep -c 'Problem catalog' .opencode/skills/ticket-runbook/SKILL.md` → 0.
- ⬜ `grep -c 'Team' .opencode/skills/ticket-runbook/SKILL.md` → >=1 within the prior-art step.
- ⬜ No register-write wording: `grep -iE 'write.*problems|problems.*write' .opencode/skills/ticket-runbook/SKILL.md` → no match.

## Abort conditions

- Halt if the prior-art phase would write to `knowledge/problems.md` (Scribe's register; prior-art is read-only).
- Halt if the version-first / stop-and-ask wording contradicts Phase 3's `knowledge/agents.md` — skills must not contradict shared rules.
- Halt if any compared field name survives from the old format (`module`, `titulo`, `description`, `reproduction`) in the Problem-records step.

## Tool whitelist / blacklist

- Whitelist: read tools; edit on `.opencode/skills/ticket-runbook/SKILL.md`.
- Blacklist: edits to any other skill, `knowledge/agents.md`, or `AGENTS.md` in this phase.
