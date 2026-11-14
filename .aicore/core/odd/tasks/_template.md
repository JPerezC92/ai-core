# Feature name

> **Status:** active
> **Owner:** Name Emoji (Role)
> **Created:** date
> **Objective:** one-line outcome, or `N/A — reason`
> **Branch:** actual branch, or `N/A — reason`
> **Delivery:** delivery strategy, authored additions + deletions forecast (generated files excluded), and slice boundaries when known, or `N/A — reason`
> **Runner:** literal applicable command, or `N/A — reason`

Load and read the `odd-workflow` skill (`.agents/skills/odd-workflow/SKILL.md`) before creating or maintaining this record. Its creation, delivery, change and closure procedures are canonical; this template illustrates their layout, not another policy definition.

## Specs

- S1 — required observable behavior; the exact requirement-defining wording retained beside it; acceptance names one action and one observable result
- S2 — next independently verifiable outcome, with its constraints and acceptance clause

Illustration only — these labels are illustrative, not required syntax, and each entry states one independently verifiable outcome: for the requirement `Show "Access denied" when access is refused.`, write `S1 — Refused access displays the requested message. Exact requirement: Show "Access denied" when access is refused. Acceptance: refuse access and verify the displayed text is exactly "Access denied".` The behavior clause accompanies, never replaces, the user's literal requirement. Approvals and directions belong in Log, not as standalone capabilities; the skill covers splitting, mixed messages and uncertainty.

Each entry is one independently verifiable outcome. The requirement-defining wording is preserved verbatim beside it and is never paraphrased or summarized. The acceptance clause names one action and one observable result. An entry states what must remain true, not how it was implemented: implementation narration — the mechanism, the files touched, the architecture applied — is excluded, except where a path, component or artifact is itself the required behaviour, which is then named as the behaviour it guarantees. A requirement is stated once; an entry that repeats a requirement another entry already states is removed rather than kept. Conversation — an approval, a direction to analyse — is authorization history and belongs in the Log, not in Specs.

## Tasks

- T1 | S1 | inline (reason/trigger) — Name Emoji (Role) | open | commit: pending
- T2 | S2 | delegated (reason/trigger) — Name Emoji (Role) | open | commit: pending

Task-row illustration: `open` → `in progress` → `done`; `commit: pending` while unfinished, a 7–64 character hexadecimal commit reference when done. See the skill's creation, delivery-forecast and closure procedures for task evidence, coherent multi-task commits, strategy thresholds and closure checks.

## Log

- L1 — original request, verbatim
- L2 — later user correction, dated and verbatim

See the skill's creation/change procedures for verbatim requests and dated corrections, approval provenance and affected-only updates. Attestational detail — reviewer identities, input identities, literal command output, preservation mappings — lives in the durable source that already carries it, and the record keeps the outcome, the verdict and a pointer to it; the skill's `### Log evidence` owns that rule. Existing closed history is not rewritten to match this illustration.

Every entry beyond `L2` carries one outcome: what happened, the outcome, the verdict, and a pointer to the durable source that carries the detail — a commit id, a path, or a pull-request number and head. An entry never copies a review transcript, an investigation narrative, a raw command-output dump, or a pull-request body. A record whose task rows are all `done` but which is not closed names its open closure prerequisite in an entry that begins `Blocked:`.
