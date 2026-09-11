---
name: sync-aicore-adoption
description: Compare an AICore adopter repository against its accepted AICore baseline and report safe updates, local drift, and conflicts without writing adopter files. Use when a project that adopted AICore needs to review upstream core changes, generate a candidate adoption lock, or detect undeclared drift in core-owned units. Read-only — `check` writes nothing and `propose-lock` writes only to stdout.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.1.0
  domain: opencode
  dependencies:
    - PyYAML==6.0.3
---

## What I do

I compare an independent adopter repository against the AICore revision its lock row last accepted. I reconcile the accepted and current core catalogs, project each declared unit's content in a logical-member namespace, and report orthogonal **mode**, **upstream delta**, **destination delta**, and **disposition** per unit. I never modify adopter files.

I am an **upstream-only AICore management tool**: run me from an AICore checkout against a runtime-supplied adopter path. I am not an adopted-content catalog unit, so I am never copied into an adopter repository. `migrate-core-to-project` is the same kind of upstream-only tool for initial installation.

I read the accepted catalog and content from each lock row's accepted source commit, and the current catalog and content from an explicit current Git commit. I read adopter destination content from exactly one explicit snapshot — a full adopter commit or the staged Git index — never the working tree. I never guess when history or mappings are ambiguous; I fail closed with a top-level error.

## When to use me

- A project adopted AICore and wants to know which upstream core units changed since it last accepted a baseline.
- A maintainer needs to generate a candidate `.aicore/adoption.lock.yaml` after reviewing an `.aicore/adoption.yaml` declaration.
- A maintainer wants to accept a specific unit while preserving every other unit's prior baseline.
- A project suspects an undeclared edit to a core-owned (mirrored) unit, a replacement member, or a renamed adapted member.
- You need a reproducible, read-only drift report for review or CI evidence.

Do NOT use me to perform the original installation (that is `migrate-core-to-project`), to apply or merge updates, or to author adopter-specific behavior.

## Arguments

From the request, extract:

- **upstream-repo** — path or checkout of the AICore upstream repository (required).
- **adopter-repo** — path to the adopter repository (required).
- **current-revision** — full 40-character upstream commit to compare against (required; never a branch name or short SHA).
- **adopter snapshot** — exactly one of:
  - **adopter-revision** — full 40-character adopter commit whose tree holds destination content; or
  - **adopter-index** — read destination content from the staged adopter index only.
- **declaration** — path to the adopter declaration (default `.aicore/adoption.yaml`).
- **lock** — path to the adopted lock (default `.aicore/adoption.lock.yaml`).
- **unit** — one or more declared unit ids to accept (repeatable; `propose-lock` update proposals only).
- **format** — `json` or `human` (default `human`).

### Argument collection form

| name | type | validation | trigger |
|---|---|---|---|
| `upstream-repo` | text | exists and is a Git repository | not provided |
| `adopter-repo` | text | exists and contains the declaration | not provided |
| `current-revision` | text | full 40-char commit in upstream | not provided |
| `adopter-revision` | text | full 40-char commit in adopter, or `adopter-index` | neither snapshot provided |
| `adopter-index` | choice | boolean | neither snapshot provided |
| `unit` | text | one or more declared unit ids | update proposal without a selection |
| `format` | choice | json / human | not provided |

Use one `question` call per missing required argument. Do not add a manual "Other" option.

## Commands

| Command | Reads | Writes | Purpose |
|---|---|---|---|
| `check` | catalog at each row's accepted commit, declaration, lock, upstream Git objects, one explicit adopter snapshot | nothing | Emit mode/delta/disposition per unit as JSON or human text. |
| `propose-lock` | catalog, declaration, accepted + current Git objects, one explicit adopter snapshot | stdout only | Emit candidate lock YAML plus one trailing newline. Diagnostics go to stderr. |

`check` and `propose-lock` perform no filesystem, worktree, index, or ref mutation. There is no apply, copy, merge, delete, or fetch command. Both are implemented in [`scripts/sync_aicore_adoption.py`](scripts/sync_aicore_adoption.py).

### Initial versus update proposals

- **Initial proposal** (no existing lock): accepts every declared unit at the current catalog-bearing revision. `--unit` is rejected. The source revision must contain the catalog; a pre-catalog revision is not a valid formal baseline.
- **Update proposal** (existing lock): requires one or more repeatable `--unit` selections. Selected rows are rebuilt at the current revision; every unselected row keeps its prior accepted source commit, catalog digest, intent digest, and content digests. Adding, removing, or remapping unselected intent is rejected.
- Older, pre-catalog history is optional adopter-owned documentation. It is never stored as machine-verified lock evidence.

## Comparison contract

I report four orthogonal fields with closed values:

- **mode** (from the declaration): `mirror | adapted | replacement | destination_owned`. A catalog unit absent from the declaration reports `not_declared`.
- **upstream delta**: `unchanged | added | modified | removed | not_applicable`.
- **destination delta**: `unchanged | added | modified | removed | not_applicable`.
- **disposition**: `current | adoption_available | update_available | local_drift | review_required | conflict | baseline_advance_required | retirement_available | unmanaged`.

Replacements declare named `replacement_members` (local id, destination, `file|tree` projection). Each member carries its own accepted and current destination digest, so a split-role replacement reports which local member drifted or conflicted; it never claims byte convergence with the upstream unit.

Baseline, catalog, schema, mapping, snapshot, identity, and selection failures are **top-level fatal errors**, never content deltas: `baseline_unavailable`, `invalid_lock`, `declaration_changed`, `catalog_changed`, `invalid_mapping`, `adopter_snapshot_unavailable`, `repository_identity_mismatch`, `invalid_selection`, `unknown_key`.

The exact schemas, digest framing, disposition table, and safety invariants are defined in [`references/protocol-v1.md`](references/protocol-v1.md). Reference examples: [`references/adoption-declaration-v1.yaml`](references/adoption-declaration-v1.yaml) and [`references/adoption-lock-v1.yaml`](references/adoption-lock-v1.yaml).

## Examples

### Example 1 — check an adopter against a newer core revision

> "Check whether my project has drifted from the AICore core."

Run `check` for the adopter against the requested full upstream commit and an explicit adopter snapshot (`--adopter-revision <sha>` or `--adopter-index`). Output lists each unit with its mode, both deltas, and a disposition; mirrored units that changed only upstream report `update_available`, adapted units never report a byte convergence, a locally edited mirror reports `review_required`, and a split-role replacement reports which local member drifted.

### Example 2 — propose an initial lock after adopting a baseline

> "Generate the adoption lock for this declaration at the accepted upstream commit."

Run `propose-lock` with a catalog-bearing `--current-revision` and an explicit adopter snapshot, and no existing lock. It prints candidate YAML to stdout only. The maintainer reviews it, then commits it as `.aicore/adoption.lock.yaml`. `propose-lock` rejects a `mirror` unit whose accepted source and destination digests differ, and rejects any mapping into `.git/**` or the adoption control files.

### Example 3 — accept a single unit while preserving the rest

> "Accept the `plan-enforce` update, leave everything else where it was."

Run `propose-lock --current-revision <sha> --adopter-revision <sha> --unit plan-enforce` with the existing lock present. The selected row is rebuilt at the new revision; every unselected row is preserved with its prior accepted source commit. A later `check` still reports every current catalog unit, so pending changes remain visible.

## Troubleshooting

- **`check` exits with `baseline_unavailable`** — a lock row's accepted commit is missing from `upstream-repo`, is not a commit, is not an ancestor of the current revision, or `--current-revision` is malformed. Cause: shallow clone, rewritten history, or a wrong repository. Fix: fetch full history into `upstream-repo` and pass full commits; never shorten an accepted SHA.
- **`check` exits with `invalid_lock`** — a lock row's accepted upstream/member/unit digest does not reproduce from its accepted source commit, or a `mirror` unit's accepted source and destination digests differ. Cause: hand-edited lock or mismatched mirror baseline. Fix: regenerate the lock with `propose-lock` and review it.
- **`check` exits with `declaration_changed`** — the declaration's raw digest differs from the lock, or a declared unit's intent digest changed. Cause: the declaration changed after the lock was generated. Fix: review the change and regenerate the lock.
- **Any command exits with `adopter_snapshot_unavailable`** — no snapshot, both snapshots, a malformed revision, or a revision that is not an adopter commit. Fix: provide exactly one full adopter commit (`--adopter-revision`) or `--adopter-index`.
- **`check` exits with `repository_identity_mismatch`** — the catalog's `catalog.upstream_repository`, the declaration, and the lock disagree. Fix: correct the identity; it must be the declared AICore repository.
- **`propose-lock` exits with `invalid_selection`** — an update proposal omitted `--unit`, selected an undeclared unit, or would add, remove, or remap an unselected unit. Fix: select exactly the units whose intent or baseline you accept.
- **A unit reports `not_declared`** — the catalog has a current unit the declaration does not mention. Fix: add a declaration row (choose a mode) or leave it reported as `unmanaged`.
- **A replacement member reports `local_drift` / `review_required` / `conflict`** — the local replacement member changed independently of upstream, upstream changed while the local member did not, or both changed. Fix: review the member and select the unit when accepting a new baseline.
- **`propose-lock` rejects a mapping** — the destination is absolute, contains `..`, escapes through a snapshot symlink, duplicates another destination, overlaps a file/tree owner, or targets `.git/**` or an adoption control file. Fix: correct the destination mapping.
- **`propose-lock` rejects an initial baseline** — the accepted source revision does not contain `.aicore/core-catalog-v1.yaml`. Fix: choose a catalog-bearing revision as the formal baseline; keep older history as adopter-owned notes.
