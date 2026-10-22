# Phase 2 — Regular-file write targets

> **Owner:** Forge 🔨 (Implementer)
> **Pre:** phase 1 accepted (project-contained temp root active); plan audit `[PASS]`; user execution authorization for this turn.
> **Reads:** `core_sync_pkg/infrastructure/filesystem.py`; `core_sync_pkg/infrastructure/composition.py`; `core_sync_pkg/domain/ports.py`; `core_sync_pkg/domain/bindings.py`; `core_sync_pkg/infrastructure/stores.py`; the core-sync test modules and application test fakes; `_core_sync_testkit.py`; `query-verification/scripts/{test_query_verification_paths.py,query_verification.py}`; approved stories `core-sync` AC25/AC8 and `python-pytest` AC8.
> **Writes:** `.opencode/skills/core-sync/scripts/core_sync_pkg/infrastructure/filesystem.py`; `.opencode/skills/core-sync/scripts/core_sync_pkg/infrastructure/composition.py`; `.opencode/skills/core-sync/scripts/core_sync_pkg/infrastructure/test_preflight_write_targets.py`; `.opencode/skills/core-sync/scripts/core_sync_pkg/application/test_enroll_destinations.py`; `.opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_source_write_protection.py`; `.opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_destination_write_boundaries.py`; `.opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_root_raw_alias.py`; `.opencode/skills/core-sync/scripts/_core_sync_testkit.py`; `.opencode/skills/query-verification/scripts/test_query_verification_paths.py`

## Assignment and resources

- Workflow / task / instance: `write-safety-test-containment-20261022` / `p2-write-targets` / `p2-forge`.
- Accepted predecessors / input identities: phase 1 accepted (containment test green); approved `core-sync` 1.6.0 with AC25; held working-tree bytes for the manifest paths.
- Permitted resource access: write only the nine declared paths; read the port and application callers; no test execution (Crucible 🔥 (Test Architect) executes).
- Ownership / output destination: Forge 🔨 (Implementer) is the only writer of these paths; no other phase writes them.
- Required gates / continuation / join owner: Bastion 🧱 (Backend & Scripts Architect) `[PASS]`, then Crucible 🔥 (Test Architect) `[PASS]`; Cipher 🔓 (Lead Orchestrator) accepts and releases phase 3.
- Capacity allocation / accounting owner: one implementer slot from the coordinator ledger.
- Readiness / serialization evidence: depends on phase 1 for the suite execution environment; no shared mutable resource with phases 1, 3, or 4.

## Steps

1. In `composition.py`, for `apply` and `init`, reject a bindings path that is a symbolic link with `EXIT_INVALID` before `YamlBindingsStore.load` reads it. `check` is unchanged because it does not write the bindings file.
2. In `preflight_write_targets`, reject a write target that is a symbolic link before resolving or writing it, and reject an existing target that is not a regular file (for example a directory). Keep the concise target-kind diagnostic, the exit-2 mapping, and the resolved-path containment for ancestors.
3. Replace the cached directory-entry stat in `_source_regular_file_inodes` with `os.stat(entry.path, follow_symlinks=True)`. Ignore identities whose inode is zero in the source set, the `visited_directories` cycle set, the single-file early return, the target inode map, and the root/non-region destination comparison (`filesystem.py:294-313`) so a filesystem without file IDs neither collapses the walk nor rejects ordinary files nor reports a false alias.
4. Remove the `link_symlink` helper from `_core_sync_testkit.py` and all uses; remove the now-unused `pytest` import. The four real-link cases in `test_source_write_protection.py` (bindings, payload, root, report) have these dispositions: bindings order → the step-6 composition case; payload/root/report → the adapter's four-kind stubbed case. Add `infrastructure/test_preflight_write_targets.py` covering against the real filesystem: a payload target escaping by `..`, a root target escaping by `..`, a payload target resolving inside the source tree, a root target resolving inside the source tree (asserting the source-containment diagnostic, not only exit 2), two canonical destinations resolving to one target, a directory as an existing non-regular target, and two ordinary targets plus a root/non-region pair on a zero-identity destination (stubbed stat). Parameterise the stubbed-predicate symlink case over the root, payload, bindings, and report target kinds.
5. Implement the approved AC25 Proof surface in `application/test_enroll_destinations.py`: the fake port returns a symlinked-target preflight error, `init` returns `CODE_INVALID`, and the fake records no write calls.
6. Add the bindings-guard order case to `tests/test_source_write_protection.py`: stub `Path.is_symlink` to return true only for the bindings path, spy on `YamlBindingsStore.load`, and assert the command exits 2 without calling it.
7. Delete `tests/test_destination_write_boundaries.py`; its escape and duplicate cases now live in the adapter test. Record the per-kind dispositions: bindings order = the composition case; bindings containment = `test_rejects_bindings_file_under_source_before_writing`; payload/root containment = the adapter source-containment pair; report rejection = the stubbed `report` kind. Report order coverage is retired with the link: `reconciliation_report_path` derives from the bindings parent, so a bindings path inside the source fails first and the report cannot be independently inside the source.
8. Replace the root/raw alias case with identical canonical root and raw-destination paths, and drop the now-invalid `is_symlink()` and resolve assertions from that case. Unskip the hard-link test on Windows and add a nested-source hard-link case (a destination payload hard-linked to a source file under a subdirectory). Keep the `newline="\n"` fixture write and refresh the stale docstring at `tests/test_source_write_protection.py:1` that still says "symlink writes".
9. Replace the `query-verification` link fixture with a targeted `Path.resolve` stub for the source path only, asserting the source-specific "path resolves outside the query root" rejection; rename the test to `test_rejects_resolved_source_escape` and remove the unused `os` and `pytest` imports.

## Output

- **Artifact:** the nine declared paths.
- **Schema / shape:** composition rejects a symlinked bindings path before the store read; preflight rejects symlinked and existing non-regular targets; inode identity uses `os.stat(entry.path)` with a zero guard on every comparison; the adapter test proves escape, source containment, duplicate, zero-identity, non-regular, and all four stubbed symlink target kinds; the application test proves `CODE_INVALID` with no writes; the composition case proves load is never called; the query-verification source-escape case still rejects; no test creates a symbolic link.
- **Attribution / identities:** instance `p2-forge`; consumed `filesystem.py`, `composition.py`, `stores.py`, test modules at the current tree; produced identities recorded on return.
- **Parent handoff:** changed paths, content identities, Bastion 🧱 (Backend & Scripts Architect) and Crucible 🔥 (Test Architect) verdicts, and current resource-use state.

## Verify commands

| Executor | Command |
|---|---|
| Crucible 🔥 (Test Architect) | `uv run --frozen --group dev pytest -q` |
| Cipher 🔓 (Lead Orchestrator) | `uv run --frozen python3 -B -c "import pathlib,sys; tokens=['symlink_to','os.symlink','link_symlink','mklink','ln -s','SymbolicLink']; roots=[pathlib.Path('.opencode/skills'), pathlib.Path('tests')]; hits=[str(p) for r in roots for p in r.rglob('*.py') if any(t in p.read_text(encoding='utf-8') for t in tokens)]; print(hits); sys.exit(1 if hits else 0)"` |

- Python `test_*.py` edits: Bastion 🧱 (Backend & Scripts Architect) `[PASS]` and Crucible 🔥 (Test Architect) `[PASS]` are required; `[UNCERTAIN]` is not acceptable.
- The reviewer confirms the hard-link test was collected and executed, not skipped, and that the scan exits 0 with no hits.

## Gate

- ⬜ A symlinked bindings path is rejected before `YamlBindingsStore.load` for `apply`/`init`; the composition case observes zero load calls.
- ⬜ A symlinked or existing non-regular payload/root/report target is rejected before writing; the four stubbed target kinds are covered and the shared non-regular branch is proven once with a directory target.
- ⬜ Payload and root targets resolving inside the source tree produce the source-containment diagnostic.
- ⬜ The application fake-port case returns `CODE_INVALID` and records no writes.
- ⬜ A hard link to a source file exits 2 on the executed platform (Windows/NTFS), including a nested source file; POSIX execution is recorded as pending in the phase return, not claimed.
- ⬜ A zero-identity destination produces neither a false inode collision nor a false root/raw alias.
- ⬜ The scan command exits 0 with no hits.
- ⬜ The query-verification source-escape case still rejects through the targeted resolve stub.
- ⬜ Legacy/dead-code sweep recorded: removed helper, unused imports, stale docstring.
- ⬜ Crucible 🔥 (Test Architect) ran the reviewed whole-suite command with exit 0; Bastion 🧱 (Backend & Scripts Architect) `[PASS]`; Crucible 🔥 (Test Architect) test-architecture `[PASS]`.
- ⬜ Reviewed content stayed stable; identities and scope recorded; parent accepted the return.

## Abort conditions

- Halt if the bindings-path guard changes `check` behaviour or any exit code.
- Halt if the zero-identity guard rejects ordinary destination files on any filesystem.
- Halt if the non-regular-target rejection blocks a legitimate region, raw, or merge write.
- Halt if any symlink-creation fixture or symlink-creating invocation remains.
- Halt if the hard-link test cannot run on Windows after the fix; report the literal failure instead of re-skipping.
- Stop before any out-of-assignment write or incompatible access; report `BLOCKED` to the parent.
