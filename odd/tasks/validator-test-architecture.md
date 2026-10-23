# Validator commit-state semantics

> **Status:** active
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-10-23

## Specs

- S1 — Every feature task has a status (`open`, `in progress`, or `done`) and a commit field; `pending` means the work has no delivery commit yet.
- S2 — A task cannot be `done` while its commit is `pending`; a done task records a non-empty hexadecimal commit identifier (7–64 characters) that names its completed work-unit.
- S3 — A feature cannot be `closed` unless every task is `done` and has a non-pending commit reference.
- S4 — The validator remains mechanical only; it checks task/commit state consistency but does not judge whether work is semantically complete or whether a commit truthfully contains it.
- S5 — Existing closed feature documents record their actual commit reference rather than `pending`.
- S6 — No second tracker, context injection, plugin, or dependency is introduced.

## Tasks

- T1 | S1, S2, S3, S4 | Update validator; split tests into structure, lifecycle, and CLI modules using a shared document factory | in progress | commit: pending
- T2 | S5 | Replace pending commit fields in the three closed feature documents with the actual delivery commit | in progress | commit: pending
- T3 | S1, S2, S3 | Update the template, skill, and checklist with the commit-state rule | in progress | commit: pending
- T4 | S4 | Run feature tests, feature validator, and whole suite | in progress | commit: pending

Allowed status: open, in progress, done. On close, every task is done and committed.

## Log

- L1 — "hey i noticed task said commit: pending another bug?"
- L2 — "REMENBER WE ARE ADOPTING THE MOST NEAREST TO ODD"
- L3 — Evidence: ODD's feature document task anatomy includes a commit field; current closed features have all tasks marked `done` with `commit: pending`. Delivery commits exist (`6e281dc` and `4d3a91d`).
- L4 — Decision: `pending` remains valid for open or in-progress work. `done` requires an actual commit reference; a feature cannot close while any task is uncommitted. The validator checks this mechanical relation only.
- L5 — Owner-gate findings: reject blank/malformed commit references mechanically; annotate the pytest capture fixture; split structure/lifecycle/CLI tests and replace hand-built fixtures with a shared factory.
- L6 — The three already-closed feature documents now cite merge commit `ae234b2eaed7ca2a64ae836a9328dc5f80fbfc1b` for their completed tasks. No legacy plan or research file was changed.
- L7 — Bastion implementation architecture `[PASS]`; Crucible test architecture `[PASS]` on the coordinator-attested current snapshot. Task fixture modules are split by structure, lifecycle, and CLI concern and use the shared factory.
- L8 — `uv run --frozen --group dev pytest -q` → 720 passed, exit 0. The feature validator returns `ok` for all four documents in `odd/tasks/`.
- L9 — Verification is complete, but tasks remain `in progress` until their work-unit commit exists. Commit/push/PR require explicit user authorization; no commit was made.
