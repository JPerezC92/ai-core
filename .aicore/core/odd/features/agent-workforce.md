# Agent workforce

The set of agents that holds the project's specialist and independent-verification responsibilities: which roles exist, what each one independently assures, and who authors and reviews their runtime specifications.

**Status:** achieved

## Requirements

- [x] R1 — Every agent in the roster carries a runtime specification under `.opencode/agents/` whose frontmatter declares a SemVer `version`.
- [x] R2 — The roster holds no role whose responsibilities duplicate another's; a role that stops supplying unique assurance is removed rather than retained as an optional duplicate.
- [x] R3 — Cipher 🔓 (Lead Orchestrator) authors runtime specifications through the agent-authoring skill, and an independent reviewer audits every agent-document change before it is accepted.
- [x] R4 — Roster additions and removals are a user decision; no agent adds or removes a team member on its own authority.
- [x] R5 — Ordinary research, evidence reuse and runtime-spec authoring are coordinator responsibilities, so no specialist is dispatched merely because a role exists.
- [x] R6 — Warden's independent assurance for a package proposal is scoped to that package and its resolved graph; it does not depend on repository-wide inventory completion, and an inventory finding that bears on the candidate is evaluated inside that candidate's own gate while an unrelated finding stays with its owner.
