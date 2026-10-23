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
- S9 — The core-sync agent-version contract test declares the Inquisitor runtime-spec version bump introduced by matcher integration and collects independently.
- S9 — The source-version contract test declares the Inquisitor runtime-spec version bump and collects independently without relying on another test module's import order.

## Tasks

- T1 | S2, S3, S5 | Add `.opencode/skills/git-pr/references/_attribution-patterns.json` and `_attribution-snapshot-template.json` | done | commit: 461e96ba7dcb1879a6a23eb2247109056abf0775
- T2 | S1, S4, S6, S7 | Implement `.opencode/skills/git-pr/scripts/scan_attribution.py` with a deterministic snapshot CLI | done | commit: 461e96ba7dcb1879a6a23eb2247109056abf0775
- T3 | S4, S5, S7 | Add `attribution_testkit.py` and cohesive matcher, exclusion, validation, and CLI test modules | done | commit: 461e96ba7dcb1879a6a23eb2247109056
- T4 | S1, S6 | Add the Inquisitor project-extension binding for Cipher-owned snapshot matching | done | commit: 461e96ba7dcb1879a6a23eb2247109056
- T5 | S1, S8 | Run the exact matcher at the matcher-delivery PR's immutable head and record the result | open | commit: pending
- T6 | S9 | Update the core-sync agent-version contract test for Inquisitor 1.7.0 | done | commit: 461e96ba7dcb1879a6a23eb2247109056
- T7 | S8 | Retire DEBT-007 in the same PR only after the exact head-bound scan passes | open | commit: pending
- T6 | S9 | Update the agent source-version contract fixture for Inquisitor 1.7.0 and make it independently collectible | in progress | commit: pending

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
- L15 — The whole suite found a stale Inquisitor version in `test_agent_versions.py`; T6 updated it to 1.7.0 and made the test independently collectible. Bastion and Crucible returned [PASS].
- L16 — Work-unit commit `461e96ba7dcb1879a6a23eb2247109056abf0775` delivered T1–T4 and T6. The commit subject has a leading BOM; no amend was performed. T5/T7 remain open until matcher PR-head evidence and debt retirement.
- L15 — T6 updated the core-sync agent-version contract test to expect Inquisitor 1.7.0 and to import independently. Bastion and Crucible returned [PASS]; `uv run --frozen --group dev pytest -q` -> 738 passed, exit 0. The ODD feature validator also passes all five documents.
- L15 — The whole suite found `test_agent_versions.py` still expected Inquisitor 1.6.2; the matcher integration correctly bumps it to 1.7.0. T6 records the required test-contract update.
- L16 — Crucible also found the test relied on `test_agent_sources.py` to add `scripts/` to `sys.path`; T6 includes the isolated import-path fix so the test does not depend on collection order.
