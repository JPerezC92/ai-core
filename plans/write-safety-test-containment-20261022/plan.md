# Plan — Regular-file write targets and contained test temp roots

> **Status:** active
> **Started:** 2026-10-22 01:18
> **Subject:** Make every sync write target a regular file, fix Windows hard-link detection, and keep test temp roots inside the project.
> **Layout:** subfolder pattern

## Context

- Prompted by: the held Windows/op-model fixes in the working tree and the user's rule that the suite must create no symbolic links and must write nothing outside the project.
- Goal: a destination can never mutate the core source through an alias, and no test creates a symlink or a host-temp artifact.
- Outcome: `core-sync` rejects symlinked and hard-linked write targets before any read or write on the executed platform; pytest temp roots live under the project; the held `op-model` change is verified without further writes.

## Goals

- ⬜ **G1:** No sync write target that is an alias for another file is accepted. *(trace: `core-sync` AC25, AC8)*
  - Issue: on Windows the source inode collection collapses to `(0,0)` and the tree walk stops after one level, so a destination hard link is accepted and a write through it overwrites the source; a symlinked target is also accepted today when it stays inside the destination.
  - How: reject any symlinked write target before the bindings file is read or written, reject existing non-regular targets, fix the source inode collection to use real file identities with a zero guard, and replace symlink-creation fixtures with non-link adapter/application cases plus a hard-link integration test.
  - Files: `.opencode/skills/core-sync/scripts/core_sync_pkg/infrastructure/filesystem.py`; `.opencode/skills/core-sync/scripts/core_sync_pkg/infrastructure/composition.py`; `.opencode/skills/core-sync/scripts/core_sync_pkg/infrastructure/test_preflight_write_targets.py`; `.opencode/skills/core-sync/scripts/core_sync_pkg/application/test_enroll_destinations.py`; `.opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_source_write_protection.py`; `.opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_destination_write_boundaries.py` (delete); `.opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_root_raw_alias.py`; `.opencode/skills/core-sync/scripts/_core_sync_testkit.py`; `.opencode/skills/query-verification/scripts/test_query_verification_paths.py`
  - Done when: a symlinked bindings or payload target is rejected before any read or write; a destination hard link to a source file exits 2 on the executed platform (Windows/NTFS), with POSIX execution recorded as pending rather than claimed; no test creates a symbolic link; files under nested source directories appear in the source inode set.
- ⬜ **G2:** Test temp roots are contained inside the project. *(trace: `python-pytest` AC8)*
  - Issue: pytest's default base temp directory is `%TEMP%\pytest-of-<user>` on this host (3 retained sessions, 1.6 MB measured), outside the project.
  - How: a root `conftest.py` sets a per-process base temp directory under `output/.pytest-tmp/` when `--basetemp` is not supplied, and a regression test asserts containment.
  - Files: `conftest.py`; `tests/test_pytest_temp_root.py`
  - Done when: under `-n auto` every `tmp_path` resolves inside the project root and no new host-temp session is created.
- ⬜ **G3:** The held `op-model` change keeps `opencode` resolution explicit on Windows. *(trace: `op-model-configuration` AC2 preserved; the held change is an accepted input, not new work)*
  - Issue: the working tree already contains the `shutil.which` resolution and the Windows `.cmd` shim; there is no remaining code delta to plan.
  - How: verify the held bytes in the suite; do not modify them.
  - Files: none (verification only)
  - Done when: the suite runs with the held change and the op-model e2e passes on Windows.

## Current state

| Area | Current file / behavior | Evidence (file + line / command output) |
|---|---|---|
| Source inode collection | Uses cached `DirEntry.stat(follow_symlinks=True)` | `core_sync_pkg/infrastructure/filesystem.py:144`; Windows probe: cached `(0,0)`, real `(12868036653430795755, 562949954269442)` |
| Source tree walk | Nested directories share `(0,0)` and are treated as already visited | Probe: `a` visited, `b` `already_visited=True`; only one level descended |
| Write-target preflight | Runs after the bindings file is read; no explicit symlink or non-regular rejection | `filesystem.py:159-343`; `enroll_destinations.py:81→162`; probe: hard link accepted (`preflight init -> None`) and a write through it produced `DESTINATION WRITE` in the source file |
| Hard-link test | Skipped on Windows | `tests/test_source_write_protection.py:218-221` |
| Symlink fixtures | 17 core-sync cases plus one query-verification case create links (measured) | `_core_sync_testkit.py:310-317`; `test_destination_write_boundaries.py:45-140`; `test_root_raw_alias.py:47-93`; `query-verification/scripts/test_query_verification_paths.py:87-97`; run output: `SKIPPED [17] ... _core_sync_testkit.py:316` |
| Pytest temp root | Defaults to host temp | `pyproject.toml` `[tool.pytest.ini_options]` has no basetemp; measured `%TEMP%\pytest-of-dexm7`: 3 sessions, 1.6 MB |
| Root conftest | Absent; only the op-model e2e conftest exists | directory listing |
| `op-model` lookup | Held change already resolves with `shutil.which` and installs the Windows `.cmd` shim | `infrastructure/process.py:24-40`; `e2e/conftest.py:49-66`; measured `.CMD` returned and executed |
| Implementation authority | Forge 🔨 (Implementer) writes Python only under plan-manifested `.opencode/skills/*/scripts/` paths; root config and docs are outside that scope | `.opencode/agents/forge.md:18,44-49` |

## Behavior change

| Goal | Before | After | Interface contracts | Do-not-break |
|---|---|---|---|---|
| G1 | Symlinked payload accepted inside destination; symlinked bindings read before any check; hard link accepted on Windows; non-regular targets reach the write | Symlinked bindings/payload/root/report rejected before read or write; existing non-regular targets rejected; hard link to source rejected | `preflight_write_targets` returns an error string or `None`; composition returns exit 2 for a symlinked bindings path | Region/raw/merge writes, exit codes 0/1/2, source read-only |
| G2 | `tmp_path` under host temp | `tmp_path` under `output/.pytest-tmp/<process>` | pytest `tmp_path` fixture path; `--basetemp` still wins when supplied | Suite discovery, `-n auto`, no collection of temp files |
| G3 | Held change present in the working tree | Verified unchanged | `OpencodeModelSource.fetch` result and error text unchanged | No edit to the held bytes |

## Design decisions

- Add `core-sync` AC25 instead of rewriting AC8 — preserves AC8's established rejection classes and their mark.
- Reject a symlinked bindings path in composition before `load_bindings` — AC25 promises "before any read or write", and the bindings file is read before the existing preflight (simplest alternative: weaken AC25 to "before any payload read or write"; rejected because it weakens the approved wording).
- Blanket symlink rejection rather than escape-only — makes the support boundary explicit and testable without creating a link.
- Replace link fixtures with adapter-level escape/duplicate/zero-identity cases, an application fake-port case, and a stubbed-predicate case parameterised over all four target kinds; keep a real hard link — keeps real-filesystem coverage and removes the platform privilege dependency.
- Skip zero identities on **both** source and target sides — a no-file-ID destination would otherwise report every pair as sharing an inode.
- `query-verification` keeps its source-escape coverage by stubbing `Path.resolve` to return outside the query root; the link fixture is removed without dropping the branch test.
- Containment phase first — every later suite run is contained under the user's rule.
- Temp root under `output/.pytest-tmp/` — already gitignored and excluded from collection.
- Per-process basetemp — a shared `--basetemp` is deleted at session start by each xdist worker.
- Keep the held `newline="\n"` fixture write and the held `op-model` bytes — they are accepted inputs.
- Phase ownership is assigned explicitly by this plan; where no role owns a surface, the assignment and its review are recorded here. Root configuration and the root containment test are coordinator-owned because Forge 🔨 (Implementer) is scoped to plan-manifested `.opencode/skills/*/scripts/` Python paths; skill prose is written by Scribe ✍️ (Docs & Problems Manager) and reviewed by Vault 🔐 (Catalog Steward).
- Reassessment after two `[FAIL]` planning audits: story marks/Proof/history are reconciled at completion (lifecycle), not as phase writes; the CLI boundary module is deleted with its cases moved rather than retained; the op-model goal is verification-only.

## Documentation

| Surface | Owner | Change |
|---|---|---|
| `.opencode/skills/core-sync/SKILL.md` | Scribe ✍️ (Docs & Problems Manager) | State that write targets must be regular files, that a symlinked bindings or payload target is rejected, and how to correct the mapping |

## Completion reconciliation

- Owner: Cipher 🔓 (Lead Orchestrator), after accepted phase evidence and a delivery-matching reference.
- Paths: `user-stories/core-sync.md` (AC8 Proof repoint to the surviving adapter test; AC25 Proof extended to `PreflightWriteTargetsTests`, the composition guard case in `test_source_write_protection.py`, and the application case, naming `## What I do` and the `## Troubleshooting` "Unsafe or aliased write target" row as the SKILL surfaces; AC25 mark; Revision tracking), `user-stories/python-pytest.md` (AC8 mark and Proof; all three AC8 clauses — one concern per module/class, undiscovered helper modules, and containment — are re-read on the post-fix snapshot before `✅`), `user-stories/index.md` (mirror check only; already updated as an accepted input).
- Change log: add one dated delivery entry per touched story. For `core-sync`, roll **both** existing `2026-10-16` entries into the `before 2026-10-17 — earlier history` rollup and retain the `2026-10-17`, `2026-10-18`, `2026-10-20`, and new delivery entries; all four short SHAs in that history are unresolvable in this clone, so repoint the retained `2026-10-17` and `2026-10-18` anchors to their verified delivery PR references and keep PR #72 as the `2026-10-20` anchor. For `python-pytest`, roll its oldest entry and set the rollup to `before 2026-10-07 — earlier history: see git history for this file`.
- `python-pytest` Revision tracking is finalized in the same pass (pending history resolved), and AC8's Proof names `tests/test_pytest_temp_root.py` as the containment proving surface. Correct the stale `### Test Execution` / `### Test Organization by Concern` references to `####` / `#####` in the same story revision.
- AC8 is **re-established on the post-fix snapshot** before its mark is retained: the unskipped Windows hard-link and nested-source cases plus the surviving adapter cases must pass; if they do not, reset AC8 to `⬜` instead of repointing it.
- Gate: no mark, Outcome, or archive before the matching delivery reference exists. These are lifecycle writes, not phase writes.

## Write/delete manifest

| Action | Path |
|---|---|
| Add | `conftest.py` |
| Add | `tests/test_pytest_temp_root.py` |
| Add | `.opencode/skills/core-sync/scripts/core_sync_pkg/infrastructure/test_preflight_write_targets.py` |
| Modify | `.opencode/skills/core-sync/scripts/core_sync_pkg/infrastructure/filesystem.py` |
| Modify | `.opencode/skills/core-sync/scripts/core_sync_pkg/infrastructure/composition.py` |
| Modify | `.opencode/skills/core-sync/scripts/core_sync_pkg/application/test_enroll_destinations.py` |
| Modify | `.opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_source_write_protection.py` |
| Delete | `.opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_destination_write_boundaries.py` |
| Modify | `.opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_root_raw_alias.py` |
| Modify | `.opencode/skills/core-sync/scripts/_core_sync_testkit.py` |
| Modify | `.opencode/skills/query-verification/scripts/test_query_verification_paths.py` |
| Modify | `.opencode/skills/core-sync/SKILL.md` |

## Phase index — dispatch table

| # | Phase | Owner | Runbook | Output | Goals |
|---|---|---|---|---|---|
| 1 | Contain test temp roots | Cipher 🔓 (Lead Orchestrator) | `phase-01-cipher.md` | `conftest.py`, `tests/test_pytest_temp_root.py` | G2 |
| 2 | Regular-file write targets | Forge 🔨 (Implementer) | `phase-02-forge.md` | core-sync guard, tests, and query-verification test | G1 |
| 3 | Write-target documentation | Scribe ✍️ (Docs & Problems Manager) | `phase-03-scribe.md` | `core-sync/SKILL.md` | G1 |
| 4 | Verify held op-model change | Crucible 🔥 (Test Architect) | `phase-04-crucible.md` | verification record in the phase return | G3 |

## Coordination and accepted joins

- Workflow identity / coordinator: `write-safety-test-containment-20261022`; Cipher 🔓 (Lead Orchestrator).
- Capacity / authoritative accounting owner: one writer slot at a time; Cipher 🔓 (Lead Orchestrator) keeps the single ledger.
- Task instances: `p1-cipher` (root config + test), `p2-forge` (core-sync guard + tests), `p3-scribe` (SKILL prose), `p4-crucible` (verification only).
- Accepted dependencies / inputs: p1 → none; p2 → accepted p1; p3 → accepted p2; p4 → accepted p2 and p3. Inputs are the approved stories and the held working-tree bytes.
- Readiness / serialization: sequential because p2's and p4's suite runs consume p1's containment, and one writer owns the code paths per phase; p3 has no suite run.
- Resource modes / ownership: each phase's Writes are disjoint; Bastion 🧱 (Backend & Scripts Architect) and Crucible 🔥 (Test Architect) review; Scribe ✍️ (Docs & Problems Manager) writes prose; Vault 🔐 (Catalog Steward) reviews skill prose; Cipher 🔓 (Lead Orchestrator) owns the validator and plan files.
- Output allocation / attribution: returns are attributed to their task instance and consumed input identities.
- Checkpoints / transfers: each phase returns `AWAITING_REVIEW`; Cipher 🔓 (Lead Orchestrator) obtains the applicable owner verdict and explicitly redispatches continuation.
- Review stability / joins: reviewed content is held stable at each phase return; a relevant change invalidates the affected verdict; Cipher 🔓 (Lead Orchestrator) accepts the combined candidate before completion.

## Critical files / tools

- `core_sync_pkg/infrastructure/filesystem.py`, `infrastructure/composition.py`, `domain/ports.py`, `domain/bindings.py`, `application/{apply_core_revision,enroll_destinations,verify_destinations}.py`
- `query-verification/scripts/{test_query_verification_paths.py,query_verification.py}`
- `pyproject.toml` `[tool.pytest.ini_options]`; `uv run --frozen --group dev pytest -q`
- `opencode.jsonc` `Crucible 🔥 (Test Architect)` grant
- Accepted inputs: held `op-model` bytes (`process.py`, `test_process.py`, `e2e/conftest.py`); revised stories `core-sync` (AC25, AC8) and `python-pytest` (AC8); mirrored `user-stories/index.md`

## Verification

- ⬜ G2 (phase 1): `uv run --frozen --group dev pytest -q` → exit 0 and `tests/test_pytest_temp_root.py` passes; the host temp parent's session-directory name set is unchanged.
- ⬜ G1 (phase 2): `uv run --frozen --group dev pytest -q` → exit 0, Bastion 🧱 (Backend & Scripts Architect) `[PASS]`, Crucible 🔥 (Test Architect) `[PASS]`; the hard-link test runs on Windows; the application fake-port case returns `CODE_INVALID` with no writes; a CLI case with a stubbed bindings symlink proves `YamlBindingsStore.load` is never called; the adapter cases prove all four stubbed symlink target kinds, the non-regular rejection, and payload/root source-containment diagnostics; the escaped-source query-verification case still rejects; the scan command recorded in `phase-02-forge.md` exits 0 with no hits for `symlink_to`, `os.symlink`, `link_symlink`, `mklink`, `ln -s`, or `SymbolicLink` under `.opencode/skills` and root `tests`.
- ⬜ G1 (phase 3): the structural check exits 0 asserting the two literals `write targets must be regular files` and `replace a link with a regular file`; Vault 🔐 (Catalog Steward) `[PASS]`.
- ⬜ G3 (phase 4): `uv run --frozen --group dev pytest -q` → exit 0 and the op-model e2e passes on Windows with the held `.cmd` shim; the held bytes are unchanged.

## Audit

- Auditor: Sentinel 🛡️ (Quality Guardian), instance `sentinel-plan-audit-7`
- Verdict: [PASS]
- Findings: 0 blocking; 9 advisories (clarifications only — class naming, wording, sampling instants — applied during execution inside the existing steps; no scope change).
- Date: 2026-10-22 02:24
- Reviewed snapshot: HEAD `6e79530` + working tree; 4 plan files, both stories, index; validator `ok plan … phases: 4`; manifest 12 = Σ phase `Writes` 12.
- History: round 1 `[FAIL]` 12; round 2 `[FAIL]` 9; round 3 `[FAIL]` 7; round 4 `[FAIL]` 3; round 5 `[FAIL]` 6; round 6 `[FAIL]` 2; round 7 `[PASS]` 0 blocking.

## Out of scope / Do-not-touch

- `knowledge/debt.md` (pre-existing operator edit), the active foundation plan, `plans/.completed/`.
- `distribution-clearance.json`, `distribution-clearance.definition.md`, `opencode.jsonc`, `pyproject.toml`, `.gitignore` — no change is required.
- New edits to the held `op-model` bytes; they are verified, not re-planned.
- Symlink creation anywhere in the repository, including tests.
- A Linux execution claim: only Windows can be executed here; the POSIX result stays pending and CI-owned.
- Incident ticket data/records/register mutation. The query-verification *test fixture* is the one incident-skill exception and is declared in the manifest.

## Pending

- POSIX execution of the hard-link case: not claimed; the same `os.stat` identity path is used and the result is CI-owned.
- Delivery-matching reference for the story history and mark reconciliation.

## Resolved decisions

- 2026-10-22 — Blanket symlink rejection chosen over escape-only resolution (user decision).
- 2026-10-22 — No test creates a symbolic link, suite-wide (user decision); the query-verification fixture is converted, not deleted (user confirmed the file is in scope).
- 2026-10-22 — `core-sync` AC25 added instead of rewriting AC8 (user approved).
- 2026-10-22 — Stash gate: `refs/stash` absent, zero entries; no collision possible (Herald 📯 (Release Manager) inventory).
- 2026-10-22 — Reassessment after two failed planning audits: root config is coordinator-owned; skill prose is owned by Scribe ✍️ (Docs & Problems Manager); the op-model goal becomes verification-only; story marks/Proof/history move to completion reconciliation; the CLI boundary module is deleted with its cases moved; the bindings-path guard is added in composition.
