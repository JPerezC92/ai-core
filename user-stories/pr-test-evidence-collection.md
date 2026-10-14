# User story — pr-test-evidence-collection

> **Created:** 2026-10-13
> **Title:** PR test evidence collection
> **Status:** active
> **version:** 1.0.0
> **Epic:** developer-tooling
> **Affected areas:** `.opencode/agents/inquisitor.md`, `AGENTS.md`, `.opencode/skills/git-pr/SKILL.md`
> **Contract approval:** 2026-10-13 — user approved CREATE + contract as active after the catalogue review, collision report, and contract preview.

## Persona

- A maintainer whose pull request has reached the review boundary and whose declared test plan must be executed and evidenced without a serial bottleneck or conflicting edits to the PR body.

## Goal

- **G:** Test-plan items at the PR boundary are executed concurrently by their grant-holding executors, and every item's evidence lands in the PR body through exactly one writer.
  - Done when: independent ready items overlap in execution while ordered items show their reason; each evidence row names its actual executor and the PR identity; the PR body is written once and live-verified after writing; and the gate verdict derives from the collected evidence.

## Scenario

- A PR carries several independent unchecked test-plan items: their executors run concurrently and one writer records a single consolidated evidence set before the verdict returns.
- Some items depend on each other or compete for the same workspace: they run in order and the ordering reason is visible.
- Boundary review work is large: read-only review slices run concurrently as separate instances, their findings are consolidated, and the PR body is still written once.
- An item's command has no grant holder: it is reported unroutable for reassignment or an explicit manual/optional decision, and no ungranted role executes it.

## Acceptance criteria

- ✅ **AC1 — Concurrent executor dispatch:** Independent ready test-plan items are dispatched to their grant-holding executors concurrently; items that must run in order carry a visible dependency or shared-resource reason.
- ✅ **AC2 — Executor attribution:** Every executed item records the executor that actually ran it; the PR body's evidence is recorded and verified by a role that never executes the items itself.
- ✅ **AC3 — Single PR-body writer:** Exactly one writer records evidence rows and checkbox states in the PR body; concurrent workers never edit the PR body.
- ✅ **AC4 — Complete evidence rows:** Each evidence row records the test-plan item, the PR number and immutable head, the literal executed command and test input, the observed verdict output, and the executor.
- ✅ **AC5 — Manifest-gated execution:** Execution is preceded by a dispatch manifest mapping each item to its executor, expected outcome, and dependency group; collected results converge on the single writer before any body write.
- ✅ **AC6 — Parallel read-only review:** Cross-cutting review work may run as concurrent read-only instances whose findings are consolidated by one coordinator; review instances never write the PR body.
- ✅ **AC7 — Unroutable items fail closed:** An item whose command no granted executor may run is marked unroutable and blocks the gate until it is reassigned or explicitly accepted as manual or optional.
- ✅ **AC8 — Live body verification:** After every PR-body write the writer re-reads the live body; a stale, divergent, or changed-head read blocks the gate instead of overwriting.
- ✅ **AC9 — Evidence-derived gate:** The gate verdict reflects the collected evidence and checkbox states, and a verified item left unticked blocks handoff completion.

## Proof

- AC1 → `.opencode/agents/inquisitor.md` `##### Dispatch protocol` Round 1–2 · completion audit `[PASS]` 2026-10-13
- AC2 → `.opencode/agents/inquisitor.md` `##### Dispatch protocol` Round 2 · `## Test evidence` row executor field · completion audit `[PASS]` 2026-10-13
- AC3 → `.opencode/agents/inquisitor.md` `##### PR-body evidence boundary` · `.opencode/skills/git-pr/SKILL.md` `## Post-PR evidence contract` · completion audit `[PASS]` 2026-10-13
- AC4 → `.opencode/agents/inquisitor.md` `##### PR-body evidence boundary` · completion audit `[PASS]` 2026-10-13
- AC5 → `.opencode/agents/inquisitor.md` `##### Dispatch protocol` Round 1 · completion audit `[PASS]` 2026-10-13
- AC6 → `.opencode/agents/inquisitor.md` `##### Dispatch protocol` Round 2 · completion audit `[PASS]` 2026-10-13
- AC7 → `.opencode/agents/inquisitor.md` `##### Edge cases` · completion audit `[PASS]` 2026-10-13
- AC8 → `.opencode/agents/inquisitor.md` `##### Dispatch protocol` Round 3 · completion audit `[PASS]` 2026-10-13
- AC9 → `AGENTS.md` `### Identity & Role` PR boundary review · `.opencode/agents/inquisitor.md` `##### Dispatch protocol` Round 3 · completion audit `[PASS]` 2026-10-13

## Constraints

- Exactly one active writer owns the PR body — because concurrent writers produce an inconsistent audit surface and race the live verification.
- Concurrency grants no new authority; existing roles, grants, and required gates remain governing — because a fan-out must not bypass role boundaries.
- The test plan stays unchecked until executed evidence exists — because an unexecuted test plan is not a result.
- The reviewing role holds no execution grant — because the gate that judges evidence must not produce it.
- Evidence rows keep verdict-only observed output — because raw dumps bury the audit surface.

## Change log
