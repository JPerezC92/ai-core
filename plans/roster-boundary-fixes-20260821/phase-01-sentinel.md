# Phase 1 — Sentinel 🛡️ (Quality Guardian): 3-bucket restructure + dev handshake fixes

> **Owner:** Sentinel 🛡️ (Quality Guardian)
> **Pre:** active plan; stash gate clean (no planned-path overlap); `sentinel.md`, `vault.md` (SP/KD sections to absorb), `lumen.md`, `warden.md`, `inquisitor.md` read in full.
> **Reads:** `.opencode/agents/sentinel.md`; `.opencode/agents/vault.md`; `.opencode/agents/lumen.md`; `.opencode/agents/warden.md`; `.opencode/agents/inquisitor.md`
> **Writes:** `.opencode/agents/sentinel.md` (edit); `.opencode/agents/lumen.md` (edit); `.opencode/agents/warden.md` (edit); `.opencode/agents/inquisitor.md` (edit)

## Steps

1. Restructure sentinel.md `## Audit Scope` into three bucket subsections with exact membership:
   - `### Dev-team artifacts` — `.opencode/agents/{atrium,bastion,crucible,forge,herald,inquisitor,lumen,sentinel,warden}.md` + their `agents/*/profile.md` CVs; `plans/**`; `user-stories/*.md`
   - `### Incident-team artifacts` — `.opencode/agents/{investigator,quill,ledger,scribe}.md` + their CVs
   - `### Cross-cutting artifacts` — `.opencode/agents/{augur,marshal,vault}.md` + their CVs; `AGENTS.md` (Cipher's runtime spec); `agents/cipher/profile.md`; `knowledge/agents.md`
2. Divide `## Roster Context` into the same three buckets: Dev (the dev team), Incident (Investigator 🔍 (Incident Investigator), Quill 🪶 (note drafter), Ledger 📒 (record-keeper), Scribe ✍️ (docs & problem management)), Cross-cutting (Cipher 🔓 (L2 Lead), Augur 🔮 (Senior Research Analyst), Marshal 🎖️ (HR Director), Vault 🔐 (Catalog Steward)).
3. Divide the naming-rule roster enumeration into the three buckets; add `Inquisitor 🔎 (PR Reviewer)` and `Investigator 🔍 (Incident Investigator)` to their buckets (defect 4).
4. Absorb the Agent Spec Audit from vault.md: add the SP-1..SP-8 checks table and its workflow (moved, not copied — applies to every runtime spec in the three buckets). Sentinel's existing "Marshal 🎖️ (HR Director) signals ready for audit" trigger covers the workflow entry; note that vault.md is audited like any other spec (no self-audit exception).
5. Absorb the Knowledge Doc Audit from vault.md for `knowledge/agents.md`: only the defined checks KD-1, KD-2, KD-7 (KD-3..KD-6 dangling references die in the move — defect 11).
6. Shrink `### Hard-out`: remove the incident-spec entries, the `knowledge/agents.md` entry, and the vault.md entry (all now in scope); keep ticket data folders, docs/wiki content, problem records, source code, i18n message files, commit messages, settings/config, lock files, generated reports, and `output/` (defects 1, 2).
7. Replace the closing coverage line under Hard-out: incident specs, cross-cutting specs, and `knowledge/agents.md` are in Sentinel's own scope (buckets above); ticket data folders, docs/wiki, problem records, source code, i18n files, config, lock files, and generated reports have no auditor agent by design and are enforced by their own validators and workflows (defect 1).
8. `inquisitor.md` Roster Context: rewrite the Sentinel 🛡️ (Quality Guardian) line to the real relationship — Sentinel 🛡️ (Quality Guardian) audits the inquisitor spec itself (Dev-team bucket); no agent audits `output/audits/` reports (temporal, gitignored artifacts) (defect 5).
9. `lumen.md` Roster Context: rewrite the Sentinel 🛡️ (Quality Guardian) line — Sentinel 🛡️ (Quality Guardian) audits the lumen spec and CV; standalone briefs and audit reports in `output/design/` have no auditor (temporal artifacts); PRODUCT.md / DESIGN.md edits keep Sentinel 🛡️ (Quality Guardian) formatting audit only when the files pass Sentinel's scope-detection rule (defect 6).
10. `lumen.md` PRODUCT.md and DESIGN.md Ownership section: correct the inverted sentence to "Marshal 🎖️ (HR Director) edits spec/persona changes; Sentinel 🛡️ (Quality Guardian) audits markdown formatting and naming-convention compliance" (defect 7).
11. `warden.md` standing-findings routing: re-route the `.gitignore` gap — report the finding to Cipher 🔓 (L2 Lead) with the explicit edit instruction; Cipher 🔓 (L2 Lead) routes the edit to the owning agent; drop the "route to Sentinel" claim (defect 8).

## Output

- **Artifact:** restructured `sentinel.md` (three buckets + absorbed SP/KD machinery); corrected `lumen.md`, `warden.md`, `inquisitor.md`
- **Schema / shape:** each bucket's membership list is exact and independently retainable/removable; the audit rulebook (naming form, placeholder checks, heading order, SP/KD checks) stays ONE shared set applied to all buckets; `Name Emoji (Role)` naming form respected on first mention per section.

## Gate

- ☑ sentinel.md carries Dev-team / Incident-team / Cross-cutting buckets in the scope lists, Roster Context, and naming roster
- ☑ SP-1..8 and KD-1/2/7 checks present in sentinel.md; no dangling KD reference survives
- ☑ inquisitor.md appears in the Dev-team bucket; Inquisitor 🔎 (PR Reviewer) and Investigator 🔍 (Incident Investigator) appear in the naming roster
- ☑ the Hard-out list no longer excludes incident specs or `knowledge/agents.md`; the coverage line names ticket/docs/problem-record/code/config artifacts as unowned-by-design
- ☑ lumen.md, warden.md, inquisitor.md contain no audit-routing claim that is absent from the named auditor's own spec
- ☑ lumen.md ownership sentence assigns editing to Marshal 🎖️ (HR Director) and auditing to Sentinel 🛡️ (Quality Guardian)

## Abort conditions

- A fix would change an agent's actual scope rather than the claim about it → stop and ask; this phase restructures Sentinel's organization and corrects claims to match scopes, it does not redesign other agents' scopes.
- The accurate wording for the unowned-by-design list needs a governance decision (e.g. whether config files deserve an auditor) → stop and ask.
- Absorbing a SP/KD check would contradict an existing Sentinel 🛡️ (Quality Guardian) rule → stop and report the conflict; never merge by deleting semantics.
