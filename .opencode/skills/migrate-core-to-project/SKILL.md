---
name: migrate-core-to-project
description: Bootstrap an atomic AICore adoption through reviewed destination edits, exact-byte approval, candidate-lock evidence, and read-only checks. Use when a project first adopts the core.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 3.2.1
  domain: opencode
---

## What I do

Bootstrap AICore's reusable, agnostic core into a target project as one atomic enrollment. Follow `sync-aicore-adoption` protocol v2 §4–§5; do not use a second order. Pin an approved refresh of the protected upstream tip, detect the profile, and prepare the complete result outside the destination: modes, extensions, dependency union, config, and consistency corrections. Freeze approval, write `.aicore/adoption.yaml` and `.aicore/adoption-review.yaml`, then write reviewed content. The destination root is `adapted` and destination-only. Source provenance lives in the `.aicore` controls. Lock generation uses `python3 -B` and an external candidate. I never run destination git; Herald 📯 (Release Manager) stages only approved paths. Shipping remains separate. There is no backup or rollback.

There is no partial or selectable enrollment: applicable units install as a complete set at one revision, and inapplicable units are recorded as `not_applicable` under a machine-checked applicability rule. I fail closed on stale or partial content.

Ownership is decided before writes: a reviewed byte-identical `mirror` receives its approved result; `merge`, `preserve`, and every other non-mirror unit keep owner bytes; a differing `adapted` file is **read and edited**, never overwritten; a destination difference with no recorded mode and reviewed bytes blocks the run before the first write. Protected mirrors still need an applied `verified_layout` decision.

## When to use me

- User wants to install the core into another project ("install AICore in X").
- User wants to enroll the agent tooling into an existing or new repository. This is not an application generator.
- A project must be brought under the atomic adoption contract for the first time.

Do NOT use me to create or edit skills or agents — those are `op-skill-creator` and `op-agent-creator` territory. Do NOT use me for recurring updates on an already-enrolled adopter — that is `sync-aicore-adoption`.

## Arguments

From the user's request, extract:

- **target** — path to the destination project (required).
- **stack hints** — optional notes (backend? TUI? ticket system?). Markers are set by mechanical existence checks; hints never override them.

### Argument collection form

| name | type | validation | trigger |
|---|---|---|---|
| `target` | text | non-empty, points to a directory | not provided |

Use one `question` call for the missing argument. Do not add a manual "Other" option.

## Steps

Every step reads any target file in full before editing it. The only sequence is protocol v2 §5: controlled preflight, pin, external full preparation, complete-output collision and recheck, frozen approval, controls then content, exact-path staging, external candidate, lock-only acceptance. Destination-before includes absence. No destination byte is written before that approval.

### 1. Detect the profile (deterministic)

Read the target root for mechanical markers, not judgments:

| Manifest exists at target root | `backend_stack` |
|---|---|
| `package.json` or `nest-cli.json` | true (`node`) |
| `pyproject.toml` or `requirements.txt` | true (`python`) |
| `Cargo.toml` / `go.mod` | false (not a backend rulebook stack) |

- `python_scripts` — true when any applicable skill ships `scripts/*.py` (true today for `op-model`, `plan-enforce`, `sync-aicore-adoption`, `query-verification`, `ticket-runbook`).
- `ticket_system` — true when the target has a ticket/support folder or workflow.

Derive the **destination identity** from the target's own declarative metadata, never from AICore: the `[project].name` in `pyproject.toml`, the `name` in `package.json`, the module name in `Cargo.toml`/`go.mod`, or the target directory name. When these disagree, ask via the `question` tool and confirm one identity before proceeding.

Output the profile triple plus the confirmed destination identity. The detected stack list feeds the external consistency preparation below.

### 2. Compute the applicable set and confirm once

Read `.aicore/core-catalog-v2.yaml`. For every unit, evaluate its `applicability` against the detected profile (`always` / `requires` / `any_of`). Produce the applicable set and the inapplicable set.

Present the profile and the two sets via the `question` tool as a single confirmation: **"Enroll the complete applicable set?"** with the profile and the applicable/inapplicable lists. Do not offer per-unit selection; the only options are confirm or correct the profile. Config merge targets are prepared outside the destination before approval.

If the user corrects the profile, recompute the sets before proceeding.

### 3. Controlled clean start and pin

Follow protocol v2 §5 steps 1–2 before any destination write. Dirty, occupied, or uncertain state aborts. Do not save, commit, stash, clean, or resume. There is no backup or rollback. A clean bisect is not dirtiness. Pin the selected source, absolute catalog, and reviewed engine. Source refresh is a separate approved upstream checkout.

### 4. External full preparation

Read destination bytes and prepare every result outside the destination. This step writes nothing to the destination.

For **every** applicable unit, read the destination's existing bytes at the mapped path (the declared member destination, or the unit's `destination` for assertion units) and confirm one ownership mode with the owner via the `question` tool, together with the reviewed destination content:

- **`mirror` for ordinary protected content** — permitted only after a full review shows the destination-prepared document is byte-identical to the selected source. Absence is not mirror. Prepare project extensions first; do not copy source project extensions to fill an absent file.
- **`mirror` for an assertion unit** — required when the unit is applicable. It has no members. Convergence is assertion presence in the prepared config fragment, not whole-file byte identity. An absent or locally customized config can still be `mirror` after the owner reviews the prepared fragment.
- **`adapted`** — the destination intentionally differs from the source revision; the reviewed destination bytes at the mapped path are the content that must survive. A differing `adapted` file is **read and edited**, never overwritten.
- **`replacement`** — the destination is adopter-local content with no byte-convergence claim (declared with `replacement_members`, never with `members`).
- **`destination_owned`** — an intentional local fork whose upstream changes are tracked through review decisions only.

Rules for this step:

1. **Every applicable unit gets a recorded mode** — no partial classification, no deferred unit. Every inapplicable unit is recorded `not_applicable` under the machine-checked applicability rule from step 2.
2. **Every protected unit, including mirrors, and every other non-mirror unit gets a reviewed prepared result** before controls are written. That result may live outside the destination path. It is not required to occupy the destination before the first write. After controls, only approved paths are written.
3. **An unreviewed difference blocks here.** If a destination path exists with content differing from the source revision and the owner has not classified it, halt. No destination copy begins.
4. **`root-runtime-spec` is `adapted`.** The prepared root carries destination-only `Project identity` and `Local version: 1.0.0`. It is not a byte-identical mirror of upstream `AGENTS.md`.
5. **An absent `knowledge-debt` or `symptom-problem-register` path is destination-owned and is never classified `mirror`.** The prepared debt register comes from the shipped 0-entry `knowledge/debt.template.md` source, and the shared symptom/problem unit additionally retains the reusable symptom catalog. A `mirror` declaration on `knowledge-debt` is rejected as `invalid_declaration`. Create that approved absent file only after controls exist. Never overwrite an existing register. Do not import source debt or problem history.

Prepare these results in the same external set, before approval:

- **Dependency union.** Read each enrolled skill's `metadata.dependencies`. A pin conflict halts for Warden 🔒 (Dependency Warden). Merge only missing approved declarations into the prepared manifest. Do not replace project identity or install packages.
- **Config.** Prepare assertion and ignore entries when missing. The root runtime is a reviewed section-aware edit: destination-only identity, exact selected mandatory bytes, compatible local extensions, and no copied AICore project extensions, debt, or history. Prepare `opencode.jsonc` permission gates and the literal `test_runner` allow. Prepare missing `.gitignore` entries `output/`, `pr-draft.md`, `commit.txt`, and `plans/.completed/`.
- **Consistency.** Fix the prepared result, not the destination after copy. Report unusable mandatory references. Do not rewrite mandatory roster bytes, delete mandatory references, or replace a rulebook body. Specs need `name`, `description`, and `mode: subagent`. CVs use `# Name Emoji — Role`.

The prepared declaration is schema v2: one entry per catalog unit, `root-runtime-spec` as `adapted`, and reviewed `test_runner` metadata or explicit `no_tests: true`. The prepared review uses a null baseline and one applied decision per applicable protected unit, including mirrors, plus every other non-mirror unit. Each decision binds reviewer, evidence, upstream digest, result digest, and `verified_layout: two-section-v1` when the unit has `rule_documents`.

### 5. Collision, recheck, and frozen approval

Check the complete intended write set: every adopted, config, manifest, and index path plus `.aicore/adoption.yaml`, `.aicore/adoption-review.yaml`, and `.aicore/adoption.lock.yaml`. An existing ignored occupant blocks. An ignore rule without a file is not unsaved work and does not authorize `git add -f`. Recheck cleanliness. Freeze the declaration, review, and prepared-result digests. Protected approval requires the model to read every complete document.

### 6. Write controls, then approved content

Write the two frozen control documents first. No adopted-content byte precedes them. Then write only approved paths. The story index is an auxiliary file, not a catalog member. Create an approved absent register only if that path is still absent, using the 0-entry `knowledge/debt.template.md` source for the debt register. Never overwrite an existing register.

- **Reviewed `copy`-and-`mirror` units receive the approved byte-identical result.** Do not copy an unreviewed upstream document, and do not inherit its project extensions:
  - **Agents** enroll as reviewed pairs (`.opencode/agents/<name>.md` + `agents/<name>/profile.md`); `cipher` is CV-only. The spec is mirror only when the prepared document is byte-identical.
  - **Skills** enroll their reviewed directories, excluding `__pycache__/` and `*.pyc`.
  - **Infra** enrolls every declared member from its approved result. After controls, create an approved absent `knowledge-debt` register from the 0-entry `knowledge/debt.template.md` source and the problem register from its structural header. A `mirror` mode on `knowledge-debt` is rejected before the write. Do not copy source debt or problem rows. Retain the reusable symptom catalog in the shared unit.
- **`merge`, `preserve`, and any non-mirror unit keep owner bytes.** Config units receive the externally prepared merge, not a post-copy fix. A `preserve` unit is never overwritten.
- **A differing `adapted` file receives its frozen prepared result, never an unreviewed overwrite.** That result edits the destination's reviewed bytes outside the destination before the write.

**Stale content fails closed.** If a destination path already exists with content that differs from the source revision, do not silently skip or overwrite. Stop and prepare the classification again. Do not resume or roll back. For a unit with `rule_documents`, the only accepting modes are `mirror`, `adapted`, or machine-valid `not_applicable`, and acceptance requires an applied decision with `verified_layout: two-section-v1` after reading the whole accepted source, the whole target source, and every destination rule surface. `replacement` and `destination_owned` cannot bypass mandatory bytes. The `knowledge-debt` unit is destination-owned: a `mirror` declaration is rejected as `invalid_declaration`, and a `preserve` member that is absent is created from its 0-entry template or schema; an existing preserve member is never overwritten. An identical present path is left untouched.

Do not run `pnpm approve-builds` or the target build.

The written root must carry the confirmed destination identity, the ancestor spec version, and `Local version: 1.0.0`. It has no AICore identity, repository, management-tool, reuse-guide, provenance, or lineage reference. The target root policy is `adopter_root_rules`.

### 7. Exact-path staging, external candidate, and acceptance

Herald 📯 (Release Manager) stages only the already approved paths and confirms they still match the frozen result. No `add -A` or `add .`. The engine selects `refs/remotes/origin/main`, then `refs/heads/main` only if the first ref is absent. That selected SHA must equal the reviewed source SHA at proposal and at final check. Hash the executing engine and every imported local production module. The selected source revision and adopter index must not change between proposal and final check, except the accepted-lock path after candidate success. Initial enrollment omits `--lock` and keeps the null baseline recorded before the first write. A missing update lock is never first enrollment. Staging may apply clean filters; unknown effects block.

For a later retirement, the declaration stays target-catalog-only: do not declare a retired unit or delete its destination content. The candidate lock carries one historical `retired: true` row for an ordinary retired non-mirror unit, preserving its predecessor member mapping and reviewed digest evidence. Ordinary retained members explicitly state `projection: file|tree`; replacement members retain their existing projection. That row participates in the normal lock and accepted-snapshot digests, preserving later verification without restoring upstream ownership. This workflow does not claim an automated recovery path.

For root and derived runtime specs, show actual source ancestor version and destination `Local version`/`local-version` values. Initialize the destination value at `1.0.0`; preserve it for upstream-only content and record a SemVer bump rationale for a destination-local rule.

Do NOT hand-write an accepted lock. The required workflow delegates *candidate* generation to the read-only sync engine:

```
python3 -B <aicore-checkout>/.opencode/skills/sync-aicore-adoption/scripts/sync_aicore_adoption.py propose-lock --upstream-repo <aicore> --catalog <aicore-checkout>/.aicore/core-catalog-v2.yaml --adopter-repo <target> --declaration <target>/.aicore/adoption.yaml --review <target>/.aicore/adoption-review.yaml --adopter-index
```

The script and catalog paths are absolute. A relative path from the destination is not the invocation. Controls are read from disk; adopted content is the explicit index.

Save stdout to an owner-approved candidate outside the resolved destination. Never use `<target>/.aicore/adoption.lock.candidate.yaml`. The candidate is evidence, not a publisher or crash transaction.

Run `check` against the same explicit staged snapshot and that external candidate:

```
python3 -B <aicore-checkout>/.opencode/skills/sync-aicore-adoption/scripts/sync_aicore_adoption.py check --catalog <aicore-checkout>/.aicore/core-catalog-v2.yaml \
  --upstream-repo <aicore> --adopter-repo <target> \
  --declaration <target>/.aicore/adoption.yaml \
  --review <target>/.aicore/adoption-review.yaml \
  --lock <external-candidate> --adopter-index
```

Only after exit 0 may the owner install the candidate as `.aicore/adoption.lock.yaml` and stage only that lock path. Declaration, review, adopted content, the story index, and the manifest stay frozen. Compare disk and index bytes for declaration, review, and the accepted lock before the final check. On failure, stop and report. Do not restore or delete applied files.

The acceptance workflow permits enrollment to be recorded complete only when the final sync-engine check reports compliance:

```
python3 -B <aicore-checkout>/.opencode/skills/sync-aicore-adoption/scripts/sync_aicore_adoption.py check --catalog <aicore-checkout>/.aicore/core-catalog-v2.yaml \
  --upstream-repo <aicore> --adopter-repo <target> \
  --declaration <target>/.aicore/adoption.yaml \
  --review <target>/.aicore/adoption-review.yaml \
  --lock <target>/.aicore/adoption.lock.yaml --adopter-index
```

- The established command interface defines Exit 0 as complete and current (every declared unit `current`/`not_applicable`, or the `unmanaged` `destination_owned` steady state); the owner may record enrollment done only after observing it.
- Exit 1 is a blocking disposition. Exit 2 is fatal. Stop and report. A later attempt is a new clean-start sequence, not a resume or rollback.

Do not report success until `check` exits 0. Do not run the target's build as an enrollment smoke test.

## Core catalog

Read [`.aicore/core-catalog-v2.yaml`](../../../.aicore/core-catalog-v2.yaml) before step 1. It is the authoritative machine inventory of adopted content: `kind`, `applicability`, `install_strategy`, `sync_projection` (`file`/`guarded_file`/`tree`/`assertions`), and the declared members/assertions. `sync-aicore-adoption` reads the same catalog.

`migrate-core-to-project` and `sync-aicore-adoption` are upstream-only AICore management tools. Neither is a catalog unit, and neither the tools nor the catalog nor the registry is copied as adopted content.

## Examples

### Example 1 — frontend portfolio, no ticket system

Target: Next.js project (`package.json`). Profile: `backend_stack: true` (node), `python_scripts: true`, `ticket_system: false`.

- Enrolled: the always units plus `bastion` (via `backend_stack`/`python_scripts`); ticket-team units and `query-verification*`/`ticket-runbook` recorded `not_applicable`.
- External preparation records every mode and protected `verified_layout` decision before any destination write. Config is in that prepared result.
- `python3 -B` `propose-lock` writes an external candidate; `check` exit 0; only the accepted lock is then installed.
- Stack differences are prepared in project extensions before enrollment. Mandatory rulebook bodies are not replaced.

### Example 2 — Rust TUI tool, no ticket system

Target: `Cargo.toml`. Profile: `backend_stack: false`, `python_scripts: true`, `ticket_system: false`.

- Enrolled: always units plus `bastion` via `python_scripts`; ticket units `not_applicable`.
- `check` exit 0 after lock generation.

## Troubleshooting

- **`check` exits 2 with `declaration_incomplete`** — the declaration omits a catalog unit. Fix: add every unit as a real mode or `not_applicable`.
- **`check` exits 2 with `invalid_applicability`** — an `always` unit is `not_applicable`, or an applicable unit was excluded. Fix: correct the profile or the mode.
- **Dirty or uncertain destination** — abort before any write. Do not stash, commit, or clean it from this skill.
- **Candidate inside the destination** — move it outside. `<target>/.aicore/adoption.lock.candidate.yaml` is not the candidate path.
- **`check` exits 1 with a config assertion failure** — stop. Correct the external preparation and start a new clean sequence. Do not patch the destination after approval.
- **A present file differs from the source** — stale or customized content. Fix: re-run mode review. A protected unit may be `mirror`, `adapted`, or machine-valid `not_applicable` only after a full three-surface review and an applied `verified_layout` decision. Never silently overwrite, and never re-copy mandatory bytes over a local mandatory edit.
- **`check` exits 2 with `schema_upgrade_required`** — the adopter still carries a v1 declaration or lock. Fix: re-declare under v2 and regenerate the lock.
- **`propose-lock` exits 2 with `policy_violation`** — the destination root runtime carries an AICore/upstream/management-tool/reuse-guide/lineage reference or is missing a required `Project identity`/`Spec version`/`Local version` marker. Fix: rewrite the root to destination-only content, then regenerate the lock.
