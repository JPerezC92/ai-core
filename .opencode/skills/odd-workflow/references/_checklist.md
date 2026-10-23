# ODD feature-document checklist

## Create

- [ ] Copy `odd/tasks/_template.md`; do not invent the format.
- [ ] Header carries Status, Owner, Created.
- [ ] `## Specs` has numbered `S#` with exact strings or acceptance checks.
- [ ] `## Tasks` has stable IDs, linked `S#`, route or owner, status (`open`, `in progress`, `done`), and commit.
- [ ] `## Log` starts with `L1` = the original request verbatim.

## Before the first write

- [ ] The request is authorized; read-only work stays read-only.
- [ ] Non-trivial work has the feature document before the first state-changing action.
- [ ] The plan-enforce threshold is unchanged.

## Change

- [ ] A requirement change rewrites only the affected spec.
- [ ] The affected task is reopened; unrelated tasks stay unchanged.

## Close

- [ ] The verified outcome is reported.
- [ ] Every failed or pending check is reported.
- [ ] The next step is stated.
- [ ] A reported failure was reproduced before deciding it already works.
- [ ] Every task is `done`.
- [ ] `Status` is `closed`, a `Closed:` date is present, and the Log has a `Close:` entry.
- [ ] `uv run --frozen python3 .opencode/skills/odd-workflow/scripts/validate_feature.py odd/tasks` exits 0. This is mechanical anatomy only; semantic correctness is Cipher's review.

## Delivery

- [ ] Closing the feature document is not delivery.
- [ ] Commit, push, PR, release, and archive have explicit user authorization.
- [ ] A PR is a reviewable slice, not the accumulated branch.

## Forbidden

- [ ] No second tracker, no Engram mirror, no per-request context injection.
- [ ] No execution transcript in the Log; decisions and evidence only.
