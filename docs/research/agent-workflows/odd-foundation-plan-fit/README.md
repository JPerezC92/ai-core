# How ODD can help achieve the agent-workflow foundation plan

## Preservation and applicability note — 2026-10-27

- Primary domain / topic: `agent-workflows` / `odd-foundation-plan-fit`; aliases/tags: foundation plan, ODD fit, plan-first, RDD, guardrails, G1–G3, R1–R4, stages A–G.
- Researched: fit-study date unknown; underlying ecosystem research dated 2026-10-22. Reviewed: 2026-10-27 by Scribe ✍️ (Docs & Problems Manager), full-text preservation/applicability only. Original independent-review date and foundation plan revision unknown; no sources refetched or fit verdicts re-scored.
- Source versions / provenance: fixed local brief and evidence map named below; underlying primary ODD usage v4.2.0. The original `research/odd-gentleman-programming/sources.md` locator is historical provenance; its current relative locator is [`../odd-gentleman-programming/sources.md`](../odd-gentleman-programming/sources.md), added separately on 2026-10-27. The old `plans/agent-workflow-foundation-20261021/plan.md` citation identifies the study's historical comparison target, not a current instruction to find or resume that plan.
- **Historical, not current authority:** the original body and every supporting chapter/evidence row below describe the former foundation-plan contract. In particular “the plan remains active and binding”, `plan-enforce` as the single binding, old threshold/one-file guardrails, debt/stage states, budgets and proposal-owner routes are preserved historical assertions, not present mandates. For new work these authority claims are superseded by current local [`knowledge/agent-workflow.md`](../../../../knowledge/agent-workflow.md) and [`AGENTS.md`](../../../../AGENTS.md): ODD governs; legacy plan/story procedures are migration-only. Preservation does not adopt, validate or silently rewrite the original judgments or proposals.
- Applicability / freshness: reuse for historical comparative reasoning only. Reassess against the current contract for a new policy decision; current plan outcomes and debt states are not established here. All `infer:` labels, quotations, source IDs and uncertainties remain intact. The [evidence map](evidence-map.md) is mirrored data, not a table to update with preservation notes.
- Original publication locator: `research/odd-foundation-plan-fit/`; current prepared locator is this topic under the [research catalog](../../README.md). Related feature: [`project-structure-and-research`](../../../../odd/tasks/project-structure-and-research.md). No superseding fit study evidenced; local-authority supersession above is not a new fit verdict or implementation approval.

---

**Abstract.** This document set maps ODD (Organic Driven Development) and the surrounding Gentleman Programming disciplines — RDD, delegation triggers, close discipline — onto `plans/agent-workflow-foundation-20261021/plan.md` (goals G1–G3, repair goals R1–R4, stages A–G), evidence-first and from a fixed local evidence base only. It reports where ODD maps strongly (close discipline, byte-frozen receipts, authorization discipline), where the fit is partial or explicitly downgraded (G1's default-on mechanism gap, R1, Stage D), where a real boundary conflict exists (authorization model, automatic task tracking, tool adoption), and where ODD contributes nothing (distribution, Stage F specifics, Stage G instrumentation). It is a decision-support research report: every recommendation is a proposal requiring user approval.

## Scope and authority notice (read first)

- **This publication authorizes nothing** — no edit, no adoption, no requirement change, no scope expansion.
- **It is not delivery evidence** for the plan or any story. No plan goal is claimed met or improved by anything in this folder.
- **The plan remains active and binding.** Per plan, Foundation planning review ("Do not import every historical recommendation as a current requirement"), every recommendation here is a **proposal requiring user approval**, never an imported requirement.
- **This folder is a user-requested research publication outside the plan's write manifest** (plan, File boundaries and splitting protocol: "New paths outside this manifest require approved scope and their own budgets before creation"). It was created on explicit user request, not as plan delivery.
- **The plan's exclusions stay visible throughout:** no bulk migration, no new competing handbook, no artificial TDD for document edits, no speedup claim (plan, Still excluded); DEBT-011/012 remain open (plan, Stage F); stage-G pilots remain pending (plan, Stage G).

## Evidence bases and citation convention

- **Fixed evidence base (sole):** `output/research/odd-foundation-fit/brief.md` (fit analysis by Augur 🔮 (Research Analyst)) and `output/research/odd-foundation-fit/evidence-map.md` (passage→mechanism→verdict table). Underlying fixed bases, already cited by the brief: [`../odd-gentleman-programming/README.md`](../odd-gentleman-programming/README.md) research set (citation IDs `S1–S29`) and `plans/agent-workflow-foundation-20261021/plan.md`. No outside research was added and no new claims are made.
- **Citation convention (preserved verbatim):** `S#` = research-set citation IDs (`research/odd-gentleman-programming/sources.md`); plan passages are cited by section name + goal/row identity; every mapping judgment keeps its `infer:` label and is never to be read as fact.
- **Namespace caution:** here `S#` **always** means the research set's citation IDs. ODD's own feature documents use internal `S#` spec IDs — a different, colliding namespace (research set, 02 §3 "Naming caution"). Where ODD's internal spec IDs matter they are spelled out in words.
- **Not relied on:** no web sources; `S29` was never fetched in the research pass and is a pointer only; the "94,000-line pull request" number is unverified and unused anywhere in this set.

## Reading order

1. `README.md` (this file) — scope, authority, summary, gaps.
2. [`01-goal-mapping.md`](01-goal-mapping.md) — G1–G3, including the G1 mechanism gap and G3 distribution `none`.
3. [`02-repair-goals-and-stages.md`](02-repair-goals-and-stages.md) — R1–R4 and stages A–G, including the R1 and Stage D downgrades.
4. [`03-conflicts-and-guardrails.md`](03-conflicts-and-guardrails.md) — the seven conflicts with guardrails, plus the non-fits.
5. [`04-recommendations.md`](04-recommendations.md) — eight proposals, each requiring user approval.
6. [`evidence-map.md`](evidence-map.md) — data artifact: row-for-row mirror of the source verdict table, consulted alongside any file above.

## Executive summary

- **Strongest fit — close discipline (high/high):** "report the verified outcome, every failed or pending check, and the next step" plus "A failure you report is reproduced before anyone decides it already works" (S4) map almost verbatim onto the plan's ordinary-feedback envelope (plan, Approved foundation contract) and R4 ("Exercise rather than merely describe verification"). Cheapest, least ambiguous fit.
- **Strong fit — byte-frozen receipts (high/high):** "change one byte after review → the receipt falls and you review again" (S8) maps onto R2 ("binding each review to its snapshot") and Stage E ("reuse only unchanged evidence"); the plan already implements this manually (SHA256-bound review inputs), so RDD validates an existing practice rather than introducing one.
- **Strong fit — authorization discipline (high/high):** ODD step 1 Authorize + "findings do not silently expand authorization" (S4, S5) map onto G2's "without silently widening work" and "For encountered defects" ("fix only authorized in-scope issues").
- **Sharpest negative — tool adoption (high/high):** adopting gentle-ai, engram or gga, or their harness writes, conflicts with the plan's exclusions ("runner/model/dependency changes", "adopter mutations"), Warden 🔒 (Dependency Warden) review (plan, Execution contracts 2), and the portable-set/destination boundary ("No destination is contacted or modified"; "No destination sync or destination mutation is authorized").
- **G1 carries a real mechanism gap:** ODD's entry is harness default-on ("ODD runs by default on every request…", S4); the plan's entry is a prose required-read, which cannot replicate true default-on behavior without the harness binary — a real gap, not a cosmetic one (`infer:`).
- **G3 distribution = `none` fit:** ODD's only distribution mechanism is the Engram topic mirror `odd/<feature-name>/tasks`, with a documented non-atomic-write caveat (S4); it has no counterpart to region clearance, `distribution-clearance.json` rows, source-neutrality or portable-set review (`infer:`).
- **Sharpest conflict — authorization model:** "no approval gate before implementation" (05 §1 `infer:` on S4/S5) and automatic task tracking (S4) conflict with the plan's execution-authorization turn and the preserved plan-enforce binding (plan, Context and authority) — a real boundary conflict, not a wording difference.
- **Downgraded mapping — Stage D:** resumability-based eligibility matches intent, but ODD's ~400-line figure ("only a planning heuristic, not a task acceptance criterion, hard cap…", S4) and the plan's Small-document budgets govern different objects (authored changed lines per work unit vs document size) — partially cosmetic (`infer:`); what transfers is the eligibility criterion, not the budget philosophy.
- **R1 is essentially a non-fit:** two thin transfers (`infer:`) are philosophical backing only — cosmetic if presented as a mechanism.
- **No instrument where the plan needs one:** Stage F specifics ("live PR evidence", DEBT-011 failure classes) have no ODD counterpart (none); Stage G gets S7's reproducibility standard and a cautionary vendor self-run, n=1 example but no instrument for preparation effort, decision rounds, correction rounds or escaped defects.

## Open questions and gaps (all 8, unsmoothed)

1. **Default-on cannot be verified for prose-only implementations.** Every ODD entry/routing claim is pinned to harness-delivered behavior (S4); no source in the fixed base tests whether a document-only required-read entry behaves like ODD's default-on. `infer:` the plan's G1 entry is weaker by construction; this gap is unresolvable from the fixed base.
2. **"No approval gate before implementation" is inference, not quoted ODD text** (05 §1 `infer:` on S4/S5). The corresponding conflict is high-plausibility but rests partly on the research set's own inference chain.
3. **The 400-line heuristic vs Small-document budgets govern different objects** (authored changed lines per work unit vs document size) — the Stage D mapping is deliberately downgraded; no source in the fixed base equates them.
4. **RDD correction count mismatch unresolved:** RDD bounds correction to one round (S6); the plan tolerates two before reassessment (plan, Verification, Stop). Which is preferable is a policy question, not an evidence question.
5. **Runtime asymmetry:** the atomic RDD lifecycle renders only for Claude Code, OpenCode, Codex and Pi (S6), and per-runtime features "can differ" (S9). OpenCode is in the covered set, but no fixed-base source verifies feature parity for this repo's exact runtime configuration.
6. **Tool claims unexercised:** gentle-ai/engram behavior is documented, never observed here (no install permitted; plan exclusions). All tool statements are vendor-documentation facts (S-cited), not observations.
7. **Benchmarks are vendor self-run, n=1 per cell** (S9, S21, S28; research set, README gap 7) — usable only as directional evidence and as S7's negative example.
8. **Terminology gap:** "honest report" is researcher shorthand, not an attested phrase (research set, README gap 5); this set uses the attested close-triad wording instead.
