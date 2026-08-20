# Plan — Deterministic delta redesign of migrate-core-to-project

> **Status:** active
> **Started:** 2026-08-20 13:19
> **Subject:** Make `migrate-core-to-project` deterministic and incremental — structured manifest, filesystem-diff inventory, derived selectable list, idempotent merge-aware copy/pass, re-diff verification
> **Layout:** subfolder pattern

## Context

- Prompted by: user's requirement for a selectable list in `migrate-core-to-project` so a partially-migrated project can migrate just the remaining items (e.g. "almost all migrated, 2 left, migrate 1") without re-running a full install.
- Goal: eliminate repetitive re-analysis of "what's already installed" via deterministic mechanics, while keeping the analysis-driven decisions (stack/relevance reading, consistency-pass judgment) intact.
- Outcome: one skill file `.opencode/skills/migrate-core-to-project/SKILL.md` rewritten to the deterministic delta flow. No code, no new files, no user story (pure skill-doc rewrite — story skip recorded here per user-story scope rules).

## Goals

- ⬜ **G1:** `SKILL.md` ships a structured machine-readable manifest (Item | Kind | Source | Destination | Include-rule) replacing the prose core manifest.- ⬜ **G2:** step 1 does a deterministic installed-set inventory against the manifest, yielding `present` / `missing` / `partial`, with `partial` failing closed.
- ⬜ **G3:** step 2 presents a selectable multi-select of only the missing eligible items; step 3 copies idempotently (present never touched; CV+spec always paired).
- ⬜ **G4:** step 4 merges (append-if-missing) instead of regenerating `AGENTS.md` / `opencode.jsonc` / `.gitignore`.
- ⬜ **G5:** step 5 runs the consistency pass on the union (existing + new); step 6 verifies by re-diff, fail-closed on any selected item still missing.

## Body

### Determinism vs analysis split

- **Deterministic (mechanical, never needs re-asking):** installed-set inventory, derived checklist, idempotent copy, merge adapts, re-diff verify. These remove repetition.
- **Analysis-driven (kept):** stack/relevance read (interpreting the target's structure), consistency-pass judgment (what a dangling reference means), judgment-call report (partial/stale/clash → surfaced, never auto-mutated).

### Flow

`M1 inventory → A1 relevance → M2 selection → M3 copy → M4 merge → A2 consistency → M5 re-diff verify → A3 report`

### Ownership

- The skill is a catalog artifact → Vault 🔐 (Catalog Steward) owns all phases.

## Phase index — dispatch table

| # | Phase | Owner | Runbook | Output |
|---|---|---|---|---|
| 1 | Manifest + inventory | Vault 🔐 | `phase-01-vault.md` | `SKILL.md` (manifest + step 1) |
| 2 | Selection + copy + merge | Vault 🔐 | `phase-02-vault.md` | `SKILL.md` (steps 2-4) |
| 3 | Union pass + re-diff verify | Vault 🔐 | `phase-03-vault.md` | `SKILL.md` (steps 5-6 + examples) |
| 4 | Arguments + description rewrite | Vault 🔐 | `phase-04-vault.md` | `SKILL.md` (description + Arguments) |
| 5 | Merge symptom pair into atomic item | Vault 🔐 | `phase-05-vault.md` | `SKILL.md` (manifest row + presence rule + selection/copy) |

## Critical files / tools

- `.opencode/skills/migrate-core-to-project/SKILL.md` (rewrite)
- Read-only reference: current skill content (manifest, steps, examples, troubleshooting)

## Verification

- ⬜ Phase 1 gate passed (manifest table present; inventory step references manifest with present/missing/partial; partial fails closed)
- ⬜ Phase 2 gate passed (multi-select of missing items; idempotent copy; merge not regenerate)
- ⬜ Phase 3 gate passed (union consistency pass; re-diff verify fail-closed; incremental example)
- ✅ Phase 4 gate passed (scope redefined as Kind-prefilter; old enum values gone; description mentions incremental)
- ✅ Phase 5 gate passed (symptom-problem-register atomic item; separate symptoms/problems rows gone; multi-file presence rule; no Requires column)
- ✅ All gates in each phase runbook passed

## Out of scope

- Editing any skill other than `migrate-core-to-project`
- Editing agent specs, persona CVs, or shared rules
- Changing the invocation model (still called from AICore, destination via `target` arg)
- Any code, script, or test writes
- Running an actual migration

## Pending

(none)

## Resolved decisions

- 2026-08-20 — deterministic mechanics for repetitive tasks, analysis retained for stack/relevance/consistency judgment (user: "the deterministic way is to avoid repetitive task but your analysis is important too").
- 2026-08-20 — installed-set detection via filesystem diff against the manifest whitelist (not a target-side manifest file): self-correcting, works for any prior migration, destination custom skills excluded by construction.
- 2026-08-20 — selection is an interactive multi-select derived from the diff (not explicit name arguments): it is the selectable list the user asked for, and maps 1:1 to manifest entries.
- 2026-08-20 — invocation model unchanged: skill is called from AICore with the destination path as `target`; it is not copied into the target.
- 2026-08-20 — `scope` redefined from the old coarse enum (`skills-only`/`skills+infra`/`roster`/`named-agents`) to a Kind-prefilter (`all`/`skills`/`agents`/`infra`/`config`) so the new multi-select does fine-grained selection; added phase 4 to rewrite the orphaned Arguments section + frontmatter description.
- 2026-08-20 — double-check correction: `config` removed from the `scope` enum (it is a merge target, never selectable — a `config` scope value would have produced an empty multi-select); "What I do" body reworded to match the new deterministic flow (was stale "propose applicable subset / preview manifest / adapt").
- 2026-08-20 — symptom pair (`knowledge/symptoms.md` + `knowledge/problems.md`) are ONE feature and must never be separated. Modeled as a single atomic manifest item named `symptom-problem-register` (two files, one row — same pattern as an agent's spec+CV), NOT two rows with a `Requires` dependency column. Atomicity is structural; the existing `partial` (fail-closed) handling covers the "one file present" failure for free. Only the symptom pair is merged; `plans/` + `user-stories/` stay separate (directories, not cross-referencing content files).
