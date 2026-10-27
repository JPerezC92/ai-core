# Evidence map — plan passage → ODD/RDD mechanism → fit verdict

> Row-for-row mirror of `output/research/odd-foundation-fit/evidence-map.md` (60 data rows). **Data artifact — copied, not rewritten:** fit verdicts and confidence values are exactly as recorded in the source; do not edit them here. Companion to [`01-goal-mapping.md`](01-goal-mapping.md), [`02-repair-goals-and-stages.md`](02-repair-goals-and-stages.md) and [`03-conflicts-and-guardrails.md`](03-conflicts-and-guardrails.md). `S#` = research-set citation IDs (`research/odd-gentleman-programming/sources.md`; see [`../odd-gentleman-programming/README.md`](../odd-gentleman-programming/README.md)). Plan passages are cited by section + goal/row identity. Fit verdicts are mapping judgments and are `infer:` throughout. Verdict vocabulary: strong / partial / none / conflict. Confidence: high / medium / low.

| Plan passage (cite) | ODD/RDD mechanism (S#) | Fit | Confidence |
|---|---|---|---|
| Goals G1 — "discoverable entry point" | ODD "runs by default on every request, in every configured runtime" (S4) | partial (implicit harness default-on vs explicit required read) | high |
| Goals G1, Done when — "Root instructions explicitly require reading the entry" | Handoffs: workers "receive a reference to the document… never a paraphrase"; read until `## Log` (S4) | strong | medium |
| Goals G1 — "every new artifact has a defined home" | One feature document `odd/tasks/<feature-name>.md` with fixed anatomy (S4) | strong (principle) | medium |
| Target structure — per-responsibility homes; "persona only; no workflow duplication" | Feature doc mixes Specs/Tasks/Log per feature; persona injected by harness (`persona.json`, S20) | partial (different home axis) | medium |
| Target structure placement rules — "New files require a distinct responsibility and owner" | Requirement-change rule "rewrites only the affected spec and reopens only its task" (S4) | strong | medium |
| Migration acceptance — "Move each obligation to exactly one authoritative home" | Single feature-document home; verbatim-quoted `## Specs` one owner per requirement (S4) | strong | medium |
| File boundaries and splitting protocol — split only at named concerns | "Small, understood work creates no durable task artifacts"; resumability decides (S4, S5) | partial (same proportionality instinct, different trigger) | medium |
| Goals G2 — "without silently widening work" | Step 1 Authorize; "findings do not silently expand authorization" (S4, S5) | strong | high |
| Evidence inspected row `AGENTS.md` — "question-routing tension" (lines 65–71) | Step 3 "one focused question for a real product decision"; at most one assumption challenge (S4) | strong | medium |
| Approved foundation contract — "narrow clarification of question routing… evidence-first, user-only decision routing" | "Only real unresolved product decisions prompt a focused user question, one at a time with a stop/wait" (S4) | partial (narrows when to ask; role-agnostic on who) | medium |
| Approved foundation contract — "load applicable instructions and relevant dependencies" | Project-local skills win over same-name global; multi-root discovery (S4) | partial | medium |
| Approved foundation contract — "critically assess the request and evidence" | Step 2 Explore "existing code and requirements first, proportionately" (S4) | partial | medium |
| Approved foundation contract — ordinary feedback envelope ("observed evidence… next action") | Close: "report the verified outcome, every failed or pending check, and the next step" (S4) | strong | high |
| For encountered defects — "fix only authorized in-scope issues" | Read-only-first; request authorizes (S4, S5) | strong | medium |
| For encountered defects — "route unrelated issues to the existing owner/register with explicit deferral" | Causal admission: "a finding can only block your change if YOUR change caused it" (S8) | strong | medium |
| For encountered defects — "stop affected work for… safety/authority conflicts" | Causal admission applied literally (S8) | conflict (rule must be subordinated to authority stops) | medium |
| For encountered defects — "not automatically accepted nonblocking debt" | Delegation triggers: "A trigger holds only when its condition truly holds; none holds by default" (S9) | partial (analogical: no default disposition) | low |
| Goals G3, Issue — "an ADR or new prose alone cannot prove reliable future execution" | "Good human decisions do not survive contact with an agent unless something enforces them" (S7) | strong | medium |
| Goals G3 — distribution clearance / portable-set neutrality | Engram topic mirror `odd/<feature-name>/tasks` (S4) | none (no clearance/neutrality concept) | high |
| Verification — "Distinguish constructed examples from observed live runs" | "A failure you report is reproduced before anyone decides it already works" (S4) | strong | medium |
| Verification scenario list — "changed evidence after a previous PASS" | Byte-frozen receipts; "change one byte after review → the receipt falls" (S8, S6) | strong | medium |
| Verification, Stop — "Two unsuccessful correction rounds trigger reassessment" | "One bounded correction" round (S6) | partial (ODD stricter: one round) | medium |
| Verification — "Code/testing applicability… Do not fabricate a pytest PASS" | "never invent a runner"; test-first only with runnable deterministic test (S4) | strong | medium |
| R1 — "effective-ignore-or-stop without skill-owned ignore edits" | Read-only-first; no silent authorization expansion (S4, S5) | partial (weak; principle only) | low |
| R1 — "enforce the existing audit contract once through common pure validation" | Enforcement maxim (S7) | partial (cosmetic as a mechanism) | low |
| R2 — "binding each review to its snapshot" | Receipt bound to exact bytes, recomputed against real git state (S8, S6) | strong | high |
| R2 — review candidate is a slice, not accumulated work | "The native review candidate is a work-unit commit or a PR slice, never… the accumulated feature branch" (S4) | strong | high |
| R2 — "count failed correction rounds within a task" | One bounded correction round (S6) | partial | medium |
| R3 — "record actual approvals… distinguish pending history from delivery" | `## Log` `L1` verbatim + appended corrections/evidence/rationale (S4) | partial (no approval/supersession concept) | low |
| R3 / Existing-story policy — "do not… reset unrelated marks" | "A requirement change rewrites only the affected spec and reopens only its task" (S4) | strong | medium |
| R4 — "Exercise rather than merely describe verification" | Close triad + failure reproduction (S4) | strong | high |
| R4 — "compact reproducible inputs/deltas… remain explicitly unmeasured" | "A number I publish and you cannot reproduce is a claim about my honesty" (S7) | strong | medium |
| Stage A — "Record a preparation/review baseline without promising a speedup" | Author publishes self-critical results (~3× slower on large tasks) beside favorable ones (S9, S28; self-run n=1) | partial | low |
| Stage A — "critical assessment, authority map, ordinary feedback and conflict handling" | Steps 1–3 (authorize / explore / one focused question) (S4) | strong | medium |
| Stage B — "explicit support-file reads" | Handoff rule: reference + read-through, never a paraphrase (S4) | partial | medium |
| Stage B — "future instructions do not reproduce bloat or contradictory authority" | Ecosystem's own stale-document sprawl: pre-v4 SDD material already stale (S11; 05 §5) | partial (cautionary evidence, no mechanism) | medium |
| Stage C — "separate promises, constraints, Proof and execution history" | Single living document mixing Specs/Tasks/Log (S4) | conflict (one-file mix vs separation) | medium |
| Stage C — verbatim requirement quoting | `## Specs` "quote your exact strings, error messages, and examples verbatim" (S4) | strong | medium |
| Stage C — full-catalogue collision review | No counterpart (skill registry is per-skill index, S4) | none | high |
| Stage D — "consistent lightweight eligibility" | Classification by resumability: "counts of files, commands, tests… never decide it" (S4) | strong (intent) | medium |
| Stage D — "contract-sized phases instead of private coding recipes" | Work-unit commits "in reviewable slices of about 400 authored changed lines" (S4) | partial (reviewability-driven sizing) | medium |
| Small-document budgets — "enforceable first-increment delivery limits" (line/word maxima) | ~400 lines "only a planning heuristic, not a task acceptance criterion, hard cap…" (S4) | conflict (heuristic vs enforceable; different objects — downgraded) | medium |
| Small-document budgets — "Do not… append running execution transcripts" | `## Log` accumulates corrections/evidence/rationale (S4) | conflict | medium |
| Stage E — "stabilize reviewed inputs… reuse only unchanged evidence" | Byte-frozen receipts (S8, S6) | strong | high |
| Stage E — "consolidate findings and corrections" | Risk-frozen review depth + one bounded correction (S6) | partial | medium |
| Stage E — evidence-classed findings | Findings require `evidence_class`, `causal_disposition`, concrete proof (S20) | strong | medium |
| Execution contracts 6 — "exact invocation evidence" | "A message may name a command only if running that command resolves the block" (S7) | strong | low |
| Stage F — "Retain user-only merge and proven-safe cleanup" | "Commit, push, PR, release, and archive… require their own explicit authorization" (S14, S5, S6) | strong (corroboration) | high |
| Stage F — "live PR evidence"; "Exercise the known DEBT-011 failure classes" | No counterpart in S1–S29 | none | high |
| Stage G — "distinguish walkthroughs from live results" | Reproducibility standard (S7); failure reproduction (S4) | strong | medium |
| Stage G — "Compare like-for-like… decision rounds, correction rounds and escaped defects" | Vendor self-run benchmarks, n=1 per cell (S9, S21, S28) as negative example | partial (standard yes, instrument none) | medium |
| Isolated foundation-only validation — matched baseline/candidate, same command serialized | S7 reproducibility standard; plan's own matched model | strong (plan already models it) | high |
| Execution contracts 4 — per-edit `AWAITING_REVIEW` checkpoints and owner gates | "no approval gate before implementation" (05 §1 `infer:` on S4/S5) | conflict | medium |
| Context and authority — "Keep the existing plan-enforce binding and its default applicability unchanged" | ODD automatic task tracking "without you asking for… task tracking" (S4) | conflict | high |
| Context and authority — "the later execution-authorization turn" | Step 1 authorization inferred from the request itself (S4) | conflict | medium |
| Still excluded — "runner/model/dependency changes" | gentle-ai binary + engram MCP/SQLite dependency (S9, S17) | conflict | high |
| Still excluded — "adopter mutations"; First increment note — "No destination sync or destination mutation is authorized" | gentle-ai "writes into each agent's own config… backed by `state.json`" (research set 01 §5; S9) | conflict | high |
| Portable-set review — "No destination is contacted or modified"; source-neutrality | Harness configurator writes runtime surfaces; non-atomic Engram mirror writes (S4) | conflict | high |
| Still excluded — "artificial TDD for document edits" | Test-first only "when a relevant runnable deterministic test and a clear expected outcome exist" (S4) | none / compatible (conditional test-first) | medium |
| Foundation planning review — "Do not import every historical recommendation as a current requirement" | SDD→ODD migration shows prior defaults retired on evidence ("SDD Retires, ODD Leads", S11) | partial (supports the withdrawal discipline) | low |
