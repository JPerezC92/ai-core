# Feature name

> **Status:** active
> **Owner:** Name Emoji (Role)
> **Created:** date
> **Objective:** one-line outcome, or `N/A — reason`
> **Branch:** actual branch, or `N/A — reason`
> **Delivery:** delivery strategy, authored additions + deletions forecast (generated files excluded), and slice boundaries when known, or `N/A — reason`
> **Runner:** literal applicable command, or `N/A — reason`

The header keeps Status, Owner, and Created and always shows all four context fields: Objective, Branch, Delivery, and Runner. Fill each field with the actual value or `N/A — reason`; do not silently omit a field. Never invent a branch or runner. Existing closed feature documents are not retrofitted.

## Specs

- S1 — exact user requirement, string, error, command, or example, preserved verbatim, with acceptance checks
- S2 — next requirement

Numbered `S#` entries preserve the user's exact requirements, strings, errors, commands, and examples verbatim, with acceptance checks alongside them. Do not paraphrase, normalize, or add unrequested requirements; record genuine uncertainty as evidence or a focused question, never an unsupported assumption.

## Tasks

- T1 | S1 | inline (reason/trigger) — Name Emoji (Role) | open | commit: pending
- T2 | S2 | delegated (reason/trigger) — Name Emoji (Role) | open | commit: pending

One line per task: stable ID, linked `S#`, route (`inline` or `delegated`) with the reason/trigger that decided it — responsible owner, status, and commit. Record the route and its trigger evidence, not the route label alone. Allowed status: open, in progress, done. `pending` is valid for open or in-progress work; a task marked done cites a 7–64 character hexadecimal commit identifier, and a feature closes only when every task is done and committed. One authorized coherent work-unit commit may evidence several tasks; do not require one commit per task. High-risk units may use separate reviewable commits.

Forecast authored additions plus deletions, excluding generated files, and record the chosen delivery strategy and slice boundaries compactly in this document. Maintain a running count from work-unit commits; when the forecast OR the running count exceeds about 400 authored changed lines, apply the chosen strategy before the next commit. The ~400-line task size is advisory only — not a hard cap, classification input, automatic review trigger, or delivery-slice boundary — and stays separate from this feature-level strategy trigger; it adds no second tracker.

## Log

- L1 — original request, verbatim
- L2 — later user correction, dated and verbatim

`L1` records the original request verbatim. Each later user correction is its own dated, verbatim entry; evidence and rationale go in separate `L#` entries, never merged into the correction text.
