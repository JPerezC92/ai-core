# Plan — knowledge-distribution

> **Status:** active
> **Started:** 2026-10-14 02:39
> **Subject:** Prepare the knowledge/ files for distribution clearance with core/project regions and the diagnostic-system rename
> **Layout:** subfolder pattern

## Context

- Prompted by: no `knowledge/` source is cleared for distribution, so nothing defines what of `knowledge/` ships to a destination and what must never ship; `debt.md` can hold AICore's filed records at any time while only its frame may ship (the `debt.template.md` seed already drifts from it); `problems.md`/`symptoms.md` must ship in full while destination-filed records must never be substituted; `query-verification-design.md` is named after one mechanism (violating the artifact-naming HARD RULE), describes the diagnostic system, and promises destinations receive it while shipping nowhere.
- Goal: the five knowledge files carry explicit core/project marker splits with content divided accordingly, the register tables live in their core regions and copy with them, and the clearance registry ships the set under uniform core-region copy semantics.
- Outcome: `core-sync apply` delivers each knowledge file's core region byte-for-byte (frame-only for the record-bearing debt register, full catalog for the shared registers), never touches any project region or destination-filed record, and README plus the definition document state the policy.

## Goals

- ✅ **G1:** Knowledge files are distribution-ready — five files carry exactly one ordered core/project marker pair each with the agreed content division, `debt.md` carries no core table, and the living design is renamed.
  - Issue: nothing defines the ship boundary inside `knowledge/`; without markers a copy can substitute destination records; the debt seed is a drifted duplicate; the living design's name violates the artifact-naming rule and its onboarding promise is undelivered.
  - How: wrap each file's shared content in a core region and its owned content in a project region (core-first reorder of `agents.md`), carve the living design at paragraph level so the pilot's proof surfaces ship, rename it to `knowledge/diagnostic-system-design.md`, delete `knowledge/debt.template.md`, and keep every cited heading verbatim.
  - Files: `knowledge/agents.md`; `knowledge/debt.md`; `knowledge/problems.md`; `knowledge/symptoms.md`; `knowledge/diagnostic-system-design.md`; `knowledge/query-verification-design.md`; `knowledge/debt.template.md`
  - Done when: every file parses under the source-marker rules (exactly one ordered core pair; a project pair only where project text exists), the rename is complete with no live reference to `query-verification-design` or `debt.template` outside `plans/.completed/`, and the pilot's three proof surfaces resolve inside the shipped core region.
  - Trace: `core-sync` AC16, AC19 · `diagnostic-system` AC6, AC7 · `incident-query-verification-pilot` AC5.

- ✅ **G2:** The clearance registry lists the knowledge set as region rows, and the knowledge distribution classes are documented.
  - Issue: `distribution-clearance.json` lists no knowledge source, so no knowledge file may ship, and the shipped classes (frame-only record-bearing register vs full shared catalog) are undocumented.
  - How: add five plain region rows for the knowledge files, document the record shapes and the knowledge distribution classes in `distribution-clearance.definition.md` and the README policy, keep the uniform copy model with no table declarations (register tables live in the core region and copy with it — user correction 2026-10-14), remove the interim `core_table` declaration everywhere it was added (registry attributes, parser field and its cases, skill prose, definition field docs), and align the agent-version test pin with the delivered `inquisitor.md` frontmatter so the whole-suite gate is green on the candidate.
  - Files: `distribution-clearance.json`; `distribution-clearance.definition.md`; `.opencode/skills/core-sync/SKILL.md`; `.opencode/skills/core-sync/scripts/core_sync_pkg/domain/clearance.py`; `.opencode/skills/core-sync/scripts/core_sync_pkg/domain/test_clearance_metadata.py`; `.opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_agent_versions.py`
  - Done when: the registry lists five knowledge region rows with no table declarations, the definition document and README record the distribution classes, the reviewed whole-suite command exits 0, and a fixture verification reports the five knowledge rows current.
  - Trace: `core-sync` AC10, AC11, AC19, AC20.

- ⬜ **G3:** Documentation and story records match the delivered behaviour.
  - Issue: README still documents the retired template seed and the old living-design name, and the touched stories carry no delivery record.
  - How: rewrite README's inventory and reuse-guide shipping policy to the delivered model (uniform core-region copy, frame-only debt register, catalogs ship fully, destination records live in project regions), sweep stale names over every non-temporal surface, and deliver each touched story's dated change-log entry with its real delivery anchor.
  - Files: `README.md`; `user-stories/core-sync.md`; `user-stories/diagnostic-system.md`; `user-stories/incident-query-verification-pilot.md`
  - Done when: semantic review of README and the definition document matches the delivered behaviour, greps for `query-verification-design` and `debt.template` are clean outside `plans/.completed/`, and each touched story carries a dated change-log entry naming this delivery with a resolvable anchor.
  - Trace: `plan-enforce` AC30 (same-change documentation) · completes `incident-query-verification-pilot` AC5.

## Current state

| Area | Current file / behavior | Evidence (file + line / command output) |
|---|---|---|
| Knowledge markers | no `knowledge/` file carries core/project markers | `grep -c "core:begin" knowledge/*.md` → `0` for every file |
| Debt seed | parallel `debt.template.md` keeps a 0-entry frame and drifts from `debt.md` | `diff knowledge/debt.md knowledge/debt.template.md` → ID line and empty-state line differ |
| README inventory | documents the old living-design name and the template seed | `README.md:55`, `README.md:58` |
| README reuse guide | ships the template seed and an "empty" problems register | `README.md:69`, `README.md:87` |
| Clearance registry | lists root runtime, config, one story payload, ten skill roots — no knowledge source | `distribution-clearance.json:4-11` |
| Clearance parser | file records accept `mode` and optional `role` only; unknown fields rejected | `core_sync_pkg/domain/clearance.py:29` `_RECORD_FIELDS`; `:84` unknown-fields error |
| Living design | named for one mechanism; onboarding promise ("destinations receive … this design document") undelivered; proof paragraphs sit in status text | `knowledge/query-verification-design.md:9`, `:21`, `:281` |
| Approved contracts | `core-sync` v1.1.0, `diagnostic-system` v1.0.0, `incident-query-verification-pilot` v1.2.0 active | `user-stories/index.md` rows; `**Contract approval:**` headers |
| Test suite | pytest whole suite across domain/application/infrastructure/tests layers | `uv run --frozen --group dev pytest -q` → `1 failed, 564 passed` at `00a6168d65e6` (Crucible 🔥 execution 2026-10-14): pre-existing `test_agent_versions.py` pin drift — `inquisitor.md` frontmatter `1.5.0` vs pinned `1.4.2`, both untouched by this plan |
| CLI and enrollment lifecycle | `core_sync.py <check\|apply\|init> --source --destination --bindings --source-revision <40-hex>`; `init` also takes `--bind-cleared`; enrollment records `pending` and appends the destination-root blocker; verification exits 0 only on empty `pending` | `composition.py:56-95`; `_core_sync_testkit.py:132-148,222-247`; `ports.py:69` `write_blocker` |

## Behavior change

| Goal | Before | After | Interface contracts | Do-not-break |
|---|---|---|---|---|
| G1 | `knowledge/` files are markerless bodies; a copy substitutes anything inside them | each file ships exactly its core region byte-for-byte; project regions and their records are never touched | marker spellings; `knowledge/diagnostic-system-design.md` path; core-first section order | every heading cited by existing story proofs; register schemas and durable IDs |
| G2 | clearance knows no knowledge source; records accept `mode`/`role` only | five plain knowledge region rows; distribution classes documented | `distribution-clearance.json` stays schema `1`; `parse_clearance` file-record shape | existing rows' semantics; skill-root record shape; exit-code classes |
| G3 | README documents the seed and the old name | README states the delivered shipping policy | README reuse-guide steps | the adoption core-region rule; the `<python>` placeholder policy |

## Design decisions

- Core tables ship by the same byte-for-byte core-region copy as every other core region — the uniform model; the row-merge machinery (upsert by record key, fail-closed collisions, relaxed verification) was considered and rejected as behavior never requested (see Resolved decisions).
- No table declaration exists — reversed on user correction 2026-10-14: the model is uniform core-region copy-paste, a declaration would be a zero-effect field, and the markers are the knowable boundary (an earlier `core_table` machine-declaration decision is superseded in `## Resolved decisions`).
- `debt.md` carries no core table — its records are AICore's own filed history and its core is the frame alone (the retired seed's payload).
- The living design is renamed rather than split into two files — the system name is the artifact's identity; a second file would duplicate the contract.
- "The pilot's three proof surfaces" names the living design's onboarding-promise paragraph (pilot AC5), destination-storage paragraph (pilot AC7), and identification-packs paragraph (the pack-pointer semantics); the AC4 investigate-step surface resolves at the runbook skill surface, which ships separately.
- The stale-name sweep covers every non-temporal surface — the tree minus `plans/`, `output/`, and tool caches, tracked and untracked alike — and runs again after the story entries land; `plans/` is temporal and machine-local by the lifecycle contract, so the active plan folder's step text is never a live reference.
- Fixture tooling verification (the `core_sync` CLI chain against a temporary destination) is a coordinator acceptance check — Cipher 🔓 (Lead Orchestrator) — not an authoring-instance grant and not the reviewed-suite grant; it mutates only the temporary fixture.
- The clearance schema stays version `1` with one optional field — a compatible extension under the definition document's versioning rule.
- Anchored story change-log entries are written only when a real delivery anchor exists (commit SHA, PR number, or ticket) — added after the release identity exists, per the delivery-match rule and the `safe-roster-parallelism-20261013` precedent; an invented anchor is forbidden and a missing anchor blocks archival.

## Documentation

| Surface | Owner | Change |
|---|---|---|
| `README.md` | Forge 🔨 (Implementer) | inventory and reuse-guide shipping policy to the delivered model |
| `distribution-clearance.definition.md` | Forge 🔨 (Implementer) | record shapes, core-table concept, knowledge distribution classes |
| `.opencode/skills/core-sync/SKILL.md` | Forge 🔨 (Implementer) | declaration mention removed — restored to pre-plan content |
| `knowledge/agents.md` | Forge 🔨 (Implementer) | core/project split (rules core, project extensions project) |
| `knowledge/debt.md` | Forge 🔨 (Implementer) | frame-only core; entries in the project region |
| `knowledge/problems.md` | Forge 🔨 (Implementer) | core region containing the register core table |
| `knowledge/symptoms.md` | Forge 🔨 (Implementer) | core region containing the catalog core table |
| `knowledge/diagnostic-system-design.md` | Forge 🔨 (Implementer) | renamed living design with its core/project split |
| `user-stories/core-sync.md` | Cipher 🔓 (Lead Orchestrator) | dated change-log entry for this delivery, with real anchor |
| `user-stories/diagnostic-system.md` | Cipher 🔓 (Lead Orchestrator) | dated change-log entry for this delivery, with real anchor |
| `user-stories/incident-query-verification-pilot.md` | Cipher 🔓 (Lead Orchestrator) | dated entry covering the approved AC5 reword and proof corrections plus the delivery, with real anchor |

## Write/delete manifest

| Action | Path |
|---|---|
| Modify | `knowledge/agents.md` |
| Modify | `knowledge/debt.md` |
| Modify | `knowledge/problems.md` |
| Modify | `knowledge/symptoms.md` |
| Add | `knowledge/diagnostic-system-design.md` |
| Delete | `knowledge/query-verification-design.md` |
| Delete | `knowledge/debt.template.md` |
| Modify | `distribution-clearance.json` |
| Modify | `distribution-clearance.definition.md` |
| Modify | `.opencode/skills/core-sync/SKILL.md` |
| Modify | `.opencode/skills/core-sync/scripts/core_sync_pkg/domain/clearance.py` |
| Modify | `.opencode/skills/core-sync/scripts/core_sync_pkg/domain/test_clearance_metadata.py` |
| Modify | `.opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_agent_versions.py` |
| Modify | `README.md` |
| Modify | `user-stories/core-sync.md` |
| Modify | `user-stories/diagnostic-system.md` |
| Modify | `user-stories/incident-query-verification-pilot.md` |

## Phase index — dispatch table

| # | Phase | Owner | Runbook | Output | Goals |
|---|---|---|---|---|---|
| 1 | Knowledge content split and rename | Forge 🔨 (Implementer) | `phase-01-forge.md` | `knowledge/diagnostic-system-design.md` | G1 |
| 2 | Clearance registry and knowledge classes | Forge 🔨 (Implementer) | `phase-02-forge.md` | `distribution-clearance.json` | G2 |
| 3 | Documentation sweep | Forge 🔨 (Implementer) | `phase-03-forge.md` | `README.md` | G3 |
| 4 | Story record convergence | Cipher 🔓 (Lead Orchestrator) | `phase-04-cipher.md` | `user-stories/incident-query-verification-pilot.md` | G3 |

## Coordination and accepted joins

- Workflow identity / coordinator: `knowledge-distribution-20261014`; Cipher 🔓 (Lead Orchestrator).
- Capacity / authoritative accounting owner: Cipher 🔓 (Lead Orchestrator) — one shared ledger; instances receive no additional allowances.
- Task instances: T1 = Forge 🔨 (Implementer) instance 1 (phase-01, knowledge content); T2 = Forge 🔨 (Implementer) instance 2 (phase-02, registry and parser); T3 = Forge 🔨 (Implementer) instance 3 (phase-03, documentation); T4 = Cipher 🔓 (Lead Orchestrator) (phase-04, story record convergence — coordinator-owned completion work).
- Accepted dependencies / inputs: T1 and T2 accept the approved stories (`core-sync` v1.1.0, `diagnostic-system` v1.0.0, `incident-query-verification-pilot` v1.2.0) and the confirmed plan goals; T3 accepts T1's and T2's accepted returns and the combined candidate; T4 accepts T1–T3 plus the completion evidence matrix.
- Readiness / serialization: T1 and T2 dispatch concurrently — verified disjoint write sets and no shared mutable resource; T3 serializes after the join because it reviews the delivered state; T4 serializes after T3 because it records delivery history for the delivered behaviour and owns the final sweep. Phase numbers are an index, not evidence of independence.
- Resource modes / ownership: T1 writes `knowledge/**` only; T2 writes `distribution-clearance.json`, `distribution-clearance.definition.md`, `.opencode/skills/core-sync/**` only; T3 writes `README.md` only; T4 writes the three `user-stories/**` files only. One active writer per canonical path; shared reads may overlap only while unchanged. Git/worktree/PR state stays coordinator and Herald 📯 (Release Manager) owned; no instance mutates git.
- Output allocation / attribution: each phase's `Output` is exclusive to its instance and attributable to its consumed inputs; the join report and combined-candidate acceptance belong to Cipher 🔓 (Lead Orchestrator).
- Checkpoints / transfers: T2's Python edits carry Bastion 🧱 (Backend & Scripts Architect) `[PASS]` and Crucible 🔥 (Test Architect) `[PASS]` before its return is accepted; every return states task identity, changed paths, content identity, gate evidence, and resource-use state; out-of-assignment needs return `BLOCKED` before any mutation.
- Review stability / joins: reviewed content is held stable through its gates; Cipher 🔓 (Lead Orchestrator) accepts every relevant return and the combined candidate before T3, T4, and completion; incomplete, failed, stale, or still-mutating predecessors never unblock dependents.
- Anchor lifecycle: T4 writes each change-log entry only when its real delivery anchor exists (the delivering commit SHA, PR number, or ticket); the release identity is created by separately authorized release work, and a missing anchor at that time is returned as the exact remaining blocker with the plan retained — no invented anchor, and archival stays blocked until resolved.

## Critical files / tools

- `user-stories/core-sync.md`, `user-stories/diagnostic-system.md`, `user-stories/incident-query-verification-pilot.md` — the approved contracts this plan consumes
- `user-stories/plan-enforce.md` — AC30 (same-change documentation) is the G3 trace; its text: "Actual affected documentation paths, owners, and proving semantic review are in the same plan/manifest as the behavior change. Final guidance, examples, diagrams, and links agree with the delivered contract."
- `knowledge/agents.md`, `knowledge/debt.md`, `knowledge/problems.md`, `knowledge/symptoms.md`, `knowledge/diagnostic-system-design.md`
- `distribution-clearance.json`, `distribution-clearance.definition.md`
- `.opencode/skills/core-sync/scripts/core_sync_pkg/domain/clearance.py`, `.opencode/skills/core-sync/scripts/core_sync_pkg/domain/test_clearance_metadata.py`
- `README.md`; reviewed whole-suite command `uv run --frozen --group dev pytest -q`

## Verification

- ⬜ G1: `awk '/core:begin/,/core:end/' knowledge/diagnostic-system-design.md \| grep -cE 'Ticket-enabled destinations receive\|Destination chooses storage\|Identification packs\|^## Purpose$'` → `4`, and `test ! -e knowledge/debt.template.md && test ! -e knowledge/query-verification-design.md` → exit 0
- ⬜ G2: `uv run --frozen --group dev pytest -q` → exit 0 (suite green including the agent-version pin fix), and the fixture chain (enrollment, documented pending-clear, verification) reports the five knowledge rows current
- ⬜ G3: `! grep -rnI -e 'query-verification-design' -e 'debt\.template' --exclude-dir=plans --exclude-dir=output --exclude-dir=.git --exclude-dir=.venv --exclude-dir=__pycache__ .` → no matches on any non-temporal surface (failure prints file:line), re-verified after the story entries land
- ⬜ G3: `grep -c 'knowledge-distribution-20261014' user-stories/core-sync.md user-stories/diagnostic-system.md user-stories/incident-query-verification-pilot.md` → one anchored entry per file, or the recorded anchor blocker

## Phase verify commands

- Python `test_*.py` edits in reviewed discovery areas: the project's approved whole-suite command is `uv run --frozen --group dev pytest -q`, assigned to Crucible 🔥 (Test Architect) as executor, with Bastion 🧱 (Backend & Scripts Architect) `[PASS]` required and Crucible 🔥 (Test Architect) `[PASS]` or `[FAIL]` returned.
- Fixture tooling verification — the `core_sync` CLI chain against a temporary destination — is a coordinator acceptance check run by Cipher 🔓 (Lead Orchestrator): it is neither an authoring-instance grant nor the reviewed-suite grant, and it mutates only the temporary fixture directory.
- Command cells are markdown-escaped: a `\|` inside a command cell is the pipe character — executors run the rendered form.

## Audit

- Auditor: Sentinel 🛡️ (Quality Guardian)
- Verdict: [FAIL]
- Findings: completion audits C2 `[FAIL]`/1 and C1 `[FAIL]`/1 — the identical single residual: the three anchor-gated change-log entries (`## Pending`; G3's checkmark, `## Outcome`, and archival hold until the release identity exists — no remediation of delivered work required, delivered matrix verified twice). Planning history: round 10 `[PASS]`/none · round 9 `[FAIL]`/3 (fixed) · round 8 `[PASS]` · round 7 `[FAIL]`/2 (fixed) · round 6 `[PASS]` · round 5 `[FAIL]`/2 (fixed) · round 4 `[PASS]` · round 3 `[PASS]`/2 advisories (applied) · round 2 `[FAIL]`/5 · round 1 `[FAIL]`/7 — all adjudicated without downgrade.
- Date: 2026-10-14
- Date: 2026-10-14

## Out of scope / Do-not-touch

- No sync behavior change beyond the clearance file-record field acceptance: no merge machinery, no row-key semantics, no exit-code changes, no marker-spelling changes.
- `plans/` history and the active plan folder are never edited by phases and are excluded from the stale-name sweep as temporal; historical references under `plans/.completed/` remain by design.
- `register-first-incident-identification` and `AGENTS.md` criterion and section text is untouched; cited headings survive verbatim.
- No git commit, branch, push, or PR is created by these phases; release work is separately authorized and supplies the delivery anchors.

## Pending

- [waiting for] release identity (delivering commit SHA or PR number) for the three anchored story change-log entries — written by phase-04 only when real; a missing anchor blocks archival.

## Resolved decisions

- 2026-10-14 — uniform core-region copy for core tables; the row-merge machinery (upsert by record key, fail-closed collisions, relaxed verification) is rejected as behavior never requested; goals were revised under drift-watch with user approval.
- 2026-10-14 — `core_table` is a machine declaration in the clearance file (user choice); `debt.md` carries no core table because its records belong to AICore alone.
- 2026-10-14 — `core-sync` corrected to v1.1.0 (uniform core-table semantics) before planning; this plan consumes `core-sync`, `diagnostic-system`, and `incident-query-verification-pilot`.
- 2026-10-14 — planning audit round 1 `[FAIL]` (7 findings) adjudicated without downgrade: G2's fixture clause operationalized, the stale-name sweep widened, the pilot's change-log bound given a drop-oldest/rollup action, the pilot entry made to name the approved revision, the anchor lifecycle made explicit after the `safe-roster-parallelism-20261013` precedent, `plan-enforce` AC30's text supplied, and AC19 added to G2's trace.
- 2026-10-14 — planning audit round 2 `[FAIL]` (5 findings) triggered the coherent reassessment required after two failed audits, not cosmetic edits: the fixture-verification premise was reworked against the real enrollment lifecycle (pending plus destination-root blocker, then the operator's documented pending-clear, then verification), the sweep premise was reworked to cover untracked deliverables over every non-temporal surface with a post-entry re-run, the bound-check command was scoped to the change-log section, phase footprint declarations were corrected to T3/T4, and the fixture executor class was recorded; goals, discovery evidence, and phase cuts were re-examined and stand unchanged.
- 2026-10-14 — planning audit round 3 `[PASS]` with two non-blocking advisories (markdown-escaped command cells could pass vacuously if run source-literal; `-q` suppressed failure evidence); both applied — sweep rows are pipe-free with file:line failure evidence and the cell-escape convention is stated — and round 4 confirmed the deltas with no regressions.
- 2026-10-14 — user-approved scope expansion under drift-watch: the pre-existing `test_agent_versions.py` pin drift (PR #62 delivered `inquisitor.md` at `1.5.0` against a `1.4.2` pin, red at baseline) joins this plan as one manifest row under G2 so the whole-suite gate exits 0 as confirmed; goal text unchanged; the plan's unverified baseline-green evidence cell is corrected to the executed `1 failed, 564 passed` output.
- 2026-10-14 — heading blocker resolutions (coordinator, evidence-based): the living-design carve produces `## Purpose` in core and `## Status` in project per the approved layout; the `diagnostic-system` AC4 proof citation is corrected to the real heading `### Bounded-query discipline (SELECT-in-WHERE)` — proof-only under the checklist Authority rule (the cited `### Query safeguards` name was invented; grep proves only that proof line carries it) — with no contract text changes.
- 2026-10-14 — fixture-verify row proven and amended after four diagnosed setup gaps against documented clauses (merge destinations must pre-exist per `core-sync` AC12; raw targets require an existing parent per AC3, and a missing parent fails before any write per AC6 — including nested skill-root directories; `init` fails before writes so the fixture stayed clean): the row now derives its complete setup from the clearance file and self-cleans the fixture directory inside its own footprint, and the chain ran green — `initialized`, `current`, exit 0 — with the registry grep reporting five knowledge rows.
- 2026-10-14 — user corrections after delivery review (drift-watch; G2 revised and reopened): the `### Knowledge registers` block moves from the project region into the core region — it describes the shipped registers and its adaptation instruction addresses destinations, which a project region never reaches — and the `core_table` declaration is removed everywhere (registry attributes, parser field and cases, skill prose, definition field docs): the model is uniform core-region copy-paste and the flag was a zero-effect field. Approved wordings, verbatim: the block becomes "The symptom-class catalog is `knowledge/symptoms.md` and the known-problem register is `knowledge/problems.md`. A project that does not enable the incident domain replaces these with its own registers in its project extension."; `core-sync` AC19 becomes "**Core table:** A cleared markdown source's tables live in its core region and ship with it byte-for-byte like the rest of the core; records the source keeps are project-region content and never ship." and AC20's "declare their distribution class" becomes "carry a documented distribution class".
