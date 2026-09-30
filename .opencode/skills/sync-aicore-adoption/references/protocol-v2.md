# AICore adoption synchronization — protocol v2

> **Status:** current
> **Supersedes:** `protocol-v1.md` (retained verbatim as migration input; never amended).
> **Scope:** The exact contract for `check`, `propose-lock`, `verify-all`, and `apply`, plus the first-enrollment ordering the migration skill must satisfy before invoking them. v2 makes adoption atomic: one upstream revision per adopter, complete catalog coverage, machine-checked applicability, deterministic merged-config assertions, and tracked reconciliation evidence. Partial per-unit acceptance is forbidden.

## Section 1 — Core / adopter split

| Artifact | Owner | Contains | Never contains |
|---|---|---|---|
| `.aicore/core-catalog-v2.yaml` | AICore upstream | unit identity, logical members, real tracked source paths, canonical destinations, machine `applicability`, `install_strategy`, `sync_projection`, member `collision_policy`, config `assertions` | adopter modes, destination overrides, digests |
| `.aicore/adoption.yaml` (declaration) | Adopter | upstream identity, `profile`, one entry per catalog unit with its `mode` and destination mapping | digests, accepted commit |
| `.aicore/adoption-review.yaml` (review) | Adopter | reconciliation decisions for changed non-mirror units | generated digests |
| `.aicore/adoption.lock.yaml` (lock) | Generated | one top-level accepted baseline and one row per declared unit | intent, modes, hand-edited content |
| `.aicore/adopters.yaml` (registry) | AICore upstream | the authoritative list of adopter repositories used by `verify-all` | credentials, machine-local paths, project source |

The declaration is intent. The review is the human reconciliation decision. The lock is generated evidence. A maintainer edits the declaration and review, runs `propose-lock`, reviews the candidate, and commits it as the lock.

`migrate-core-to-project` and `sync-aicore-adoption` are upstream-only operator tools; neither the tools nor the catalog nor the registry is an adopted-content unit.

## Section 2 — Declaration schema v2

```yaml
schema_version: 2
upstream_repository: JPerezC92/ai-core
profile:
  backend_stack: false
  python_scripts: true
  ticket_system: false
units:
  - id: <catalog-unit-id>
    mode: mirror | adapted | replacement | destination_owned | not_applicable
    members:
      - { id: <catalog-member-id>, destination: <repo-relative path> }
  - id: <catalog-unit-id>
    mode: replacement
    replacement_members:
      - { id: <adopter-local-id>, destination: <repo-relative path>, projection: file | tree }
  - id: <catalog-unit-id>
    mode: not_applicable
```

Rules:

- Every catalog unit id appears exactly once. A missing id is `declaration_incomplete`; an unknown or duplicated id is `invalid_declaration`. Both are fatal (exit 2).
- `profile` markers are `backend_stack`, `python_scripts`, `ticket_system`, each boolean.
- `not_applicable` is valid only when the catalog unit is not `always` and its applicability conditions are false under the declared `profile`; otherwise `invalid_applicability` (fatal).
- `mirror` and `adapted` and `destination_owned` map every catalog member exactly once; a member absent from the current catalog is `invalid_declaration`.
- `replacement` uses named local `replacement_members` with a unique id, a destination, and an explicit `file|tree` projection; it never claims byte convergence.
- Each `file`/`tree` member maps to exactly one rooted destination; `assertions` units must not declare members — their destination is `destination` in the catalog.

## Section 3 — Review schema v2

```yaml
schema_version: 2
upstream_repository: JPerezC92/ai-core
decisions:
  - unit: <catalog-unit-id>
    decision: applied | declined | superseded
    evidence: <short human-verifiable reference or note>
    reviewer: <role responsible for the decision>
```

- A decision is required whenever a `mirror`-excluded unit's upstream digest changed between the accepted baseline and the target revision: `adapted`, `replacement`, and `destination_owned`.
- `declined` and `superseded` must carry an `evidence` note explaining why the upstream change does not apply or is overridden locally.
- The review file's raw digest is bound into the lock as `review_digest`; a changed review invalidates the lock (`declaration_changed`-class, fatal).

## Section 4 — Lock schema v2

```yaml
schema_version: 2
upstream_repository: JPerezC92/ai-core
accepted_source_commit: <40-char sha>
accepted_catalog_digest: sha256:<hex>
declaration_digest: sha256:<hex>
review_digest: sha256:<hex>
accepted_snapshot_digest: sha256:<hex>
units:
  - id: <catalog-unit-id>
    mode: mirror | adapted | replacement | destination_owned
    declaration_unit_digest: sha256:<hex>
    accepted_upstream_digest: sha256:<hex>
    members:
      - id: <catalog-member-id>
        destination: <repo-relative path>
        accepted_upstream_digest: sha256:<hex>
        accepted_destination_digest: sha256:<hex>
  - id: <assertion-unit-id>
    mode: mirror
    declaration_unit_digest: sha256:<hex>
    accepted_upstream_digest: sha256:<hex>
    members:
      - id: assertions
        destination: <repo-relative path>
        accepted_upstream_digest: sha256:<hex>
        accepted_destination_digest: sha256:<hex>
  - id: <catalog-unit-id>
    mode: not_applicable
  - id: <catalog-unit-id>
    mode: replacement
    declaration_unit_digest: sha256:<hex>
    accepted_upstream_digest: sha256:<hex>
    replacement_members:
      - id: <adopter-local-id>
        destination: <repo-relative path>
        projection: file | tree
        accepted_destination_digest: sha256:<hex>
```

Rules:

- There is exactly one `accepted_source_commit` for the whole lock and one `accepted_catalog_digest`. Per-unit source commits do not exist; any lock row carrying its own source commit is `invalid_lock` (fatal).
- Every non-`not_applicable` row's evidence must reproduce from the single accepted source commit; a mismatch is `invalid_lock`.
- Every catalog unit has a row. A `not_applicable` row carries only `id` and `mode`.
- `mirror` rows require accepted upstream and destination digests to be equal. Assertion units are `mirror` rows whose digests cover the assertion list and the assertion-status map (Section 7).
- `accepted_snapshot_digest` is a digest over the ordered `(unit id, member id, accepted_destination_digest)` tuples plus the declaration and review digests, binding the lock to one adopter snapshot.

## Section 5 — Catalog schema v2

- `schema_version: 2`; `catalog.version` is SemVer and changes when any unit, member, applicability, or assertion changes.
- `applicability` is one of `{ always: true }`, `{ requires: [marker, ...] }`, or `{ any_of: [marker, ...] }`.
- `sync_projection` is `file`, `guarded_file`, `tree`, or `assertions`. There is no `none`.
- `guarded_file` is a single tracked file with a closed `destination_policy`. The only defined policy is `adopter_root_runtime`; a `destination_policy` on any other projection, or an unknown policy value, is `invalid_mapping` (fatal). `guarded_file` normalizes to the `file` projection for all digest framing, so lock and declaration member shapes are unchanged.
- The projection set is closed: an engine that does not understand `guarded_file` fails with `unsupported_projection` (fatal) instead of skipping the unit. A guarded root can therefore never be silently accepted by an older engine.
- Assertion units declare a `destination` and an ordered `assertions` list of `{ id, contains }` required substrings.
- A catalog member may declare `collision_policy`; the only known value is `core_wins` and any other value is `invalid_mapping` (fatal). It is declared by portable story members and honoured only by the story index projection (Section 17). A member without `collision_policy: core_wins` never wins a collision: its destination bytes and index rows are untouched by any merge, and no core-wins collision is reported for it.
- Portable stories are `kind: user-story` units with `install_strategy: copy` and `sync_projection: file`, split by applicability class into `portable-stories-always` (`{ always: true }`), `portable-stories-ticket` (`requires: [ticket_system]`), and `portable-stories-python` (`requires: [python_scripts]`); every member carries `collision_policy: core_wins`. The `user-stories` scaffold unit stays `install_strategy: preserve` with its sole `gitkeep` member. `user-stories/index.md` and `aicore-adoption-sync.md` are never catalog members: the index is never mirrored wholesale, and the management-tools story never ships to a destination.

## Section 6 — Applicability model

For each catalog unit the engine evaluates applicability under the declaration `profile`:

- `always` → applicable.
- `requires: [m1, m2]` → applicable iff every marker is true.
- `any_of: [m1, m2]` → applicable iff at least one marker is true.

A unit that is applicable must be adopted with a real mode; a unit that is not applicable must be `not_applicable`. Any mismatch is fatal (`invalid_applicability`). This is how a dev-only project excludes the incident team without silently abandoning it: the exclusion is declared, machine-checked, and current.

## Section 7 — Digest protocol (v2)

`sha256`, output `sha256:<lowercase hex>`.

- `file` / `guarded_file` / `tree` member digests use the v1 framing (path/mode/size/content, ascending logical path, `__pycache__` and `*.pyc` excluded) — unchanged.
- Unit digest uses the v1 member framing — unchanged.
- Declaration-unit intent digest is the v1 framing — unchanged.
- Assertion-list digest: for each assertion in catalog order,
  ```
  b"assertion\n" b"id:"+id+b"\n" b"contains:"+contains+b"\n"
  ```
- Assertion-status digest: for each assertion in catalog order,
  ```
  b"status\n" b"id:"+id+b"\n" b"present:"+(b"1"|b"0")+b"\n"
  ```

## Section 8 — Semantic config assertions

- A destination fragment is read from the adopter snapshot, then every line whose trimmed form begins with `//` (JSONC) or `#` (ignore files) is dropped. Remaining text is matched literally.
- An assertion is `present` when its `contains` substring appears in the stripped text.
- `opencode-config` covers permission gates (stash push/apply allows; stash pop/drop/clear, update-ref, reflog, gc, prune, repack, symbolic-ref denial; `sudo`, `rm -rf /*`, `git push --force`, `gh pr merge`, `gh repo delete`, root redirect denials; `mv plans/*-*` allow).
- `gitignore-config` covers the required ignore entries.
- A missing required assertion is `local_drift` at minimum and `conflict` if upstream also changed; the unit can never be `current` while an assertion is absent.

## Section 9 — Explicit adopter snapshot

`check`, `propose-lock`, and the classification phase of `apply` read adopter destination content from exactly one explicit source:

- `--adopter-revision <40-char sha>` — that commit's tree.
- `--adopter-index` — the staged Git index only.

Missing, ambiguous, malformed, or non-commit inputs are `adopter_snapshot_unavailable`. Apart from `apply`'s post-write phase (Section 18), no command reads the adopter worktree. The declaration, review, and lock are read from the upstream invocation paths, not from destination content; the engine requires them to belong to the same snapshot when a revision is supplied.

## Section 10 — Trusted revision and diagnostic mode

- Compliance mode resolves the trusted revision as the tip of the upstream repository's protected default branch (`refs/remotes/origin/main`, falling back to `refs/heads/main`). The lock's `accepted_source_commit` must be an ancestor of it, or `baseline_unavailable` (fatal).
- `--diagnostic-revision <sha>` is diagnostic only: it compares against that explicit revision and always reports `compliance: false`, exiting 1 at best. It can never exit 0.

## Section 11 — Comparison and dispositions

| mode | upstream delta | destination delta | disposition |
|---|---|---|---|
| mirror | unchanged | unchanged | `current` |
| mirror | changed | unchanged | `update_available` |
| mirror | unchanged | changed | `local_drift` |
| mirror | changed | changed | `conflict` |
| adapted | unchanged | unchanged | `current` |
| adapted | changed | unchanged | `update_available` |
| adapted | unchanged | changed | `local_drift` |
| adapted | changed | changed | `review_required` |
| replacement | unchanged | unchanged | `current` |
| replacement | unchanged | changed | `local_drift` |
| replacement | changed | any | `review_required` |
| destination_owned | changed | any | `review_required` |
| destination_owned | unchanged | any | `unmanaged` |
| any | accepted baseline behind target | any | `baseline_advance_required` when otherwise `current` |
| not_applicable | n/a | n/a | `not_applicable` |

A delta is `changed` or `unchanged` (the engine does not distinguish added/removed/modified). Assertion units follow the `mirror` rows using their assertion-list delta (upstream) and assertion-status delta (destination). `replacement` never reports `update_available`.

A `guarded_file` unit evaluates its `destination_policy` against the snapshot before any delta is reported. For `adopter_root_runtime`, the mapped root is decoded as UTF-8 text and must contain no case-insensitive prohibited reference (`aicore`, `ai-core`, `migrate-core-to-project`, `sync-aicore-adoption`, `.aicore/`, `upstream provenance`, `upstream lineage`, `reuse guide`) and must carry the `Project identity`, `Spec version`, and `Local version` markers. A violating root reports the disposition `policy_violation` regardless of upstream or destination delta, is always blocking, and can never be `current`. The policy applies to the adopter snapshot only; AICore's own upstream root is not subject to it.

An `opencode-config` unit whose destination basename is `opencode.jsonc` additionally evaluates its **runner policy** against the snapshot bytes before any delta is reported. Every `agent.*.permission.bash` entry whose action is `allow` is classified: a `deny` entry is never judged, so deny-first ordering is not itself a violation. Among `allow` entries, a broad catch-all (`*`, `**`, or a bare interpreter/runner head such as `uv *`, `pytest *`, `bash *`) is a violation. An `allow` that is identified as a test runner — it contains `pytest`, or names a package test script (`pnpm test`, `npm test`, `yarn test`, `cargo test`, with or without arguments) — must then be exactly the project's reviewed fixed suite command or an exactly matching bounded package script: compared **literally**, with no whitespace normalisation, so an appended test path, a wildcard, reordered tokens, or interior double-spaces are all violations. `allow` entries that are neither catch-alls nor test runners (for example `pnpm install`) are skipped, and a config carrying no test-runner `allow` at all is not a violation — some destinations legitimately have no Python suite. A violating config reports `policy_violation` regardless of delta, is always blocking, and can never be `current`. Each destination keeps its own reviewed suite; AICore's fixed suite command is never imposed as a default on an adopter that reviews a different one.

## Section 12 — Exit contract

| Exit | Meaning |
|---:|---|
| 0 | Compliance pass: complete declaration, all units `current` or `not_applicable` (or the `unmanaged` `destination_owned` steady state), all changed non-mirror units reviewed, catalog current. |
| 1 | Valid input but non-compliant: any `baseline_advance_required`, `update_available`, `local_drift`, `review_required`, `conflict`, or `policy_violation` on any declared unit; diagnostic mode. `unmanaged` — a `destination_owned` unit whose upstream is unchanged — is the non-blocking steady state of an intentional local fork. |
| 2 | Fatal: schema/identity/mapping/snapshot/trust failure, `declaration_incomplete`, `invalid_applicability`, `invalid_lock`, `invalid_declaration`, `schema_upgrade_required`. |

## Section 13 — Top-level fatal errors

`baseline_unavailable`, `invalid_lock`, `invalid_declaration`, `declaration_incomplete`, `invalid_applicability`, `declaration_changed`, `review_changed`, `catalog_changed`, `invalid_mapping`, `unsupported_projection`, `unsupported_special_file`, `adopter_snapshot_unavailable`, `repository_identity_mismatch`, `schema_upgrade_required`, `unknown_key`.

`policy_violation` is the guard-specific code and is not a top-level parse failure: `propose-lock` emits it (exit 2) when a guarded root violates its `destination_policy` or an adopter `opencode.jsonc` violates its runner policy, `check` reports it as a blocking disposition (exit 1), and `apply` refuses on it before any write (Section 18).

`apply` adds two fatal codes of its own: `apply_write_failed` for a write IO error after the journal is taken, and `apply_restore_failed` when a best-effort restore cannot put a journaled path back. Its refusals exit 2 under the refusal's own code, reusing codes already named in this section or the dispositions of Section 11.

## Section 14 — v1 migration

- A v1 lock or declaration is upgrade-only input. Any command reading one fails with `schema_upgrade_required` (exit 2) and prints upgrade guidance to stderr.
- Upgrade is not a per-unit carry-forward: the adopter re-declares under v2 (adding `profile`, covering every catalog unit including the former `none` config units), authors the review, and regenerates a fresh v2 lock at one revision.

## Section 15 — `propose-lock`

- Inputs: validated declaration + review, catalog-bearing current revision, one explicit adopter snapshot.
- Removes `--unit`: a proposal rebuilds every declared unit at the one current revision. There is no partial mode.
- Rejects an incomplete declaration, a missing review decision for a changed non-mirror unit, an incomplete mirror subtree, a missing required assertion, invalid applicability, a guarded root that violates its `destination_policy`, or an `opencode.jsonc` whose test-runner grants violate the runner policy (stable code `policy_violation`).
- Emits candidate lock YAML plus one trailing newline to stdout only; diagnostics to stderr, including portable-story index collisions (Section 17).

## Section 16 — `verify-all`

- Reads `.aicore/adopters.yaml` (registry) from the upstream repository.
- For every registered adopter: resolves the registry repository at `default_branch`, obtains a read-only checkout (a fresh `gh repo clone` into a temp directory unless a cached checkout is supplied), and runs compliance `check` at that commit.
- Produces one verdict per adopter and a blocking aggregate: any adopter that is missing, unreachable, stale, or not at the trusted revision fails the run (exit 1).
- Registry entries carry `id`, `repository`, `default_branch`, `declaration_path`, `lock_path`, and `review_path`. Every registered adopter is mandatory — there is no `required` flag and no entry that can be exempted. No credentials or machine-local paths.

## Section 17 — Portable story projection (index merge)

For every applicable `kind: user-story` unit that is not declared `replacement`, `check` and `propose-lock` compute the story index merge in memory:

- The core index is the `index.md` beside the unit's catalog member sources; the destination index is the `index.md` beside the declared member destinations.
- Fresh destination (absent or empty index): the result is the core document with every non-member row removed, so only the applicable members' core rows are seeded.
- Existing table: a missing member row is inserted at the end of the existing table; a differing member row is replaced inside the table only when the member declares `collision_policy: core_wins`; an identical row is left untouched.
- Destination-only rows, rows of members without `core_wins`, and every byte before and after the table — line endings included — are preserved byte-for-byte. A destination index that holds prose but no table gains the applicable core table block appended after its own bytes.
- A differing `core_wins` member yields exactly two report strings: `collision: path <destination>; core wins` and `collision: slug <slug>; core wins`. Identical rows yield none. A member without `core_wins` never writes and never reports.
- Collisions are diagnostics, not dispositions: `check` lists them under `collisions` in its report (and prints them in human format) without changing any unit disposition or exit code; `propose-lock` prints them to stderr so stdout stays pure lock YAML; `apply` prints any that remain to stderr from its lock rebuild (Section 18).
- `not_applicable` story units are never projected: their slugs receive no rows and no collisions.
- `check` and `propose-lock` compute the merged bytes in memory only. Only `apply` persists the merge, and only for writable story units (Section 18); Section 20's read-only guarantee covers the read-only commands and is unchanged.

## Section 18 — `apply` (the single bounded write path)

`apply` is the fourth subcommand, alongside `check`, `propose-lock`, and `verify-all`. It serves exactly one situation: an already-enrolled adopter with a valid v2 declaration, review, and baseline lock that is ready to take an upstream update it is allowed to take. It is not first enrollment — first enrollment stays `migrate-core-to-project` (Section 19) — and it is not a merge tool: non-mirror, drifted, and conflicting content is refused and stays governed by its review.

- **Inputs.** A validated declaration, a review (a missing review path is read as an empty decision list), the catalog, the accepted baseline lock (required), the upstream repository, and exactly one explicit adopter snapshot (`--adopter-revision` or `--adopter-index`). Classification reads that declared snapshot (Section 9); the target is the trusted revision with no diagnostic mode (Section 10); an accepted commit that is not an ancestor of it is `baseline_unavailable` (fatal). `apply` takes no `--diagnostic-revision`.
- **Classification.** Every declared catalog unit receives exactly one decision against its baseline lock row — `writable`, `refused`, `skipped` (mode `not_applicable`), or `no_action` — so no unit is classified by omission. Mapping validation is `propose-lock`'s (Section 15). A baseline row whose mode is `not_applicable` carries no member evidence and is treated as having no baseline row; a member declared after the accepted snapshot has no recorded destination digest and is seeded as unchanged while its destination holds no bytes, so nothing that was never accepted can be lost.
- **Write set.** Exactly `install_strategy: copy` intersected with mode `mirror` intersected with disposition `update_available` (Section 11) is writable. Nothing else is ever written: `merge` and `preserve` units, every non-mirror mode, and assertion units are never written.
- **Refusals.** Any unit that needs a write `apply` can never perform is refused before the first byte is written. The run names every refused unit and its reason on stderr under the first refusal's code, emits no report, writes nothing, and exits 2:
  - `policy_violation` — a guarded root violates its destination policy, or the adopter's `opencode.jsonc` test-runner grants violate the runner policy (Section 11).
  - `review_changed` — a non-mirror unit (`adapted`, `replacement`, `destination_owned`) whose upstream changed at the target revision carries no review decision (Section 3).
  - `local_drift` / `conflict` — a `copy` + `mirror` unit whose destination changed; destination bytes are never overwritten by `apply`.
  - a blocking disposition — `update_available`, `local_drift`, `review_required`, `conflict`, `baseline_advance_required` (Section 12) — on **any** applicable unit outside the writable set, whatever its `install_strategy` or mode. Because Section 4 makes the lock one global document, writing it re-baselines every declared unit; allowing it while a non-written unit is still blocking would silently clear that unit's pending change. This single rule therefore covers a changed `copy` + `mirror` unit, a `merge`/`preserve` unit, and a non-`mirror` `copy` unit alike.
- **No-op.** With no writable unit, `apply` prints its report with `apply: noop`, touches nothing, and exits 0.
- **Staging plan.** Every writable member destination and the lock path are validated with Section 15's mapping rules — no absolute path, no parent traversal, no protected control path, no duplicate or overlapping destination — before anything is written, so an invalid mapping can never reach the worktree. A missing or empty source is `baseline_unavailable`; `apply` never deletes a destination file.
- **Journal.** Before the first mutation, `apply` records, in memory only, every path it intends to write — staged members, story indexes, and the lock — with its current bytes and file mode; a path that does not exist yet records no bytes, marking a creation. The journal is never persisted, and a shared story index is journaled once.
- **Writes.** One guarded region performs, in order: the staged member writes; the portable-story index merges of Section 17, with units sharing one destination index — the portable-story units composing across the shared `user-stories/index.md` — merging in declared order and each index written once; lock regeneration through the shared `propose-lock` builder (Section 15) at the one trusted target revision, reading the post-write worktree, written only after every content byte is staged; and finally the `check` report (Section 12) against that written worktree. Classification reads the declared snapshot, but lock regeneration and verification read the post-write worktree, so the result reported is the state actually written. Story collisions stay stderr diagnostics from the lock rebuild and never change a disposition or an exit code.
- **Failure and best-effort restore.** Any failure inside the guarded region restores every journaled path to its recorded bytes and file mode — removing a file the run created — before the failure is surfaced. When every path verifies back, the run exits 2 under the original code, or `apply_write_failed` for a write IO error, with the restore stated on stderr. When a path cannot be put back, `apply` emits two stderr lines under `apply_restore_failed`: first the JSON recovery record `{"original":..., "paths":[...]}` naming the original failure and every path that may now be inconsistent, then the failure summary; the run exits 2 and those paths are reconciled by hand from the record. The restore is best-effort only: `apply` claims no atomicity and no crash-transaction semantics, only journaled paths are restored (directories the run created stay in place), and `KeyboardInterrupt` and `SystemExit` propagate untouched.
- **Verification and exit codes.** Success requires the post-write `check` to pass: exit 0 for `apply: success` or `apply: noop`; exit 1 when content and lock were written and are mutually consistent but the worktree check still reports blocking reasons (for example a guarded-root `policy_violation` that the classification snapshot did not show); exit 2 for every refusal and every fatal failure, including a restore failure. The report is machine-readable in `json` or `human` format with fields `apply`, `written`, `lock`, `verify`, and `blocking`.
- **Bounded surface.** `apply` writes only adopter worktree content and the adopter lock file. It never stages the Git index, never creates a commit, never mutates a ref, and never fetches into the adopter.

## Section 19 — First-enrollment contract (modes bound before the first write)

`migrate-core-to-project` binds ownership before it writes any adopted-content byte:

- For every applicable unit the owner records a mode — `mirror`, `adapted`, `replacement`, or `destination_owned` — in the declaration, and every non-mirror unit's reviewed destination bytes exist at its mapped path. Inapplicable units are recorded `not_applicable`.
- Only after every applicable unit has a recorded mode, and every non-mirror unit reviewed destination bytes, may the first adopted-content byte be staged. The declaration and review are the record of that ordering.
- `install_strategy: copy` units in mode `mirror` receive core bytes. `merge` and `preserve` units, and every non-mirror unit, keep owner bytes. A differing `adapted` file is read and edited, never overwritten. A destination difference with no recorded mode and reviewed bytes blocks enrollment before the first copy.
- Portable story core-wins applies only to members declaring `collision_policy: core_wins` (Section 5, honoured by the projection in Section 17): only those members' differing rows are replaced by core rows and reported as collisions; every other member's destination bytes and index rows are untouched by any merge.
- Lock generation stays delegated to `propose-lock` (Section 15) and completion is `check` (Section 12) exit 0. This section describes ordering only; it claims no crash-transaction semantics.

## Section 20 — Read-only guarantee

`check`, `verify-all`, and `propose-lock` write nothing: `check` and `verify-all` mutate no filesystem, worktree, index, or ref of the upstream or adopter repositories, and `propose-lock` writes only to stdout. No command in this protocol other than `apply` (Section 18) persists the story index merge of Section 17, and no command performs a delete, a fetch-into-adopter, or any adopter Git mutation.

`apply` is the single deliberate exception to this guarantee, bounded by Section 18: it refuses everything outside its write set before the first byte, writes only adopter worktree content and the adopter lock file, restores journaled paths best-effort on failure, and never touches Git state. Tests assert the adopter worktree and Git state are byte-identical before and after `check`, `propose-lock`, and `verify-all`.
