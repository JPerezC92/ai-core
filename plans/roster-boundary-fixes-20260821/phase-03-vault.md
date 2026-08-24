# Phase 3 — Vault 🔐 (Catalog Steward): catalog-pure rewrite

> **Owner:** Vault 🔐 (Catalog Steward)
> **Pre:** phase 2 complete; `vault.md` and `knowledge/agents.md` read in full.
> **Reads:** `.opencode/agents/vault.md`; `knowledge/agents.md`; `.opencode/agents/sentinel.md` (absorbed SP/KD checks)
> **Writes:** `.opencode/agents/vault.md` (edit); `knowledge/agents.md` (edit governance-split lines)

## Steps

1. Rewrite vault.md frontmatter description and `## Your Role` so Vault 🔐 (Catalog Steward) governs the complete skills catalog only: all skills, both teams, all harnesses; quality, lifecycle, onboarding, deprecation, and registry cross-references.
2. Remove the shared-rules table and the agent-runtime-spec paragraph from `## Scope (in)` — `knowledge/agents.md` and every agent runtime spec now belong to Sentinel 🛡️ (Quality Guardian) (G2).
3. Replace the dev-spec enumeration in `## Scope (out)` with one explicit boundary: all agent runtime specs (including AGENTS.md) and persona CVs are Sentinel's document-audit territory. Keep ticket handling, SQL execution, and `output/` out of Vault's scope.
4. Rewrite the Sentinel 🛡️ (Quality Guardian) line in Vault's Roster Context: Sentinel 🛡️ (Quality Guardian) audits all agent specs and CVs, including vault.md itself. Remove the vague "downstream auditor of Vault's own process compliance" claim (defect 13).
5. Delete `## Knowledge Doc Audit` and `## Agent Spec Audit` sections in full — their defined checks and workflows moved to sentinel.md in phase 2; no duplicate checklist remains (defect 11).
6. Remove the self-audit exception from Vault's hard rules. State instead that sentinel.md audits vault.md as an ordinary cross-cutting agent spec.
7. Scope QC-20, QC-21, and QC-22 to Template A diagnostic skills that embed SQL; non-diagnostic skills are exempt (defect 12).
8. Rewrite `knowledge/agents.md` governance edge cases: Sentinel 🛡️ (Quality Guardian) audits all agent documents (specs + CVs, both teams, plans, user stories, shared rules); Vault 🔐 (Catalog Steward) governs the skills catalog (all harnesses, both teams) for skill quality/lifecycle; Warden 🔒 (Dependency Warden) covers skill/package security.

## Output

- **Artifact:** catalog-pure `vault.md`; corrected `knowledge/agents.md` governance-split lines
- **Schema / shape:** vault.md contains skills-only scope, no SP/KD sections, no incident-side audit scope, and no self-audit exception; QC SQL checks carry their diagnostic-only condition; the shared-rules file states the three-way governance split.

## Gate

- ☑ vault.md description and role are catalog-only; no incident-side audit scope survives
- ☑ vault.md has no Agent Spec Audit / Knowledge Doc Audit section and no self-audit exception
- ☑ QC-20/21/22 carry the diagnostic-only applicability condition
- ☑ knowledge/agents.md states Sentinel 🛡️ (Quality Guardian) = all agent documents, Vault 🔐 (Catalog Steward) = skills catalog, Warden 🔒 (Dependency Warden) = skill/package security

## Abort conditions

- Removing a Vault 🔐 (Catalog Steward) section would drop a unique catalog responsibility rather than a moved SP/KD audit rule → stop and ask.
- Rewording the governance split would alter Sentinel's, Vault's, or Warden's actual jurisdiction beyond the approved artifact-type structure → stop and ask.
