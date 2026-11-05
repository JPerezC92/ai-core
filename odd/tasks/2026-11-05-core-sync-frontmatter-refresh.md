# core-sync frontmatter refresh

> **Status:** active
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-05
> **Objective:** Make region-mode synchronization refresh a destination file's YAML frontmatter identity keys from the source, so a destination skill cannot advertise a stale description forever, while preserving destination-owned frontmatter keys.
> **Branch:** `feat/core-sync/frontmatter-refresh`
> **Delivery:** single slice, authored additions + deletions forecast ≈300 excluding generated files; chained-PR strategy if the running count crosses ≈400 before the next commit.
> **Runner:** `uv run --frozen --group dev pytest -q`

Load and read the `odd-workflow` skill (`.opencode/skills/odd-workflow/SKILL.md`) before creating or maintaining this record. Its creation, delivery, change and closure procedures are canonical; this template illustrates their layout, not another policy definition.

## Specs

- S1 — A region-mode sync writes the source's frontmatter identity keys into the destination file. Exact requirement: "Make sync rewrite destination frontmatter". Acceptance: take a destination whose `SKILL.md` carries an older `description`, run `apply` with a newer source revision, then read the destination file; its `description` equals the source's while `<!-- core:begin -->` and everything below it are unchanged.
- S2 — Destination-only frontmatter keys survive the refresh, and `local-version` is never reset. Exact requirement: `AGENTS.md` → Reuse guide → "An AICore sync never resets local-version". Acceptance: refresh a destination agent file that carries `local-version: 1.0.1` and a lower `version`; the destination keeps `local-version: 1.0.1` byte-identically and its `version` becomes the source's.
- S3 — `check` reports drift when a destination's frontmatter identity keys do not match what a sync would write. Exact requirement: derived from S1 — a write that `check` does not verify would report `current` on a file `apply` is about to change. Acceptance: run `check` against a destination holding a stale `description`; it exits non-zero and names the affected path; after `apply`, the same `check` prints `current`.
- S4 — DEBT-038 is retired in the delivery that clears it. Exact requirement: `knowledge/debt.md` → "Clear and retire a debt in the same PR: the PR that clears a debt deletes its entry from this register". Acceptance: read `knowledge/debt.md`; it contains no `DEBT-038` heading, and the commit that removes it carries the resolution evidence.
- S5 — No destination project is written by this feature's work. Exact requirement: "dont touch nothing on tismart-support project". Acceptance: inspect both commit trees; every path lies inside the ai-core repository.

## Tasks

- T1 | S1, S2 | delegated (pure domain transformation plus two application call sites; the merge rule needs one definition shared by write and verify) — Forge 🔨 (Implementer) | open | commit: pending
- T2 | S3 | delegated (drift comparator in the verify operation) — Forge 🔨 (Implementer) | open | commit: pending
- T3 | S1, S2, S3 | delegated (behaviour tests including the `local-version` preservation case) — Forge 🔨 (Implementer) | open | commit: pending
- T4 | S1, S4 | delegated (SKILL.md description of the new frontmatter rule, and the DEBT-038 retirement) — Scribe ✍️ (Docs & Problems Manager) | open | commit: pending
- T5 | S1, S2, S3, S5 | delegated (whole-suite execution and test-architecture verdict) — Crucible 🔥 (Test Architect) | open | commit: pending

## Log

- L1 — 2026-11-05 — Original request, verbatim: "Make sync rewrite destination frontmatter" (selected in answer to "DEBT-038 needs one of its two treatments actually built to close. Which one?"), preceded by the clarification "I DONT UNDERSTAND WHAT ARE U DOING, U ARE MODIFYING THE VERSION IN THE DESTINY?".
- L2 — 2026-11-05 — Why this is a new feature and not a continuation. The prior record `odd/tasks/2026-11-05-core-sync-creation-and-qmd-index.md` fixed only the creation path: a newly created region target now carries source frontmatter. It deliberately left an existing destination's frontmatter frozen, and DEBT-038 stays open on that surviving consequence. S1 changes that existing-file behaviour, which is a different mechanism, a different failure and a different acceptance check.
- L3 — 2026-11-05 — Evidence for the defect this feature closes. Source `.opencode/skills/odd-workflow/SKILL.md` carries `metadata.version: 2.2.0`; destination `G:\projects-personal-tismart\tismart-support\.opencode\skills\odd-workflow\SKILL.md` carries `metadata.version: 1.0.2` with a different `description`, both with `<!-- core:begin -->` at line 10. Region mode re-emits `destination["before"]` verbatim (`domain/regions.py:107-115`), so no sync ever corrects it. Both files were read on 2026-11-05.
- L4 — 2026-11-05 — Constraint that bounds S2. `AGENTS.md` → Reuse guide item 6 states each destination-derived agent spec adds frontmatter `local-version` and that "An AICore sync never resets local-version". Destination agent files carry it today (`atrium.md:5-6`: `version: 1.0.1`, `local-version: 1.0.1`; `sentinel.md:5-6`: `version: 1.4.1`, `local-version: 1.0.1`). So the refresh must merge by key with the source winning only on keys the source defines, never deleting a destination-only key.
- L5 — 2026-11-05 — Scope boundary carried forward from the prior feature. The user's standing instruction is that no destination project is written by this work (S5). The refresh is implemented and tested against isolated fixtures; the motivating destination receives it only through a sync the user authorizes separately.
- L6 — 2026-11-05 — Mirror: pending recovery. Feature identity `ai-core` / `core-sync frontmatter refresh`, locator `odd/tasks/2026-11-05-core-sync-frontmatter-refresh.md`. No backend round trip is performed or claimed; the repository file is authority.
