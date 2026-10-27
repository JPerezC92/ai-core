# AI-first repository navigation in an ODD-first project

## Record metadata

- Primary domain: `agent-workflows`
- Topic: `ai-repository-navigation`
- Aliases / tags: repository structure, instruction routing, progressive retrieval, ODD, research reuse, context engineering.
- Researched: 2026-10-26, prior executor Augur 🔮 (Research Analyst) for primary-source retrieval; Explore and Augur 🔮 (Research Analyst) for static routes, with coordinator rereads as detailed below.
- Reviewed: 2026-10-27, Scribe ✍️ (Docs & Problems Manager), documentary synthesis/preservation and original-snapshot inspection only; independent semantic review not evidenced here.
- Source versions / revisions: gentle-ai v4.2.0 and mutable `main`; unversioned external guidance as accessed by the prior executor; local pre-change baseline `5087ecf406b65849d18324b45dd342fd5b71f427` plus research originals identified in the feature's L14.
- Applicability: choosing scoped navigation and preserving local ODD authority; static pointer defects at the recorded baseline, not claims about the present implementation.
- Freshness / recheck triggers: changed instructions, source versions, harness discovery rules or task routes. The publication date is not a fresh web fetch.
- Related features / decisions: [`project-structure-and-research`](../../../../odd/tasks/project-structure-and-research.md), especially L8–L11 and S8–S9.
- Supersedes / superseded by: rejects the unsupported flat-`odd/` recommendation for this question; no later study evidenced. Findings below remain dated baseline observations, not a remediation verdict.

## Question and boundaries

How should an AI-first, ODD-first repository guide models to applicable instructions and reusable research without cosmetic relocation or avoidable context loading? Distinguish upstream observations, current local authority, historical evidence and proposed checks. This study grants no implementation, tool-adoption or release approval.

## Method and provenance

This record preserves research already reported in the governing feature's L8–L11. Scribe ✍️ (Docs & Problems Manager) did not retrieve the web sources again. Access dates below identify the prior executor's reported successful fetches, not new retrievals. The prior primary-source passes were `structure-research/primary-evidence1` and `primary-evidence2`, both by Augur 🔮 (Research Analyst). Static walkthrough `structure-research/routes1` was by Explore; `routes2` was by Augur 🔮 (Research Analyst). Cipher 🔓 (Lead Orchestrator) reread the affected entries after routes1. Routes2 reused L8–L9 evidence without more online research.

The local observation baseline is the pre-implementation checkout at `5087ecf406b65849d18324b45dd342fd5b71f427`, not a controlled candidate run. The existing research collections were nonignored untracked inputs at that baseline; their separate L14 SHA256 identities must not be represented as committed contents of that revision. Original snapshots and their manifest were accepted as preparation inputs; this record does not claim new hash measurements or a post-change route test.

## Sources

IDs P1–P6 below are local to this study, not the sibling ecosystem publication's S# IDs or the feature's numbered specs.

| ID | Locator and section | Version / revision | Access or observation date; executor | Supports / limits |
|---|---|---|---|---|
| P1 | https://raw.githubusercontent.com/Gentleman-Programming/gentle-ai/v4.2.0/docs/usage.md — The ODD protocol / One feature document | v4.2.0 tag | 2026-10-26; Augur 🔮 (Research Analyst), primary-evidence1, reported successful fetch; existing ecosystem S4 also reused | Explicit feature path/anatomy; examined sections, not an exhaustive absence proof |
| P2 | https://raw.githubusercontent.com/Gentleman-Programming/gentle-ai/v4.2.0/docs/intended-usage.md — Everyday work: ODD | v4.2.0 tag | 2026-10-26; same prior executor/pass, reported successful fetch | Corroborates prescribed path; distinct from the older ecosystem S5 mutable locator |
| P3 | https://raw.githubusercontent.com/Gentleman-Programming/gentle-ai/main/docs/usage.md — ODD guidance | mutable `main`; commit unknown | 2026-10-26; same prior executor/pass, reported successful fetch | Contemporary comparison only, not a pinned policy dependency |
| P4 | https://openai.com/index/harness-engineering/ — We made repository knowledge the system of record | unversioned case study; page revision unknown | 2026-10-26; Augur 🔮 (Research Analyst), primary-evidence2 | Repository knowledge and instruction entry map; not a local performance experiment |
| P5 | https://agents.md/ — Why AGENTS.md; nested instruction guidance; conflict FAQ | unversioned format guidance; page revision unknown | 2026-10-26; same prior executor/pass | Scoped instruction guidance; not universal proof of harness discovery/precedence |
| P6 | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents — The anatomy of effective context; Context retrieval and agentic search | unversioned engineering guidance; page revision unknown | 2026-10-26; same prior executor/pass | High-signal context/progressive retrieval; no AICore-specific benchmark |
| B1 | [`knowledge/agent-workflow.md`](../../../../knowledge/agent-workflow.md), ODD protocol / Feature document; [`AGENTS.md`](../../../../AGENTS.md), Shared agent rules / adoption guidance | local baseline above; original AGENTS spec 3.0.5 | 2026-10-26; L8 local comparison, L10 routes1 and coordinator reread | Local ODD home, no mirror, canonical entry; old adoption pointers described below |
| B2 | [`knowledge/agents.md`](../../../../knowledge/agents.md), Clean architecture, original line 67; [`architecture/README.md`](../../../../architecture/README.md), original lines 39–126 | local baseline above | 2026-10-26; Explore routes1, coordinator reread | Applicability ambiguity and history in full-read route; not current defect certification |
| B3 | [Implementer runtime](../../../../.opencode/agents/forge.md), Per-step execution, original line 83 | original v1.6.7 in accepted snapshot; local baseline above | 2026-10-26; Explore routes1, coordinator reread | JS/TS test patterns omit Python `test_*.py` in that branch despite broader gate |
| B4 | [Research runtime](../../../../.opencode/agents/augur.md), Research Workflow, original lines 49–54; [saved ODD sources](../odd-gentleman-programming/sources.md) | original runtime v1.2.3; research dated 2026-10-22 | 2026-10-26; Augur 🔮 (Research Analyst), routes2 | No saved-research lookup edge in original runtime; existing evidence used via assignment |

Local links identify canonical owners for a present reader; line numbers and observations refer to original inputs, not whatever later edits put at those paths. The feature L8–L11 retains executor reports; L13–L14 retains baseline/input provenance. In particular, docs navigation and this catalog were absent during the original walkthrough, even though this record links the newly prepared research entry.

## Findings

### ODD location is evidenced; flattening is not

P1 and P2 explicitly prescribe `odd/tasks/<feature-name>.md` with Specs, Tasks and Log. The examined sections prescribe no additional filesystem siblings. `odd/<feature-name>/tasks` is an Engram topic, not a directory (P1; feature L8). This supports retaining the established artifact location rather than flattening for aesthetics; it does not prove no other upstream directory example exists. Local B1 retains that artifact home and prohibits an Engram mirror. Upstream behavior cannot silently override that local distinction or import unrelated tools/gates.

### Context guidance favors an entry map, not a particular folder spelling

P4–P6 support an instruction entry map, high-signal task-specific context and progressive retrieval. These are external guidance/case studies, not local runtime authority. P5 does not establish universal AGENTS.md discovery or precedence: those vary by harness. No examined source establishes that moving `knowledge/` beneath `docs/` reduces tokens, typos, missed instructions, searches or task errors (feature L9). Such improvements remain unmeasured.

### Static routes expose specific pointer/applicability defects

Explore traced code explanation, a Python skill-script change with tests, and frontend review from the actual entry/runtime/architecture pointers (L10). Frontend review was coherent; the explanation and Python routes had applicability/branch ambiguity. Baseline findings, not claims of fixes:

- B2: `knowledge/agents.md:67` lacks an explicit task-applicability qualifier for architecture mandatory reading, creating ambiguity for read-only explanation versus implementation/conformance work. No existing obligation was waived by reporting this.
- B3: `.opencode/agents/forge.md:83` enumerates `*.spec.*` / `*.test.*` but not Python `test_*.py`, despite the broader existing test-owner gate. Repair should clarify the existing branch, not assign another gate owner.
- B1: `AGENTS.md:114–119` uses bare reviewer filenames, while canonical runtimes reside at `.opencode/agents/atrium.md`, `.opencode/agents/bastion.md`, `.opencode/agents/crucible.md` and `.opencode/agents/lumen.md`. Exact locators remove a real resolution ambiguity without a directory migration.
- B2: `architecture/README.md:39–126` puts source-local historical extraction accounting inside a mandated full read. A history extraction with a concise owner pointer can distinguish the current contract from receipts without losing historical evidence.

Static inspection found no need to relocate the governing `knowledge/`, `architecture/` or `odd/tasks/` documents to address these findings (L10). It did not execute a model, code behavior or a controlled benchmark.

### Research reuse needs a saved-evidence edge; incident order already has one

Augur 🔮 (Research Analyst) traced saved ODD research reuse and incident framing (L11). The symptom → problem → verdict route was coherent; destination operational bindings remain project-specific. That observation is not a live incident result and does not relax register-first order.

The original research runtime B4 went directly from investigation to a transient `output/research/` brief; `docs/README.md` and `docs/research/README.md` did not exist. Saved ODD evidence was reached via the assignment, not a project catalog. Both existing topics fit `agent-workflows`. The suggested missing edge is catalog → matching topic → source IDs → applicability/freshness/gap assessment → reuse or bounded extension → durable evidence and catalog update. The walkthrough reused P1–P6 evidence rather than repeating online research (L11).

## Recommendations and alternatives

Retain one authoritative workflow router reached from `AGENTS.md`; let README map locations without becoming a second router. Prefer task-specific exact read-pointers with scope and conditional next steps, preserving owner procedures, exploration when necessary, gates and explicit uncertainty. Keep current rules, feature scope, research evidence and history visibly distinct. Do not make history/persona reading a blanket prerequisite beyond an owner's actual procedure. Missing paths should be reported exactly, not replaced by a guess (feature S8–S9; design recommendation, not a measured result).

Prefer navigation-only corrections and a durable research catalog before proposing further relocation. Reject the repeated unsupported flat-`odd/` proposal for this question (L8). Consolidating `knowledge/` beneath `docs/`, adding ODD sibling folders or moving tool/runtime boundaries has no demonstrated performance benefit in this evidence. Research classification is by primary subject; cross-cutting tags need not create duplicate copies.

Before attributing performance benefit to a migration, compare representative read-only routes against a navigation-only candidate with fixed task/model/harness inputs: record reached authority, omitted obligations, irrelevant reads and ambiguity (L9). This is a proposed evaluation, not an executed experiment or a new runtime gate.

## Limitations and open questions

- Model gains, reduced tokens/searches, spelling errors and instruction misses are unmeasured. Static route coherence is not behavioral reliability.
- No post-change route run, benchmark, incident execution or implementation-conformance verdict is provided here. Candidate repairs must be verified by their owners.
- Mutable web sources have access dates but no captured commit/page identity; do not present them as immutable. Raw fetch payloads are not reproduced in this record; primary-source claims are attributed to the earlier successful retrieval reports.
- The examined upstream sections do not prove an exhaustive directory inventory; no broader upstream adoption follows.
- Harness-specific instruction precedence and tool behavior require bounded evidence for the harness actually used. No named destination's implementation was inspected.
- Missing past research cannot be reconstructed from recollection; preserve explicit unknowns rather than fabricating source dates or results.

## Reuse and supersession notes

Reuse P1–P2 for the pinned ODD path question and P4–P6 as qualified navigation-design guidance; use the sibling [ecosystem record](../odd-gentleman-programming/README.md) for its wider historical scope. Recheck changed upstream claims or runtime pointers rather than repeating the whole study. Use the current local workflow as authority, never this research record. The static findings retain their original baseline after correction; a later verification should add dated evidence/supersession rather than silently turning them into a claim that they are fixed.
