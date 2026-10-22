# ADR 0001 — Agent workflow foundation

- **Status:** Accepted
- **Date:** 2026-10-21

## Context

Agents lacked one entry for authority, critical assessment, ordinary feedback, and conflict routing. Instructions, decisions, and history were easy to mix. New files needed final homes before further repairs.

## Decision

- Shared entry: `knowledge/agent-workflow.md`, region-cleared.
- Policy stays in `knowledge/agents.md`; language conventions in role specs; procedures in skills; behavior in stories; delivery in plans.
- Source-local ADRs: `docs/architecture/decisions/`. History: `docs/architecture/history/`. New source-local decisions use the next numbered ADR there, not the shared workflow guide.
- Move `planning-workflow-decisions.md` unchanged to `docs/architecture/history/planning-workflow-decisions.md`. It is history, not runtime.
- First-increment budgets (source delivery limits, not portable policy): guide ≤100 lines/900 words; this ADR ≤80/600; root additions ≤10 lines/150 words; README additions ≤20/250; foundation story ≤80/600.
- Later stages repair authoring, stories, planning, review, and completion. This ADR does not rewrite those procedures.

## Alternatives

- Extend only `knowledge/agents.md` — rejected; entry sequence is a distinct responsibility.
- Treat stories as universal authority — rejected; stories own behavior, not permissions or proof.
- Postpone ADRs — rejected; placement must exist before new files land.

## Consequences

Agents must read the entry. Shared payloads stay identity-neutral and must not depend on this ADR. Existing gates remain. Completion still needs current evidence.
