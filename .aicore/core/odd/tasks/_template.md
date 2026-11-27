# Feature name

> **Status:** active
> **Disposition:** completed | cancelled | superseded (state one on closure and delete the alternatives; `completed` is the only one that claims delivery)
> **Superseded-by:** replacement delivery identity (a `superseded` closure only)
> **Residual risks:** accepted findings and their deciding authority (a closure carrying accepted residual risks only)
> **Owner:** Name Emoji (Role)
> **Created:** date
> **Objective:** one-line outcome, or `N/A — reason`
> **Branch:** actual branch, or `N/A — reason`
> **Delivery:** delivery strategy and relevant unit boundaries, or `N/A — reason`
> **Runner:** literal applicable command, or `N/A — reason`

Load and read the `odd-workflow` skill (`.agents/skills/odd-workflow/SKILL.md`) before creating or maintaining this record. Its creation, delivery, change and closure procedures are canonical; this template illustrates their layout, not another policy definition.

## Specs

- S1 — required observable behavior; acceptance names one action and one observable result
- S2 — next independently verifiable outcome, with its constraints and acceptance clause

Illustration only — these labels are not required syntax: for `Show "Access denied" when access is refused.`, write `S1 — Refused access displays "Access denied". Acceptance: refuse access and verify that exact text.` The exact error matters to acceptance. Approvals and directions are authorization history, not standalone capabilities; the skill covers mixed messages and uncertainty.

Each entry is one independently verifiable outcome with an action and observable result. Preserve material exact wording once in the record under the skill; reference it from the spec when needed. An entry states what must remain true, not implementation narration, unless a specific path or component is the required behavior. Do not duplicate requirements.

## Tasks

- T1 | S1 | inline (reason/trigger) — Name Emoji (Role) | open | commit: pending
- T2 | S2 | delegated (reason/trigger) — Name Emoji (Role) | open | commit: pending

Task-row illustration: `open` → `in progress` → `done`; `commit: pending` while unfinished, a 7–64 character hexadecimal commit reference when done. See the skill's creation, delivery-planning and closure procedures.

## Log

- L1 — material intent and authorization
- L2 — material correction and its date

See the skill's creation/change procedures for selective exact wording, material corrections, approval provenance and affected-only updates. Keep approved scope, current state, unresolved decisions and next action recoverable without the conversation. Attestational detail lives at its appropriate durable source. Existing closed history is not rewritten.

Every entry beyond `L2` carries one outcome: what happened, the outcome, the verdict, and a pointer to the durable source that carries the detail — a commit id, a path, or a pull-request number and head. An entry never copies a review transcript, an investigation narrative, a raw command-output dump, or a pull-request body. A record whose task rows are all `done` but which is not closed names its open closure prerequisite in an entry that begins `Blocked:`.
