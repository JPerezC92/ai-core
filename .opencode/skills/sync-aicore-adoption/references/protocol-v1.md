# AICore adoption synchronization — protocol v1

> **Scope:** The exact contract for `check` and `propose-lock`. It defines the declaration and lock schemas, the catalog relationship, the digest framing, the explicit adopter snapshot, the closed enums, the top-level fatal errors, and the read-only guarantees. The core never writes adopter files and never reads an adopter worktree.

## Section 1 — Core / adopter split

| Artifact | Owner | Contains | Never contains |
|---|---|---|---|
| `.aicore/core-catalog-v1.yaml` | AICore upstream | `catalog.upstream_repository`, unit identity, logical members, real tracked source paths, default canonical destinations, eligibility, `install_strategy`, `sync_projection` | adopter modes, destination overrides, digests |
| `.aicore/adoption.yaml` (declaration) | Adopter | upstream repository identity, unit `mode`, destination-member mapping, replacement-member mapping | digests, accepted commit |
| `.aicore/adoption.lock.yaml` (lock) | Generated | one row per declared unit with its accepted source commit, accepted catalog digest, unit intent digest, and accepted upstream and destination digests; one top-level declaration digest | intent, modes, hand-edited content |

The declaration is intent. The lock is evidence. A maintainer edits the declaration, runs `propose-lock`, reviews the candidate, and commits it as the lock. Removing a unit from the declaration expresses intent to retire it; the corresponding lock row is omitted from the candidate only when that unit's locked id is explicitly selected in an update proposal.

The AICore management tools (`migrate-core-to-project` and `sync-aicore-adoption`) are upstream-only operator tools, invoked from an AICore checkout against runtime-supplied adopter paths. Neither is an adopted-content catalog unit, and neither the migration tool nor the catalog itself is copied as adopted content.

## Section 2 — Declaration schema (`adoption-declaration-v1.yaml`)

```yaml
schema_version: 1
upstream_repository: <owner/repo>
units:
  - id: <catalog-unit-id>
    mode: mirror | adapted | destination_owned
    members:
      - id: <catalog-member-id>
        destination: <repo-relative path>
  - id: <catalog-unit-id>
    mode: replacement
    replacement_members:
      - id: <adopter-local-id>
        destination: <repo-relative path>
        projection: file | tree
```

Rules:

- `upstream_repository` must equal the catalog's `catalog.upstream_repository` and the lock's `upstream_repository`.
- Every unit `id` must exist in the catalog.
- For `mirror`, `adapted`, and `destination_owned`: `members` must map every catalog member of that unit exactly once, and each `members[].id` must exist in the catalog unit.
- For `replacement`: `replacement_members` is a non-empty list of adopter-owned members; each has a unique adopter-local `id`, a repository-relative `destination`, and an explicit `projection` (`file` or `tree`). `members` is omitted. A replacement never claims byte convergence with the upstream unit.
- `sync_projection: none` units MUST NOT appear (they are installer-only).
- `destination_owned` MUST reference exactly one catalog unit whose `sync_projection` is `file` or `tree`, and provide a local destination mapping. Arbitrary local-only files are outside checker scope.
- Unknown keys for the schema version are rejected.
- Destinations are validated by Section 8.

## Section 3 — Lock schema (`adoption-lock-v1.yaml`)

```yaml
schema_version: 1
upstream_repository: <owner/repo>
declaration_digest: sha256:<hex>      # raw bytes of the declaration file
units:
  - id: <catalog-unit-id>
    mode: mirror | adapted | destination_owned
    accepted_source_commit: <40-char sha>
    accepted_catalog_digest: sha256:<hex>   # catalog at the accepted source commit
    declaration_unit_digest: sha256:<hex>    # deterministic intent digest of this unit
    accepted_upstream_digest: sha256:<hex>   # unit digest at the accepted source commit
    members:
      - id: <catalog-member-id>
        destination: <repo-relative path>
        accepted_upstream_digest: sha256:<hex>
        accepted_destination_digest: sha256:<hex>
  - id: <catalog-unit-id>
    mode: replacement
    accepted_source_commit: <40-char sha>
    accepted_catalog_digest: sha256:<hex>
    declaration_unit_digest: sha256:<hex>
    accepted_upstream_digest: sha256:<hex>   # digest of the replaced catalog unit
    replacement_members:
      - id: <adopter-local-id>
        destination: <repo-relative path>
        projection: file | tree
        accepted_destination_digest: sha256:<hex>
```

- `accepted_source_commit` MUST be a full 40-character commit present in the upstream repository and an ancestor of the current revision.
- `accepted_catalog_digest` binds the catalog **at that row's accepted source commit**, not the current catalog.
- `declaration_unit_digest` binds the exact declaration intent for this unit (mode plus normalized member/replacement-member mapping), so an intent change is detectable per unit.
- `accepted_upstream_digest` is independently reproduced from the catalog at the row's accepted source commit; any mismatch is `invalid_lock`.
- For `mirror`, `adapted`, and `destination_owned`, each member's `accepted_upstream_digest` and `accepted_destination_digest` are member-level digests; the accepted upstream digest is also independently reproduced from the row's accepted source commit.
- For `replacement`, `accepted_upstream_digest` is the replaced catalog unit's digest and each replacement member carries its own `accepted_destination_digest`; there is no 1:1 convergence claim.
- Unknown keys for the schema version are rejected.

## Section 4 — Digest protocol (version 1)

Algorithm: `sha256`. Output form: `sha256:<lowercase hex>`.

Projection:

- A member is a `file` or a `tree`.
- A `file` member projects exactly one entry with logical path `""` (empty).
- A `tree` member projects every included file beneath its root; the logical path is the POSIX-relative path from the tree root.
- Excluded paths (never projected): any path matching `**/__pycache__/**` or `**/*.pyc`.
- Unsupported special files (fifo, socket, device) are rejected as a top-level error. Gitlink/submodule entries are unsupported.

Framing (bytes, UTF-8 except mode ASCII):

```
for each entry, in ascending byte order of logical path:
    b"entry\n"
    b"path:"   + path_bytes     + b"\n"
    b"mode:"   + mode_bytes     + b"\n"      # 100644 | 100755 | 120000
    b"size:"   + decimal_bytes  + b"\n"      # len(content)
    b"content:"+ content        + b"\n"
```

- `mode` normalizes to `100644` (regular), `100755` (executable), or `120000` (symlink).
- For a symlink, `content` is the link target bytes.
- For a regular/executable file, `content` is the raw file bytes. Line endings are preserved exactly; no normalization.

Member digest = `sha256` over the framing of that member's entries.

Unit digest = `sha256` over:

```
for each member, in catalog member order:
    b"member\n"
    b"id:"     + member_id_bytes + b"\n"
    b"digest:" + member_digest_bytes + b"\n"
```

Declaration-unit intent digest = `sha256` over:

```
b"mode:" + mode_bytes + b"\n"
for each member, in ascending id byte order:
    b"member\n"
    b"id:"          + member_id_bytes + b"\n"
    b"destination:" + normalized_destination_bytes + b"\n"
for each replacement member, in ascending id byte order:
    b"replacement\n"
    b"id:"          + member_id_bytes + b"\n"
    b"destination:" + normalized_destination_bytes + b"\n"
    b"projection:"  + projection_bytes + b"\n"
```

Comparison happens in the **logical-member namespace** after applying the declaration mapping, so a renamed one-to-one member can converge. One-to-many replacements report each member's independent destination delta and cannot claim byte convergence with the upstream unit.

Golden vectors (self-check for the implementation):

| Fixture | Entry set | Digest |
|---|---|---|
| file, path `""`, mode `100644`, content `hello\n` | 1 entry | `sha256:cf41078b082e3740168bd7ad534ba1b70b12489c7ab43c6fb53743b0f3527887` |
| tree, `a.txt` `100644` `hello\n` + `sub/b.txt` `100755` `bye\n` | 2 entries | `sha256:4b49b94b71240c8933269684873b2eecf0f53de69ed8ded25eda1e172d3637d7` |

## Section 5 — Explicit adopter snapshot

`check` and `propose-lock` read adopter destination content from exactly one explicit, mutually exclusive source:

- `--adopter-revision <40-char sha>` — read destination content from that full adopter commit's tree.
- `--adopter-index` — read destination content from the staged Git index only.

Rules:

- Exactly one is required. Missing, ambiguous (both supplied), malformed, or non-commit revision inputs are rejected as `adopter_snapshot_unavailable`.
- No command reads the adopter worktree. An unstaged worktree edit is invisible to `--adopter-index`; an untracked file is invisible to both.
- No command writes the worktree, index, refs, object database, or network state.

The declaration and lock are supplied to the command as explicit file paths and are not destination content.

## Section 6 — Repository identity

The catalog's `catalog.upstream_repository`, the declaration's `upstream_repository`, and the lock's `upstream_repository` MUST all be equal, and the catalog read at every accepted source commit MUST match that identity. A mismatch is a `repository_identity_mismatch` top-level error before any report or lock YAML is produced.

## Section 7 — Comparison

For each declared unit, read the accepted catalog and content from that lock row's `accepted_source_commit`. Read the current catalog and content from the explicit current revision. Reconcile by stable unit/member IDs:

- `upstream delta` = `added` (in current only), `removed` (accepted only), `modified` (digest differs), `unchanged`.
- `destination delta` = `added` (destination present, no accepted destination digest), `removed` (accepted destination absent now), `modified`, `unchanged`, `not_applicable`.
- `mode` = the declaration mode, or `not_declared` when the unit is absent from the declaration.
- A `not_declared` current catalog unit is reported with `upstream_delta: added` and disposition `adoption_available`, so pending upstream units remain visible.
- `disposition` is derived from mode + both deltas per Section 9.

## Section 8 — Mapping validation (fail closed)

Reject, as an `invalid_mapping` top-level error:

- absolute destination paths;
- any `..` segment;
- destinations that escape the repository root through a symlink recorded in the adopter snapshot;
- duplicate destinations across members;
- overlapping ownership (one member's destination is a prefix of another file/tree destination in a conflicting way);
- any destination under `.git/**`, `.aicore/adoption.yaml`, or `.aicore/adoption.lock.yaml`;
- a tree projection whose included paths would contain any control path above;
- duplicate replacement-member local ids.

## Section 9 — Disposition table

| mode | upstream delta | destination delta | disposition |
|---|---|---|---|
| mirror | unchanged | unchanged | `current` |
| mirror | modified/added | unchanged | `update_available` |
| mirror | unchanged | modified/removed | `local_drift` |
| mirror | modified/added | modified/removed | `conflict` |
| adapted | unchanged | unchanged | `current` |
| adapted | modified/added | unchanged | `update_available` |
| adapted | unchanged | modified/removed | `local_drift` |
| adapted | modified/added | modified/removed | `review_required` |
| replacement | removed | any | `retirement_available` |
| replacement | unchanged | unchanged | `current` |
| replacement | unchanged | modified/added/removed | `local_drift` |
| replacement | modified/added | unchanged | `review_required` |
| replacement | modified/added | modified/added/removed | `conflict` |
| destination_owned | unchanged | unchanged | `unmanaged` |
| destination_owned | modified/added/removed | any | `retirement_available` |
| not_declared | n/a (current preset) | n/a | `adoption_available` |
| any | accepted commit behind current | any | `baseline_advance_required` when the base disposition is `current` |

A replacement destination delta is the aggregate of its replacement-member deltas; `replacement` never reports `update_available`, because it never claims byte convergence with the upstream unit.

## Section 10 — Top-level fatal errors

These abort the whole run; they are never per-unit deltas:

| Error | Condition |
|---|---|
| `baseline_unavailable` | accepted commit missing, not a commit, not an ancestor of the current revision, or a malformed current revision |
| `invalid_lock` | lock schema invalid; a `mirror` member's accepted source/destination digests differ; or an accepted upstream/member/unit digest does not reproduce from its row's accepted source commit |
| `declaration_changed` | declaration raw digest differs from `declaration_digest` |
| `catalog_changed` | catalog missing at a required commit, or a catalog raw digest differs from the row's accepted catalog digest |
| `invalid_mapping` | any Section 8 rejection |
| `unsupported_projection` | a declaration references a `sync_projection: none` unit or an unknown projection |
| `unsupported_special_file` | a projected path is not regular, executable, or symlink |
| `adopter_snapshot_unavailable` | missing, ambiguous, malformed, or non-commit adopter snapshot input |
| `repository_identity_mismatch` | catalog/declaration/lock `upstream_repository` disagree |
| `invalid_selection` | an update proposal has no `--unit`, selects an id absent from both the declaration and the existing lock, or would add/remove/remap unselected intent |
| `unknown_key` | a document contains a key outside its schema version's closed key set |

## Section 11 — Formal bootstrap contract

- The first lock is accepted only from a catalog-bearing source revision and an explicit adopter snapshot. If the catalog is missing at the accepted source, the run fails with `catalog_changed`; a formal accepted source without its catalog is always a fatal error.
- An initial `propose-lock` (no existing lock) builds a row for every declared unit at the current catalog-bearing revision and rejects any `--unit` selection.
- An existing pre-catalog adopter history is **optional adopter-owned documentation**. It is never represented as a machine-verified lock field, and the protocol does not fabricate a catalog over older revisions.
- An update `propose-lock` requires the existing lock plus one or more explicit repeatable `--unit` selections. A selected id is valid when it is currently declared or present in the existing lock (`declared_ids ∪ locked_ids`); any id in neither set is `invalid_selection`. The four outcomes are: rebuild a selected declared+locked row, add a selected declared-only row, retire a selected locked-only row by omitting it from the candidate YAML, and preserve every unselected row byte-for-byte with its prior per-unit accepted source commit, catalog digest, intent digest, and content digests. A lock row removed from the declaration must be selected to retire it; an unselected removed row, or added, removed, or remapped unselected intent, is rejected as `invalid_selection`. Retirement requires no current-catalog row and changes only the stdout candidate.
- A later `check` still reports every current catalog unit, so pending changes remain visible after another unit is accepted. A retired unit that still exists in the current catalog is reported as `not_declared` with upstream delta `added` and disposition `adoption_available`.

## Section 12 — `propose-lock` contract

- Reads the validated declaration, the current catalog-bearing revision, and the explicit adopter snapshot.
- Enforces the mirror invariant: a `mirror` unit is rejected unless its accepted logical source and destination digests match.
- An initial proposal (no existing lock) accepts every declared unit at the current catalog-bearing revision and rejects any `--unit` selection.
- An update proposal validates each `--unit` id against the union of current declaration ids and existing lock ids. A selected declared+locked row is rebuilt, a selected declared-only row is added, and a selected locked-only row is retired by omitting it from the candidate YAML; an id in neither set is `invalid_selection`.
- Emits candidate lock YAML plus exactly one trailing newline to **stdout**. Diagnostics go to **stderr**.
- Performs no filesystem, worktree, index, ref, or network mutation. A retirement changes candidate YAML only; the prior lock file is never edited in place.

## Section 13 — Read-only guarantee

`check` writes nothing. `propose-lock` writes only to stdout. There is no apply, copy, merge, delete, fetch, or Git-mutation path in the skill. Tests assert the whole adopter worktree and Git state are byte-identical before and after each command, and that the adopter snapshot source is explicit. A retirement proposal is stdout-only candidate evidence: it omits the retired row from the emitted YAML and never deletes, edits, or tombstones the prior lock row in place.
