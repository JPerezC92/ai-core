# AICore adoption synchronization — protocol v1

> **Scope:** The exact contract for `check` and `propose-lock`. It defines the declaration and lock schemas, the catalog relationship, the digest framing, the closed enums, the top-level fatal errors, and the read-only guarantees. The core never writes adopter files and never reads a worktree.

## Section 1 — Core / adopter split

| Artifact | Owner | Contains | Never contains |
|---|---|---|---|
| `.aicore/core-catalog-v1.yaml` | AICore upstream | unit identity, logical members, real tracked source paths, default canonical destinations, eligibility, `install_strategy`, `sync_projection` | adopter modes, destination overrides, digests |
| `.aicore/adoption.yaml` (declaration) | Adopter | upstream repository identity, unit `mode`, destination-member mapping, replacement mapping | digests, accepted commit |
| `.aicore/adoption.lock.yaml` (lock) | Generated | accepted full source commit, exact catalog and declaration digests, accepted upstream and destination digests per declared unit | intent, modes, hand-edited content |

The declaration is intent. The lock is evidence. A maintainer edits the declaration, runs `propose-lock`, reviews the candidate, and commits it as the lock.

## Section 2 — Declaration schema (`adoption-declaration-v1.yaml`)

```yaml
schema_version: 1
upstream_repository: JPerezC92/ai-core
units:
  - id: <catalog-unit-id>
    mode: mirror | adapted | destination_owned
    members:
      - id: <catalog-member-id>
        destination: <repo-relative path>
  - id: <catalog-unit-id>
    mode: replacement
    replacement_destinations:
      - <repo-relative path>
```

Rules:

- Every `id` must exist in the catalog.
- For `mirror`, `adapted`, and `destination_owned`: `members` must map every catalog member of that unit exactly once, and each `members[].id` must exist in the catalog unit.
- For `replacement`: `replacement_destinations` is a non-empty list of adopter-owned paths; the row's `id` is the replaced catalog unit, and one row may replace it with many local files. `members` is omitted.
- `sync_projection: none` units MUST NOT appear (they are installer-only).
- `destination_owned` MUST reference exactly one catalog unit whose `sync_projection` is `file` or `tree`, and provide a local destination mapping. Arbitrary local-only files are outside checker scope.
- Destinations are validated by Section 6.

## Section 3 — Lock schema (`adoption-lock-v1.yaml`)

```yaml
schema_version: 1
upstream_repository: JPerezC92/ai-core
accepted_source_commit: <40-char sha>
catalog_digest: sha256:<hex>          # raw bytes of the accepted catalog file
declaration_digest: sha256:<hex>      # raw bytes of the declaration file
units:
  - id: <catalog-unit-id>
    mode: mirror | adapted | destination_owned
    members:
      - id: <catalog-member-id>
        destination: <repo-relative path>
        accepted_upstream_digest: sha256:<hex>
        accepted_destination_digest: sha256:<hex>
  - id: <catalog-unit-id>
    mode: replacement
    replacement_destinations:
      - <repo-relative path>
    accepted_upstream_digest: sha256:<hex>
    accepted_destination_digest: not_applicable
```

- `accepted_source_commit` MUST be a full 40-character commit present in the upstream repository and an ancestor of the current revision.
- `catalog_digest` binds the catalog **at the accepted commit**, not the current catalog.
- For `mirror`, `adapted`, and `destination_owned`, `accepted_upstream_digest` and `accepted_destination_digest` are member-level digests: the accepted upstream member content and the adopter's accepted member content at lock-generation time.
- For `replacement`, `accepted_upstream_digest` is the replaced catalog unit's digest and `accepted_destination_digest` is `not_applicable` (no 1:1 member).
- The declaration digest is bound so a later declaration edit is detectable.

## Section 4 — Digest protocol (version 1)

Algorithm: `sha256`. Output form: `sha256:<lowercase hex>`.

Projection:

- A member is a `file` or a `tree`.
- A `file` member projects exactly one entry with logical path `""` (empty).
- A `tree` member projects every included file beneath its root; the logical path is the POSIX-relative path from the tree root.
- Excluded paths (never projected): any path matching `**/__pycache__/**` or `**/*.pyc`.
- Unsupported special files (fifo, socket, device) are rejected as a top-level error.

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

Comparison happens in the **logical-member namespace** after applying the declaration mapping, so a renamed one-to-one member can converge. One-to-many replacements detect independent upstream/destination deltas but cannot claim byte convergence (destination delta is `not_applicable`).

Golden vectors (self-check for the implementation):

| Fixture | Entry set | Digest |
|---|---|---|
| file, path `""`, mode `100644`, content `hello\n` | 1 entry | `sha256:cf41078b082e3740168bd7ad534ba1b70b12489c7ab43c6fb53743b0f3527887` |
| tree, `a.txt` `100644` `hello\n` + `sub/b.txt` `100755` `bye\n` | 2 entries | `sha256:4b49b94b71240c8933269684873b2eecf0f53de69ed8ded25eda1e172d3637d7` |

## Section 5 — Comparison

Read the accepted catalog and content from `accepted_source_commit`. Read the current catalog and content from the explicit current revision. Reconcile the two catalogs by stable unit/member IDs:

- `upstream delta` = `added` (in current only), `removed` (accepted only), `modified` (digest differs), `unchanged`.
- `destination delta` = `added` (destination present, no accepted destination digest), `removed` (acceptable destination absent now), `modified`, `unchanged`, `not_applicable` (replacement with no 1:1 member).
- `mode` = the declaration mode, or `not_declared` when the unit is absent from the declaration.
- `disposition` is derived from mode + both deltas per Section 7.

## Section 6 — Mapping validation (fail closed)

Reject, as an `invalid_mapping` top-level error:

- absolute destination paths;
- any `..` segment;
- destinations that escape the repository root through a symlink;
- duplicate destinations across members;
- overlapping ownership (one member's destination is a prefix of another file/tree destination in a conflicting way);
- any destination under `.git/**`, `.aicore/adoption.yaml`, or `.aicore/adoption.lock.yaml`;
- a tree projection whose included paths would contain any control path above.

## Section 7 — Disposition table

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
| replacement | any | any | `review_required` |
| destination_owned | unchanged | unchanged | `unmanaged` |
| destination_owned | modified/added/removed | any | `retirement_available` |
| not_declared | added | n/a | `adoption_available` |
| not_declared | removed | n/a | `retirement_available` |
| any | accepted commit behind current | any | `baseline_advance_required` (informational) |

## Section 8 — Top-level fatal errors

These abort the whole run; they are never per-unit deltas:

| Error | Condition |
|---|---|
| `baseline_unavailable` | accepted commit missing, not a commit, or not an ancestor of the current revision |
| `invalid_lock` | lock schema invalid, or a `mirror` unit's accepted source/destination digests differ |
| `declaration_changed` | declaration raw digest differs from `declaration_digest` |
| `catalog_changed` | accepted catalog raw digest differs from `catalog_digest` |
| `invalid_mapping` | any Section 6 rejection |
| `unsupported_projection` | a declaration references a `sync_projection: none` unit or an unknown projection |
| `unsupported_special_file` | a projected path is not regular, executable, or symlink |

## Section 9 — `propose-lock` contract

- Reads the validated declaration, the accepted commit, and the current revision.
- Enforces the mirror invariant: a `mirror` unit is rejected unless its accepted logical source and destination digests match.
- Emits candidate lock YAML plus exactly one trailing newline to **stdout**. Diagnostics go to **stderr**.
- Performs no filesystem, worktree, index, ref, or network mutation.

## Section 10 — Read-only guarantee

`check` writes nothing. `propose-lock` writes only to stdout. There is no apply, copy, merge, delete, fetch, or Git-mutation path in the skill. Tests assert the whole adopter worktree and Git state are byte-identical before and after each command.
