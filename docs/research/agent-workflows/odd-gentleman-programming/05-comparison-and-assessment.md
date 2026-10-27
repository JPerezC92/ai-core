# 05 — Comparison and assessment

> Part of the [Gentleman Programming / ODD research set](README.md). Research date: 2026-10-22. All claims carry `S#` citations ([sources.md](sources.md)). **This chapter is analysis: every inference is labeled `infer:` and must not be read as fact.** Factual baselines are in [`02-odd-workflow.md`](02-odd-workflow.md) and [`03-rdd-receipt-driven-development.md`](03-rdd-receipt-driven-development.md).

## 1. ODD vs plan-first / plan-approval workflows

**Resemblance** (S4): ODD step 5 (track before the first write) and the single feature document mirror a plan artifact created before code, and the "execution review" moment maps to ODD's one-line announcement of the created document and task count.

**Difference** — `infer:` ODD is automatic and proportional — no plan for small work, no approval gate before implementation (authorization is inferred from the request itself, step 1), and the document is a living spec+task+log, not a one-shot plan awaiting user sign-off. ODD says outright "you do not need to request task tracking or choose a storage mode." (S4)

## 2. ODD vs spec-driven development (spec-kit, Kiro specs)

**Resemblance** (S4): both quote requirements verbatim and derive tasks from numbered specs with acceptance criteria.

**Difference** — `infer:` ODD is spec-lite and asymmetric — one file instead of requirements/design/tasks triplets; SDD was literally retired in gentle-ai v4.0.0 ("SDD Retires, ODD Leads", S11) after being the earlier default, so ODD is positioned as the proportional successor to SDD, with heavy spec phases now only where the work earns them (S4). ODD's `## Log` (L1 = request verbatim) has no counterpart in spec-kit (S4).

## 3. ODD vs TDD-first

**Resemblance** (S4, S10): RED→GREEN→REFACTOR is ODD's default when a runnable deterministic test fits ("Strict TDD" flag retired in v4.0.0 because test-first became the default posture).

**Difference** — `infer:` TDD is a coding discipline inside ODD step 6; ODD adds delivery structure (work-unit commits, review candidates) that TDD does not address, and it permits explained exceptions where no runnable test applies (S4). RDD's stated relationship is complementary, not competitive: "TDD te garantiza que el código hace lo que promete. RDD te garantiza que nadie lo tocó después de que fue verificado." (S8)

## 4. ODD vs "vibe coding"

Direct opposition: `infer:` the entire stack is engineered against unconstrained generation ("verifying beats generating", S9; "Most people use AI as autocomplete on steroids. I think that's a trap", S3). ODD's read-only default, verbatim spec quoting, observed-proof checkoffs, and RDD's byte-frozen receipts are anti-vibe mechanisms (S4, S6, S8).

`infer:` RDD is specifically an answer to the "green checkmark that keeps lying after a rebase" problem that vibe coding ignores entirely — its receipt is bound to exact bytes and recomputed against real git state at each lifecycle point (S8).

## 5. Neutral assessment

### Strengths (drawn only from cited material)

- **Verification is structural, not aspirational**: the receipt binds approvals to exact bytes and recomputes them at each lifecycle point (S8), and reported failures are reproduced before anyone claims success (S4).
- **Proportionality is explicit**: small work creates no durable artifacts (S4, S5), classification is by resumability rather than size (S4), and the ~400-line figure is disclaimed as a heuristic rather than a cap (S4).
- **Honest failure reporting is designed in**: Close reports "every failed or pending check" (S4), findings require `evidence_class` and concrete proof (S20), and the author publishes self-critical benchmark results (the ~3× slowdown on large tasks) alongside the favorable ones (S9, S28).
- **Human authority is preserved**: commit, push, PR, release, and archive require their own explicit authorization (S5, S6, S14).
- **Proportionate delegation**: named triggers only, "none holds by default" (S9).

### Risks (drawn only from cited material)

- **The default-on review switch is contested** by the project's own community: issue #3412 argues RDD should be opt-in (S15).
- **Evidence base is vendor-controlled**: benchmarks are self-run with n=1 per cell (S9, S21, S28); the author's own reproducibility standard ("A number I publish and you cannot reproduce is a claim about my honesty", S7) sets a bar these numbers have not been shown to clear independently.
- **Version sprawl**: multiple coexisting major lines (engram v1.20.0 / v2.0.0 / v3; gentle-ai unsuffixed → /v2 → /v3 → /v4) create stale-documentation risk (S11, S18) — pre-v4 "SDD workflow" material is already stale (S11).
- **Runtime asymmetry**: the atomic RDD lifecycle only renders for Claude Code, OpenCode, Codex, and Pi (S6), and per-runtime features "can differ" (S9) — `infer:` the ecosystem's guarantees are not uniform across its advertised 17 agents.
- **Non-atomic mirror writes** require explicit conflict-preservation discipline at resume (S4); `infer:` this places recovery burden on the worker/parent.

### Open questions

- What does "The 94,000-line pull request" actually describe? The number is **unverified** (talk title only, S1) — see [README.md](README.md#open-questions-and-gaps), gap 1. Chapter 21 of the free book (S29) and the InnoIT talk were not retrievable as text in the research pass.
- Which stable RDD baseline is canonical: "stable path as of v2.2.0" (S26) or "the first stable release of receipt-driven development" = gentle-ai v2.5.0 (S27)? Both appear in the evidence base; see [`03-rdd-receipt-driven-development.md`](03-rdd-receipt-driven-development.md) §6.
- `infer:` whether "proportional spec" (ODD's one-file model) scales to multi-team, long-lived feature work is not addressed by any source read; S4's resume test ("request plus `git diff`") is the only sizing criterion offered.

Back to the overview: [`README.md`](README.md).
