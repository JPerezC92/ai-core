---
name: sync-aicore-adoption
description: Compare an AICore adopter repository against its accepted AICore baseline and report safe updates, local drift, and conflicts without writing adopter files. Use when a project that adopted AICore needs to review upstream core changes, generate a candidate adoption lock, or detect undeclared drift in core-owned units. Read-only — `check` writes nothing and `propose-lock` writes only to stdout.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.0.0
  domain: opencode
  dependencies:
    - PyYAML==6.0.3
---

## What I do

I compare an independent adopter repository against the AICore revision it last accepted. I reconcile the accepted and current core catalogs, project each declared unit's content in a logical-member namespace, and report orthogonal **mode**, **upstream delta**, **destination delta**, and **disposition** per unit. I never modify adopter files.

I read the accepted catalog and content from the lock's accepted Git commit, and the current catalog and content from an explicit current Git commit. I never compare against a working tree, and I never guess when history or mappings are ambiguous — I fail closed with a top-level error.

## When to use me

- A project adopted AICore and wants to know which upstream core units changed since it last accepted a baseline.
- A maintainer needs to generate a candidate `.aicore/adoption.lock.yaml` after reviewing an `.aicore/adoption.yaml` declaration.
- A project suspects an undeclared edit to a core-owned (mirrored) unit.
- You need a reproducible, read-only drift report for review or CI evidence.

Do NOT use me to perform the original installation (that is `migrate-core-to-project`), to apply or merge updates, or to author adopter-specific behavior.

## Arguments

From the request, extract:

- **upstream-repo** — path or checkout of the AICore upstream repository (required).
- **adopter-repo** — path to the adopter repository (required).
- **current-revision** — full 40-character Git commit in `upstream-repo` to compare against (required; never a branch name or short SHA for the accepted baseline).
- **declaration** — path to the adopter declaration (default `.aicore/adoption.yaml`).
- **lock** — path to the adopted lock (default `.aicore/adoption.lock.yaml`).
- **format** — `json` or `human` (default `human`).

### Argument collection form

| name | type | validation | trigger |
|---|---|---|---|
| `upstream-repo` | text | exists and is a Git repository | not provided |
| `adopter-repo` | text | exists and contains the declaration | not provided |
| `current-revision` | text | full 40-char commit in upstream | not provided for `check` |
| `format` | choice | json / human | not provided |

Use one `question` call per missing required argument. Do not add a manual "Other" option.

## Commands

| Command | Reads | Writes | Purpose |
|---|---|---|---|
| `check` | catalog, declaration, lock, both repos' Git objects | nothing | Emit mode/delta/disposition per unit as JSON or human text. |
| `propose-lock` | catalog, declaration, accepted + current Git objects | stdout only | Emit candidate lock YAML plus one trailing newline. Diagnostics go to stderr. |

`check` and `propose-lock` perform no filesystem, worktree, index, or ref mutation. There is no apply, copy, merge, delete, or fetch command. Both are implemented in [`scripts/sync_aicore_adoption.py`](scripts/sync_aicore_adoption.py).

## Comparison contract

I report four orthogonal fields with closed values:

- **mode** (from the declaration): `mirror | adapted | replacement | destination_owned`. A catalog unit absent from the declaration reports `not_declared`.
- **upstream delta**: `unchanged | added | modified | removed | not_applicable`.
- **destination delta**: `unchanged | added | modified | removed | not_applicable`.
- **disposition**: `current | adoption_available | update_available | local_drift | review_required | conflict | baseline_advance_required | retirement_available | unmanaged`.

Baseline, catalog, schema, and mapping failures are **top-level fatal errors**, never content deltas: `baseline_unavailable`, `invalid_lock`, `declaration_changed`, `catalog_changed`, `invalid_mapping`.

The exact schemas, digest framing, disposition table, and safety invariants are defined in [`references/protocol-v1.md`](references/protocol-v1.md). Reference examples: [`references/adoption-declaration-v1.yaml`](references/adoption-declaration-v1.yaml) and [`references/adoption-lock-v1.yaml`](references/adoption-lock-v1.yaml).

## Examples

### Example 1 — check an adopter against a newer core revision

> "Check whether my project has drifted from the AICore core."

Run `check` for the adopter against the requested full upstream commit. Output lists each unit with its mode, both deltas, and a disposition; mirrored units that changed only upstream report `update_available`, adapted units never report a byte convergence, and a locally edited mirror reports `review_required`.

### Example 2 — propose a lock after adopting a baseline

> "Generate the adoption lock for this declaration at the accepted upstream commit."

Run `propose-lock`. It prints candidate YAML to stdout only. The maintainer reviews it, then commits it as `.aicore/adoption.lock.yaml` in the adopter repository. `propose-lock` rejects a `mirror` unit whose accepted source and destination digests differ, and rejects any mapping into `.git/**` or the adoption control files.

## Troubleshooting

- **`check` exits with `baseline_unavailable`** — the lock's accepted commit is missing from `upstream-repo`, or it is not an ancestor of the current revision. Cause: shallow clone, rewritten history, or a wrong repository. Fix: fetch full history into `upstream-repo` and pass the correct full commit; never shorten the accepted SHA.
- **`check` exits with `invalid_lock`** — a mirrored unit's accepted source and destination digests do not match, or a unit/digest is missing. Cause: hand-edited lock or a mismatched mirror baseline. Fix: regenerate the lock with `propose-lock` and review it.
- **`check` exits with `declaration_changed`** — the declaration's raw digest differs from the accepted lock. Cause: the declaration changed after the lock was generated. Fix: review the change and regenerate the lock.
- **A unit reports `not_declared`** — the catalog has a unit the declaration does not mention. Cause: a new upstream unit, or an intentionally unmanaged unit. Fix: add a declaration row (choose a mode) or leave it reported as `unmanaged`.
- **`propose-lock` rejects a mapping** — the destination is absolute, contains `..`, escapes through a symlink, duplicates another destination, overlaps a file/tree owner, or targets `.git/**` or an adoption control file. Cause: an unsafe declaration. Fix: correct the destination mapping to a safe in-repo path.
