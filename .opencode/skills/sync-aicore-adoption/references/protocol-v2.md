# AICore adoption synchronization — protocol v2

> **Status:** current
> **Supersedes:** `protocol-v1.md` (retained verbatim as migration input; never amended).
> **Scope:** The exact contract for `check`, `propose-lock`, and `verify-all`. v2 makes adoption atomic: one upstream revision per adopter, complete catalog coverage, machine-checked applicability, deterministic merged-config assertions, and tracked reconciliation evidence. Partial per-unit acceptance is forbidden.

## Section 1 — Core / adopter split

| Artifact | Owner | Contains | Never contains |
|---|---|---|---|
| `.aicore/core-catalog-v2.yaml` | AICore upstream | unit identity, logical members, real tracked source paths, canonical destinations, machine `applicability`, `install_strategy`, `sync_projection`, config `assertions` | adopter modes, destination overrides, digests |
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
- `sync_projection` is `file`, `tree`, or `assertions`. There is no `none`.
- Assertion units declare a `destination` and an ordered `assertions` list of `{ id, contains }` required substrings.

## Section 6 — Applicability model

For each catalog unit the engine evaluates applicability under the declaration `profile`:

- `always` → applicable.
- `requires: [m1, m2]` → applicable iff every marker is true.
- `any_of: [m1, m2]` → applicable iff at least one marker is true.

A unit that is applicable must be adopted with a real mode; a unit that is not applicable must be `not_applicable`. Any mismatch is fatal (`invalid_applicability`). This is how a dev-only project excludes the incident team without silently abandoning it: the exclusion is declared, machine-checked, and current.

## Section 7 — Digest protocol (v2)

`sha256`, output `sha256:<lowercase hex>`.

- `file` / `tree` member digests use the v1 framing (path/mode/size/content, ascending logical path, `__pycache__` and `*.pyc` excluded) — unchanged.
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

`check` and `propose-lock` read adopter destination content from exactly one explicit source:

- `--adopter-revision <40-char sha>` — that commit's tree.
- `--adopter-index` — the staged Git index only.

Missing, ambiguous, malformed, or non-commit inputs are `adopter_snapshot_unavailable`. No command reads the adopter worktree. The declaration, review, and lock are read from the upstream invocation paths, not from destination content; the engine requires them to belong to the same snapshot when a revision is supplied.

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

## Section 12 — Exit contract

| Exit | Meaning |
|---:|---|
| 0 | Compliance pass: complete declaration, all units `current` or `not_applicable` (or the `unmanaged` `destination_owned` steady state), all changed non-mirror units reviewed, catalog current. |
| 1 | Valid input but non-compliant: any `baseline_advance_required`, `update_available`, `local_drift`, `review_required`, or `conflict` on any declared unit; diagnostic mode. `unmanaged` — a `destination_owned` unit whose upstream is unchanged — is the non-blocking steady state of an intentional local fork. |
| 2 | Fatal: schema/identity/mapping/snapshot/trust failure, `declaration_incomplete`, `invalid_applicability`, `invalid_lock`, `invalid_declaration`, `schema_upgrade_required`. |

## Section 13 — Top-level fatal errors

`baseline_unavailable`, `invalid_lock`, `invalid_declaration`, `declaration_incomplete`, `invalid_applicability`, `declaration_changed`, `review_changed`, `catalog_changed`, `invalid_mapping`, `unsupported_projection`, `unsupported_special_file`, `adopter_snapshot_unavailable`, `repository_identity_mismatch`, `schema_upgrade_required`, `unknown_key`.

## Section 14 — v1 migration

- A v1 lock or declaration is upgrade-only input. Any command reading one fails with `schema_upgrade_required` (exit 2) and prints upgrade guidance to stderr.
- Upgrade is not a per-unit carry-forward: the adopter re-declares under v2 (adding `profile`, covering every catalog unit including the former `none` config units), authors the review, and regenerates a fresh v2 lock at one revision.

## Section 15 — `propose-lock`

- Inputs: validated declaration + review, catalog-bearing current revision, one explicit adopter snapshot.
- Removes `--unit`: a proposal rebuilds every declared unit at the one current revision. There is no partial mode.
- Rejects an incomplete declaration, a missing review decision for a changed non-mirror unit, an incomplete mirror subtree, a missing required assertion, or invalid applicability.
- Emits candidate lock YAML plus one trailing newline to stdout only; diagnostics to stderr.

## Section 16 — `verify-all`

- Reads `.aicore/adopters.yaml` (registry) from the upstream repository.
- For every registered adopter: resolves the registry repository at `default_branch`, obtains a read-only checkout (a fresh `gh repo clone` into a temp directory unless a cached checkout is supplied), and runs compliance `check` at that commit.
- Produces one verdict per adopter and a blocking aggregate: any adopter that is missing, unreachable, stale, or not at the trusted revision fails the run (exit 1).
- Registry entries carry `id`, `repository`, `default_branch`, `declaration_path`, `lock_path`, and `review_path`. Every registered adopter is mandatory — there is no `required` flag and no entry that can be exempted. No credentials or machine-local paths.

## Section 17 — Read-only guarantee

`check` and `verify-all` write nothing. `propose-lock` writes only to stdout. There is no apply, copy, merge, delete, fetch-into-adopter, or adopter Git-mutation path. Tests assert the adopter worktree and Git state are byte-identical before and after each command.
