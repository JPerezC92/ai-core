# 03 — RDD: Receipt-Driven Development

> Part of the [Gentleman Programming / ODD research set](README.md). Research date: 2026-10-22. All claims carry `S#` citations ([sources.md](sources.md)); inferences are labeled `infer:`.

## 1. Thesis and origin (written form)

X article by @G_Programming, 2026-07-19, *"Receipt-Driven Development: la confianza no se recuerda, se re-deriva"* (S8):

- The trigger was **the v2 fork decision**; every AI code reviewer "leaves opinions… that stop being true five minutes later when someone pushes one more change".
- Thesis: ***"la confianza no se recuerda, se re-deriva"*** — trust is not remembered, it is re-derived.
- The approval is a cryptographic **receipt bound to the exact bytes reviewed** — not to the branch, not to the PR — recomputed against real git state at each lifecycle point; "change one byte after review → the receipt falls and you review again."
- Division of labor: "TDD te garantiza que el código hace lo que promete. RDD te garantiza que nadie lo tocó después de que fue verificado." (TDD guarantees the code does what it promises; RDD guarantees nobody touched it after it was verified.)
- **Four adversarial AI lenses** — security, reliability, resilience, readability — with evidence-required findings (the "4R lenses").
- **Causal-admission rule:** "a finding can only block your change if YOUR change caused it."
- Full technical chapter: chapter 21 of the free book (the-amazing-gentleman-programming-book.vercel.app, "Verifiable Trust") (S29 — named in S8 as the full technical treatment of RDD receipts/gates; **not fetched in the research pass**, cited as pointer only).

## 2. "The 94,000-line pull request" — UNVERIFIED

The phrase appears as the title of the closing talk of a Gentleman Programming × InnoIT event: *"The 94,000-line pull request, and how Receipt-Driven Development was born"* (gentlemanprogramming.com events section) (S1).

> **Gap (reproduced from the brief):** the title and the related narratives below were found, but **no written source telling the 94,000-line-PR story itself**. **The number 94,000 is unverified** — treat it as an unverified talk title, not an established fact. The two written origin narratives describe the v2 fork and an over-build failure, not a 94,000-line PR (S7, S8). See [README.md](README.md#open-questions-and-gaps), gap 1.

## 3. A second origin narrative

`docs/architecture/the-organic-rdd-story.md` (S7): the first RDD build (Codex GPT-5.6 ultra) over-built unrequested infrastructure from an audit document, costing **"three monthly Codex resets"**. Lessons and rules born from that failure:

- *"Good human decisions do not survive contact with an agent unless something enforces them"*
- *"A message may name a command only if running that command resolves the block."* — rule born from a green-tested dead-end message.

The same document records the community bug-hunt and the reproducible benchmark method: *"A number I publish and you cannot reproduce is a claim about my honesty"*. `infer:` this quote is the stated reason the benchmark claims in [`04-tooling-install-and-configuration.md`](04-tooling-install-and-configuration.md) carry reproducibility caveats.

## 4. Relation to ODD

ODD produces the candidate; RDD reviews it. **"ODD never enables RDD"** (S4, usage.md). `infer:` the two disciplines are deliberately decoupled: ODD is the workflow that shapes the work, and RDD is a review layer whose activation is governed by its own switch.

## 5. Mechanics (docs/architecture/organic-rdd.md, S6)

- **Byte-frozen candidate** — one immutable candidate frozen at START; the receipt is bound to those exact bytes and recomputed against real git state (S6, S8).
- **Risk-frozen review depth** — risk is frozen at START and decides depth:

  | Risk at START | Review depth |
  |---|---|
  | **low** | silent structural checks |
  | **medium** | 1 focus lens + consent |
  | **high** | canonical 4R + consent + forecast |

- **One bounded correction** — a single bounded correction round, not unlimited iteration (S6).
- **Authority burn** — approval burns authority via an exact one-time `acknowledge-approved` token (lifecycle: STATUS→START→collect→`acknowledge-approved` burn) (S6).
- **Causal-admission rule** — "a finding can only block your change if YOUR change caused it" (S8).
- **Human-owned delivery boundary** — review outcome is informational; delivery stays with ordinary repository policy: "Delivery remains human-owned" (S14); RDD approval "never commits, pushes, opens a PR, or overrides repository policy" (S6).
- **Runtime boundary** — the atomic lifecycle renders only for **Claude Code, OpenCode, Codex, and Pi** (S6). `infer:` other configured runtimes may run ODD without the atomic RDD lifecycle.
- **Review-workload protection and evidence classes** (gentle-pi's review layer): findings require `evidence_class`, `causal_disposition`, and concrete changed-hunk / candidate-created-path / differential-test / before/after proof (S20).

## 6. Version history of the RDD switch

| Version / date | State |
|---|---|
| **v1.47.0** (2026-07-10) | RDD begins (S26) |
| v2 line | Unstable; earlier v2.2.0-rc notes "RDD unstable… use v1.46.0 without RDD" (S26) |
| **v2.2.0** (2026-07-27) | "supported stable path as of v2.2.0" (S26) |
| **v3.5.0** (2026-09-22) | **"Receipt-Driven Development On by Default"** — opt-out from here (S11) |
| v4.x | On by default; "run `gentle-ai review mode disable` to turn it off"; explicit OFF choices remain OFF (S4, S6, S21) |

`infer:` the v2-era "opt-in" and v3.5+ "on by default" statements describe successive releases, not a contradiction (S27 records RDD opt-in wording in older gentle-pi releases).

**Note (not smoothed):** S27 (gentle-pi Releases) also states "the first stable release of receipt-driven development" = **gentle-ai v2.5.0**, which sits uneasily beside the "stable path as of v2.2.0" line from S26. Both are reproduced here as found; see [README.md](README.md#open-questions-and-gaps) and the publication report.

## 7. The contested default

Issue **#3412** argues RDD "should be opt-in, not the default" (S15) — evidence that the default is genuinely on and genuinely contested. `infer:` the issue is the public counterweight to the v3.5.0 release title; the docs' explicit opt-out commands ("`gentle-ai review mode disable`", gentle-shell's "`/gentle:review-mode disable`") acknowledge the disagreement (S4, S21).

Next: [`04-tooling-install-and-configuration.md`](04-tooling-install-and-configuration.md) — tooling, runtimes, install, and licensing.
