# Phase 13 — Cipher 🔓 (L2 Lead): roster and policy acceptance audit

> **Owner:** Cipher 🔓 (L2 Lead)
> **Pre:** phases 5 through 12 complete; OpenCode restarted after all runtime-spec edits; full migration map, auditor output, and locked Python environment are available.
> **Reads:** all 17 CVs; every runtime authority; Sentinel 🛡️ (Quality Guardian) CV/SP-3 rule; Warden 🔒 (Dependency Warden) manifest/lock audit output; all phase gates
> **Writes:** `.opencode/agents/ledger.md`; `knowledge/agents.md`; `knowledge/symptoms.md`; `README.md`; `plans/**/*.md` — Marshal 🎖️ (HR Director) and Sentinel 🛡️ (Quality Guardian) normalize mechanical roster-name, roster-count, plan-comment, and mapping-reference drift; `output/audits/{warden-pyyaml-20260824,sentinel-roster-20260824,phase13-validation-20260824}.md` — Warden 🔒 (Dependency Warden), Sentinel 🛡️ (Quality Guardian), and Cipher 🔓 (L2 Lead) record independent evidence; Sentinel 🛡️ (Quality Guardian) and Warden 🔒 (Dependency Warden) return independent audit evidence to Cipher 🔓 (L2 Lead)

## Steps

1. Dispatch Sentinel 🛡️ (Quality Guardian) for a full read-only audit of all CVs, every runtime authority, exact heading/H1 order, persona/runtime separation, and all previously identified profile/runtime contradictions.
2. Dispatch Warden 🔒 (Dependency Warden) for the locked PyYAML audit under its corrected policy and require an evidence-separated PASS/INFO result or a concrete evidence-backed gate.
3. Normalize every first ownership-table roster mention in `knowledge/agents.md` to contiguous `Name Emoji (Role)` form, preserving the separate functional-role column and all coverage text.
4. Normalize historical-plan prose in `plans/**/*.md` to the current contiguous roster-name form without changing factual content, status, phase order, or commands; remove only leading stale HTML comments that fail the plan validator; normalize `README.md`, `knowledge/agents.md`, `knowledge/symptoms.md`, `ledger.md`, and the CV migration map's current-heading references.
5. Require Warden 🔒 (Dependency Warden) to persist its evidence-separated locked-PyYAML audit to `output/audits/warden-pyyaml-20260824.md`.
6. Run both validator test suites, all three active and two completed plan validators, and `git diff --check`; record each exact result in `output/audits/phase13-validation-20260824.md`; no release command is allowed.
7. Require Sentinel 🛡️ (Quality Guardian) to persist its full acceptance audit to `output/audits/sentinel-roster-20260824.md`.
8. Return PASS only when Sentinel 🛡️ (Quality Guardian) and Warden 🔒 (Dependency Warden) pass, every verification command exits zero, all three evidence artifacts exist, and all G1–G13 done conditions are evidenced.

## Output

- **Artifact:** normalized ownership table, roster README/plan records, and three persisted independent evidence artifacts proving roster standards and Warden 🔒 (Dependency Warden) provenance policy pass together
- **Schema / shape:** every CV/runtime pair conforms; PyYAML provenance is visible without false release friction; no release action occurs

## Gate

- ☑ Sentinel 🛡️ (Quality Guardian) returns PASS for every CV and runtime authority
- ☑ Warden 🔒 (Dependency Warden) returns PASS with evidence-separated provenance observation and no concrete dependency gate
- ☑ `knowledge/agents.md` ownership table uses the exact contiguous roster-name form for all 17 owners
- ☑ `README.md`, `knowledge/agents.md`, `knowledge/symptoms.md`, and all plan prose use current roster naming; README counts 9 skills and 17 CVs
- ☑ All active and completed plan validators and `git diff --check` exit zero
- ☑ Persisted Sentinel 🛡️ (Quality Guardian), Warden 🔒 (Dependency Warden), and Cipher 🔓 (L2 Lead) acceptance evidence artifacts all exist

## Abort conditions

- Any migrated CV has an operating rule without a runtime counterpart → reopen its team phase.
- Any runtime authority remains structurally nonconformant or behaviorally contradictory → reopen phase 9.
- Any Warden 🔒 (Dependency Warden) ADVISORY or BLOCK has concrete evidence → report it without downgrade.
