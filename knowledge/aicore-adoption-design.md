# AICore adoption and synchronization — design

> **Status:** current
> **Scope:** Why v2 makes AICore adoption atomic, how applicability, reconciliation evidence, and the registry work, and how the reusable-core boundary is preserved. This is the design rationale; the exact contract lives in `.opencode/skills/sync-aicore-adoption/references/protocol-v2.md`.

## 1. Why v2 exists

v1 tracked a per-unit `accepted_source_commit`, so an adopter could advance one unit and leave another on an older AICore revision. `check` reported a `baseline_advance_required` unit but still exited 0, and `propose-lock --unit` deliberately preserved the stale rows. In practice an adopter could run indefinitely on old governance while every check looked green.

v2 removes that failure mode: adoption is one transaction at one trusted AICore revision. It keeps the genuinely useful parts of v1 — declaration/lock separation, explicit snapshots, deterministic digests, and the read-only `check` / `propose-lock` / `verify-all` commands — and adds the guardrails that make "fully current" verifiable, plus one bounded write path (`apply`, Section 13).

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

The checker reads adopter content from exactly one explicit snapshot (a commit or the staged index), never the working tree. Compliance compares against the trusted revision — the tip of the upstream protected default branch; an explicit `--diagnostic-revision` is diagnostic only and can never pass.

The read-only guarantee is scoped to the three read-only commands: `check` and `verify-all` mutate no filesystem, worktree, index, or ref of the upstream or adopter repositories, and `propose-lock` writes only to stdout. `apply` (Section 13) is the single bounded write path and the only exception: it writes only adopter worktree content and the adopter lock file, never stages the Git index, creates a commit, mutates a ref, or fetches into the adopter, and it writes nothing outside its bounded write set and never deletes a pre-existing destination file. The portable-story index merge of Section 12 is computed in memory by `check` and `propose-lock`; `apply` is the only command that persists the merge, and only as part of a reviewed write.

## 10. Migrating from v1

v1 files are retained verbatim as migration input and are never amended. Any command reading a v1 declaration or lock fails with `schema_upgrade_required` (exit 2) and prints upgrade guidance. Upgrade is not a per-unit carry-forward: the adopter re-declares under v2, authors the review, and regenerates one fresh lock at one revision. AICore contains only neutral fixtures and the management engines; every real declaration, lock, review, and registry entry is created in its owning repository.

## 11. The adopter runtime identity boundary

Byte digests prove consistency, not identity separation. An adopter could pass migration, a human audit, and atomic compliance while its **active** root runtime still described AICore — the upstream core, its management tools, and its reuse guidance — as the running system. A lock can only confirm the bytes it was generated around; it cannot tell whether those bytes name the wrong project.

The boundary is therefore machine-enforced at the root runtime. The catalog's `root-runtime-spec` is a `guarded_file` unit with the closed `destination_policy: adopter_root_runtime`. Before any disposition or lock is produced, the mapped destination root is decoded as UTF-8 text and must:

- contain no case-insensitive AICore/upstream reference — `aicore`, `ai-core`, `migrate-core-to-project`, `sync-aicore-adoption`, `.aicore/`, `upstream provenance`, `upstream lineage`, or `reuse guide`; and
- carry its own `Project identity`, `Spec version`, and `Local version` markers.

A violating root can never be `current`. `propose-lock` fails closed with the stable code `policy_violation` (exit 2) and emits no candidate YAML, and `check` reports the blocking disposition `policy_violation` and exits 1 even when the root bytes already match the accepted lock. The policy is scoped to the adopter snapshot's mapped root only: AICore's own source root keeps its reuse guide, and machine provenance (`upstream_repository`, accepted commit, digests) remains authoritative in `.aicore/adoption.yaml`, `.aicore/adoption-review.yaml`, and `.aicore/adoption.lock.yaml`.

The projection set stays closed so the guard fails closed on older engines too: an engine that predates `guarded_file` rejects the catalog with `unsupported_projection` (fatal) rather than ignoring the policy and blessing a non-conforming root. Lock and declaration schemas are unchanged — `guarded_file` normalizes to the `file` projection for digest framing.

**Rollout consequence.** The guard is a compliance-tightening change: every existing adopter whose active root still carries AICore or upstream text becomes non-compliant the moment it is checked against the released guard, and stays blocking until the root is rewritten to destination-only identity and the lock is regenerated against the trusted revision. This is intentional fail-closed behavior — the previous run was compliant only because the defect could not be expressed. Downstream adopters are synchronized after the AICore release; this upstream plan neither edits an adopter repository nor registers one.

## 12. Portable stories are catalog-owned

Catalog 2.4.0 makes `.aicore/core-catalog-v2.yaml` the ownership map for portable stories:

- Three `copy` units split by applicability class deliver the portable stories as `file` members: `portable-stories-always` (`{ always: true }`), `portable-stories-ticket` (`requires: [ticket_system]`), and `portable-stories-python` (`requires: [python_scripts]`). Every member carries `collision_policy: core_wins` — the machine-declared rule for which side wins an index-row collision, replacing what used to be prose-only knowledge. Any other policy value is `invalid_mapping`.
- The `user-stories` scaffold unit stays `install_strategy: preserve` with its sole `gitkeep` member: the directory exists at a destination whether or not any story applies, and no story file is delivered through the scaffold. `user-stories/index.md` is never a catalog member — it is never mirrored wholesale — and `aicore-adoption-sync.md` remains AICore-only, never a member.
- The story projection merges core index rows into the destination's existing table: a fresh index is seeded with only the applicable core rows; inside an existing table, missing rows are inserted and differing rows are replaced only under `core_wins`; destination-only rows and every byte before and after the table are preserved byte-for-byte. Each differing `core_wins` member reports exactly `collision: path <destination>; core wins` and `collision: slug <slug>; core wins`; identical rows report nothing, and a member without `core_wins` never writes and never reports.
- Collisions are reported diagnostics — `check` lists them under `collisions` and `propose-lock` prints them to stderr — and never change a disposition or an exit code. `check` and `propose-lock` compute the merged bytes in memory only and never persist them; the merge is persisted solely by `apply` (Section 13), as part of a reviewed write, so Section 9's read-only guarantee for those three commands is unchanged.
- Unit additions are atomic-catalog events: an already-enrolled destination enrolls the three story units with its next reviewed revision like any other unit, and `not_applicable` remains the explicit, machine-checked way to exclude an inapplicable story class.

## 13. `apply`: the single bounded write path

`apply` is the fourth subcommand of `sync-aicore-adoption`, alongside the three read-only commands of Section 9, and the only one that writes. It serves exactly one situation: an already-enrolled adopter with a valid v2 declaration, review, and baseline lock that is ready to take an upstream update it is allowed to take. First enrollment stays with `migrate-core-to-project`, and `apply` is not a merge tool — non-mirror, drifted, and conflicting content stays governed by its review.

- **Selection rule.** Every declared unit is classified against its baseline lock row, and exactly the intersection `install_strategy: copy` ∧ mode `mirror` ∧ disposition `update_available` (the disposition table of protocol Section 11) is writable. `merge` and `preserve` units — including the two assertion units, both `merge` — and every non-mirror mode are never written.
- **Refusals, before any write.** A unit that needs a write `apply` can never perform is refused fail-closed: the run names every refused unit and its reason on stderr under the first refusal's code — `policy_violation`, `review_changed`, or a blocking disposition on **any** applicable unit outside the writable set, whatever its `install_strategy` or mode. That last rule covers a changed `copy` + `mirror` unit, a `merge`/`preserve` unit, and a non-`mirror` `copy` unit alike: the lock is one global document, so letting it be rewritten while a non-written unit is still blocking would silently clear that unit's pending change. Every refusal emits no report, writes nothing, and exits 2. A no-op run with no writable unit reports `apply: noop`, touches nothing, and exits 0.
- **Write, re-lock, verify.** In a refusal-free run, the writable members are staged, the portable-story index merges of Section 12 are written for writable story units (units sharing one destination index compose in declared order and each index is written once), and the lock is regenerated through the shared `propose-lock` builder under protocol Section 15's mapping rules at the one trusted target revision — written only after every content byte is staged. The `check` report then runs against that written worktree, so lock regeneration and verification read the state actually written rather than the declared snapshot.
- **Journal and best-effort restore.** Before the first mutation, `apply` records in memory every path it intends to write with its current bytes and file mode. Any failure inside the guarded region restores every journaled path from that record before the failure is surfaced; when every path verifies back, the run exits 2 under the original code (`apply_write_failed` for a write IO error). When a path cannot be put back, `apply` prints two stderr lines under `apply_restore_failed`: first the JSON recovery record `{"original":..., "paths":[...]}` naming the original failure and every path that may now be inconsistent, then the failure summary; the run exits 2 and those paths are reconciled by hand from that record. The restore is best-effort only: it claims no atomicity and no crash-transaction semantics, only journaled paths are restored (directories the run created stay in place), and `KeyboardInterrupt` and `SystemExit` propagate untouched.
- **Exit codes.** 0 for `apply: success` or `apply: noop`; 1 when content and the regenerated lock were written and are mutually consistent but the post-write `check` still reports blocking reasons; 2 for every refusal, every fatal failure, and a restore failure. The bounded surface is adopter worktree content plus the adopter lock file: `apply` never stages the Git index, never creates a commit, never mutates a ref, and never fetches into the adopter.
