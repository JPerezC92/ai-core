# Evidence file — Architecture agnostic fallback

> **Record:** [odd/tasks/2026-11-06-architecture-agnostic-fallback.md](../tasks/2026-11-06-architecture-agnostic-fallback.md) — the sole authoritative intent, task and status record for this feature.
> **Owner:** Cipher 🔓 (Lead Orchestrator) — author of this extraction
> **Created:** 2026-11-06

## What this file is for

Attestational detail behind the feature record's `## Log`: obligation accounting dispositions, reviewer verdicts and identities, original/candidate identities, literal commands with observed results, and preservation mapping. Each `E#` section is referenced from a record entry as `E#`. Disposable working evidence; disposable per `### Evidence retention`, with Git history as the recovery archive.

## E1 — obligation accounting

- Documentation side, complete original/candidate dispositions and exclusions: `output/research/architecture-fallback-doc-accounting.md` (author Scribe ✍️, 108 lines; pointer only, `output/` is gitignored). Independent reviewers recomposed it against the baseline captures rather than trusting the author's table: Crucible 🔥 C2 and Sentinel 🛡️ final.
- Runtime side, per-clause dispositions, archived originals and version rationale: `output/research/architecture-fallback-runtime-accounting.md` (author Marshal 🎖️; pointer only). Version classification corrected patch → minor on adjudication J1; stale candidate identity relabelled M1-R2.
- Retirements accepted under L2/L3 authority: guide-required prerequisites (forge/bastion/atrium/crucible), missing-mapping uncertainty stops, `knowledge/agents.md` missing-mapping halt, testing `T25` absent-guide `[UNCERTAIN]`, Python-runner-requires-new-guide. Every retirement names its replacement obligation.

## E2 — original and candidate identities

- Baseline: HEAD `c58255bc47d097b9ade409c7672722606b7e32db` on `main`, captured read-only by Herald 📯 H1 as `output/research/architecture-fallback-originals.md` (785 lines, full originals under path headings) and `output/research/architecture-fallback-baseline-diff.txt` (164 lines). Herald reported no command errors or permission denials; captures are manual transcriptions, not byte-compared.
- Candidate labels: docs D1 / corrections R2; runtime M1-R1 then M1-R2 (`forge.md` 3.1.0, `bastion.md` 1.16.0, `atrium.md` 1.12.0, `crucible.md` 1.16.0). Labels identify rounds, not content hashes; no hash was computed in this feature.
- Limitation recorded by reviewers: no Git identity bound by review sessions; the commit performed under T4 is the mechanical diff identity.

## E3 — reviewer verdicts and identities

| Gate | Owner | Verdict | Scope |
|---|---|---|---|
| B1 | Bastion 🧱 (Backend & Scripts Architect) | [PASS] | canonical selection policy S1–S4 |
| C1 round 1 | Crucible 🔥 (Test Architect) | [BLOCK] | accounting original unavailable to reviewer |
| C1 round 2 | Crucible 🔥 | [PASS] | after Herald baseline capture |
| S1 | Sentinel 🛡️ (Quality Guardian) | ⚠️ [ADVISORY], F1 LOW | runtime specs and accounting |
| S1 F1 re-review | Sentinel 🛡️ | [PASS] | descriptor accounting rows |
| B2 | Bastion 🧱 | [PASS] | combined candidate, backend/scripts scope |
| A2 | Atrium 🏛️ (Frontend Architect) | [PASS] | combined candidate, frontend scope |
| C2 | Crucible 🔥 | [PASS] | combined candidate, test-review scope |
| Whole-feature round 1 | Sentinel 🛡️ | [PASS] | S1–S4, actions A1/A2/A3, calls J1–J3 |
| C3 | Crucible 🔥 | [FAIL] LOW | Python review-history claim "narrowed" |
| C4 | Crucible 🔥 | [FAIL] LOW | index rows promised verdicts absent from statement |
| C5 settled unit | Crucible 🔥 | [PASS] | rows 75/76 + statement 80 |
| Whole-feature round 2 | Sentinel 🛡️ | [PASS] | final combined candidate |

- Coordination deviation: Atrium 🏛️ A2 disclosed one out-of-envelope read-only `Get-ChildItem output/research -Filter *.md` listing. No mutation, no external fetch, no source write; the verdict is retained with the deviation recorded rather than silently accepted.
- Loop cap: the review-record surface failed twice (C3, C4). Settlement was one coherent edit of the three-line unit, then a single confirmation (C5), per the cap's prescribed path.

## E4 — literal commands and observed results

- Herald 📯 H1, read-only inventory, all zero-exit with no denials: `git branch --show-current`; `git status --short`; `git diff --no-ext-diff --no-textconv -- <five doc paths>`; `git show HEAD:<each of the five doc paths>`.
- Observed status at H1: five modified doc paths plus the untracked feature record; all within recorded feature scope; nothing discarded.
- Cipher 🔓 mechanical checks: `uv run --frozen python3 .opencode/skills/odd-workflow/scripts/validate_feature.py odd/tasks` — see record Log close entry for the observed result.
- No test suite was run for this feature: the delivered surface is instruction and architecture policy, so behavioral verification is the recorded normal/adverse walkthroughs. No execution PASS is claimed anywhere.

## E5 — preservation mapping

- Moved to this file: reviewer verdict table, baseline identities, literal command list, deviation note. The record keeps the decisions, their outcomes and the `E1`–`E5` pointers.
- Superseded author artifacts remain point-in-time: `doc-accounting.md:33` ("pending update marked in both rows") is superseded by the dated review statement at `architecture/testing/architecture.md:80` plus the resolved status cells.
- No durable surface outside `odd/` cites this file.
