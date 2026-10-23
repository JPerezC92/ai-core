# Agent workflow

<!-- core:begin -->
## Mandatory core

Read this entry before acting. ODD is the governing workflow: one feature document per feature, tracked before the first write. This entry routes work; it does not grant authority, replace an owner procedure, or prove delivery.

### ODD protocol

1. **Authorize** — Does the request authorize a change? Read-only requests stay read-only. Findings do not silently expand authorization.
2. **Explore** — Read the governing source and its required dependents, proportionately. Load applicable instructions and relevant dependencies.
3. **Resolve uncertainty** — Ask one focused question for a real user-only decision; investigate accessible facts first. Delegated workers report gaps to Cipher and never invoke the user-facing question tool.
4. **Classify** — Small work is understood, risk is contained, and resumable from the request plus the diff. Large work is anything else. File, command, test, or todo counts never decide it. The existing plan-enforce threshold remains the authority; ODD classification does not override it.
5. **Track before the first write** — For non-trivial work, create or update the feature document before the first state-changing action. Read-only work creates no artifact.
6. **Implement task by task** — Work the tasks in the feature document in order, one coherent slice at a time. Tests and documentation ship with the slice. Do not invent a runner or a test where none applies.
7. **Close** — Report the verified outcome, every failed or pending check, and the next step. Reproduce a reported failure before deciding it already works.

### Feature document

- One feature owns one document: `odd/tasks/<feature-name>.md`.
- `## Specs` carries numbered `S#` requirements, exact strings, and acceptance checks.
- `## Tasks` carries one line per task: stable ID, linked `S#`, route or owner, status, and commit.
- `## Log` carries `L1` = the original request verbatim, then corrections, evidence, and rationale appended in order.
- A requirement change rewrites only the affected spec and reopens only its task.
- Handoffs reference the document and its `S#`; the worker reads until `## Log` and reports which specs it covered.
- No second tracker, no Engram mirror, no per-request context injection.
- The Log holds decisions and evidence, not a running execution transcript.

### Template rule

Every repeatable artifact has exactly one template. Create a new file by copying its template and filling it; never reconstruct the format by research. If a second instance of a file type is needed and no template exists, create the template first.

| Artifact | Template |
|---|---|
| Feature document | `odd/tasks/_template.md` |
| Feature-document checklist | `.opencode/skills/odd-workflow/references/_checklist.md` |
| Legacy plan, migration only | `.opencode/skills/plan-enforce/references/_template.md` |
| Legacy story, migration only | `.opencode/skills/user-story/references/_template-user-story.md` |

### Conflict

Identify both obligations, their authority, owner, impact, and disposition. Stop affected action while unresolved. Do not silently expand unrelated work. Do not defer mandatory safeguards or necessary touched-file rework because correction is complex. Route unrelated defects to their owner with explicit deferral; reporting is not accepted debt.

### Keep files small

Put each concern in its owner. Before growing a file, remove duplication or extract a named responsibility with purpose, applicability, owner, and an explicit read-pointer. Do not split by arbitrary parts.

Extract skill support to `.opencode/skills/<skill>/references/<concern>.md`; executable tooling to `scripts/`; a new common policy to `knowledge/<concern>.md`. Move each obligation to one home, replace the old body with a pointer, update consumers, and verify links and clearance before deleting the old copy. Shared required extracts ship with clearance; source-local history is not a shared dependency.

Durable history lives at its owner: the feature document's `## Log`, the story's change log if a story still exists, the ADR, and `docs/architecture/history/`. A plan's `## Resolved decisions` is temporal; it does not replace the owner record.
<!-- core:end -->

<!-- project:begin -->
## Project extensions
<!-- project:end -->
