# Plan — roster boundary fixes (artifact-type governance split)

> **Status:** completed
> **Started:** 2026-08-21 03:46
> **Completed:** 2026-08-21 05:33
> **Subject:** Fix roster boundary defects via an artifact-type governance split — Vault 🔐 (Catalog Steward) becomes catalog-pure (skills only), Sentinel 🛡️ (Quality Guardian) audits ALL agent documents divided into Dev / Incident / Cross-cutting buckets, Investigator 🔍 (Incident Investigator) hire completed, single audit route, convention records.
> **Layout:** subfolder pattern

## Context

> Why is this being done? What prompted it? What is the intended outcome?

- Prompted by: user confusion about agent responsibilities; a full per-agent audit found one-sided scope claims (spec A asserts a relationship spec B never defines), an unaudited spec (the Inquisitor 🔎 (PR Reviewer) spec), a half-built agent (Investigator 🔍 (Incident Investigator)), and Vault's dual role documented in only one of two places.
- Goal: every agent's boundaries verifiable from both sides of each handshake — no crack for work to fall through.
- Outcome: 10 spec/knowledge files corrected/restructured plus the lead-spec convention so a dev-only or incident-only adopter can deterministically retain or remove whole Sentinel 🛡️ (Quality Guardian) team buckets instead of hand-stripping mixed references; a re-run of the relationship audit finds zero one-sided claims.
- Story: skipped — pure docs/process governance plan, no feature-visible behavior.

## Goals

- ☑ **G1:** Every audit handshake is two-sided — each "X audits this" claim in any spec also exists in X's own spec, and the Inquisitor 🔎 (PR Reviewer) spec has exactly one named auditor.
- ☑ **G2:** Vault 🔐 (Catalog Steward) is catalog-pure — governs the skills catalog only (both teams, all harnesses); its spec carries zero incident-side audit content; the shared-rules file states the governance split (Vault 🔐 (Catalog Steward) = skill quality/lifecycle, Sentinel 🛡️ (Quality Guardian) = all agent documents, Warden 🔒 (Dependency Warden) = skill/package security).
- ☑ **G3:** Marshal's hiring workflow routes every post-hire audit to Sentinel 🛡️ (Quality Guardian) — one route for both teams, no side-based branch.
- ☑ **G4:** Investigator 🔍 (Incident Investigator) is a fully conformant roster member — emoji, persona CV, persona reference line, Roster Context, canonical section order, roster-table row updated.
- ☑ **G5:** Sentinel's spec is fully divided into Dev-team / Incident-team / Cross-cutting buckets — scope lists, Roster Context, and naming roster all carry the three-bucket division; it absorbs the Agent Spec Audit (SP-1..8) and the defined Knowledge Doc checks (KD-1/2/7) from vault.md; each bucket is independently retainable or removable during migration.
- ☑ **G6:** Release evidence and execution are separated — AGENTS.md states that Cipher 🔓 (L2 Lead) evaluates audit evidence before release and is Cipher's runtime spec by design; Herald 📯 (Release Manager) executes only from Cipher's evaluated gate packet, and its Hard Rules are organized into maintainable groups without changing their protections.

## Body

Defects found by the relationship audit (all evidence read in full, 2026-08-21):

| # | Defect | Evidence |
|---|---|---|
| 1 | sentinel.md claims Vault 🔐 (Catalog Steward) audits all its Hard-out files — false for ticket folders, docs/wiki, problem records, source code, i18n, config, lock files | `sentinel.md:64` |
| 2 | vault.md mislabeled "incident agent spec" in sentinel.md's Hard-out | `sentinel.md:52` |
| 3 | Shared-rules edge case describes only Vault's incident job; the catalog job (all skills, both teams, all harnesses) is unstated — root of "who owns dev skills?" confusion | `knowledge/agents.md:74` |
| 4 | inquisitor.md in nobody's audit list — missing from Sentinel's default-in AND Vault's dev-side scope-out | `sentinel.md:31`, `vault.md:37` |
| 5 | inquisitor.md claims sentinel.md audits its `output/audits/pr-*.md` reports — `output/` is hard-excluded there | `inquisitor.md:23`, `sentinel.md:36` |
| 6 | lumen.md claims sentinel.md audits PRODUCT.md / DESIGN.md — not present in any scope list there | `lumen.md:26` |
| 7 | lumen.md says spec changes "route through Marshal 🎖️ (HR Director) for audit" — that route inverts the edit/audit split | `lumen.md:149` |
| 8 | warden.md routes `.gitignore` gap findings to the Quality Guardian — never accepted; `.gitignore` is not in that scope | `warden.md:98` |
| 9 | marshal.md's post-hire audit invokes the Quality Guardian for dev-side files only — incident-side hires go unaudited | `marshal.md:24` |
| 10 | investigator.md nonconformant: no emoji, no CV, no persona reference line, no Roster Context, Hard Rules not last | `investigator.md` (whole file), `knowledge/agents.md:55` |
| 11 | Vault's Knowledge Doc workflow cites KD-3..KD-6; only KD-1, KD-2, KD-7 are defined | `vault.md:171-181` |
| 12 | Vault's QC-20/21/22 SQL checks marked "every skill" — meaningless for non-diagnostic skills | `vault.md:115-138` |
| 13 | Vault's roster table carries a vague "Sentinel 🛡️ (Quality Guardian) is downstream auditor of Vault's process compliance" claim | `vault.md:48` |
| 14 | herald.md carries 20+ hard rules in one block plus an executor-verifier blur — Cipher's audit-evidence authority and Herald's execution boundary must be made explicit; the block must be grouped without weakening protections | `herald.md:34,106-138`; `AGENTS.md:19` |
| 15 | Vault's spec audits agent runtime specs + shared rules under a "Catalog Steward" title — two organizing principles (artifact type vs team side) stitched into one agent; dev-only migrations inherit half-dead incident references | `vault.md:14-37` |
| 16 | Final acceptance audit: Investigator 🔍 (Incident Investigator) has one direct-to-user rejected-hypothesis path that bypasses Cipher 🔓 (L2 Lead); Sentinel 🛡️ (Quality Guardian) SP-1/2 do not define the root AGENTS.md runtime-spec exception | `investigator.md:16,67`; `sentinel.md:120` |

Resolution model: defects 9, 11, 13 are resolved by deletion/move under the artifact-type split (single audit route; SP/KD checks move to Sentinel; vague claim removed) rather than by patching.

## Phase index — dispatch table

| # | Phase | Owner | Runbook | Output | Goals |
|---|---|---|---|---|---|
| 1 | Sentinel 🛡️ (Quality Guardian) 3-bucket restructure + dev handshake fixes | Sentinel 🛡️ (Quality Guardian) | `phase-01-sentinel.md` | restructured `sentinel.md` (3 buckets + SP/KD absorbed), corrected `lumen.md`, `warden.md`, `inquisitor.md` | G1, G5 |
| 2 | Investigator 🔍 (Incident Investigator) hire completion + single audit route | Marshal 🎖️ (HR Director) | `phase-02-marshal.md` | conformant `investigator.md`, new `agents/investigator/profile.md`, corrected `marshal.md`, roster rows (🔍 emoji, Sentinel 🛡️ (Quality Guardian) → Both) | G3, G4 |
| 3 | Vault 🔐 (Catalog Steward) catalog-pure rewrite | Vault 🔐 (Catalog Steward) | `phase-03-vault.md` | catalog-pure `vault.md`, `knowledge/agents.md` governance-split lines | G2 |
| 4 | Cipher 🔓 (L2 Lead) lead-spec convention + release evidence gate | Cipher 🔓 (L2 Lead) | `phase-04-cipher.md` | `AGENTS.md` lead-spec line + explicit Cipher 🔓 (L2 Lead) evidence-gate responsibility | G6 |
| 5 | Herald 📯 (Release Manager) execution-boundary refactor | Marshal 🎖️ (HR Director) | `phase-05-marshal-herald.md` | structured, execution-only `herald.md` | G6 |
| 6 | Acceptance-audit definition remedies | Marshal 🎖️ (HR Director) | `phase-06-marshal-remedies.md` | corrected Cipher 🔓 (L2 Lead) return path in `investigator.md`; explicit AGENTS.md exception in Sentinel 🛡️ (Quality Guardian) SP-1/2 | G1, G4, G5 |

> Every phase traces to ≥ 1 goal ID. A phase with no Goals column entry is speculative — remove or merge it.

## Critical files / tools

- `.opencode/agents/investigator.md`, `agents/investigator/profile.md` (new)
- `.opencode/agents/marshal.md`
- `.opencode/agents/sentinel.md`, `.opencode/agents/lumen.md`, `.opencode/agents/warden.md`, `.opencode/agents/inquisitor.md`
- `.opencode/agents/vault.md`, `.opencode/agents/herald.md`
- `knowledge/agents.md`, `AGENTS.md`

## Verification

- ☑ Phase 1: sentinel.md carries the three buckets (Dev / Incident / Cross-cutting) in scope lists, Roster Context, and naming roster; SP-1..8 + KD-1/2/7 checks present; inquisitor.md in the Dev bucket and naming roster; zero one-sided claims remain in lumen.md / warden.md / inquisitor.md; the coverage line names what is unowned-by-design
- ☑ Phase 2: Investigator 🔍 (Incident Investigator) conforms (emoji, CV with all five sections, persona line, Roster Context, Hard Rules last); marshal.md routes every hire audit to Sentinel 🛡️ (Quality Guardian) with no side-based branch; roster-table rows updated (Investigator 🔍 (Incident Investigator) emoji, Sentinel 🛡️ (Quality Guardian) team = Both)
- ☑ Phase 3: vault.md has no Agent Spec Audit / Knowledge Doc Audit sections, no incident-side scope, no self-audit exception, catalog-only description; QC-20/21/22 scoped to diagnostic skills; knowledge/agents.md states the three-way split (Sentinel 🛡️ (Quality Guardian) = all agent documents, Vault 🔐 (Catalog Steward) = skills catalog, Warden 🔒 (Dependency Warden) = skill/package security)
- ☑ Phase 4: AGENTS.md carries the lead-spec convention line and explicitly assigns audit-evidence evaluation before release to Cipher 🔓 (L2 Lead)
- ☑ Phase 5: herald.md requires Cipher's evaluated gate packet before release execution, removes Herald 📯 (Release Manager)'s evidence-quality judgment, and groups Hard Rules without changing a protection; all Herald 📯 (Release Manager) handoffs are two-sided with AGENTS.md
- ☑ Phase 6: Investigator 🔍 (Incident Investigator) sends rejected-hypothesis findings to Cipher 🔓 (L2 Lead), not directly to the user; Sentinel 🛡️ (Quality Guardian) SP-1/2 explicitly distinguish `.opencode/agents/*.md` frontmatter from Cipher's root AGENTS.md runtime spec

## Out of scope / Do-not-touch

- `.opencode/skills/` — both recently upgraded skills stay untouched
- Clean specs: `quill.md`, `ledger.md`, `scribe.md`, `augur.md`, `atrium.md`, `bastion.md`, `crucible.md`, `forge.md`
- Adding `version:` frontmatter to agent specs (offered, not confirmed by user)
- Adding an auditor agent for ticket-data / docs / problem-record artifacts — they stay enforced by their own validators and workflows (documented as unowned-by-design, not restructured)
- Inquisitor's subagent-dispatching-subagents capability question (runtime concern, separate from boundary fixes)
- Splitting `knowledge/agents.md` shared rules into universal vs incident-ops rulesets (flagged during design; separate follow-up plan if wanted)
- Automating per-bucket extraction in `migrate-core-to-project` — this plan makes Sentinel's blocks deterministic to retain/remove but does not change the migration tool
- Recording DEBT-001 for Herald's rule density — replaced by direct remediation in G6

## Resolved decisions

- 2026-08-21 — Investigator 🔍 (Incident Investigator) emoji: 🔍 (user-approved).
- 2026-08-21 — Cipher's runtime spec is AGENTS.md by design (user decision); recorded as convention, not debt.
- 2026-08-21 — Ticket-data, docs/wiki, and problem-record artifacts keep no auditor agent by design; Sentinel's false coverage line is corrected to say so.
- 2026-08-21 — Governance structure locked: artifact-type purity (option B). Vault 🔐 (Catalog Steward) = skills catalog only; Sentinel 🛡️ (Quality Guardian) = ALL agent documents. G2/G3/G5 reworded accordingly (user-approved); defects 9, 11, 13 resolve by deletion/move instead of patching.
- 2026-08-21 — Sentinel's spec division: 3 buckets (Dev-team / Incident-team / Cross-cutting), full-spec division (scope lists + Roster Context + naming roster), so each bucket is independently retainable/removable during migration (user-approved). Automated section extraction is explicitly out of scope.
- 2026-08-21 — Herald's rule-density / executor-evidence-review issue is remediated directly, not entered as accepted debt (user-directed). G6 and phases 4-5 reworded accordingly.
- 2026-08-21 — Final-audit findings 16 are remediated before closure under G1/G4/G5; phase 6 added (no new goal).
