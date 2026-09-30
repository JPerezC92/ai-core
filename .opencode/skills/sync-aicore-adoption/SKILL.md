---
name: sync-aicore-adoption
description: Compare an atomic AICore adopter repository against the trusted AICore revision, report per-unit compliance, and apply a bounded reviewed update. Use when a project that adopted AICore must confirm every applicable core unit is current at one revision, generate a single-revision adoption lock, verify all registered adopters, or take an upstream update on an already-enrolled adopter. `check` and `verify-all` write nothing, `propose-lock` writes only to stdout, and `apply` is the single write path.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 2.2.0
  domain: opencode
  dependencies:
    - PyYAML==6.0.3
---

## What I do

I compare an independent adopter repository against the trusted AICore revision in one pass. I reconcile the accepted and current core catalogs, project each declared unit's content in a logical-member namespace, and report orthogonal **mode**, **upstream delta**, **destination delta**, and **disposition** per unit. I also enforce the adopter root runtime's closed destination policy: a mapped root carrying AICore or upstream identity, or missing its destination markers, is a blocking `policy_violation`. `check`, `propose-lock`, and `verify-all` never modify adopter files; `apply` is my single write path, bounded by the write-set rule documented under Commands.

I enforce atomic adoption: a lock carries exactly one accepted source commit for the whole adopter, every catalog unit must be accounted for (adopted or explicitly `not_applicable` under a machine-checked applicability rule), and `check` exits 0 only when the whole adopter is complete, current, and resolved. Partial per-unit acceptance does not exist in v2.

I am an **upstream-only AICore management tool**: run me from an AICore checkout against a runtime-supplied adopter path. I am not an adopted-content catalog unit, so I am never copied into an adopter repository. `migrate-core-to-project` is the same kind of upstream-only tool for initial installation.

I read the accepted catalog and content from the lock's single accepted source commit, and the current catalog and content from the trusted upstream revision. I read adopter destination content from exactly one explicit snapshot — a full adopter commit or the staged Git index — never the working tree. Only `apply` touches the working tree, and only after classification, for staging, lock regeneration, and verification. I never guess when history or mappings are ambiguous; I fail closed.

## When to use me

- A project adopted AICore and must confirm every applicable core unit is current at one revision.
- A maintainer needs to generate a single-revision `.aicore/adoption.lock.yaml` after reviewing an `.aicore/adoption.yaml` declaration and `.aicore/adoption-review.yaml`.
- A project suspects drift in a core-owned unit, a replacement member, an adapted member, or a merged config fragment.
- A maintainer has reviewed an upstream update for an already-enrolled adopter and wants it taken: `check` shows `update_available` on `copy` + `mirror` units and nothing else blocking, then `apply` writes exactly that set.
- The user wants to verify every adopter registered in `.aicore/adopters.yaml` against the trusted revision.
- You need a reproducible compliance report for review evidence — run `check` or `verify-all`, which write nothing.

Do NOT use me to perform the original installation or first enrollment (that is `migrate-core-to-project`; `apply` is never a first-enrollment path), to merge, overwrite, or reconcile non-mirror, drifted, or conflicting content (such runs are refused and the content stays governed by its review), or to author adopter-specific behavior.

## Arguments

From the request, extract:

- **upstream-repo** — path or checkout of the AICore upstream repository (required).
- **adopter-repo** — path to the adopter repository (required for `check`, `propose-lock`, and `apply`).
- **adopter snapshot** — exactly one of (required for `check`, `propose-lock`, and `apply`):
  - **adopter-revision** — full 40-character adopter commit whose tree holds destination content; or
  - **adopter-index** — read destination content from the staged adopter index only.
- **diagnostic-revision** — full 40-character upstream commit to compare against for diagnosis (`check` only; optional; never yields a compliance pass).
- **declaration** — path to the adopter declaration (default `.aicore/adoption.yaml`).
- **review** — path to the adopter review (default `.aicore/adoption-review.yaml`).
- **lock** — path to the adopted lock (default `.aicore/adoption.lock.yaml`).
- **registry** — path to the upstream registry (default `.aicore/adopters.yaml`; `verify-all` only).
- **format** — `json` or `human` (default `human`).

### Argument collection form

| name | type | validation | trigger |
|---|---|---|---|
| `upstream-repo` | text | exists and is a Git repository | not provided |
| `adopter-repo` | text | exists and contains the declaration | not provided for check/propose-lock/apply |
| `adopter-revision` | text | full 40-char commit in adopter, or `adopter-index` | neither snapshot provided |
| `adopter-index` | choice | boolean | neither snapshot provided |
| `diagnostic-revision` | text | full 40-char commit in upstream | optional |
| `format` | choice | json / human | not provided |

Use one `question` call per missing required argument. Do not add a manual "Other" option.

## Commands

| Command | Reads | Writes | Purpose |
|---|---|---|---|
| `check` | catalog, declaration, review, lock, upstream Git objects, one explicit adopter snapshot | nothing | Emit mode/delta/disposition per unit plus a compliance verdict; exit 0/1/2. |
| `propose-lock` | catalog, declaration, review, current Git objects, one explicit adopter snapshot | stdout only | Emit a complete single-revision candidate lock YAML plus one trailing newline. Diagnostics to stderr. |
| `verify-all` | `.aicore/adopters.yaml`, upstream Git objects, each registered adopter repository | nothing | Read-only checkout of each registered adopter and a compliance verdict per adopter; exit 0 only if all pass. |
| `apply` | catalog, declaration, review, the accepted baseline lock, upstream Git objects, one explicit adopter snapshot (classification), the on-disk adopter working tree (lock regeneration and verification) | adopter working-tree content and `.aicore/adoption.lock.yaml` | Refuse every unit outside a bounded write set before writing anything, stage that set, merge writable story indexes, regenerate the lock at the trusted revision, verify with the `check` logic; exit 0/1/2. |

`check`, `propose-lock`, and `verify-all` perform no filesystem, worktree, index, or ref mutation of the upstream or adopter repositories. `apply` is the only writer, and it writes only adopter working-tree content and the adopter lock file — it never stages the index, creates a commit, mutates a ref, fetches into the adopter, or deletes a destination file. There is no merge or overwrite path for anything outside its write set. All four are implemented in [`scripts/sync_aicore_adoption.py`](scripts/sync_aicore_adoption.py).

### Atomic proposals

- `propose-lock` rebuilds **every** declared unit at the one current revision. There is no `--unit` and no partial mode.
- A changed non-mirror unit (`adapted`, `replacement`, `destination_owned`) requires a matching `.aicore/adoption-review.yaml` decision before the lock can be generated.
- An incomplete declaration, an invalid applicability claim, an unsatisfied required assertion, a missing review decision, or a guarded root that violates its destination policy fails closed.

### Applying a reviewed update (`apply`)

- **When to use it.** An already-enrolled adopter with a valid v2 declaration, review, and baseline lock is ready to take an upstream update it is allowed to take — `check` reports `update_available` on `copy` + `mirror` units and nothing else blocking. It is NOT first enrollment: first installation stays with `migrate-core-to-project`, and `apply` never enrolls an adopter that has no baseline lock. It is not a merge tool either — non-mirror, drifted, and conflicting content is refused and stays governed by `.aicore/adoption-review.yaml`.
- **Selection rule.** Exactly the units whose catalog `install_strategy` is `copy`, whose declared mode is `mirror`, and whose disposition is `update_available` are written. `not_applicable` units are skipped; every other unit is an explicit `no_action` row, so no unit is decided by omission. Nothing outside that set is ever written.
- **Refusals — all before any write, all exit 2 with no partial output.** `policy_violation` (guarded root breaks its destination policy), `review_changed` (a non-mirror unit changed upstream with no review decision), and — because the regenerated lock re-baselines *every* declared unit — any blocking disposition (`update_available`, `local_drift`, `review_required`, `conflict`, `baseline_advance_required`) on **any** applicable unit outside the writable set, whatever its `install_strategy` or mode. That last rule covers a `copy` + `mirror` unit whose destination changed (destination bytes are never overwritten), a non-`copy` unit, and a `copy` + non-`mirror` unit alike; refusing is what stops the lock write from silently clearing a pending change. The stderr line names every refused unit and its reason under the first refusal's code; the report is never printed.
- **Write sequence.** Validate every destination and the lock path with `propose-lock`'s mapping rules; journal every intended path with its current bytes and file mode, in memory, before the first mutation; stage the writable members' core content; merge the portable-story indexes — the shared `user-stories/index.md` composes across the applicable portable-story units in declared order, core rows only for members carrying `collision_policy: core_wins`, preserving destination-only rows and trailing sections byte-for-byte; regenerate the lock through the shared `propose-lock` builder at the one trusted revision, writing it only after every content byte is staged; then verify with the existing `check` logic against the written working tree.
- **Verification.** Success requires the post-write `check` to pass. Classification reads the declared explicit snapshot; lock regeneration and verification read the working tree `apply` just wrote, so the reported result is the state actually staged. Story collisions stay stderr diagnostics and never change a disposition or an exit code.
- **Exit codes.** 0 for `apply: success` or `apply: noop` (nothing to write — the adopter is untouched); 1 when content and lock were written and are mutually consistent but the post-write `check` still reports blocking reasons; 2 for every refusal and every fatal failure.
- **Failure and recovery.** Any failure after the first write restores every journaled path to its recorded bytes and file mode — removing a file the run created — before the failure is surfaced, then exits 2 under the original code (or `apply_write_failed` for a write IO error). The restore is best-effort: never atomic, never a crash transaction. If a path cannot be put back, two `apply_restore_failed` lines go to stderr — first the JSON recovery record `{"original":..., "paths":[...]}` naming every path that may now be inconsistent, then the failure summary — the run exits 2, and those paths are reconciled by hand from the record. `KeyboardInterrupt` and `SystemExit` propagate untouched and are not restored.

## Comparison contract

I report four orthogonal fields with closed values:

- **mode** (from the declaration): `mirror | adapted | replacement | destination_owned | not_applicable`.
- **upstream delta**: `changed | unchanged` (a `not_applicable` unit reports `n/a`).
- **destination delta**: `changed | unchanged` (a `not_applicable` unit reports `n/a`).
- **disposition**: `current | not_applicable | update_available | local_drift | review_required | conflict | baseline_advance_required | policy_violation | unmanaged`.

Assertion units (`opencode-config`, `gitignore-config`) behave as `mirror` rows over a normalized assertion-status map: a missing required permission gate or ignore entry is `local_drift` (or `conflict` if upstream also changed) and can never be `current`.

A `guarded_file` unit (the adopter root runtime) carries a closed `destination_policy: adopter_root_runtime`. The mapped root is validated as UTF-8 text against the policy before any disposition is computed:

- **Prohibited** (case-insensitive substrings): `aicore`, `ai-core`, `migrate-core-to-project`, `sync-aicore-adoption`, `.aicore/`, `upstream provenance`, `upstream lineage`, `reuse guide`.
- **Required markers** (exact `> **…:**` lines): `Project identity`, `Spec version`, and `Local version`.

A violating root is never `current`, even when its bytes match the accepted lock: `propose-lock` fails closed with stable code `policy_violation` (exit 2) and emits no YAML, and `check` reports the unit disposition `policy_violation`, adds it to the blocking reasons, and exits 1. The policy applies only to the adopter snapshot's mapped root; AICore's own upstream `AGENTS.md` keeps its reuse guide.

## Exit contract

| Exit | Meaning |
|---:|---|
| 0 | Compliance pass: complete declaration, every declared unit `current` or `not_applicable` (or the `unmanaged` `destination_owned` steady state), all changed non-mirror units reviewed, catalog current. |
| 1 | Valid input but non-compliant (stale/`update_available`/`local_drift`/`conflict`/`review_required`/`baseline_advance_required`/`policy_violation`) or diagnostic mode. |
| 2 | Fatal: schema/identity/mapping/snapshot/trust failure, `declaration_incomplete`, `invalid_applicability`, `invalid_lock`, `invalid_declaration`, `schema_upgrade_required`. |

The trusted revision is the tip of the upstream repository's protected default branch. `--diagnostic-revision` compares against an explicit revision for diagnosis and can never exit 0.

`propose-lock` fails closed with stable code `policy_violation` (exit 2) before emitting any candidate YAML when a guarded root violates the destination policy.

`apply` maps onto the same inputs with its own outcome on top of this contract: exit 0 for a successful write or a no-op, exit 1 when content and lock were written and are mutually consistent but the post-write `check` is non-compliant, and exit 2 for every refusal — emitted under the refusal's own code, so dispositions that `check` reports at exit 1 can refuse `apply` at exit 2 — and every fatal failure.

The exact schemas, digest framing, disposition table, and safety invariants are defined in [`references/protocol-v2.md`](references/protocol-v2.md). Reference examples: [`references/adoption-declaration-v2.yaml`](references/adoption-declaration-v2.yaml), [`references/adoption-lock-v2.yaml`](references/adoption-lock-v2.yaml), and [`references/adoption-review-v2.yaml`](references/adoption-review-v2.yaml). The previous `protocol-v1.md` is retained only as migration input.

## Examples

### Example 1 — check an adopter for compliance

> "Is my project fully current with AICore?"

Run `check` with an explicit adopter snapshot (`--adopter-revision <sha>` or `--adopter-index`). Output lists each unit with its mode, both deltas, and a disposition plus a `compliance` verdict. Exit 0 means complete and current; exit 1 lists the blocking units (`update_available`, `baseline_advance_required`, `local_drift`, `review_required`, `conflict`); exit 2 means the inputs themselves are invalid.

### Example 2 — propose a complete lock

> "Generate the adoption lock at the trusted revision."

Run `propose-lock` with the trusted catalog-bearing revision and an explicit adopter snapshot. It prints one complete candidate lock to stdout. The maintainer reviews it, then commits it as `.aicore/adoption.lock.yaml`. A changed non-mirror unit without a review decision is rejected.

### Example 3 — verify every registered adopter

> "Check that every AICore adopter is current."

Run `verify-all`. It reads `.aicore/adopters.yaml`, checks each registered adopter at its default branch, and exits 0 only when every registered adopter passes. A missing, unreachable, stale, or unregistered adopter fails the run.

### Example 4 — apply a reviewed update

> "Take the upstream update on our adopted project."

Run `check` first and confirm every blocking reason is `update_available` on a `copy` + `mirror` unit, with all changed non-mirror units already carrying review decisions. Then run `apply` with the same explicit adopter snapshot. It writes exactly that set, merges the writable story indexes, regenerates `.aicore/adoption.lock.yaml` at the trusted revision, and verifies with the `check` logic: exit 0 on success, exit 1 if the written state is still non-compliant (reported reasons included), exit 2 on a refusal with nothing written.

## Troubleshooting

- **`check` exits 2 with `schema_upgrade_required`** — the adopter still uses a v1 declaration or lock. Fix: re-declare under v2 (add `profile`, cover every catalog unit including the former config `none` units), author the review, regenerate a v2 lock.
- **`check` exits 2 with `declaration_incomplete`** — a catalog unit is missing from the declaration. Fix: add its row as a real mode or, when applicability allows, `not_applicable`.
- **`check` exits 2 with `invalid_applicability`** — a required/always unit was marked `not_applicable`, or an applicable unit was. Fix: correct `profile` or the unit mode.
- **`check` exits 1 with `baseline_advance_required`** — the accepted baseline is behind the trusted revision. Fix: regenerate the lock at the trusted revision after reviewing changed non-mirror units.
- **`check` exits 2 with `baseline_unavailable`** — the accepted commit is missing, not a commit, or not an ancestor of the trusted revision. Fix: fetch full history into `upstream-repo`; never shorten an accepted SHA.
- **`check` exits 2 with `invalid_lock`** — a row carries its own source commit (v1 shape) or its evidence does not reproduce from the single accepted commit. Fix: regenerate with `propose-lock`.
- **A config unit reports `local_drift`** — a required permission gate or ignore entry is missing from `opencode.jsonc` or `.gitignore`. Fix: re-add the required gate/entry, then regenerate the lock.
- **`verify-all` reports a missing or unreachable adopter** — the registry entry or repository access is wrong. Fix: correct `.aicore/adopters.yaml` or repository access; the run stays blocking until every registered adopter passes.
- **A replacement member reports `local_drift` / `review_required` / `conflict`** — the local member changed, upstream changed, or both. Fix: record a review decision and regenerate the lock.
- **`propose-lock` exits 2 with `policy_violation`** — the mapped adopter root contains a prohibited AICore/upstream/management-tool/reuse/lineage reference or is missing a required destination marker. Fix: rewrite the root to destination-only identity, then regenerate the lock.
- **`check` exits 1 with `policy_violation`** — the explicit adopter snapshot's mapped root violates the destination policy, even when the locked bytes already match. Fix: correct the root, then regenerate the lock.
- **`apply` exits 2 with a refusal code** — nothing was written. Fix the named units first: record the review decision for `review_changed`; correct the guarded root for `policy_violation`; for any other blocking disposition on a unit outside the writable set — which covers a changed `copy` + `mirror` unit, a `merge`/`preserve` unit, and a non-`mirror` `copy` unit alike — either take the update, advance the baseline, restore the destination bytes, or re-declare the unit's mode so it is no longer blocking. Then re-run `check` and `apply`.
- **`apply` exits 1** — content and lock were written and are mutually consistent, but the post-write `check` reports blocking reasons. Fix: resolve the reported units against the written working tree, then re-run `check` (and `apply` again if more updates remain).
- **`apply` exits 2 with `apply_restore_failed`** — a failure hit after the first write and the best-effort restore could not put every journaled path back. Fix: reconcile every path named in the stderr recovery record `{"original":..., "paths":[...]}` by hand against its recorded pre-apply bytes and mode (or remove a file the run created), then re-run `check`. The restore is best-effort — no atomicity or crash-transaction guarantee is claimed.
