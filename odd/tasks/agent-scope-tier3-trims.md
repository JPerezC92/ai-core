# Agent scope — Tier 3 trims

> **Status:** active
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-10-30
> **Objective:** Apply the proportional-depth principle to the three incident/cross-cutting specs deferred from the Tier 2 feature, removing their unbounded reads and duplicate authoring without touching any gate.
> **Branch:** N/A — not yet created; Herald 📯 (Release Manager) creates `feat/tier3-agent-scope-trims` at first commit.
> **Delivery:** One slice per spec, committed together after review. Forecast approximately 70 authored additions plus deletions, excluding generated files and the version-fixture lines.
> **Runner:** `uv run --frozen --group dev pytest -q`

## Specs

- S1 — `scribe.md`: read the dispatched draft plus the cited ticket evidence instead of the whole draft folder. Acceptance: the publish path names the target draft and its evidence; a folder-wide read is no longer mandated; the exact-word approval gate and evidence discipline are unchanged.
- S2 — `augur.md`: one authored research artifact instead of a transient copy plus a durable copy; scope corpus access to the assigned question. Acceptance: catalog lookup, provenance, freshness and reused-versus-new labelling survive; the assigned question bounds which corpora are read; publication still routes through its existing owner and gate.
- S3 — `investigator.md`: name the specific reference documents instead of "follow whatever the project maintains". Acceptance: register-first order, bounded queries, prior-incident parameter quarantine and evidence discipline are unchanged; the pointer resolves to concrete paths.
- S4 — Stability: no gate, approval, verdict format, escalation or stop condition is removed or softened; every retired obligation is recorded with what it protected before acceptance.
- S5 — Version discipline: each edited runtime spec receives a declared minor bump with the fixture updated; no model, provider, dependency or permission change is made.

## Tasks

- T1 | S1, S2, S3, S4, S5 | inline (governing feature-document bootstrap and coordinator accounting) — Cipher 🔓 (Lead Orchestrator) | in progress | commit: pending
- T2 | S1, S2, S3 | delegated (runtime specs are maintained by Marshal 🎖️ (HR Director)) — Marshal 🎖️ (HR Director) | open | commit: pending
- T3 | S1, S2, S3, S4 | delegated (shared-rule changes require canonical ownership and obligation-preservation review) — Sentinel 🛡️ (Quality Guardian) | open | commit: pending
- T4 | S5 | delegated (test-file edits and the approved whole-suite run are Crucible-owned) — Crucible 🔥 (Test Architect) | open | commit: pending
- T5 | S1, S2, S3, S4, S5 | delegated (independent acceptance must not be authored by the implementer) — Inquisitor 🔎 (PR Reviewer) | open | commit: pending
- T6 | S1, S2, S3, S4, S5 | delegated (Git is exclusively release-owned; local commits are standing-authorized) — Herald 📯 (Release Manager) | open | commit: pending

## Log

- L1 — 2026-10-30 — Original request, verbatim:
  > yes please go with those
- L2 — 2026-10-30 — Preceding correction, verbatim:
  > wait whats the option 1? when i told u to analyze the agents to fix u left these ones outside?
- L3 — Scope evidence: `scribe.md:45,51` mandates reading the whole draft area on publish; `augur.md:53–55,57,79` requires catalog inspection per brief and authors the same findings as a transient file plus a durable handoff, with role-wide corpora at `:67`; `investigator.md:69` points at "the project's own reference docs … follow whatever the project maintains". Carried from `odd/tasks/token-efficient-orchestration.md` L11 (Tier 3 deferred at L13). Those findings were ranked below the repeated-read items by Cipher 🔓 (Lead Orchestrator)'s own recommendation, not omitted from the analysis.
- L4 — Classification: understood goal, but it changes shared agent safety rules and a publication path, so it is not risk-contained as a small change and is not resumable from request plus diff. Non-small. This template-based document is the sole bootstrap write; no spec edit precedes the execution-review pause.
- L5 — Planned acceptance: each spec keeps its load-bearing obligations (S4); version bumps declared with fixtures aligned (S5); test gate green; Sentinel obligation review clean; independent acceptance clean. Retired obligations recorded individually with what each protected.
- L6 — 2026-10-30 — Slice applied and verified. Changed: `scribe.md` (`:45,:51`, 1.2.2→1.3.0), `augur.md` (`:57,:58,:67,:79`, 1.4.0→1.5.0), `investigator.md` (`:69` now an architecture routing reference; catalogs stay at `:70–71`, 1.3.3→1.4.0), fixture `test_agent_versions.py`. Sentinel 🛡️ (Quality Guardian) returned **[PASS]** with zero findings and two INFO notes: the hire-brief transient path in `marshal.md:101` remains reachable only when a dispatch names the file as required, and the `:69` label was broader than its target — the label was tightened to "Architecture routing reference". Test gate: Crucible 🔥 (Test Architect) **[PASS]**, `871 passed, 6 skipped, exit 0`, 16/16 fixtures equal their frontmatter. **Retired** with what each protected: Scribe's whole-draft-area read and open draft-folder tool grant (cross-draft consistency detection for one incident → the dispatch-named draft plus explicitly referenced drafts); Augur's duplicate transient-plus-durable authoring (delivery continuity while publication is pending → the durable brief is the single authored artifact, with a throwaway copy only when a dispatch explicitly requires one); Augur's role-wide corpora access (discovery outside the assigned question → the question bounds which corpora are read, and unconsulted corpora are recorded); Investigator's open-ended project-docs pointer (reaching destination references unknown at core level → concrete named paths, with any extra destination reference arriving as a project binding). No gate, approval, verdict format, escalation or stop condition was removed.
- L7 — Known residual carried from Sentinel's INFO note: a hire research brief is delivered to `output/research/<name>-hire.md` per `marshal.md:101`, so a hire dispatch must state that the throwaway copy is required. Nothing in the specs enforces that; it is a dispatch-time expectation recorded here rather than an open finding.
