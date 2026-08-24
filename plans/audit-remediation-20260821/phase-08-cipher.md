# Phase 8 — Cipher 🔓 (L2 Lead): resolve runtime decision and map

> **Owner:** Cipher 🔓 (L2 Lead)
> **Pre:** phase 7 completed; OpenCode restarted with the phase-5 Warden 🔒 (Dependency Warden) policy; roster baseline audit and Marshal's full CV migration map are available; no G9–G12 roster-wide CV or runtime migration has started.
> **Reads:** all 17 CVs; all 16 `.opencode/agents/*.md` runtime specs; `AGENTS.md`; Sentinel 🛡️ (Quality Guardian) CV/SP-3 rule; roster baseline and migration-map evidence
> **Writes:** `plan.md`; `cv-migration-map.md`

## Steps

1. Ask the user to choose one Quill 🪶 (note drafter) correction contract: a fresh complete draft for every correction, or surgical patch updates without full regeneration. Do not resolve the incompatible runtime clauses by inference.
2. Record the user's Quill 🪶 (note drafter) decision in `plan.md` and specify the exact runtime clause that becomes authoritative and the exact incompatible clause that must be removed or revised.
3. Confirm each other identified profile/runtime contradiction has an existing runtime authority: Herald 📯 (Release Manager) does not reassess evidence; Inquisitor 🔎 (PR Reviewer) does not submit GitHub comments or reviews; Sentinel 🛡️ (Quality Guardian) audits its approved Dev/Incident/Cross-cutting scope; Vault 🔐 (Catalog Steward) is catalog-only. These runtime sources are authoritative for CV normalization.
4. Classify every operational CV statement as retained by an existing runtime counterpart, moved into its owner runtime source, or retired as stale only after owner-first analysis proves no current contract owns it. Preserve canonical roster roles in CV H1s, including Ledger 📒 (record-keeper) and Scribe ✍️ (docs & problem management), and preserve persona voice only inside the five required CV sections.
5. Stop before source edits until the user decision is recorded and `cv-migration-map.md` gives an evidence-backed destination or retirement reason for every removed operational statement.

## Output

- **Artifact:** explicit Quill 🪶 (note drafter) correction decision and complete CV/runtime migration map
- **Schema / shape:** one authoritative Quill 🪶 (note drafter) correction contract; each removed operational statement has a named runtime destination or an owner-first stale-retirement reason; no behavior is deleted by inference

## Gate

- ☑ User's Quill 🪶 (note drafter) correction decision is recorded verbatim enough to implement one runtime contract
- ☑ Every removed operational CV statement has a named runtime counterpart, a planned owner-runtime move, or an owner-first stale-retirement reason
- ☑ Canonical H1 role mappings are listed for Ledger 📒 (record-keeper), Quill 🪶 (note drafter), Scribe ✍️ (docs & problem management), and all other roster members

## Abort conditions

- Any profile-only operational rule lacks both a runtime destination and an owner-first stale-retirement reason → stop and ask rather than deleting it.
- Quill's correction model remains contradictory or undecided → stop before Phase 9.
