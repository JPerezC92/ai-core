# Agent workflow

<!-- core:begin -->
## Mandatory core

Read this entry before acting. It routes work; it does not grant authority, replace an owner procedure, or prove delivery.

### Find the governing source

| Concern | Owner |
|---|---|
| Required behavior | Approved story in `user-stories/` |
| Cross-cutting policy | `knowledge/agents.md` |
| Language conventions | Applicable `.opencode/agents/` rulebook |
| Recurring procedure | Owning skill `SKILL.md` |
| Delivery sequence | Current plan |
| Execution grant | Permissions and explicit user authorization |
| Current verification | Fresh evidence on the current snapshot |

Load the applicable owner and its required dependents. Keep mandated full reads, incident register-first order, approvals, and owner gates. Approval and inherited marks are not current proof.

### Assess the request

1. Separate the requested decision, verified facts, interpretations, uncertainty, and missing evidence.
2. Challenge unsupported user or subagent conclusions with evidence.
3. Investigate accessible facts before asking a genuine user-only decision.
4. Do not guess, silently continue, or treat a `[PASS]` as proof by itself.

### Report an outcome

Ordinary feedback states: status; governing source and observed evidence; impact and scope; recommendation and next action; decision needed (`none` when factual). Label conflict, blocker, decision, review, or completion when applicable. Omit unused fields in routine progress. Preserve specialized audit, incident, and PR formats.

### Handle a conflict

Identify both obligations, their authority, owner, impact, and disposition. Stop affected action while unresolved. Do not silently expand unrelated work. Do not defer mandatory safeguards or necessary touched-file rework because correction is complex. Route unrelated defects to their owner with explicit deferral; reporting is not accepted debt.

### Keep files small

Put each concern in its owner. Before growing a file, remove duplication or extract a named responsibility with purpose, applicability, owner, and an explicit read-pointer. Do not split by arbitrary parts.

Extract skill support to `.opencode/skills/<skill>/references/<concern>.md`; executable tooling to `scripts/`; a new common policy to `knowledge/<concern>.md`. Move each obligation to one home, replace the old body with a pointer, update consumers, and verify links and clearance before deleting the old copy. Shared required extracts ship with clearance; source-local history is not a shared dependency.
<!-- core:end -->

<!-- project:begin -->
## Project extensions
<!-- project:end -->
