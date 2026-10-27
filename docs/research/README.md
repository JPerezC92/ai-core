# Research catalog

Source-local reusable evidence, not runtime policy, implementation approval, or feature progress. The workflow entry remains [`knowledge/agent-workflow.md`](../../knowledge/agent-workflow.md); this catalog routes only research reuse.

## Find and reuse evidence

1. Look up the question here by topic, aliases and tags; read the matching topic entry and relevant source IDs before external research.
2. Check its scope, provenance, source versions, dates, applicability and freshness. A recent preservation review is not a fresh source fetch or independent verification.
3. Reuse sound evidence for the matching question. Extend the existing topic when the question still matches; do not repeat the whole study by default.
4. Research only bounded gaps: changed, stale, disputed or missing claims. State what needs checking and preserve uncertainty; a fixed freshness interval is not a substitute for applicability.
5. Save reusable findings and their source trail durably using [`_template.md`](_template.md). `output/research/` is temporary briefs/drafts/audits, not the only home of reusable conclusions. Cite related features/ADRs and dated supersession; research does not authorize implementation.
6. Update this catalog's scope, dates, source identities and applicability after the durable record changes. Some repetition may remain necessary; there is no zero-repetition guarantee.

## Classification and format

Use one primary subject domain and a stable topic slug: `docs/research/<domain>/<topic>/README.md`. Tags and aliases express cross-cutting subjects; dates, freshness and review scope belong in metadata, not status/date directory trees. New small studies may consist only of their topic README. Existing multi-file publications retain their entry README and supporting evidence; they are preserved publications, not retroactively reconstructed template instances. The single template for new research records is [`_template.md`](_template.md). New path names use ASCII kebab-case; document text need not be ASCII.

## Topics

### [AI-first repository navigation](agent-workflows/ai-repository-navigation/README.md)

- Domain / aliases / tags: `agent-workflows`; AI-first, ODD-first, context retrieval, repository structure, instruction routing, research reuse.
- Scope: primary-source guidance on ODD artifact placement and progressive context retrieval; static local routes and their ambiguities. Sources P1–P6 and B1–B4 in the record.
- Dates / versions: prior primary-source research and static walkthroughs 2026-10-26; gentle-ai v4.2.0 plus mutable `main`, OpenAI/AGENTS.md/Anthropic web guidance; local baseline `5087ecf406b65849d18324b45dd342fd5b71f427` with the feature's preserved research inputs.
- Applicability / freshness: navigation design and targeted route checks, not proof of fewer tokens/errors or universal harness precedence. Recheck changed runtime pointers or upstream claims before using them as current facts.
- Prior review scope: 2026-10-27 documentary synthesis by Scribe ✍️ (Docs & Problems Manager) from the prior executors' evidence and original local snapshots; no new web retrieval, controlled benchmark, or independent completion verdict.

### [Gentleman Programming / ODD ecosystem](agent-workflows/odd-gentleman-programming/README.md)

- Domain / aliases / tags: `agent-workflows`; Organic Driven Development, Receipt-Driven Development, RDD, gentle-ai, Engram, Alan Buscaglia.
- Scope: ecosystem, ODD protocol, review receipts, tools, installation documentation and inferential comparisons; original S1–S29 citation namespace retained, including S29 as an unfetched pointer.
- Dates / versions: researched 2026-10-22 by Augur 🔮 (Research Analyst); primary ODD usage pinned at gentle-ai v4.2.0; other version lines and mutable sources remain as attributed in the publication.
- Applicability / freshness: historical documentary snapshot, not installation verification or current adoption advice. Latest tags, contested defaults, runtime parity and install paths require targeted rechecking when relevant; original gaps remain.
- Prior review scope: original independent publication-review date unknown; 2026-10-27 preservation/applicability read by Scribe ✍️ (Docs & Problems Manager), without refetch or tool execution.

### [ODD fit against the historical foundation plan](agent-workflows/odd-foundation-plan-fit/README.md)

- Domain / aliases / tags: `agent-workflows`; foundation plan, plan-first, ODD fit, guardrails, G1–G3, R1–R4, stages A–G.
- Scope: fixed-base mapping, seven original conflicts, proposals and row-for-row evidence-map judgments against the former foundation plan; uses the sibling publication's S1–S29 IDs.
- Dates / versions: fit-study research date and original independent-review date unknown; underlying ecosystem research dated 2026-10-22, primary ODD v4.2.0; foundation plan revision unknown.
- Applicability / freshness: historical decision-support only. Claims that the old plan or `plan-enforce` binds new work are superseded by current local ODD authority, not re-adopted through preservation. Do not infer current debt/stage state from this snapshot.
- Prior review scope: 2026-10-27 full-text preservation/applicability read by Scribe ✍️ (Docs & Problems Manager); no new source research, re-scoring or verification of original plan outcomes.
