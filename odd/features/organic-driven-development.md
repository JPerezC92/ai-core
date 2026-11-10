# Organic Driven Development

Organic Driven Development governs every request. Read-only and small work leave no artifact; non-small state-changing work gets one file in `odd/tasks/` that states what the feature must achieve.

**Status:** partial

## Requirements

- [x] R1 `upstream` — the work obeys the seven protocol steps: authorize, explore, resolve uncertainty, classify, track before the first write, implement task by task, close. Evidence: `odd/tasks/2026-11-10-durable-feature-file.md` `## Log` L20–L27 record the route this change followed.
- [ ] R2 `local · conflicts` — a change in requirement or acceptance restarts the route at step 1. Divergence: the original rewrites only the affected spec and reopens only its task.
- [x] R3 `upstream` — every requirement states its exact wording. Evidence: record `## Specs` S1–S7.
- [x] R4 `upstream` — acceptance per requirement names one action and one observable result. Evidence: record `## Specs` acceptance clauses.
- [x] R5 `upstream · local detail` — every task names its requirement, route, owner and status. Evidence: record `## Tasks` T1–T8; the validator enforces the row shape.
- [ ] R6 `upstream · local detail` — the check that ran is recorded, not a verdict.
- [ ] R7 `local` — each piece of evidence is bound to the commit it ran against.
- [ ] R8 `upstream` — the failure that existed first is recorded, or the reason an executable failure cannot apply is stated.
- [x] R9 `upstream` — what was not verified is named. Evidence: `odd/tasks/2026-11-10-durable-feature-file.md` `## Log` L23, L24 and L27 name what remains unverified.
- [ ] R10 `local` — every requirement is accounted as met, restated or retired.
- [ ] R11 `local` — evidence invalidated by a change is voided, never carried forward.
- [ ] R12 `local` — an independent reviewer's verdict per requirement before close.
- [x] R13 `local` — the feature validation passes before close. Evidence: `uv run --frozen python3 .opencode/skills/odd-workflow/scripts/validate_feature.py odd/tasks` exits 0 over the whole directory.
- [x] R14 `upstream · narrowed` — closing the record is not delivery; push, PR and merge stay separately authorized.
