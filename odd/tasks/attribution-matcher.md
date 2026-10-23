# Exact attribution matcher

> **Status:** active
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-10-23

## Specs

- S1 — The matcher scans complete commit messages, PR title/body, and every changed-file body at one immutable PR head.
- S2 — Approved attribution markers are exactly the `markers` entries in `.opencode/skills/git-pr/references/_attribution-patterns.json`.
- S3 — Approved identity tokens are exactly the `identities` entries in `.opencode/skills/git-pr/references/_attribution-patterns.json`.
- S4 — Matching is case-insensitive and line-based: a trimmed line must start with an approved marker and contain an approved identity. Ordinary mentions without an attribution marker do not match.
- S5 — The literal policy file is excluded from automated matching to prevent self-matches; changes to the policy file require explicit review against the approved list.
- S6 — The scanner is deterministic, standard-library-only, and performs no Git, GitHub, network, or environment access. Cipher executes it against a complete content snapshot supplied by the owning actors.
- S7 — Findings include surface, artifact/path, line number, and matched marker/identity. Exit 1 means a match; exit 0 means no matches; malformed input is a distinct error.
- S8 — DEBT-007 is resolved only in the matcher-delivery PR after an exact scan is run and documented at that PR's immutable head; implementing the matcher alone does not resolve it.
- S9 — The core-sync agent-version contract test expects Inquisitor 1.7.0 and collects independently without relying on another test module's import order.
- S10 — PR drafting for new work uses the governing ODD feature document's Specs/Tasks/Log, not a `plans/` file.

## Tasks

- T1 | S2, S3, S5 | Add `.opencode/skills/git-pr/references/_attribution-patterns.json` and `_attribution-snapshot-template.json` | done | commit: 461e96ba7dcb1879a6a23eb2247109056abf0775
- T2 | S1, S4, S6, S7 | Implement `.opencode/skills/git-pr/scripts/scan_attribution.py` with a deterministic snapshot CLI | done | commit: 461e96ba7dcb1879a6a23eb2247109056abf0775
- T3 | S4, S5, S7 | Add `attribution_testkit.py` and cohesive matcher, exclusion, validation, and CLI test modules | done | commit: 461e96ba7dcb1879a6a23eb2247109056abf0775
- T4 | S1, S6 | Add the Inquisitor project-extension binding for Cipher-owned snapshot matching | done | commit: 461e96ba7dcb1879a6a23eb2247109056abf0775
- T5 | S1, S8 | Run the exact matcher at the matcher-delivery PR's immutable head and record the result | open | commit: pending
- T6 | S9 | Update the core-sync agent-version contract test for Inquisitor 1.7.0 and make it independently collectible | done | commit: 461e96ba7dcb1879a6a23eb2247109056abf0775
- T7 | S8 | Retire DEBT-007 in the same PR only after the exact head-bound scan passes | open | commit: pending
- T8 | S10 | Retarget `git-pr` skill motivation/goal lookup from plans to the ODD feature document and advance its version | in progress | commit: pending

Allowed status: open, in progress, done. `pending` is valid for open or in-progress work. A task marked done must cite its completed work-unit commit. A feature closes only when every task is done and committed.

## Log

- L1 — "can u create it?"
- L2 — User selected the full attribution matcher and approved the proposed markers, identities, and one policy-file self-exclusion.
- L3 — Evidence: `inquisitor.md` requires scanning complete commit messages, PR title/body, and changed-file bodies; DEBT-007 records that the prior approved literal set was unavailable.
- L4 — Policy boundary: the pattern file is repository-readable and excluded only from automatic matching; its changes receive explicit manual policy review. No matcher code or policy was written before this feature document.
- L5 — PR #80 remains separate and unchanged.
- L6 — Crucible's first test-architecture review required separating matcher/reporting, policy exclusion, validation, and CLI concerns and using factory-built cases; those findings were fixed.
- L7 — Forge's first implementation identified malformed `surface` values could raise `TypeError`; validation was corrected to return the malformed-input exit path.
- L8 — Final owner gates: Bastion implementation architecture [PASS], Crucible test architecture [PASS] for the final scanner/test modules.
- L9 — Test execution: `uv run --frozen --group dev pytest -q` -> 738 passed, exit 0. Feature validator reports `ok` for all five ODD documents; policy and snapshot-template JSON parse.
- L10 — Invocation handoff: Herald supplies live PR title/body, full commit messages, and every changed-file body at the pinned head in a snapshot copied from `_attribution-snapshot-template.json`; Cipher runs `uv run --frozen python3 .opencode/skills/git-pr/scripts/scan_attribution.py --policy .opencode/skills/git-pr/references/_attribution-patterns.json --snapshot <snapshot-file>`; Inquisitor reviews the exact head-bound output and records the evidence.
- L11 — A preliminary Inquisitor project-extension binding was reverted when the user deferred the earlier source-specific binding reorganization. After the user approved the full attribution matcher, this feature added only the matcher-specific project-extension binding and advanced Inquisitor to version 1.7.0.
- L12 — T5 and DEBT-007 remain pending until the matcher runs on an actual PR head and the exact result is recorded there. PR #80 remains separate and unchanged.
- L13 — Sentinel audited the Inquisitor integration at its current snapshot and returned [PASS]; policy, snapshot, and scanner bindings remain in Project extensions.
- L14 — The first PR #80 snapshot was rejected because `pr_number` was serialized as a string. The snapshot template now uses a numeric placeholder; regenerate from live metadata before scanning.
- L15 — The initial whole-suite run found the version fixture expected Inquisitor 1.6.2 and depended on another test's `sys.path` setup; T6 updated the expectation and made the test independently collectible.
- L16 — Final owner gates: Bastion and Crucible [PASS]. `uv run --frozen --group dev pytest -q` -> 738 passed, exit 0; the feature validator passes all five ODD documents.
- L17 — Work-unit commit `461e96ba7dcb1879a6a23eb2247109056abf0775` delivered T1–T4 and T6. Its subject has a leading UTF-8 BOM; no amend was performed.
- L18 — T5 exact scan at the matcher-delivery PR head and T7 DEBT-007 retirement remain pending.
- L19 — User authorized push and PR creation for the matcher. Pre-write inspection found `git-pr` Step 2 still requires a plan; T8 retargets this prerequisite to the ODD feature document so the PR can be drafted without the old flow.
- L20 — `git-pr/SKILL.md` Step 2 original input is blob `a5ee41c54fd33ea940f5e1e11c7ddf8051ed331c`; candidate SHA256 `F98A135D22642E0C4B4D92FB593E0E752AFD5C6373952FD800579E8077B0DF50`. Retained: do not select by filename/date/status; stop on missing/ambiguous owner; use governing context for Summary; retain commit-subject ticket references. Translated: plan Context to feature Specs/Tasks/Log. Retired: plan-layout/archive search and reopen guidance for new-work PR drafting, because the feature document is now the single ODD record.
- L21 — Inquisitor snapshot assembly now states the scanner's required input constraints: positive integer PR number, 7–64 hex head, non-empty base, one title/body, at least one sourced commit message, and non-empty safe changed-file paths. Inquisitor candidate SHA256: `406E9EBFC9FE4074D6F241DB8BD8EAA97EDB7A7A072861193DBF4FD929B8833F`.
