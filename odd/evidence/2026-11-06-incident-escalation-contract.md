# Evidence file — Incident escalation contract

> **Record:** [odd/tasks/2026-11-06-incident-escalation-contract.md](../tasks/2026-11-06-incident-escalation-contract.md) — the sole authoritative intent, task and status record for this feature.
> **Owner:** Cipher 🔓 (Lead Orchestrator) — author of this extraction
> **Created:** 2026-11-06

## What this file is for

Attestational evidence behind the feature Log: identity tables, reviewer verdicts and literal observed results. Decisive conclusions live in the record.

## What this file is not

Disposable working evidence, not a feature record, status tracker, authority, approval or adoption certificate.

## E1 — obligation accounting

Reviewed retained/translated/retired accounting for the permanent owner, workflow navigation, clearance definition, incident-workflow skill/references and core-sync blocker. Superseded C1 wording and the removed temporary-adoption subsection are documented in the record (L24–L30); no valid original obligation was retired — each was retained, translated, or explicitly reassigned to the blocker or the existing synchronization owner. Full pre-condensation version is reproducible from commit `3167df0` and its follow-ups.

## E2 — candidate identities (C3, coordinator-measured SHA256)

| Path | SHA256 |
|---|---|
| knowledge/escalation.md | 1774FA1F9D84C3A53142358B876B0E6011A590595CB7362CCB632D53010581C2 |
| knowledge/agent-workflow.md | 5BBAF1428B32BE73C79167DF265B7FE3532D73FA7FCA79ACFAA516C8A95CCD5A |
| distribution-clearance.definition.md | 06770AC17D7A9DE861670FE7DECC1B39EF4B79825D6109867A716ED69E3C0EEC |
| distribution-clearance.json | 2B22D8E6AB1545409988BF27FAF26383B6B1F1F1D6F46E2EA06F7A019F786582 |
| incident-workflow/SKILL.md | D68251BE541FEF87F7A7294DCCD315669DEEF3F3CC2D44C4D5AFAD6F08AB0243 |
| incident-workflow references/analysis/03-synthesize.md | CCCF2AD73CEF1CD0E785F92D93742C38F34D8ED34BE71B6F6F09773B9A43667A |
| incident-workflow references/_consistency-checklist.md | D25A70731CEAC7D4EF5D2731EB7727977C22E3112CCB120CDF3430FDDC458021 |
| core-sync/SKILL.md | 06AEF70492F0D3FF31815F2FB0BA7F62C1AEC3249359CE2E52493E01A333C02A |
| core_sync_pkg/domain/constants.py | 5E6B6B431F16E204913B3B4291DCBC700CD64F0C76B34EE8AD7F2EA5744A90AA |
| core_sync_pkg/domain/test_reconcile_blocker.py | F4DA1C7227D095EFCA46D23E44B9D8D3B4E550E32B4D31B91B720A1C0403E25C |
| scripts/_core_sync_testkit.py | 2C5392FD970136BF7A35FD11B3EC601A25100122A443326F893D8A3C3AE80DB8 |

Original pre-change copies were preserved during review under a temporary `output/` snapshot (gitignored, not shipped); the committed originals at `main` are the durable comparison source.

## E3 — reviewer verdicts

- T1/sentinel-ready-1 — [PASS] corrected readiness, zero findings.
- T2/vault-review-1 and T2/sentinel-owner-1 — [PASS] on the superseded C1 wording.
- T2/sentinel-owner-2 — [PASS] agnostic project-facing core, no migration guidance, obligations reassigned not retired.
- T2/vault-review-2 — [PASS] skill/metadata/obligation/blocker-interface review, zero findings.
- T5/bastion-impl-2 — [PASS] pure text-constant delta, independent oracle, no schema/lifecycle change.
- T5/crucible-testgate-2 — [PASS] test architecture, independent oracle, hermetic data.
- T3/accept-1 — [PASS] independent whole-feature semantic acceptance at `3167df0`, zero findings, one INFO naming note (no action).

## E4 — literal results

- RED (Crucible 🔥): `uv run --frozen --group dev pytest -q` → exit 1, `1 failed, 982 passed, 6 skipped`, intended new guidance test failing `0 == 1`.
- GREEN (Crucible 🔥): same command → exit 0, `983 passed, 6 skipped in 12.24s`.
- Combined structure check: existing `parse_clearance` accepted the registry; escalation region binding, unique markers, shared-rule link and sole five-column template verified (exit 0).
- Repo-wide anatomy: `uv run --frozen python3 .opencode/skills/odd-workflow/scripts/validate_feature.py odd/tasks` → exit 1 while the unrelated reopened record had a historical Close entry; after closing that delivered record truthfully, the same command exits 0 with all 71 records `ok`.

## E5 — preservation mapping

No content was moved out of the feature record. Review inputs above are reproducible from committed Git history.
