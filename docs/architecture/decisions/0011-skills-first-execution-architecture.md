# ADR 0011 — Skills-first execution architecture

- **Status:** Accepted
- **Date:** 2026-11-24
- **Accepted:** 2026-11-24 — explicit user approval of the skills-first direction and of the delivery authorization, with the operative rules propagated in the same work unit into the owners named under `## Propagation`. Owner-text verification was performed by the author because the user authorized a bounded transitional exception for this migration; **no independent reviewer verified this record**, and none is claimed.

## Context

AICore carried a fourteen-role specialist roster behind a lead orchestrator, with mandatory dispatches for implementation, architecture review, test review, documentation audit and pull-request review, per-mutation `AWAITING_REVIEW` checkpoints, and independent verdicts as delivery prerequisites. The recurring operational symptoms are recorded in the governing feature's `## Log` (L1): mandatory audits became execution bottlenecks, context transfers and coordination overhead dominated small changes, verification was duplicated between roles, and work remained blocked despite delivered implementation and available evidence.

Two documented facts bounded the decision:

- **The enforced permission surface never matched the roster.** Of fourteen specialist runtimes, only four carried an agent-scoped permission block (`forge`, `crucible`, `herald`, `warden`); the remaining ten inherited the global shell allow and held no isolation relative to each other. The roster was buying context separation and a second model pass, not authority separation, for most of its roles.
- **Most of the mandatory checks were local inventions, not upstream ODD.** Official ODD (`docs/usage.md` and `docs/trigger-rules.md` at `main`, inspected 2026-11-24) routes work inline by default, delegates only for named reasons, and treats native review as an optional, user-owned, risk-tiered mechanism that never authorizes delivery. Per-requirement closure acceptance, gate packets, per-mutation checkpoints and mandatory PR verdicts had no upstream counterpart.

## Decision

1. **The primary agent owns the complete lifecycle.** Cipher authorizes, explores, classifies, tracks, implements, verifies, closes, and prepares delivery evidence directly, retaining execution context throughout.
2. **One custom subagent remains: Herald**, the exclusive Git and GitHub executor. The boundary is preserved in configuration, not prose: `git` and `gh` are denied globally and re-opened only for Herald, and a pull-request merge is never an agent operation.
3. **The other thirteen specialist runtimes are removed.** Their unique procedural knowledge moves to three on-demand skills (`code-review`, `dependency-review`, `visual-review`) or to an existing canonical owner; their orchestration-only content is retired.
4. **Verification is proportionate and evidence-bound.** Automated checks (test suites, linters, formatters, type checking, record validators) are the primary gate. Self-review is a checklist step and is never described as independent. Independent review is available on explicit user request and may be recommended when a declared high-risk item justifies it; it is never a delivery prerequisite.
5. **The seven ODD protocol steps are unchanged.** Only the execution inside steps 6 and 7 changes.
6. **No replacement governance is introduced.** No new orchestration engine, audit framework, receipt system, hook, script, communication protocol or approval layer.

## Alternatives

- **Retain the roster and reduce dispatch frequency.** Rejected: it addresses cost without addressing the head-bound verdict invalidation that turns a linear task into a quadratic one, and rejects the user's direction.
- **Single agent with no Git boundary.** Rejected: it removes the only genuinely enforced authority boundary in the system and collapses Git integrity, release safety and user-merge separation onto the author of the change.
- **Keep mandatory independent review at the PR boundary only (hybrid).** Rejected by the user: it retains the delivery bottleneck the change exists to remove. It remains available as an explicitly requested review.
- **Optional native RDD instead of local mandatory review.** Rejected: the user excluded RDD adoption, and the repository has never claimed an RDD integration.

## Consequences

- **Benefit:** the mandatory multi-agent pipeline, its handoff protocol, its checkpoints and its verdict plumbing are gone; the primary agent's context is no longer transferred per edit.
- **Benefit:** the repository's instruction surface shrinks by thirteen runtime specifications and the procedure that supported them.
- **Cost, accepted:** defect classes no automated check encodes — a wrong abstraction, a misread requirement, silent scope creep — are no longer caught by a second context unless the user requests a review. This is a **local departure from official ODD**, which couples a named high-risk item to an automatic independent verifier. It is recorded as `local · conflicts` in the durable feature file and is not presented as upstream equivalence.
- **Cost, accepted:** dependency review loses its deny-all audit envelope, because the review now runs inside the primary agent's shell context. Installation remains user-authorized independently of the review.
- **Migration boundary:** retired `.opencode/agents/*.md` files are `region`-mode cleared sources, so they are **preserved** on existing destinations and become `pending` entries; each destination reconciles them itself after preserving any destination-owned `project`-region content. No automatic deletion is claimed.
- **Unresolved:** the full-feature-mirror contract stays in its existing pending-recovery state; this decision neither improves nor worsens it.

## Propagation

- `AGENTS.md` → `### Identity & Role` (what Cipher owns and does not), `### Roster`, `### Risk and verification`, `### Conventions`, `### Hard Rules`, `### Merged-branch cleanup`.
- `.aicore/core/knowledge/agent-workflow.md` → `### ODD protocol`, `### Canonical ODD flow` (including its diagram), `### Behavioral verification and runner selection`, `### Feature document`, `### Scope changes and readiness`.
- `.aicore/core/knowledge/agents.md` → `### Shared conduct — all agents`, `### Finding disposition`, `### Internal quality checks`, removal of the safe-parallel coordination and PR-findings-adjudication sections and the roster ownership table, and `### Message presentation`.
- `.aicore/core/knowledge/release.md` → `### PR release readiness`, `### Post-review finding actions`, `### Execution owners`.
- `.aicore/core/knowledge/architecture-decision-workflow.md` → `### Acceptance gate`, `### Ownership`.
- `.agents/skills/odd-workflow/SKILL.md` → `### Close`, `### Completion stages`, `### Handoff`, `### Validate`.
- `.opencode/agents/herald.md` → `### Your Role`, `#### Upstream trigger`, `#### Execution steps` 7–8, `### Output Format`, `### Hard Rules`.
- `docs/architecture/odd-adoption-status.md` → `## Explicit local deviations`.
