# Phase 3 — align guidance and final acceptance evidence

> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Goal:** G1, G2, G3, G4
> **Pre:** Phases 1–2 gates `[PASS]`; current scoped code/test architecture and whole-suite results recorded.
> **Reads:** `plan.md`; preceding Outputs in full; core-sync skill, AGENTS.md, README and adoption story in full; read-only story index; current implemented CLI and tests.
> **Writes:** `.opencode/skills/core-sync/SKILL.md`; `AGENTS.md`; `README.md`; `user-stories/aicore-adoption-sync.md`

## Steps

1. Dispatch Vault 🔐 (Catalog Steward) to update only the core-sync skill to 2.0.0: mode authority, schema-2 records, root role, fresh/bulk/root flags, source-mode assertions, creation rules, detection/priority, validation barrier, exits and migration troubleshooting. Remove old statements that a source mode is chosen by destination metadata, source clearance is a string list, bindings must always exist or newly registered parents cannot be created. Explain existing root prerequisite and operator reconciliation.
2. Cipher 🔓 (Lead Orchestrator) updates only the AGENTS.md source-owned reuse guide and compatible version marker to 2.7.2; mandatory core bytes stay unchanged. Dispatch Sentinel 🛡️ (Quality Guardian) for that root-document edit. Dispatch Scribe ✍️ (Docs & Problems Manager) to update only README adoption instructions with the short init --bind-cleared command, v2 source modes, automatic instruction-root detection, fresh bindings and reconciliation. No docs/wiki publication or external system is involved.
3. Update the existing adoption story's Goal/Scenario and affected criteria to the actual v2 behavior. Add durable source-authority, all-cleared/fresh-init and root-detection criteria with test-symbol evidence. Replace obsolete default-region authority and new-parent restrictions; retain markerless-region support only when region is explicitly source-declared. Remove historical destination-run events from current feature acceptance and record their retirement in a bounded dated feature log; never access that destination to revive the evidence.
4. Preserve metadata Title/Status/Epic and existing affected-area/index equality. Reconcile all story criteria to current evidence or explicitly scoped removal, avoiding temporal plan/output dependencies and volatile counts. Re-read all written files; run the validator and criterion check below.
5. Obtain independent non-authoring Vault 🔐 (Catalog Steward) skill review and Sentinel 🛡️ (Quality Guardian) root/story/plan audit. A separate final audit binds code architecture, test architecture, test execution and guidance to the current candidate; planning readiness cannot substitute. Reuse the phase-2 suite result if only reviewed documentation changed afterwards.
6. After all layers pass, present the four-goal resume, write per-goal Outcome, complete and archive under plan-enforce, and filesystem-verify all archived artifacts. No release or real sync operation is authorized.

## Output

- **Artifact:** v2 skill/reuse/README guidance and reconciled adoption story; final layered evidence in this plan.
- **Schema / shape:** one coherent source-authority/full/fresh/detection contract; migration rejects legacy source policy instead of guessing; all touched criteria have current durable evidence.
- **Evidence:** independent docs/skill verdicts, validator/criterion results and a distinct final completion audit before goal checkmarks, Outcome or archival.

## Verify commands

| Executor | Command |
|---|---|
| Cipher 🔓 (Lead Orchestrator) | `uv run --frozen python3 .opencode/skills/plan-enforce/scripts/validate_plan.py plans/clearance-v2-bulk-init-20261011 --stories user-stories` |
| Cipher 🔓 (Lead Orchestrator) | `uv run --frozen python3 -B -c "from pathlib import Path;t=Path('user-stories/aicore-adoption-sync.md').read_text();assert not any(l.startswith(('- ⬜','- ❌')) for l in t.splitlines());assert '--bind-cleared' in t and 'instructions.md' in t;print('v2 story reconciliation: PASS')"` |

## Gate

- ⬜ Skill, reuse guide, README and story agree on actual v2 behavior and no stale mode-selection/bootstrap claims survive.
- ⬜ Source root mandatory bytes are unchanged; all reviews are current and independent of authoring.
- ⬜ Story criteria are evidence-reconciled, index metadata matches and validator exits 0.
- ⬜ Final layered completion audit `[PASS]` is recorded before Outcome/status/archive.

## Abort conditions

- Stop on a conflicting rule, unauthorized mandatory-root edit, undetermined criterion or adverse/missing evidence layer.
- Stop if guidance requires an unimplemented capability or any real destination access; return exact discrepancy rather than promise it.
