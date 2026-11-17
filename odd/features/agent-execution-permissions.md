# Agent execution permissions

The boundary between what a role's runtime says it must do and what the harness actually lets it run: which command families each role holds, how a mandatory obligation acquires an authorized executor, and how a privilege a role does not hold is satisfied without widening that role.

**Status:** achieved

## Requirements

- [x] R1 — Every command a role's runtime declares mandatory resolves to an authorized execution path for that role, or is reported unavailable with the control it discharges recorded as unverified and no clean verdict issued.
- [x] R2 — A role's granted command set stays inside the operations its documented responsibility names, and a name appearing in an agent runtime is never itself an authorization.
- [x] R3 — The implementing role can run the repository's own read-only lint, format-check, typecheck and reviewed test verification for its assigned slice, without gaining any mutating package-manager operation.
- [x] R4 — Git and GitHub execution remains a single role's authority: no other role's command set reaches a Git or GitHub invocation, and that exclusion is enforced by the command layer rather than by instruction alone.
- [x] R5 — Pull-request merge stays outside every agent's reach, by any mechanism including the hosting API and browser automation.
- [x] R6 — An operation a role is not granted is satisfied by routing it to the role that owns it or by a user decision, never by widening the requester's command set.
- [x] R7 — A granted or denied command is established by observed harness behaviour, never by reading the configuration that is supposed to produce it.
