# AICore adoption synchronization — protocol v2

> **Status:** current
> **Scope:** Schema-v2 evidence contract for `check`, `propose-lock`, and `verify-all`. `apply` is removed. Existing-repository reads do not mutate; `verify-all` may use its own temporary clone. Destination edits are owner operations. There is no backup or rollback.

## 1. Atomic adoption and ownership

The upstream catalog owns unit identity, members, applicability, strategy, projections, and assertions. The adopter declaration owns profile, mode, and destination mappings. The review owns human reconciliation decisions. The generated lock owns one accepted source commit and digest evidence. Every catalog unit is declared once as an applicable mode or machine-justified `not_applicable`; partial acceptance is forbidden.

The accepted catalog is read at `accepted_source_commit`; the target catalog is read at the trusted revision. That trusted revision is an approved refresh of the protected upstream default-branch tip; a local origin or main ref alone is not that evidence. Both catalogs remain distinct. Added, retired, member, applicability, and effective-mode changes are reported. Retirement never authorizes deletion of destination content.

## 2. Declaration and lock framing

`schema_version` remains `2`.

- `mirror`, `adapted`, and `destination_owned` map every ordinary catalog member through `members`.
- `replacement` has only `replacement_members`, with `id`, `destination`, and `file|tree` projection.
- `not_applicable` has no members.
- Assertion declarations have no members and support only `mirror` or `not_applicable`. An applicable assertion lock row is `mirror` with exactly one `members` entry `id: assertions`; a not-applicable assertion row has no members.
- A lock has one `accepted_source_commit`, `accepted_catalog_digest`, declaration digest, review digest, accepted snapshot digest, and a row for every unit. Per-unit source commits and incompatible member framing are invalid.

### Retired lock-only descriptor

The declaration is target-catalog-only: a retired unit is absent from it. For an ordinary retired non-mirror unit, the lock retains exactly one historical row marked `retired: true`. Its predecessor mapping remains in that row; ordinary retained members explicitly carry `projection: file|tree`, while replacement members retain their existing projection. The row's mapping and reviewed destination facts participate in the normal lock and accepted-snapshot digests. It is historical verification evidence only: retirement neither deletes destination content nor restores upstream ownership. Historical rows carry forward across later locks until a future protocol explicitly supersedes their retention.

Digest framing remains v2: SHA-256 file/tree member framing, ordered unit-member framing (including retained retired rows), declaration mapping framing, ordered assertion-list framing, and ordered assertion-status framing. The accepted snapshot digest binds declaration digest, review digest, and accepted destination member facts, including retained retired-row facts.

## 3. Review schema and fresh transition bindings

Historical accepted v2 review documents remain readable. A transition-bound fresh acceptance adds this optional existing-document block:

```yaml
transition:
  baseline_lock_digest: sha256:<hex> # null only for first enrollment
  target_source_commit: <40-char SHA>
  declaration_digest: sha256:<hex>
decisions:
  - unit: <every applicable protected unit, including mirrors>
    decision: applied
    verified_layout: two-section-v1
    reviewer: <role>
    evidence: <nonempty note>
    reviewed_upstream_digest: sha256:<hex>
    reviewed_destination_digest: sha256:<hex>
```

For fresh acceptance the three transition fields and every required decision binding are mandatory. The baseline digest must identify the supplied existing lock: the lock's `accepted_source_commit` is pinned to a full 40-character lowercase SHA (a movable revspec such as `HEAD` fails `invalid_lock`), and `propose-lock` reads each control file exactly once so `baseline_lock_digest` is computed from the same bytes that produced the parsed baseline rows. A supplied missing update lock fails, while first enrollment explicitly omits `--lock` and uses null baseline. Changing the baseline, target, declaration, reviewed source, or prepared destination result invalidates authorization. Duplicate and unknown decisions fail. `applied`, `declined`, and `superseded` are all evidence-bearing choices. A historical unit-only decision remains readable but cannot clear a fresh transition.

`check` validates an accepted transition against the lock's accepted source, declaration digest, and locked destination member facts; it uses a live snapshot only for current policy and newer-delta classification.

## 4. Actors and command boundary

Three actors stay separate. A passing `check`, or a test-local driver, is not permission to mutate a destination.

- **Engine:** `check` and `propose-lock` read an explicit local content snapshot and the supplied control files, then emit evidence. Adopted content comes from the explicit commit or staged index. Declaration, review, and lock bytes are read from their disk paths. Do not claim every input comes from HEAD. These commands do not edit, stage, commit, fetch, or clean the selected existing repository. Missing objects fail. The invocation must be the installed trusted Git with `--no-optional-locks`, an empty command-local `core.fsmonitor` value so a repository hook path is not executed, hooks and configured read helpers disabled, inherited repository/index/config/trace redirection removed, and no lazy fetch. `false` is not used because Git can execute it as a hook name. This is not an arbitrary host sandbox.
- **Verifier clone:** `verify-all` may use the network, clone into a temporary directory it creates, and remove only that directory. A supplied checkout is read and is never fetched, checked out, or cleaned. `--checkouts-root` does not promise offline verification: a missing cache entry may still clone. That temporary activity is not an existing-repository write and not a publisher.
- **Workflow:** the model and Herald 📯 (Release Manager) confirm cleanliness and may edit or `git add` only approved adoption paths. That add updates the index and object storage and may apply repository clean filters. Unknown helper or transform effects block. Do not edit owner Git configuration or force normalization. A test-local driver demonstrates this contract only; it is not a shipping mutation gate.

| Command | Existing repository | Other effect |
|---|---|---|
| `check` | no mutation | none |
| `propose-lock` | no mutation | stdout only |
| `verify-all` | supplied checkout unchanged | may clone and remove its own temporary directory |

`apply` is not a protocol command. It must be rejected as an unrecognized CLI command without writes. No engine command edits content, stages, commits, stashes, resets, restores, or accepts a lock.

## 5. One operator sequence

Migration and sync abort before any destination change when the destination has unsaved or uncommitted work, or when cleanliness cannot be confirmed. The operation does not save, commit, stash, reset, clean, or resume. There is no backup, checkpoint, or rollback. If application fails after a clean start, stop and report the current state. Do not restore or delete applied files automatically.

This is the only sequence. Skills reference it; they do not publish a second order.

1. **Controlled preflight.** Require a committed HEAD, saved-editor evidence, and no assume-unchanged or skip-worktree entries. `status --porcelain=v2 -z --untracked-files=all --ignore-submodules=none` must succeed with empty stdout. Resolve `MERGE_HEAD`, `CHERRY_PICK_HEAD`, `REVERT_HEAD`, `rebase-merge`, `rebase-apply`, and `sequencer` with `rev-parse --git-path`, relative to the destination. A linked-worktree gitfile is supported layout, not dirtiness. A clean bisect is not unsaved work and is not banned. Unknown editor evidence, index flags, or command results abort. Read-only failure is not cleanliness.
2. **Pin inputs.** Pin `refs/remotes/origin/main`, then `refs/heads/main` only if the first ref is absent, the absolute catalog whose disk bytes match that commit, and the reviewed engine. Source refresh belongs to a separate approved upstream checkout.
3. **External full preparation.** Prepare extensions, dependency union, config, consistency corrections, absent register headers, retained records, and the story-index merge outside the destination. Mandatory bytes stay exact. Do not import source project extensions or history. Do not install packages or build an application.
4. **Complete-output collision and recheck.** The intended write set is every adopted, config, manifest, and index path plus `.aicore/adoption.yaml`, `.aicore/adoption-review.yaml`, and `.aicore/adoption.lock.yaml`. An existing ignored or untracked occupant of any such path blocks. An ignore rule with no existing file is not unsaved work, and absence does not authorize `git add -f`. Recheck cleanliness immediately before the first write. New work aborts and is not restored.
5. **Freeze approval.** Record declaration, review, and prepared-result digests before the first destination write. Protected units, including mirrors, need an applied `verified_layout: two-section-v1` decision after the model reads every complete document. Assertion units are `mirror` over ordered assertion presence, not whole-file identity. The initial baseline is null. An update baseline is the predecessor lock, not the candidate hash.
6. **Write controls, then reviewed content.** Controls are written before adopted content. The story index is an approved auxiliary file, not a catalog member. Create an approved absent register only after controls exist. Never overwrite an existing register.
7. **Exact-path staging.** Stage only approved paths. No `add -A`, `add .`, pull, checkout, switch, merge, rebase, cherry-pick, bisect, commit, stash, reset, restore, or clean. Disk and index bytes must equal the frozen result. Index digests verify the earlier approval; they do not create it.
8. **External candidate.** Invoke the engine with `python3 -B` and the absolute reviewed engine and catalog. Save `propose-lock` stdout outside the resolved destination. Never use `<target>/.aicore/adoption.lock.candidate.yaml`. Check that same explicit snapshot against the external candidate.
9. **Lock-only acceptance.** After exit 0, install and stage only `.aicore/adoption.lock.yaml`, then final-check. Declaration, review, content, index, and manifest stay frozen.
10. **Failure.** Stop and report the step and current state. Do not claim acceptance, roll back, clean, or resume.

A dirty snapshot may be diagnosed. That diagnosis does not authorize migration or sync. Whole-worktree and index comparisons are verification only, never a restorable journal.

## 5.1 Digest framing

Algorithm: `sha256`. Output: `sha256:<lowercase hex>`. A file member is one entry with logical path `""`. A tree member includes files under its root except `__pycache__` and `*.pyc`. Framing, in ascending path order, is `entry`, `path`, `mode` (`100644`, `100755`, or `120000`), `size`, and raw `content` bytes. Unit digests use catalog member order. The declaration digest is the SHA-256 of the exact serialized declaration bytes. Golden file vector: path `""`, mode `100644`, content `hello\n` is `sha256:cf41078b082e3740168bd7ad534ba1b70b12489c7ab43c6fb53743b0f3527887`.

## 6. Runtime lineage review

For a root or derived runtime spec, reviewers read actual before/after ancestor version and destination `Local version` / `local-version` values under the root runtime spec's `## Project extensions` → `### Reuse guide (adopting this core)` version-governance clause. Upstream-only sync preserves the destination value. A destination-local rule change has a reviewed SemVer bump and recorded rationale. The independent model review reads every complete previous-core, target-core, destination-before, and result document and judges incorporation, mandatory precedence, preservation of a compatible local business rule, and the bump rationale; Python binds the reviewed bytes and never substitutes a token or digest for that review. Source ancestors remain free of destination local-version markers.

## 7. Errors and compatibility

v1 remains upgrade-only input and fails `schema_upgrade_required`. Fatal v2 input failures include `baseline_unavailable`, `invalid_lock`, `invalid_declaration`, `declaration_incomplete`, `invalid_applicability`, `declaration_changed`, `review_changed`, `catalog_changed`, `invalid_mapping`, `unsupported_projection`, `adopter_snapshot_unavailable`, and `repository_identity_mismatch`.

## 8. Test-runner governance

A declaration records its reviewed whole-project test disposition in a `test_runner` block required for acceptance, present either as explicit `no_tests` or as whole-project `commands`:

```yaml
test_runner:
  commands:            # approved whole-suite command(s), literal
    - pnpm test
  executor: crucible   # the designated agent that runs the whole suite
  scope: whole_project
  reviewer: <role>
  evidence: <nonempty note>
```

- The block is a mapping with only these keys: `no_tests`, `commands`, `executor`, `scope`, `reviewer`, `evidence`. An unknown key is `invalid_declaration`.
- `commands` is a nonempty list of nonempty literal strings: an entry containing `*` or `?` is `invalid_declaration`, so a wildcard can never be declared as an approved command and the broad-grant approved-command exemption cannot launder a wildcard grant. `executor`, `reviewer`, and `evidence` are nonempty strings; `scope` is exactly `whole_project`. A missing, empty, wildcarded, or wrong-typed field is `invalid_declaration`.
- An explicit no-tests disposition is `no_tests: true` with nonempty `reviewer` and `evidence`, and no `commands`, `executor`, or `scope`.
- An absent block is a `policy_violation`: the adopter declares no reviewed `test_runner` metadata.

Validation is literal and placement-bound. `check` and `propose-lock` parse the adopter's `opencode.jsonc` and inspect only `agent.<executor>.permission.bash`. A `//` comment terminates at the first of `\n`, `\r`, `\u2028`, `\u2029` — a `\r\n` pair is one terminator and an `\u2028`/`\u2029` terminator is normalized to `\n` so it stays valid JSON whitespace — so the checker never accepts a document whose comment structure a conformant JSONC parse sees differently (it is stricter for bare ECMAScript-only whitespace outside comments), and a terminated comment can never hide following rules from the checker. The nominated executor's rules are evaluated in document order with OpenCode `*`/`?` wildcard semantics and last-match-wins, so an approved command is executable only when its last matching rule is a literal `allow`:

- Every approved command must resolve to a literal `allow` as its final matching rule; a later matching `deny` or `ask` makes an earlier literal `allow` non-executable, and a missing approved command fails.
- An entry whose value is not exactly `allow`, `ask`, or `deny` is a config violation in both the ordered-effect evaluation and the broad-grant scan; an unrecognized action never skips a rule or resolves an approval.
- A blanket string `"allow"`, a broad wildcard `allow` that is not itself an approved command literal, or malformed/non-object JSONC fails.
- Unrelated agents and top-level/global grants are never inspected; other non-test `allow` entries (`git`, build, install) are ignored.
- A `no_tests` declaration skips grant checks.

Command text does not prove suite coverage; the destination's own `reviewer` and `evidence` attest it. Validation never imposes AICore's UV command and never accepts a finite runner-name list.
