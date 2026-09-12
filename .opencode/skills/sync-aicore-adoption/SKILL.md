---
name: sync-aicore-adoption
description: Compare an atomic AICore adopter repository against the trusted AICore revision and report compliance without writing adopter files. Use when a project that adopted AICore must confirm every applicable core unit is current at one revision, generate a single-revision adoption lock, or verify all registered adopters. Read-only — `check` and `verify-all` write nothing and `propose-lock` writes only to stdout.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 2.0.0
  domain: opencode
  dependencies:
    - PyYAML==6.0.3
---

## What I do

I compare an independent adopter repository against the trusted AICore revision as one atomic transaction. I reconcile the accepted and current core catalogs, project each declared unit's content in a logical-member namespace, and report orthogonal **mode**, **upstream delta**, **destination delta**, and **disposition** per unit. I never modify adopter files.

I enforce atomic adoption: a lock carries exactly one accepted source commit for the whole adopter, every catalog unit must be accounted for (adopted or explicitly `not_applicable` under a machine-checked applicability rule), and `check` exits 0 only when the whole adopter is complete, current, and resolved. Partial per-unit acceptance does not exist in v2.

I am an **upstream-only AICore management tool**: run me from an AICore checkout against a runtime-supplied adopter path. I am not an adopted-content catalog unit, so I am never copied into an adopter repository. `migrate-core-to-project` is the same kind of upstream-only tool for initial installation.

I read the accepted catalog and content from the lock's single accepted source commit, and the current catalog and content from the trusted upstream revision. I read adopter destination content from exactly one explicit snapshot — a full adopter commit or the staged Git index — never the working tree. I never guess when history or mappings are ambiguous; I fail closed.

## When to use me

- A project adopted AICore and must confirm every applicable core unit is current at one revision.
- A maintainer needs to generate a single-revision `.aicore/adoption.lock.yaml` after reviewing an `.aicore/adoption.yaml` declaration and `.aicore/adoption-review.yaml`.
- A project suspects drift in a core-owned unit, a replacement member, an adapted member, or a merged config fragment.
- The user wants to verify every adopter registered in `.aicore/adopters.yaml` against the trusted revision.
- You need a reproducible, read-only compliance report for review evidence.

Do NOT use me to perform the original installation (that is `migrate-core-to-project`), to apply or merge updates, or to author adopter-specific behavior.

## Arguments

From the request, extract:

- **upstream-repo** — path or checkout of the AICore upstream repository (required).
- **adopter-repo** — path to the adopter repository (required for `check` and `propose-lock`).
- **adopter snapshot** — exactly one of:
  - **adopter-revision** — full 40-character adopter commit whose tree holds destination content; or
  - **adopter-index** — read destination content from the staged adopter index only.
- **diagnostic-revision** — full 40-character upstream commit to compare against for diagnosis (optional; never yields a compliance pass).
- **declaration** — path to the adopter declaration (default `.aicore/adoption.yaml`).
- **review** — path to the adopter review (default `.aicore/adoption-review.yaml`).
- **lock** — path to the adopted lock (default `.aicore/adoption.lock.yaml`).
- **registry** — path to the upstream registry (default `.aicore/adopters.yaml`; `verify-all` only).
- **format** — `json` or `human` (default `human`).

### Argument collection form

| name | type | validation | trigger |
|---|---|---|---|
| `upstream-repo` | text | exists and is a Git repository | not provided |
| `adopter-repo` | text | exists and contains the declaration | not provided for check/propose-lock |
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

All three perform no filesystem, worktree, index, or ref mutation of the upstream or adopter repositories. There is no apply, copy, merge, delete, or fetch-into-adopter command. They are implemented in [`scripts/sync_aicore_adoption.py`](scripts/sync_aicore_adoption.py).

### Atomic proposals

- `propose-lock` rebuilds **every** declared unit at the one current revision. There is no `--unit` and no partial mode.
- A changed non-mirror unit (`adapted`, `replacement`, `destination_owned`) requires a matching `.aicore/adoption-review.yaml` decision before the lock can be generated.
- An incomplete declaration, an invalid applicability claim, an unsatisfied required assertion, or a missing review decision fails closed.

## Comparison contract

I report four orthogonal fields with closed values:

- **mode** (from the declaration): `mirror | adapted | replacement | destination_owned | not_applicable`.
- **upstream delta**: `changed | unchanged` (a `not_applicable` unit reports `n/a`).
- **destination delta**: `changed | unchanged` (a `not_applicable` unit reports `n/a`).
- **disposition**: `current | not_applicable | update_available | local_drift | review_required | conflict | baseline_advance_required | unmanaged`.

Assertion units (`opencode-config`, `gitignore-config`) behave as `mirror` rows over a normalized assertion-status map: a missing required permission gate or ignore entry is `local_drift` (or `conflict` if upstream also changed) and can never be `current`.

## Exit contract

| Exit | Meaning |
|---:|---|
| 0 | Compliance pass: complete declaration, every declared unit `current` or `not_applicable` (or the `unmanaged` `destination_owned` steady state), all changed non-mirror units reviewed, catalog current. |
| 1 | Valid input but non-compliant (stale/`update_available`/`local_drift`/`conflict`/`review_required`/`baseline_advance_required`) or diagnostic mode. |
| 2 | Fatal: schema/identity/mapping/snapshot/trust failure, `declaration_incomplete`, `invalid_applicability`, `invalid_lock`, `invalid_declaration`, `schema_upgrade_required`. |

The trusted revision is the tip of the upstream repository's protected default branch. `--diagnostic-revision` compares against an explicit revision for diagnosis and can never exit 0.

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
