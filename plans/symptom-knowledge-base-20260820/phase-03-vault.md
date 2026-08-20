<!--
HARD RULE — fill every Step / Output / Gate / Abort. No `TBD` placeholders. Agent improvisation forbidden.
-->

# Phase 3 — Wire prior-art rule + hard rules

> **Owner:** Vault 🔐 (Catalog Steward)
> **Pre:** `knowledge/symptoms.md` + `knowledge/problems.md` exist (Phases 1-2 gates passed).
> **Reads:** `knowledge/agents.md` (current `## Prior-art before re-investigation` section), `knowledge/symptoms.md`, `knowledge/problems.md`
> **Writes:** `knowledge/agents.md` (edited)

## Steps

1. In `knowledge/agents.md`, in the `## Prior-art before re-investigation` section, replace the item-1 line:
   - From: `1. **Problem catalog** — known-recurring-pattern records.`
   - To: `1. **Problem records** — the \`knowledge/problems.md\` register of known-recurring-pattern records, indexed by symptom class in \`knowledge/symptoms.md\`; match only records whose \`Symptom\` (S-xx) and \`Team\` fields align with the current case.`
   - Leave items 2-5 (resolved-ticket archive, patterns register, KBA/RCA, knowledge search) unchanged.
2. Add a `Symptom-first diagnostic` paragraph after the existing match-strength sentence ("If an exact prior-art match exists…"): "On any unexpected tool error, match the error signature against `knowledge/symptoms.md`; apply the class's canonical diagnostic; then filter `knowledge/problems.md` by that S-xx + Team for a prior occurrence. Apply the known fix if found; file a new P-NNN under the class if the problem is novel (Scribe ✍️ owns the register)."
3. Add two HARD RULE lines to the section, styled like the existing evidence-discipline rules:
   - `**Version-first rule (S-01/2-class errors):** before any workaround, check for a newer supported version of the offending tool and upgrade first; re-verify.`
   - `**Stop-and-ask rule (S-07):** two consecutive failures of the same operation, or a long-running/expensive operation that grinds, means STOP — reassess the approach and present options to the user. Do not keep retrying.`
4. Confirm the `## User-Authority-Only rule` section below still reads intact — no new rule may weaken it.

## Output

- **Artifact:** `knowledge/agents.md` (edited)
- **Schema / shape:** item 1 references both knowledge files with Team-filtered matching; symptom-first diagnostic paragraph present; version-first + stop-and-ask hard rules present; all other sections unchanged.

## Gate

- ⬜ `grep -c 'knowledge/symptoms.md' knowledge/agents.md` → >=1; `grep -c 'knowledge/problems.md' knowledge/agents.md` → >=1.
- ⬜ `grep -cE 'Symptom-first|Version-first|Stop-and-ask' knowledge/agents.md` → >=1 each hit.
- ⬜ `grep -c 'User-Authority-Only rule' knowledge/agents.md` → >=1.
- ⬜ Other shared rules (evidence discipline, bounded-query, screenshot-ready, tag forbidden field names) untouched.

## Abort conditions

- Halt if any existing shared-rule text beyond the prior-art section is deleted or reworded.
- Halt if the symptom-first diagnostic weakens the User-Authority-Only rule — state mutations still require user approval.

## Tool whitelist / blacklist

- Whitelist: read tools; edit on `knowledge/agents.md`.
- Blacklist: edits to skills, `AGENTS.md`, `knowledge/symptoms.md`, `knowledge/problems.md` in this phase.
