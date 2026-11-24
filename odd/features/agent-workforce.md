# Agent workforce

The set of agents that holds the project's execution responsibilities: which roles exist, what each one assures, and where specialist knowledge lives when it is not a role.

**Status:** achieved

## Requirements

- [x] R1 `local` — every agent in the roster carries a runtime specification whose frontmatter declares a SemVer `version`.
- [x] R2 `local` — the roster holds no role whose responsibilities duplicate another's, and a role that stops supplying unique assurance is removed rather than retained as an optional duplicate.
- [x] R3 `local` — the primary agent performs implementation, verification and closure directly, and no separate authoring or accepting role is required for that work to proceed.
- [x] R4 `local` — specialist procedural knowledge that is not architectural authority lives in an on-demand skill rather than in a role, and no skill is presented as an independent reviewer, as a separate execution context, or as permission isolation.
- [x] R5 `local` — roster additions and removals are a user decision.
- [x] R6 `upstream` — work is performed inline by default, and delegation happens only for a named reason rather than because a role exists.
- [x] R7 `local · conflicts` — an independent review is available when the user requests one and may be recommended when a declared high-risk change justifies it, but it is never a delivery prerequisite, its absence is never a finding or a pending check, and no stand-in verdict is created when it does not run. Divergence: the upstream standard couples a named high-risk change to an automatic independent verifier.
- [x] R8 `local` — the exclusive Git and GitHub execution boundary is held by one role, enforced in configuration, and merging a pull request is never an agent operation.
- [x] R9 `local` — a dependency-surface change is reviewed against integrity, approved source, licence, advisories and install-time execution before installation, and that review never authorizes the installation itself.
