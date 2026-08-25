# Phase 1 — Retirement-rule edit + DEBT-001 prune

> **Owner:** Cipher 🔓 (L2 Lead)
> **Pre:** No active plan, empty stash inventory, confirmed G1-G3, no user-story requirement.
> **Reads:** `knowledge/debt.md` and `plans/debt-register-retirement-20260825/plan.md`
> **Writes:** `knowledge/debt.md`

## Steps

1. Replace the rule "Clearing a debt updates the record with the resolution" with the clear+retire-in-same-PR rule: the PR that clears a debt deletes its entry; the Resolution evidence (criteria met, validation/audit results) lives in that PR's body and commit; git history is the permanent record.
2. Add an explicit prohibition: never open a dedicated PR whose sole purpose is pruning cleared entries.
3. Keep the entry-format contract and the other two rules (nonblocking conditions, open-debt disclosure) unchanged.
4. Apply the rule immediately: remove the DEBT-001 entry so the register section holds no entries.
5. Re-read the file and confirm the Rules section describes record → disclose → clear+retire with no residual "updates the record" wording.

## Output

- **Artifact:** `knowledge/debt.md`
- **Schema / shape:** three lifecycle rules (record conditions, open-debt disclosure, clear+retire-in-same-PR) plus an empty register section.

## Gate

- ☑ G1-G2 are satisfied without changing the entry-format contract or Herald's disclosure duty.

## Abort conditions

- Stop if the edit would need to touch any file other than `knowledge/debt.md`.
- Stop if the rule text cannot forbid prune PRs while keeping one-debt-one-PR semantics.
