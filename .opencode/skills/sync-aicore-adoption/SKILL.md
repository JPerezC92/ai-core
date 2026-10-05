---
name: sync-aicore-adoption
description: Read-only adoption evidence and candidate-lock management. Use when assessing an atomic AICore adoption, preparing a complete candidate lock after a reviewed reconciliation, or verifying the registered adopters.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 3.2.1
  domain: opencode
  dependencies:
    - PyYAML==6.0.3
---

## What I do

I provide evidence for an atomic AICore adoption. `check` compares one explicit adopter snapshot with the accepted and trusted upstream revisions. `propose-lock` emits a complete candidate lock to stdout. `verify-all` checks every registered adopter. I never edit an adopter, stage content, or accept a lock. `verify-all` may clone into and remove only a temporary directory it creates; a supplied checkout stays unchanged.

The skills and the destination owner perform reconciliation. The catalog identifies units, mappings, modes, applicability, and accepted digests; it does not replace reading content or deciding semantics. An adopted revision is complete only when every catalog unit is adopted or explicitly `not_applicable` under the declared profile.

## Commands

| Command | Writes | Purpose |
|---|---|---|
| `check` | nothing | Report mode, upstream/destination deltas, catalog transition, and compliance for one explicit adopter revision or staged index. |
| `propose-lock` | stdout only | Emit one complete candidate v2 lock for the supplied reviewed snapshot. |
| `verify-all` | supplied checkout unchanged | Compliance check for every registry adopter. A missing cache may clone into and remove a verifier-owned temporary directory. |

`apply` was removed in 3.0.0. It is not an alias, compatibility command, or write path. An `apply` invocation must fail through normal CLI argument handling without writes.

## Reviewed reconciliation workflow

Follow [`references/protocol-v2.md`](references/protocol-v2.md) §4–§5. Do not use another order. Diagnosis is not permission to migrate or sync.

1. **Inventory.** Run `check` against the accepted explicit snapshot. Read its accepted/target catalog transition. When an ordinary non-mirror unit retires, keep one lock-only historical row with `retired: true`. The target declaration contains no retired row. Retirement never authorizes destination deletion or upstream-ownership restoration.
2. **Controlled clean start.** Abort before any destination change when work is unsaved, uncommitted, or cleanliness cannot be confirmed. Do not save, commit, stash, clean, or resume. There is no backup or rollback.
3. **External preparation and review.** Prepare the complete result outside the destination, including config, dependencies, and consistency corrections. Read every protected document. Ordinary protected mirror is byte-identical content only. An assertion unit is `mirror` over ordered assertion presence. Mandatory conflicts, including unchanged local and cross-file rules, require a notice that cites both rules, the winner, and the result change. Python does not judge that prose.
4. **Freeze, then write.** Recheck the complete output set. An existing ignored occupant blocks; an ignore rule without a file does not. Freeze approval, write controls, then reviewed content, and stage exact approved paths only.
5. **External candidate.** Run `python3 -B` with the absolute engine and catalog. Save stdout outside the destination, never at `<target>/.aicore/adoption.lock.candidate.yaml`. Check that snapshot. After exit 0, install and stage only the accepted lock, then final-check. Failure stops and reports. Do not roll back.

### Runtime-spec lineage review

For `AGENTS.md` and derived runtime specs, apply the root runtime spec's `## Project extensions` → `### Reuse guide (adopting this core)` version-governance clause during the three-version review. Show actual before/after ancestor spec versions and destination `Local version` / `local-version` values. An upstream-only synchronization preserves the destination local version. A destination-local rule change receives a reviewed SemVer bump and a recorded rationale (major authority/safety break, minor new enforceable capability, patch compatible correction). The independent model review reads every complete previous-core, target-core, destination-before, and result document and judges incorporation, mandatory precedence over a conflicting extension, preservation of a compatible local business rule, and the bump rationale; Python only binds reviewed bytes, layout framing, and the `verified_layout` attestation. Never infer that bump in Python, and never treat a token or a digest as that review; existing runtime-spec review judges it. Source ancestor files never gain destination local-version markers.

### Test-runner metadata

The declaration records the destination's reviewed whole-project suite in a `test_runner` block required for acceptance — present either as `commands` (one or more literal whole-suite commands), `executor` (the designated agent), `scope: whole_project`, `reviewer`, and `evidence`, or as `no_tests: true` with nonempty `reviewer` and `evidence` and no `commands`/`executor`/`scope`. An absent block is a `policy_violation`; a wrong-typed or unknown key is `invalid_declaration`.

`check` and `propose-lock` validate only `agent.<executor>.permission.bash` in the adopter's `opencode.jsonc`, evaluating the nominated executor's rules in document order with OpenCode `*`/`?` wildcard semantics and last-match-wins: every approved command must end as a literal `allow`, so a later matching `deny` or `ask` makes an earlier literal `allow` non-executable. A blanket `"allow"`, a broad wildcard allow that is not itself an approved command literal, an unapproved or changed test-command allow, malformed JSONC, or a missing approved command fails; unrelated agents' and top-level/global grants are never inspected, and AICore's UV command is never imposed on another project. Command text does not prove suite coverage — the destination's `reviewer` and `evidence` attest it, and installation approval stays separate.

## Inputs and safety

`check` and `propose-lock` require a declaration and exactly one of `--adopter-revision <40-char SHA>` or `--adopter-index`; `--upstream-repo` defaults to `.` and `--catalog` defaults to `.aicore/core-catalog-v2.yaml`; `--review` is optional and omission supplies an empty review. `check` also requires `--lock`. `propose-lock --lock` means an existing update baseline and fails if that supplied path is absent. First enrollment omits `--lock` and uses an explicit null-baseline transition with complete fresh evidence.

The trusted revision is an approved source-refresh of the protected upstream default-branch tip. A local origin or main ref alone is not that evidence. The accepted catalog is read at the lock's accepted commit and the target catalog at that trusted commit. Missing trusted baseline data blocks; an absent update lock is never silently treated as first enrollment.

From a destination, invoke `python3 -B` on the absolute script path in an AICore checkout. Always pass `--catalog` as the absolute path of the reviewed checkout catalog. Controls are disk paths; adopted content is the explicit commit or index. Pass explicit `--upstream-repo`, `--adopter-revision` or `--adopter-index`, `--declaration`, `--review`, and `--lock` when they are not the documented defaults. The engine selects `refs/remotes/origin/main`, then `refs/heads/main`; that SHA must equal the reviewed source. Do not describe an unrefreshed local branch as live remote truth. Do not add a destination updater package. Local operator notes belong in comments on the existing `.aicore` controls; the active root stays destination-only.

## Exit contract

| Exit | Meaning |
|---:|---|
| 0 | `check`/`verify-all` compliant, or `propose-lock` emitted a candidate. |
| 1 | Valid but non-compliant state. |
| 2 | Invalid schema, identity, mapping, snapshot, review, or trusted baseline. |

Use [`references/protocol-v2.md`](references/protocol-v2.md) for exact schema and digest framing. `migrate-core-to-project` owns first-enrollment ordering; this skill remains upstream-only and is never an adopted catalog unit.

## Examples

- Assess one adopter: invoke the absolute manager script with `check`, an explicit adopter snapshot, and the accepted lock. Exit 0 is compliance for that snapshot, not proof that a notice was delivered.
- Prepare a candidate: after frozen approval and exact-path staging, invoke `python3 -B` `propose-lock` on the same explicit snapshot and save stdout outside the destination.

## Troubleshooting

- **Exit 2 on a protected unit:** the declaration uses `replacement` or `destination_owned`, or the review lacks an applied `verified_layout: two-section-v1` decision. Fix: use `mirror`, `adapted`, or machine-valid `not_applicable`, and record the attestation only after the three-surface review.
- **A local mandatory edit is reported as drift:** that is ownership drift, not an adaptation to preserve. Fix: restore the selected core's mandatory bytes and keep the compatible change in project extensions.
