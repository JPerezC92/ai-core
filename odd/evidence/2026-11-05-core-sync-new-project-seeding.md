# Evidence file — core-sync new-project seeding

> **Record:** [odd/tasks/2026-11-05-core-sync-new-project-seeding.md](../tasks/2026-11-05-core-sync-new-project-seeding.md) — the sole authoritative intent, task and status record for this feature.
> **Owner:** Cipher 🔓 (Lead Orchestrator) — author of this extraction
> **Created:** 2026-11-06

## What this file is for

Hold the attestational evidence behind one feature record's `## Log`: obligation accounting, reviewer verdicts and identities, original/candidate identities, literal commands with observed results, and the preservation mapping for anything moved out of the record. Each `E#` section is referenced from a record entry as `E#`.

## What this file is not

Disposable working evidence. It is not a feature record, task tracker, status register, intent authority, approval, adoption proof or delivery evidence. A verdict, hash or observed result recorded here establishes only what its own entry states; anatomy validation, a green check or a copied reviewer verdict never certifies the feature.

## E1 — obligation accounting

Instruction surface changed: `.opencode/skills/core-sync/SKILL.md`. Original input: the file at commit `e750816` (before this feature's documentation edit). Candidate input: the same path at `b2667d0`. The change follows the delivered behaviour, in which a merge destination absent at `--bind-cleared` discovery is created by merging the source into an empty object, while `apply`, `check`, a stored binding and a later `init` still refuse.

| Original obligation | Disposition |
|---|---|
| "a merge target is never created" (commands section, merge bullet, exit contract, troubleshooting, examples) | **Translated**, not retired: creation is now permitted on first enrollment only. The prohibition survives as the four negative cases named at `SKILL.md:79` — `check`, `apply`, a stored binding, a later `init`. |
| "existing merge targets" precondition on enrollment | **Retired**, because the condition it guarded is now a supported case. Authority: S1 and the verified end-to-end seed. |
| "…which no sync creates" in the examples' merge sentence | **Retired** with the same authority; the created-file rule replaces it. |
| Canonical `.aicore/core.yaml` bindings path sentence | **Relocated/compacted**, still present at `:52`, `:65`, `:69-71`, `:178`. No obligation lost. |
| Region-write LF-normalization clause | **Relocated** to `:13`; the behaviour is unchanged. |
| `apply`-then-`check` recurrence sentence | **Relocated** to `:69-70`; unchanged. |
| Merge-versus-create boundary | **Added** at `:59`, `:61`, `:79`, `:157-158`, `:161` and the troubleshooting entry, so one rule per write path is stated where a reader will look. |
| "verify retrieval works" and the merge-drift guidance | **Retained** unchanged. |

Version rationale: `metadata.version` advanced 2.7.0 → 2.8.0 because a command that previously failed now creates files and a documented prohibition became a bounded rule — a backward-compatible capability addition, so a minor bump rather than a major one.

## E3 — reviewer verdicts and identities

**Bastion 🧱 (Backend & Scripts Architect)** — architecture gate, snapshot `e750816` plus the reviewed uncommitted tree. Verdict `[ADVISORY]`, one finding:

> A1 — `odd/tasks/2026-11-05-core-sync-new-project-seeding.md:15` (S1) vs `application/verify_destinations.py:240-243` — S1 requires a following `check` to print `current`. It cannot: `init` appends every created region target to `pending` (`enroll_destinations.py:352-353, 371-372`) and `check` returns `pending changes` drift. `tests/test_init_seed_new_project.py:136-148` confirms by clearing `pending` by hand first. Fix: rewrite S1's acceptance to include the recorded pending reconciliation (recommended; matches the established creation contract), or authorize a behavior change so first-created region targets record no `pending`.

Bastion also confirmed the trigger is narrow (creation eligible only for a merge binding absent at `--bind-cleared` discovery), that merging into `{}` is the right construction because `check` compares through `is_merged` with the same project name, and that the `filesystem.py` fallback-root observation is out of scope on every reachable seed path.

**Crucible 🔥 (Test Architect)** — test gate, round 1. Verdict `[BLOCK]`, both named inputs reported absent:

> `tests/` holds only `test_pytest_temp_root.py`; a repo-wide grep for `test_init_seed_new_project|test_init_bind_cleared` returns 0 matches.

That block was a path error by the reviewer. The seeding test is at `.opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_init_seed_new_project.py`; the reviewer had run a literal grep over a `|`-joined pattern and read the resulting zero as absence. Confirmed by listing the directory and by the reviewer's own re-gate.

**Crucible 🔥** — test gate, round 2, after the path correction. Verdict `[PASS]`, zero findings:

> Q1 — yes, at the real entry point … asserts the tree, merge key-set equality with source, `qmd` index retargeted to `new-project` and the source index string absent, second `init` exit 0 with the merge document byte-identical. Q2 — yes, and it is effective under `--bind-cleared` … a create branch wrongly keyed on presence would drop all three and fail. Q3 — honest … never claims an immediate `current`. Q4 — nothing vacuous; S2 keeps real coverage.

Execution, owned and run by Crucible: `uv run --frozen --group dev pytest -q` → exit `0`, `952 passed, 6 skipped` (958 collected), and the seeding test confirmed to have executed rather than been skipped.

## E4 — literal commands and observed results

**Failure before the fix**, run by the coordinator against a genuinely empty directory outside every project (`C:\Users\dexm7\AppData\Local\Temp\opencode\empty-dest-test`):

```
$ init --bind-cleared --root AGENTS.md --destination <empty dir>
missing destination: <dir>\opencode.jsonc (merge mode cannot create it; the destination must exist)
exit 1
```

Directory contents afterwards: **0 entries**. Two earlier attempts on the same directory — `apply` with a bindings path inside it (`invalid bindings`), and `init --bind-cleared` without `--root` (`destination instruction root not found; pass --root`) — likewise left 0 entries.

**Success after the fix**, run against a fresh empty directory (`C:\Users\dexm7\AppData\Local\Temp\opencode\new-project-test`):

```
$ init --bind-cleared --root AGENTS.md --destination <empty dir>
initialized
```

Directory contents afterwards: `.aicore/`, `.opencode/`, `architecture/`, `knowledge/`, `odd/`, `AGENTS.md`, `opencode.jsonc`. The created `opencode.jsonc:317` reads `"command": ["npx", "-y", "@tobilu/qmd@2.8.3", "--index", "new-project-test", "mcp"]` — the new folder's own name.

Both paths lie under the operator temp directory, outside `G:\projects-personal-tismart\tismart-support` and outside any other destination project. No destination project was written by this feature.

## E5 — preservation mapping

**Superseded S1 acceptance wording** (original, unachievable — the record first appears in `b2667d0` already corrected, so this is the only retained copy):

> Acceptance: run `init --bind-cleared --root AGENTS.md` against an empty directory, then list it; the tree exists and a following `check` prints `current`.

**Replacement** (record `:15`):

> Acceptance: run `init --bind-cleared --root AGENTS.md` against an empty directory, then list it; the tree exists including `opencode.jsonc` whose `qmd` index names that folder, and a following `check` reports the created region targets awaiting their project-region reconciliation — printing `current` once that pending list is cleared.

Authority for the correction: Bastion's A1 above, plus the pre-existing enrollment behaviour that records `pending` for created region targets, exercised by `test_init_seed_new_project.py:141-148`.
