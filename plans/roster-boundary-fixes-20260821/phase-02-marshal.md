# Phase 2 — Marshal 🎖️ (HR Director): Investigator 🔍 (Incident Investigator) hire completion + single audit route

> **Owner:** Marshal 🎖️ (HR Director)
> **Pre:** phase 1 complete; investigator.md, marshal.md, sentinel.md, and one conformant exemplar of each artifact (quill.md as spec, agents/quill/profile.md as CV) read in full.
> **Reads:** `.opencode/agents/investigator.md`; `.opencode/agents/marshal.md`; `.opencode/agents/sentinel.md`; `.opencode/agents/quill.md` (spec exemplar); `agents/quill/profile.md` (CV exemplar); `knowledge/agents.md`
> **Writes:** `.opencode/agents/investigator.md` (edit); `agents/investigator/profile.md` (create); `.opencode/agents/marshal.md` (edit); `knowledge/agents.md` (edit roster rows)

## Steps

1. Create `agents/investigator/profile.md` following the CV format: H1 `# Investigator 🔍 — Incident Investigator`, then `## Personality`, `## Traits` (3–5 bullets), `## Role within the roster`, `## Collaboration Style`, `## What the Investigator Does NOT Do`. Source the content from investigator.md's mission and hard rules; generic incident-domain wording only, no source-project references.
2. Restructure `.opencode/agents/investigator.md` to the spec standard, preserving every existing rule verbatim: identity line gains the emoji form `Investigator 🔍 (Incident Investigator)`; add the persona reference line (`**Persona / personality:** see agents/investigator/profile.md (source of truth — do not duplicate here).`); rename `## Mission` to `## Your Role` keeping its body; add `## Roster Context` listing Cipher 🔓 (L2 Lead), Quill 🪶 (note drafter), Ledger 📒 (record-keeper), Scribe ✍️ (docs & problem management), Vault 🔐 (Catalog Steward) with one-line relationships; move `## Data-grounding discipline` (and `## Learnings`, `## Reference`) ABOVE `## Hard rules` so Hard rules is the final section.
3. Edit `knowledge/agents.md` roster table: the Investigator 🔍 (Incident Investigator) row gains the 🔍 emoji (bare name otherwise unchanged); the Sentinel 🛡️ (Quality Guardian) row's Team column changes Dev → Both.
4. Edit `marshal.md` hiring workflow step 5: drop the "(dev-side files)" qualifier — every hire audit (both teams) invokes Sentinel 🛡️ (Quality Guardian) for the new CV + runtime spec. Keep the apply-fixes / re-invoke-until-clean tail unchanged.

## Output

- **Artifact:** conformant `investigator.md`; new `agents/investigator/profile.md`; corrected `marshal.md`; updated roster rows in `knowledge/agents.md`
- **Schema / shape:** investigator.md passes the Agent Spec Audit checks SP-1..SP-8 (frontmatter, section order, persona line, Roster Context, Hard Rules last); profile.md has the five CV sections; marshal.md names exactly one audit route with no team-side branch.

## Gate

- ☑ investigator.md has the persona line, `## Roster Context`, and `## Hard rules` as final section; no rule text changed semantically
- ☑ `agents/investigator/profile.md` exists with all five CV sections
- ☑ marshal.md step 5 routes every hire audit to Sentinel 🛡️ (Quality Guardian) — no side-based routing remains
- ☑ roster-table rows show Investigator 🔍 (Incident Investigator) and Sentinel 🛡️ (Quality Guardian) with Team = Both

## Abort conditions

- Any restructure step would change the meaning of an Investigator 🔍 (Incident Investigator) rule rather than its placement → stop and ask; restructuring is structural only.
- The CV content cannot be sourced from existing spec text without inventing personality claims → stop and ask; never fabricate persona content.
