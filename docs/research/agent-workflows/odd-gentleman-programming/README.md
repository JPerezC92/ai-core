# Research — Gentleman Programming (Alan Buscaglia) & ODD (Organic Driven Development)

## Preservation and applicability note — 2026-10-27

- Primary domain / topic: `agent-workflows` / `odd-gentleman-programming`; aliases/tags: ODD, RDD, gentle-ai, Engram, Alan Buscaglia, developer-tooling ecosystem.
- Researched: 2026-10-22, Augur 🔮 (Research Analyst), as recorded by the original publication below. Reviewed: 2026-10-27 by Scribe ✍️ (Docs & Problems Manager), full-text preservation and applicability only; original independent publication-review date unknown. No sources were refetched and no tool/install behavior was exercised for this copy.
- Source versions: primary ODD usage v4.2.0; other versions and mutable source locators remain attributed in [sources.md](sources.md). Freshness: historical snapshot, not confirmation of current tags, defaults, runtime parity, install availability or benchmark reproducibility. Recheck only relevant changed/disputed claims before current use.
- Applicability: external ecosystem evidence, not this repository's runtime policy, implementation approval or delivery proof. Current local ODD authority is [`knowledge/agent-workflow.md`](../../../../knowledge/agent-workflow.md); in particular the local workflow has no Engram mirror or second tracker. Preserve upstream descriptions as observations, not adopted instructions.
- Provenance: original locator `research/odd-gentleman-programming/` is retained as dated historical context; this topic is its prepared current locator under the [research catalog](../../README.md). Related feature: [`project-structure-and-research`](../../../../odd/tasks/project-structure-and-research.md). No superseding ecosystem study evidenced.
- Source-access qualification: the original publication's blanket access wording does not mean S29 was fetched. Its explicit S29 caveat and source-table pointer-only label control that claim. Original quotations, source IDs, uncertainty and bodies below and in supporting files are preserved, not updated to new research conclusions.

---

> Published research document set. Evidence base: `output/research/odd-gentleman-programming/brief.md` (research brief by Augur 🔮 (Research Analyst)) and `output/research/odd-gentleman-programming/sources.md` (citations S1–S29). Research date: **2026-10-22**.

## Abstract

This set documents the "Gentleman Programming" AI-coding ecosystem created by **Alan Buscaglia** (GitHub `Alan-TheGentleman`; Barcelona, Spain; App Lead at Prowler, Angular Google Developer Expert, Microsoft MVP) and its default development workflow, **ODD — Organic Driven Development**, plus its companion review discipline **RDD — Receipt-Driven Development**. It catalogues the ecosystem components and their version evidence (gentle-ai, engram, gentle-pi/gentle-shell, gga, Gentleman.Dots), reproduces the ODD protocol and feature-document structure in detail (quotes pinned to gentle-ai `docs/usage.md` @ v4.2.0), explains the RDD receipt model and its contested default-on status, covers installation and configuration, and closes with an explicitly inferential comparison against plan-first, spec-driven, TDD-first, and vibe-coding approaches. Every claim carries a source ID (`S#`); every inference is labeled `infer:`; unverifiable claims are flagged, not smoothed.

## What this is / what this is not

**What this is:**
- A traceable research report on a developer-tooling ecosystem and its documented workflows, compiled from a fixed evidence base (S1–S29, all accessed 2026-10-22).
- A structural description of ODD and RDD sufficient for later comparison with other planning/review disciplines.

**What this is not:**
- **Not about the game studio "The Odd Gentlemen."** The confirmed referent of "Gentleman Programming" here is the **AI-coding / developer-tooling ecosystem** by Alan Buscaglia. No sources were consulted for the game studio (brief, Objective).
- Not a benchmark of these tools, not an endorsement, and not adoption advice for any repository.
- Not primary research: no new sources were consulted for this publication; the evidence base is fixed.

## Reading order

1. [`01-overview-and-ecosystem.md`](01-overview-and-ecosystem.md) — who/what, positioning, persona-as-product, org inventory, and the component/version table.
2. [`02-odd-workflow.md`](02-odd-workflow.md) — ODD in full: the seven protocol steps and the `odd/tasks/<feature-name>.md` document anatomy.
3. [`03-rdd-receipt-driven-development.md`](03-rdd-receipt-driven-development.md) — RDD: byte-frozen receipts, risk-frozen review depth, authority burn, origin stories, and the contested default.
4. [`04-tooling-install-and-configuration.md`](04-tooling-install-and-configuration.md) — personas, presets, components, delegation triggers, runtimes, install paths, licensing, determinism and benchmark claims.
5. [`05-comparison-and-assessment.md`](05-comparison-and-assessment.md) — analysis (heavily `infer:`): ODD vs plan-first, spec-driven, TDD-first, and vibe coding, plus a neutral assessment.
6. [`sources.md`](sources.md) — the S1–S29 citation table (mirror of the original data artifact).

## Executive summary

- **Alan Buscaglia** is the person behind "Gentleman Programming": App Lead at Prowler, Angular GDE, Microsoft MVP, with 120k+ YouTube, ~15k Twitch, ~50k Instagram, 10k+ Discord followers; the GitHub org `Gentleman-Programming` hosts the tool repos (S1, S2, S3, S24).
- The ecosystem's stated ethos is *"one rule for AI-assisted work — verifying beats generating"*, framed as "the toolset Alan Buscaglia uses every day, refined in public" (S1, S9).
- **ODD is default-on and read-only-first**: it "runs by default on every request, in every configured runtime", while explanation, investigation, and proposal-only requests stay read-only (S4, S5).
- ODD's core artifact is **one feature document** (`odd/tasks/<feature-name>.md`) with verbatim-quoted numbered specs (`S#`), one line per task, and a `L1` log whose first entry is the user's original request verbatim — mirrored to an Engram topic (S4).
- Work is classified as small/large by **resumability, not size**: "Counts of files, commands, tests, fixes, or a requested todo list never decide it", and the ~400-authored-line figure is explicitly a planning heuristic, not a cap (S4).
- **RDD (Receipt-Driven Development)** freezes the exact reviewed bytes into a receipt: "change one byte after review → the receipt falls and you review again" — "la confianza no se recuerda, se re-deriva" (trust is not remembered, it is re-derived) (S8).
- RDD is **on by default and opt-out** since gentle-ai v3.5.0 (2026-09-22) and in v4.x; the default is contested in issue #3412 (S6, S11, S15).
- Delivery stays human-owned: commit, push, PR, release, and archive "require their own explicit authorization" and RDD approval "never commits, pushes, opens a PR, or overrides repository policy" (S5, S6, S14).
- Delegation is trigger-based — "Delegate for a reason, not for size" — with named triggers (Exploration, Parallel writers, Context backstop, Independent verifier) and none holding by default (S9).
- Ecosystem breadth: **17 supported agents** in v4.x (counts differ by version: 13/15/17), MIT licenses with trademark notices, and self-run (n=1 per cell) benchmark claims that the author himself flags as open work (S9, S11, S21, S28).

## Open questions and gaps

The research brief records 8 conflicts, gaps, and uncertainties. They are reproduced here in full and are **not** smoothed (source: `output/research/odd-gentleman-programming/brief.md`, "Conflicts, gaps & uncertainties"):

1. **"The 94,000-line pull request" — UNVERIFIED number.** Verified only as a talk title (gentlemanprogramming.com events, S1). The story's content is unverified. The two written origin narratives found (the X article of 2026-07-19, S8; `the-organic-rdd-story.md`, S7) describe the v2 fork and an over-build failure, not a 94,000-line PR. **Treat the specific number as unverified wherever it appears in this document set** — including [`03-rdd-receipt-driven-development.md`](03-rdd-receipt-driven-development.md).
2. **engram version lines** — v2.0.0 (2026-09-18) is confirmed (S18), but pkg.go.dev simultaneously reports "highest tagged major version is v3" and Homebrew "remains on the stable v1.20.0 line." Multiple major lines coexist; "engram v2.0.0" is correct but not the whole picture (S17, S18).
3. **gentle-ai latest version** — the releases-page crawl shows v4.1.1 at top (S11), while pkg.go.dev and Alan's LinkedIn post (2026-10-20) show v4.2.0 / Gentle Shell v4.3.0 (S9, S28). Reported as v4.2.0 current, v4.1.1 previous; exact latest tag not re-verified against the GitHub tags page.
4. **Windows install** — the request said "Windows/PowerShell `go install`", which matches current docs (Go 1.25.10+, S9, S16), but older README versions say Scoop; current platforms.md says Scoop/Windows binaries are temporarily unavailable (Authenticode gate) (S16). Both statements are given in [`04-tooling-install-and-configuration.md`](04-tooling-install-and-configuration.md).
5. **"honest report on every change"** — the behavior is documented (report every failed/pending check; reproduce reported failures; evidence-classed findings) (S4, S20), but the exact phrase is not attested in the sources read. `infer:` the label "honest report" is the researcher's shorthand.
6. **Agent counts vary by version** (13/15/17) (S9, S10) — quoted per version, not reconciled into one number.
7. **Benchmarks are self-run, n=1 per cell**, published by the vendor (the author flags this himself) — treat as directional only (S9, S21, S28).
8. **deepwiki.com pages on gentle-ai** were seen in search results but deliberately not used as evidence (secondary aggregator, not primary).

## Evidence note

- **Research date: 2026-10-22.** All sources S1–S29 were accessed on that date (see [`sources.md`](sources.md)).
- **Every claim in this document set carries a source ID (`S#`)** referring to the citation table in [`sources.md`](sources.md), which mirrors `output/research/odd-gentleman-programming/sources.md`.
- **Inferences are labeled `infer:`** and must not be read as facts. They appear mostly in [`05-comparison-and-assessment.md`](05-comparison-and-assessment.md).
- Quoted strings are reproduced verbatim from the cited source and kept in quotation marks with their `S#` tag. Where the brief flags a claim as unverified (see gap 1), it is marked unverified here too.
- Primary ODD evidence is pinned to a tag: gentle-ai `docs/usage.md` **@ v4.2.0** (S4).
