# Initial instruction context

> **Status:** closed
> **Closed:** 2026-11-27
> **Disposition:** completed
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-27
> **Objective:** Reduce always-loaded instruction context by deferring two specialized owners behind explicit read-before-action triggers, relocating contributor guidance out of the root runtime spec, and preserving every accepted safeguard.
> **Branch:** `refactor/instruction-context`, based on `d7433d28639db69a720081839912e3432733c3c4`.
> **Delivery:** Four work units: the change across seven files, the closure, the review remediation that restored seven task records and corrected two routing statements, and the re-closure carrying the final record state. Commit, push and PR publication authorized; merge, tag and branch deletion are not.
> **Runner:** `node .agents/skills/odd-workflow/scripts/validate_feature.ts odd/tasks`

## Specs

- S1 — `release.md` and `architecture-decision-workflow.md` leave the configured instruction list while keeping their cleared paths and distribution modes. Acceptance: read `.opencode/opencode.jsonc` `instructions` and `distribution-clearance.json`; neither path is configured and both are still cleared with their prior mode.
- S2 — the always-loaded entry states, for every conditionally loaded owner, the action before which that owner must be consulted, covering delivery actions and not only pull-request body writing. Acceptance: read the routing section and match each conditional owner to a named triggering action; a delivery-readiness action is among them.
- S3 — contributor adoption, version-marker, destination-binding and retired-definition guidance moves to the documentation owner with its meaning preserved, and every live reference resolves. Acceptance: search the root runtime spec for the relocated headings (absent), search the documentation owner (present), and resolve every reference that pointed at the relocated content.
- S4 — System One keeps concise optional-invocation and result-handling obligations in the always-loaded entry, and its technical trace and marker documentation moves to an existing owner instead of being deleted. Acceptance: read the retained section (optional invocation, result shape, footer duty, no-enforcement claim) and the receiving owner's section (trace path, overrides and markers).
- S5 — genuine duplication consolidates without losing an obligation: the pre-existing pointer and authority sections become one routing section, and every original obligation is accounted as retained, translated or retired. Acceptance: compare the original and candidate text and record one disposition per original obligation; no safeguard sentence is dropped unaccounted.
- S6 — the shared behavioral rulebook opens with the H1 `# Shared Agent Rules` inside its core region. Acceptance: read the first lines of `.aicore/core/knowledge/agents.md`; the H1 follows the core marker and precedes the mandatory-core heading.
- S7 — the reported context measurements are candidate-measured, reconcilable and unit-explicit. Acceptance: recompute character and UTF-8 byte totals from the candidate files and match them against the recorded before-and-after figures, with no document counted twice in a scenario.
- S8 — both supported harness configurations can still reach every conditional owner. Acceptance: walk the OpenCode and Cursor configurations statically; in each, the always-loaded entry names a path that exists at its distribution location for every conditional owner.

## Tasks

- T1 | S1 | inline (configuration and clearance verification) — Cipher 🔓 (Lead Orchestrator) | done | commit: 105344cc224132bbf4e021c5846f793e3ddf0394
- T2 | S2, S5 | inline (routing section authoring) — Cipher 🔓 (Lead Orchestrator) | done | commit: 105344cc224132bbf4e021c5846f793e3ddf0394
- T3 | S3, S4 | inline (contributor guidance relocation and System One condensation) — Cipher 🔓 (Lead Orchestrator) | done | commit: 105344cc224132bbf4e021c5846f793e3ddf0394
- T4 | S6 | inline (rulebook heading) — Cipher 🔓 (Lead Orchestrator) | done | commit: 105344cc224132bbf4e021c5846f793e3ddf0394
- T5 | S7, S8 | inline (measurement reconciliation and harness walkthroughs) — Cipher 🔓 (Lead Orchestrator) | done | commit: 105344cc224132bbf4e021c5846f793e3ddf0394
- T6 | S2, S5, S7, S8 | inline (remediation of the independent review's finding 1 and advisories 2–6, including restoration of the seven retired records) — Cipher 🔓 (Lead Orchestrator) | done | commit: 02071cbd9aec59ac49c1cfe6cf95504fafa448b2

## Log

- L1 — 2026-11-27 — Stage A approval, verbatim:

````
Stage A is approved, with the refinements below.

## Decisions

- D1: Stage A only.
- D2: Accept applicability-based cooperative loading for specialized release and ADR procedures only.
- D3: Keep the existing agents.md filename. Do not rename it.
- D4: Relocate contributor adoption guidance to README.
- D5: Add a concise H1: "Shared Agent Rules".
- D6: Defer Stage B for separate evaluation and authorization.

## 1. Initial instruction loading

Remove release.md and architecture-decision-workflow.md from unconditional OpenCode instructions.

Preserve their existing paths and distribution ownership.

Ensure the portable entry instructions contain explicit, unambiguous read-before-action triggers covering every applicable operation.

Release requirements must remain available before the relevant delivery actions, not merely before writing a PR body.

Preserve ADR authorization and acceptance boundaries.

Do not claim cooperative instructions provide runtime enforcement.

Keep agents.md and agent-workflow.md unconditionally loaded during this phase.

## 2. Contributor and System One documentation

Move the non-runtime adoption and destination-binding guidance into the existing README owner.

Preserve its meaning and update affected live references.

For System One, retain concise optional invocation and result-handling obligations.

Relocate necessary technical documentation to an appropriate existing owner rather than silently deleting useful information.

Do not call System One, troubleshoot it, modify its configuration, or restore mandatory invocation.

## 3. Rule ownership

Consolidate genuine duplication and improve instruction routing without weakening existing safeguards.

Keep universally applicable authorization, security, evidence, risk-warning, and unrelated-work protection rules available.

However, do not treat the current size of every universal section as inherently irreducible. Detailed report formats and specialized procedures may deserve later evaluation.

Do not implement Stage B or reopen ODD in this phase.

Preserve live section consumers or update them within the approved scope.

## 4. Measurement correctness

Reconcile the preliminary context estimates using actual candidate measurements.

Avoid double-counting documents already included in the always-loaded set, particularly release.md in the PR preparation scenario.

Reconcile the individual Stage A reductions with the resulting total.

Distinguish characters, UTF-8 bytes, estimated tokens, mandatory retrieval operations, and measured runtime behavior.

Do not claim actual API savings or measured performance improvements.

## 5. Proportionate verification

Perform the approved obligation accounting, affected path and anchor checks, and representative operation walkthroughs.

Verify that the release and ADR procedures remain reachable in both supported harness configurations.

Distinguish documented harness capabilities from cooperative agent behavior and static walkthroughs.

Use existing checks directly relevant to the modified instructions and configuration.

Do not run the entire Core Sync test suite merely as ceremony. Broader verification is appropriate only if required by the governing contract or justified by an actual affected dependency.

No new tests, validators, infrastructure, or harness mechanisms solely to verify documentation.

## 6. Scope

Authorize Stage A changes to:

- AGENTS.md
- .opencode/opencode.jsonc
- README.md
- .aicore/core/knowledge/agents.md
- The necessary ODD tracking and applicable durable feature records.

Preserve the temporary-task and durable-feature semantics established in PR #223.

No unrelated feature rewrites, destination modifications, synchronization, Core Sync changes, skill modifications, permissions changes, compaction changes, or provider changes.

Do not remediate the out-of-scope findings reported in F9.

Use LF line endings.

If an additional live dependency requires modification outside the approved scope, report the concrete dependency and request authorization.

## 7. Completion

Proceed with implementation and author verification.

Avoid another general audit or unnecessary intermediate reports.

Provide the final changed paths, preserved obligations, verified routing, corrected before-and-after context measurements, remaining limitations, and explicit implementation status.

Do not create commits, push, open a PR, or dispatch independent review until separately authorized.
````

- L2 — 2026-11-27 — Baseline established before the first write: PR #223 `MERGED`, squash commit `d7433d2` equals `HEAD`, `origin/main` and the live remote head; both PR #223 records present and closed. Evidence: Herald 📯 (Release Manager) read-only report in the conversation.

- L3 — 2026-11-27 — Stage A delivered. `.opencode/opencode.jsonc` configures only `agent-workflow.md` and `agents.md`; `AGENTS.md` gains `### Instruction routing` carrying one trigger per conditional owner and replaces `### Shared agent rules`; `### Reuse guide` and `### Destination bindings` moved to `README.md` (new `### Version markers and synced surfaces` and `### Neutral core and source-owned state`, plus an atomic-adoption statement and the retired-definition reconciliation sequence at `README.md:110`); `### System 1 execution contract` condensed with its trace detail pointing at `docs/tooling.md`, which already owned it; `.aicore/core/knowledge/agents.md` gains the H1 `# Shared Agent Rules`. Every original obligation is accounted as retained, translated or relocated; no obligation was retired without a reading owner. Evidence: the candidate files and the obligation accounting in this session's delivery report.

- L4 — 2026-11-27 — Verification: `node .agents/skills/odd-workflow/scripts/validate_feature.ts odd/tasks` and `validate_feature_file.ts odd/features` exit 0 with every record `ok`; `pnpm lint` completes with no diagnostic; `pnpm format:check` reports `Checked 459 files … No fixes applied` after one `pnpm format` pass. Candidate-measured always-on instructions are 109,630 characters / 109,972 UTF-8 bytes, against 126,239 / 126,745 before, a reduction of 16,609 characters (13.16%) reconciled exactly across the six changes; all 17 conditional owners named in the routing section resolve to existing paths; both clearance rows for the deferred documents are unchanged (`raw` and `region`). Static reachability walkthroughs recorded for OpenCode (four configured sources) and Cursor (AGENTS.md only). No runtime token measurement was performed and no API saving is claimed.

- L5 — 2026-11-27 — Authorized refinement and feature-semantics correction. The System One trace-resilience clause moved from `AGENTS.md` into `docs/tooling.md`'s existing Operational trace paragraph, which now owns the degradation behaviour; `AGENTS.md` keeps only the pointer. `odd/features/instruction-context.md` R1 was corrected — the always-loaded set is the root spec plus every document it configures, not one file — and R8 was restated as a title-distinguishability guarantee rather than an editorial act; both stayed `achieved` on re-verification. Requirement evidence: R1 the `AGENTS.md` core keeps the universal sections and the routing section names the always-loaded set; R2 `.opencode/opencode.jsonc` configures two sources and the routing list carries one trigger per conditional owner; R3 the routing section's non-enforcement paragraph; R4 `distribution-clearance.json` rows for both deferred documents unchanged (`raw` and `region`); R5 the delivery-action and decision-record rows, with both owner files unmodified; R6 the `### Contributor guidance` pointer and the `README.md` sections; R7 the configuration comment and `README.md:118`; R8 `.aicore/core/knowledge/agents.md:2`. Final candidate measurements supersede L4: always-on **109,557 characters / 109,999 UTF-8 bytes** against 126,239 / 126,745, a reduction of **16,682 characters (13.21%)**, reconciled exactly as A1 −5,122, A2 −6,260, A3 −6,267, A4 −337, A5 +1,279, D5 +22 and identity wording +3.

- L6 — 2026-11-27 — Reopened on the authorized independent review of `b3b3069`, which returned `[BLOCK]` for the closure work unit's seven record deletions and four advisories. Finding 1: the deletion contradicted `odd/tasks/2026-11-27-odd-workflow-efficiency.md` L10, which had retained those same seven records the same day because "the durable-evidence safeguard was not established", with per-record content-based reasons (two truncated evidence reads, an assertion-preservation mapping, an obligation accounting, user-directed exclusions and observations, a user-authorized supersession, and material authorization and acceptance). My safeguard check tested only inbound citations from durable surfaces, which is narrower than the safeguard, which asks whether a durable surface depends on the record as the sole home of *required evidence*. Finding 1 is confirmed against that record and against `odd-workflow/SKILL.md` `### Retire a task record`; the seven records are restored and no deletion stands. Advisories 2–6 are confirmed and fixed: the absolute "no owner listed here is restated" claim is narrowed; the release trigger gains the post-merge reporting action; S5's obligation accounting and S8's walkthroughs are recorded durably at L7 rather than cited to a session report; `docs/tooling.md` is recorded as an out-of-enumeration dependency carrying explicit user authorization; and the size unit is labelled precisely. Evidence: the reviewer's findings and this session's remediation.

- L7 — 2026-11-27 — S5 obligation accounting and S8 reachability walkthroughs, recorded here because a session report is not a durable source. **Accounting, original to disposition.** `### Shared agent rules`: 6 of 6 retained — workflow-entry topics in the always-loaded parenthetical, the feature-record/template/skill bullet, the tooling adoption contract as a trigger, the `### Stop and next-step reporting` bullet, and the analysis-tools/project-bindings sentence; the release pointer is translated into the delivery-action trigger and its "this runtime does not restate that workflow" into the narrowed no-restated-procedure statement. `### Reuse guide` items 1–7 plus the active-runtime paragraph: 8 of 8 relocated — item 1 to `README.md` step 1 plus the new atomicity sentence, item 2 to the `## Repository map` pointer, item 3 to README step 3, item 4 to `### Neutral core and source-owned state`, item 5 to the same subsection's incident paragraph, item 6 to the retired-definitions paragraph with preserve-delete-clear inlined, item 7 to `### Version markers and synced surfaces`, and the identity paragraph to the same subsection. `### Destination bindings`: 4 of 4 relocated to `### Neutral core and source-owned state`. `### System 1 execution contract`: 13 of 13 retained or relocated — provider and non-injection premise, server and tool, call shape, optional invocation, both result branches, the three markers, empty-block meaning, Execute and Observe duties verbatim, the unavailable-branch prohibition, the no-unestablished-claim rule and the footer pointer stay; the trace path, image directory, environment overrides and the unwritable-trace degradation move to `docs/tooling.md`'s Operational trace paragraph, which already owned the first three. `.opencode/opencode.jsonc`: 2 entries retired from unconditional loading, 0 documents retired — both keep their cleared path and mode. `agents.md`: no obligation changed; only the H1 was added. **Walkthroughs.** OpenCode loads `AGENTS.md` by discovery plus the two configured sources, and reaches the other nine routing rows through the list; all 20 paths and skills named there resolve on disk. Cursor loads `AGENTS.md` only, because the merge row sets `cursor: {"omitted": true}`, and reaches the same nine rows by path; no `instructions` mechanism is available to it. A delivery action — readiness packet, delivery body, pre-publication statement or post-merge report — hits row 1; writing, checking or accepting a decision record hits row 2, whose statuses and acceptance gate live unmodified in the owner file.

- L8 — 2026-11-27 — S7 unit precision and the out-of-enumeration dependency. The recorded figure is the UTF-16 code-unit length of each decoded file, which is what `.Length` returns; the candidate always-on total is 109,557 code units and 109,524 Unicode code points, the 33-unit difference being surrogate pairs, and 109,999 UTF-8 bytes. The reduction is 16,682 code units (13.21%) and 16,746 bytes; no code-point reduction is claimed because the base-side code-point total was not measured. `docs/tooling.md` lies outside the file enumeration of approval section 6, which requires an out-of-scope dependency to be reported for authorization; the user then authorized it explicitly in the refinement that permitted relocating the System One trace-resilience clause to an appropriate existing owner, and that authorization is this entry's record of the dependency.

- L9 — Close: delivered and closed with `Disposition: completed`. Every `S#` is verified against the candidate through `02071cbd9aec59ac49c1cfe6cf95504fafa448b2` — two configured instruction documents instead of four, one trigger per conditional owner covering delivery actions through post-merge reporting and decision records, contributor guidance relocated to `README.md`, System One trace documentation owned by `docs/tooling.md`, and `# Shared Agent Rules` present in the core region. No cleared path or distribution mode changed, so no destination owes a reconciliation, and the retirement check's candidates all remain retained because their durable-evidence safeguard was not established — no record was deleted. The independent review of `b3b3069` returned `[BLOCK]` on the deletion and five advisories; all six were confirmed and remediated at L6–L8, and the restoration is carried by `02071cb`. The confirmation re-review of the final head was not complete when this entry was written, so it is reported with the delivery evidence rather than claimed here. Not established and not claimed: runtime token consumption, and Cursor behaviour beyond its documented AGENTS.md loading.
