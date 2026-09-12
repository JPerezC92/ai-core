# AICore adoption and synchronization — design

> **Status:** current
> **Scope:** Why v2 makes AICore adoption atomic, how applicability, reconciliation evidence, and the registry work, and how the reusable-core boundary is preserved. This is the design rationale; the exact contract lives in `.opencode/skills/sync-aicore-adoption/references/protocol-v2.md`.

## 1. Why v2 exists

v1 tracked a per-unit `accepted_source_commit`, so an adopter could advance one unit and leave another on an older AICore revision. `check` reported a `baseline_advance_required` unit but still exited 0, and `propose-lock --unit` deliberately preserved the stale rows. In practice an adopter could run indefinitely on old governance while every check looked green.

v2 removes that failure mode: adoption is one transaction at one trusted AICore revision. It keeps the genuinely useful parts of v1 — declaration/lock separation, explicit snapshots, deterministic digests, read-only tools — and adds the guardrails that make "fully current" verifiable.

## 2. Two operations, two upstream-only tools

| Operation | Tool | Question it answers |
|---|---|---|
| Initial adoption | `migrate-core-to-project` | Which applicable core units does this project need, and how are they enrolled? |
| Recurring synchronization | `sync-aicore-adoption` | Is the whole adopter current at the trusted revision, and what needs review? |

Both are **AICore-owned management tools**. They run from an AICore checkout against a runtime-supplied adopter path and are never copied into an adopter repository. They read one authoritative machine catalog (`.aicore/core-catalog-v2.yaml`).

## 3. One revision, one transaction

- The lock has exactly one `accepted_source_commit` and one `accepted_catalog_digest`. Per-unit source commits do not exist.
- `propose-lock` rebuilds every declared unit at that one revision; there is no `--unit`.
- `check` exits 0 only when the whole adopter is complete, current, and resolved. Every blocking disposition (`baseline_advance_required`, `update_available`, `local_drift`, `review_required`, `conflict`) exits nonzero. `unmanaged` — a `destination_owned` unit whose upstream is unchanged — is the non-blocking steady state of an intentional local fork; a `destination_owned` unit whose upstream did change is `review_required` and blocks.

This is what makes "if I update AICore, every subproject must receive the new rules" checkable: a project can no longer be partially modern.

## 4. Applicability: all applicable units, not all units

Atomic does not mean one-size-fits-all. The catalog marks each unit with machine `applicability`:

- `always` — every project must adopt it.
- `requires: [marker]` — adopted only when the marker is true (for example, ticket-only units require `ticket_system`).
- `any_of: [marker]` — adopted when any listed marker is true (for example, `bastion` for a backend stack or Python scripts).

The adopter declaration carries an explicit `profile` (`backend_stack`, `python_scripts`, `ticket_system`). The engine checks that every applicable unit is adopted and every inapplicable unit is `not_applicable`. A dev-only project therefore excludes the incident team *explicitly and auditably* rather than by silent omission, and cannot later drift because the exclusion is re-checked on every run.

## 5. Ownership modes and reconciliation evidence

Modes still let an adopter customize: `mirror` must match exactly; `adapted` may differ; `replacement` substitutes named local members; `destination_owned` is kept locally. What changes is proof: when the upstream digest of a non-mirror unit changes, the adopter must record a decision in `.aicore/adoption-review.yaml` (`applied`, `declined`, or `superseded`, with evidence). The review's raw digest is bound into the lock, so a stale review cannot silently re-baseline new upstream rules. Digests alone cannot prove a prose rule was incorporated; the review is the explicit, reviewable reconciliation.

## 6. Merged configuration is deterministic

`opencode.jsonc` permissions and `.gitignore` entries are merged fragments, not copied files, so v1 excluded them with `sync_projection: none` and never checked them. v2 replaces `none` with deterministic **assertions**: an ordered list of required substrings (comment lines ignored). A missing permission gate or ignore entry is drift and cannot be `current`. The previously invisible safety surface is now part of compliance.

## 7. The registry and `verify-all`

A per-project lock answers "is this project current?". It cannot answer "did we update every project?". `.aicore/adopters.yaml` is AICore's authoritative registry of adopter repositories, and `verify-all` checks each one against the trusted revision, blocking if any registered adopter is missing, unreachable, stale, or not current. The registry stores repository identity and adoption-file paths only — no credentials, no machine-local paths, no project source.

## 8. The one external-reference exception

AICore is a reusable, agnostic core: it must not embed any adopter's topology. The registry is the single, deliberate exception — one file whose entire purpose is to name external adopter repositories. Every other **shipped** AICore surface stays neutral (local plans and gitignored temporal output are not shipped and may reference adopters). This keeps the core reusable while giving AICore a verifiable adopter set.

## 9. Snapshots, trusted revision, and read-only design

The checker reads adopter content from exactly one explicit snapshot (a commit or the staged index), never the working tree. Compliance compares against the trusted revision — the tip of the upstream protected default branch; an explicit `--diagnostic-revision` is diagnostic only and can never pass. All commands are read-only: `check` and `verify-all` write nothing, `propose-lock` writes only to stdout. There is no apply/merge/delete path.

## 10. Migrating from v1

v1 files are retained verbatim as migration input and are never amended. Any command reading a v1 declaration or lock fails with `schema_upgrade_required` (exit 2) and prints upgrade guidance. Upgrade is not a per-unit carry-forward: the adopter re-declares under v2, authors the review, and regenerates one fresh lock at one revision. AICore contains only neutral fixtures and the management engines; every real declaration, lock, review, and registry entry is created in its owning repository.
