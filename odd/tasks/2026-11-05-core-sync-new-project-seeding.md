# core-sync new-project seeding

> **Status:** active
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-05
> **Objective:** Let `init --bind-cleared` seed a brand-new empty destination project, which it currently cannot because merge-mode bindings refuse to create their file.
> **Branch:** `feat/core-sync/creation-frontmatter-qmd-index`
> **Delivery:** single slice, authored additions + deletions forecast ≈120 excluding generated files.
> **Runner:** `uv run --frozen --group dev pytest -q`

Load and read the `odd-workflow` skill (`.opencode/skills/odd-workflow/SKILL.md`) before creating or maintaining this record. Its creation, delivery, change and closure procedures are canonical; this template illustrates their layout, not another policy definition.

## Specs

- S1 — A brand-new empty destination can be seeded by `init --bind-cleared`. Exact requirement: "this ai core project is to SYNC THIS PROJECT FILES TO NEW OR NOT NEW PROJECT WDF U BIUILD SOMETHING THAT DONT WRITE NOTHING ON A NEW EMPTY PROJECT". Acceptance: run `init --bind-cleared --root AGENTS.md` against an empty directory, then list it; the tree exists including `opencode.jsonc` whose `qmd` index names that folder, and a following `check` reports the created region targets awaiting their project-region reconciliation — printing `current` once that pending list is cleared.
- S2 — `apply` still refuses to create a merge destination. Exact requirement: derived from S1 — creation belongs to enrollment, not to update. Acceptance: run `apply` against a destination whose merged config is absent; it reports `missing destination` for that file and creates nothing.
- S3 — No destination project is written by this feature's work. Exact requirement: "dont touch nothing on tismart-support project". Acceptance: every path in the delivering commits lies inside the ai-core repository.

## Tasks

- T1 | S1, S2 | delegated (one creation branch in enrollment, plus the merge-mode contract it changes) — Forge 🔨 (Implementer) | open | commit: pending
- T2 | S1, S2 | delegated (tests for seeding and for the unchanged refusal) — Forge 🔨 (Implementer) | open | commit: pending
- T3 | S1, S2 | delegated (documentation of the changed merge contract) — Scribe ✍️ (Docs & Problems Manager) | open | commit: pending
- T4 | S1, S3 | delegated (whole-suite execution and test-architecture verdict) — Crucible 🔥 (Test Architect) | open | commit: pending

## Log

- L1 — 2026-11-05 — Original request, verbatim: "u r a shit, this ai core project is to SYNC THIS PROJECT FILES TO NEW OR NOT NEW PROJECT WDF U BIUILD SOMETHING THAT DONT WRITE NOTHING ON A NEW EMPTY PROJECT".
- L2 — 2026-11-05 — Defect verified before any fix. Against an empty directory: `apply` returns `invalid bindings`; `init --bind-cleared` alone returns `destination instruction root not found; pass --root`; `init --bind-cleared --root AGENTS.md` returns `missing destination: <dir>\opencode.jsonc (merge mode cannot create it; the destination must exist)`. After every attempt the directory held zero entries, because writes flush only after classification succeeds. Root cause: `opencode.jsonc` is a merge binding, merge mode never creates its destination, and every enrollment includes it — so seeding a new project aborts before anything is written.
- L3 — 2026-11-05 — Why this was missed. The only destination exercised in the prior feature already contained `opencode.jsonc`, so enrollment never needed to create a merge target. The feature record `2026-11-05-core-sync-creation-and-qmd-index.md` verified creation for region and raw targets only, and its S5 excluded merge on the stated grounds that "there is nothing to merge into" — true for an update, false for a first enrollment, which is the case this record fixes.
- L4 — 2026-11-05 — Mirror: pending recovery. Feature identity `ai-core` / `core-sync new-project seeding`, locator `odd/tasks/2026-11-05-core-sync-new-project-seeding.md`. No backend round trip is performed or claimed.
- L5 — 2026-11-05 — Verified end to end by the coordinator against a genuinely empty directory: `init --bind-cleared --root AGENTS.md` printed `initialized` and the directory then held `AGENTS.md`, `opencode.jsonc`, `.aicore/`, `.opencode/`, `architecture/`, `knowledge/` and `odd/`, with `opencode.jsonc` naming `new-project-test` as the `qmd` index. The same command previously wrote zero files. `check` on the fresh destination reports the created region targets awaiting their project-region reconciliation, which is the established creation contract and why S1's acceptance was corrected rather than the behaviour. Gates: Bastion 🧱 `[PASS]` with one advisory that produced that correction; Crucible 🔥 `[PASS]` after an initial `[BLOCK]` that rested on its own wrong path — it searched the repository-root `tests/` directory instead of the skill's, and confirmed the seeding test executes (`952 passed, 6 skipped`, exit 0). Documentation updated by Scribe ✍️ in the same slice, with `metadata.version` advanced 2.7.0 → 2.8.0 because a command that previously failed now creates files.
