<!--
HARD RULE — fill every Step / Output / Gate / Abort. No `TBD` placeholders. Agent improvisation forbidden.
-->

# Phase 7 — Wire investigator prior-art scan

> **Owner:** Vault 🔐 (Catalog Steward)
> **Pre:** `knowledge/symptoms.md` + `knowledge/problems.md` exist; Phase 3 gate passed.
> **Reads:** `.opencode/agents/investigator.md` (Prior-Art Scanner + Hypothesis Framer hard rule), `knowledge/symptoms.md`, `knowledge/problems.md`
> **Writes:** `.opencode/agents/investigator.md` (edited)

## Steps

1. In `.opencode/agents/investigator.md`, in the `Prior-Art Scanner + Hypothesis Framer` hard rule, rewrite the two prior-art scan sub-steps to reference the concrete artifacts and the symptom-first flow:
   - Sub-step 1 → `1. **Symptom-first diagnostic:** match the error signature against \`knowledge/symptoms.md\`; if a class matches, note the S-xx and its canonical diagnostic, then filter \`knowledge/problems.md\` by that S-xx + \`Team\`.`
   - Sub-step 2 → `2. **Prior-art scan:** search the knowledge base + resolved tickets + the \`knowledge/problems.md\` register (Team-filtered to \`incident\`); then the domain-scoped knowledge-base articles, problem records matching the framed symptom, recent resolved tickets filtered by domain+module, and the project's diagnostic-skill catalog.`
   - Leave sub-steps 3-5 (exact-match return, hypothesis framing, investigation dispatch) unchanged.
2. Do not touch the evidence-discipline, data-grounding, Where-not-How, or User-Authority-Only rules.

## Output

- **Artifact:** `.opencode/agents/investigator.md` (edited)
- **Schema / shape:** prior-art hard rule opens with symptom-first diagnostic referencing `knowledge/symptoms.md`, then a Team-filtered `knowledge/problems.md` scan; the remaining hard rules untouched.

## Gate

- ⬜ `grep -c 'knowledge/symptoms.md' .opencode/agents/investigator.md` → >=1; `grep -c 'knowledge/problems.md' .opencode/agents/investigator.md` → >=1.
- ⬜ `grep -c 'Symptom-first' .opencode/agents/investigator.md` → >=1.
- ⬜ `grep -c 'H1/H2/H3' .opencode/agents/investigator.md` → >=1 (hypothesis framing intact).
- ⬜ `grep -c 'User-Authority-Only' .opencode/agents/investigator.md` → >=1.

## Abort conditions

- Halt if any hard rule outside the Prior-Art Scanner block is altered (evidence discipline, data-grounding, Where-not-How, User-Authority-Only).
- Halt if the investigator's symptom-first wording contradicts Phase 3's `knowledge/agents.md` symptom-first diagnostic.

## Tool whitelist / blacklist

- Whitelist: read tools; edit on `.opencode/agents/investigator.md`.
- Blacklist: edits to any other agent spec, skill, or `knowledge/` file in this phase.
