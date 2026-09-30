---
name: migrate-core-to-project
description: Bootstrap an atomic AICore adoption into a target project — deterministically. Detects the target's profile, reads the machine catalog, decides every applicable unit's ownership mode with reviewed destination bytes before the first write, enrolls the complete applicable unit set at one revision, merges the required config assertions, bootstraps the declaration/review/lock, and verifies with the sync engine's compliance check. Use when the user wants to install the core into another project or scaffold a project with the agent tooling.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 2.3.0
  domain: opencode
---

## What I do

Bootstrap AICore's reusable, agnostic core into a target project as one atomic enrollment. I detect the target's profile mechanically, confirm the destination project identity, read the machine catalog (`.aicore/core-catalog-v2.yaml`), run a **mode review** that records every applicable unit's ownership mode together with reviewed destination bytes and writes the adopter control surfaces (`.aicore/adoption.yaml`, `.aicore/adoption-review.yaml`) **before any adopted-content byte is written**, enroll the **complete applicable unit set** at one AICore revision, merge the required config assertions, write the destination's root runtime as an `adapted` document that presents the destination as the active project with destination-only identity (source provenance lives in the `.aicore` controls), delegate lock generation and verification to `sync-aicore-adoption`, and report stack-mismatched rulebook bodies that need destination-side adaptation. I never run git; shipping (branch/commit/PR) happens separately.

There is no partial or selectable enrollment: applicable units install as a complete set at one revision, and inapplicable units are recorded as `not_applicable` under a machine-checked applicability rule. I fail closed on stale or partial content.

Ownership is decided before writes: `install_strategy: copy` units in mode `mirror` receive core bytes; `merge`, `preserve`, and every non-mirror unit keep owner bytes; a differing `adapted` file is **read and edited**, never overwritten; a destination difference with no recorded mode and reviewed bytes blocks the run before the first copy.

## When to use me

- User wants to install the core into another project ("install AICore in X").
- User wants to scaffold a new project with the agent tooling.
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

Every step reads any target file in full before editing it. Steps 1-3 decide and record ownership; no adopted-content byte is written until step 3 has a recorded mode for every applicable unit and reviewed destination bytes for every non-mirror unit.

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

Output the profile triple plus the confirmed destination identity. The detected stack list also feeds the step-7 mismatch report.

### 2. Compute the applicable set and confirm once

Read `.aicore/core-catalog-v2.yaml`. For every unit, evaluate its `applicability` against the detected profile (`always` / `requires` / `any_of`). Produce the applicable set and the inapplicable set.

Present the profile and the two sets via the `question` tool as a single confirmation: **"Enroll the complete applicable set?"** with the profile and the applicable/inapplicable lists. Do not offer per-unit selection; the only options are confirm or correct the profile. Config merge targets are always handled in step 6.

If the user corrects the profile, recompute the sets before proceeding.

### 3. Mode review and control surfaces (before any content write)

This step decides ownership. It reads destination bytes and writes only the two control documents — never adopted content.

For **every** applicable unit, read the destination's existing bytes at the mapped path (the declared member destination, or the unit's `destination` for assertion units) and confirm one ownership mode with the owner via the `question` tool, together with the reviewed destination content:

- **`mirror`** — the destination is absent or byte-identical to the source revision; the unit will receive core bytes in step 4.
- **`adapted`** — the destination intentionally differs from the source revision; the reviewed destination bytes at the mapped path are the content that must survive. A differing `adapted` file is **read and edited**, never overwritten.
- **`replacement`** — the destination is adopter-local content with no byte-convergence claim (declared with `replacement_members`, never with `members`).
- **`destination_owned`** — an intentional local fork whose upstream changes are tracked through review decisions only.

Rules for this step:

1. **Every applicable unit gets a recorded mode** — no partial classification, no deferred unit. Every inapplicable unit is recorded `not_applicable` under the machine-checked applicability rule from step 2.
2. **Every non-mirror unit gets reviewed destination bytes** before anything is written; that reviewed content lives at the mapped destination path and is never replaced by core bytes.
3. **An unreviewed difference blocks here.** If a destination path exists with content differing from the source revision and the owner has not classified it as `mirror`, `adapted`, `replacement`, or `destination_owned`, halt this step — no copy begins. This is upstream of the "stale content fails closed" override in step 4.
4. **`root-runtime-spec` is `adapted`.** The destination root runtime carries its own destination-only `Project identity` and is intentionally not a byte-identical mirror of the upstream `AGENTS.md`; the `Local version: 1.0.0` marker rule is applied in step 6.

Only after every unit has a recorded mode and — for non-mirror units — reviewed destination bytes, write the control surfaces:

1. Write `.aicore/adoption.yaml` (schema v2): the `profile` triple, and **one entry per catalog unit** — `mirror` for byte-identical copies, `adapted`/`replacement`/`destination_owned` only where the destination intentionally differs, and `not_applicable` for every inapplicable unit. Declare the `root-runtime-spec` unit as mode `adapted` as required by rule 4 above.
2. Write `.aicore/adoption-review.yaml` (schema v2): empty `decisions` initially; decisions are added when a non-mirror unit changes upstream.
3. These two control documents are the record of the mode review. No adopted-content byte may be written before both exist and together cover every catalog unit.

### 4. Enroll the complete applicable set

Copy content only now — after step 3 has recorded a mode for every applicable unit and reviewed destination bytes for every non-mirror unit. Never write beyond the catalog's declared members.

- **`copy`-and-`mirror` units receive core bytes.** Copy every applicable unit declared `mirror`:
  - **Agents** copy as pairs (`.opencode/agents/<name>.md` + `agents/<name>/profile.md`); `cipher` is CV-only.
  - **Skills** copy their directories, excluding `__pycache__/` and `*.pyc`.
  - **Infra** copies every declared member.
- **`merge`, `preserve`, and any non-mirror unit keep owner bytes.** Config units (`root-runtime-spec`, `opencode-config`, `gitignore-config`) are merged in step 6, not copied; a `preserve` unit is never overwritten.
- **A differing `adapted` file is read and edited, never overwritten** — apply the upstream change onto the destination's own reviewed bytes instead of replacing them with core bytes.

**Stale content fails closed.** If a destination path already exists with content that differs from the source revision, do NOT silently skip or overwrite: report the mismatch and require an explicit user override, which re-runs the mode review for that unit. An identical present path is left untouched.

### 5. Dependency union

For each enrolled skill, read its `SKILL.md` frontmatter `metadata.dependencies`. Compute the union.

- **Conflict** (same package, different pins) — blocking mismatch; halt until the user resolves it.
- **Non-empty union** — generate a `pyproject.toml` (`[project]` with the target name, `version = "0.0.0"`, `requires-python = ">=3.9"`, the union `dependencies`; `[tool.uv]` with `package = false`), then print the lock instruction `uv lock --project <target>`.
- **Empty union** — skip.

### 6. Merge config (assertion units)

These units keep owner bytes: merge appends what is missing and never rewrites the file. Read the target file in full before editing it.

- **`AGENTS.md` (`root-runtime-spec`)** — establish the destination as the active project with destination-only identity. Merge new roster lines into an existing root file; write fresh if absent. When written, the destination root runtime must carry:
  - a `Project identity` marker naming the step-1 confirmed destination identity as the active project;
  - the ancestor AICore spec version in the copied spec's version field, plus a destination `Local version: 1.0.0` marker that advances only on destination-local edits, never on an AICore sync;
  - destination-only content: no AICore identity, upstream repository, management-tool, reuse-guide, provenance, or lineage reference, and no inherited AICore reuse guidance. The engine enforces this closed policy (`guarded_file` + `adopter_root_runtime`) at proposal and check; source identity and provenance live only in the adopter's `.aicore` controls.
- **`opencode.jsonc` (`opencode-config`)** — append the required permission gates declared as catalog assertions (grep before adding; never duplicate): stash push/apply allows, stash pop/drop/clear/update-ref/reflog/gc/repack/prune/symbolic-ref denies, `sudo` / `rm -rf /*` / `git push --force` / `gh pr merge` / `gh repo delete` / root-redirect denies, and the `mv plans/*-*` allow.
- **`.gitignore` (`gitignore-config`)** — append-if-missing `output/`, `pr-draft.md`, `commit.txt`, `plans/.completed/`.
- **Build approvals** — if the target uses pnpm ≥ 11, approve native build scripts via `pnpm approve-builds`.

### 7. Consistency pass

After enrollment, verify and fix cross-references on the union of enrolled + already-present content:

1. **Broken file pointers** — trim references only to agents that are neither enrolled nor already present.
2. **Roster lists** — align `AGENTS.md`, `knowledge/agents.md`, and Sentinel 🛡️ (Quality Guardian) audit lists to the enrolled roster.
3. **Non-enrolled team references** — de-reference teams that were not enrolled (only when genuinely inapplicable).
4. **Frontmatter** — every spec has `name` (matching filename), `description`, and `mode: subagent`.
5. **CV ↔ spec reconciliation** — persona CVs and runtime specs agree.
6. **Grammar/emoji** — CV H1 headings use `# Name Emoji — Role`.
7. **Stack-mismatch report** — compare each stack-bound rulebook body (`atrium` React/web, `bastion` NestJS-TS + Python, `crucible` Vitest/Playwright, `lumen` web) against the detected stacks and report mismatches as `adapt destination-side`. Report only.

### 8. Lock generation

Do NOT hand-write the lock. Delegate lock generation to the sync engine:

```
python3 .opencode/skills/sync-aicore-adoption/scripts/sync_aicore_adoption.py propose-lock --upstream-repo <aicore> --adopter-repo <target> --declaration <target>/.aicore/adoption.yaml --review <target>/.aicore/adoption-review.yaml --adopter-index
```

and have the user commit the emitted candidate as `.aicore/adoption.lock.yaml`. There is no parallel migrator and no disk-crash transaction claim: the lock is generated evidence, rebuilt only from the recorded declaration, the review, and the staged destination bytes.

### 9. Verify (compliance)

Enrollment is complete only when the sync engine reports compliance:

```
python3 .opencode/skills/sync-aicore-adoption/scripts/sync_aicore_adoption.py check \
  --upstream-repo <aicore> --adopter-repo <target> \
  --declaration <target>/.aicore/adoption.yaml \
  --review <target>/.aicore/adoption-review.yaml \
  --lock <target>/.aicore/adoption.lock.yaml --adopter-index
```

- Exit 0 — complete and current (every declared unit `current`/`not_applicable`, or the `unmanaged` `destination_owned` steady state); enrollment is done.
- Exit 1 — a blocking disposition remains (stale/drift/conflict/unresolved); fix and re-run.
- Exit 2 — fatal (incomplete declaration, invalid applicability, invalid lock, schema upgrade); fix and re-run.

Do not report success until `check` exits 0. Run the target's build command as a final smoke test.

## Core catalog

Read [`.aicore/core-catalog-v2.yaml`](../../../.aicore/core-catalog-v2.yaml) before step 1. It is the authoritative machine inventory of adopted content: `kind`, `applicability`, `install_strategy`, `sync_projection` (`file`/`guarded_file`/`tree`/`assertions`), and the declared members/assertions. `sync-aicore-adoption` reads the same catalog.

`migrate-core-to-project` and `sync-aicore-adoption` are upstream-only AICore management tools. Neither is a catalog unit, and neither the tools nor the catalog nor the registry is copied as adopted content.

## Examples

### Example 1 — frontend portfolio, no ticket system

Target: Next.js project (`package.json`). Profile: `backend_stack: true` (node), `python_scripts: true`, `ticket_system: false`.

- Enrolled: the always units plus `bastion` (via `backend_stack`/`python_scripts`); ticket-team units and `query-verification*`/`ticket-runbook` recorded `not_applicable`.
- Mode review first: every applicable unit gets its recorded mode and non-mirror units their reviewed destination bytes; declaration + review written before any content byte.
- Config merged so `opencode-config`/`gitignore-config` assertions pass.
- Lock generated by `propose-lock`; `check` exit 0.
- Mismatch report flags `atrium`/`bastion`/`crucible`/`lumen` bodies to adapt destination-side.

### Example 2 — Rust TUI tool, no ticket system

Target: `Cargo.toml`. Profile: `backend_stack: false`, `python_scripts: true`, `ticket_system: false`.

- Enrolled: always units plus `bastion` via `python_scripts`; ticket units `not_applicable`.
- `check` exit 0 after lock generation.

## Troubleshooting

- **`check` exits 2 with `declaration_incomplete`** — the declaration omits a catalog unit. Fix: add every unit as a real mode or `not_applicable`.
- **`check` exits 2 with `invalid_applicability`** — an `always` unit is `not_applicable`, or an applicable unit was excluded. Fix: correct the profile or the mode.
- **`check` exits 1 with a config assertion failure** — a required permission gate or ignore entry is missing. Fix: merge it, then regenerate the lock.
- **A present file differs from the source** — stale or customized content. Fix: explicit user override to re-copy, or declare the unit `adapted` with a review decision — never silent overwrite.
- **`check` exits 2 with `schema_upgrade_required`** — the adopter still carries a v1 declaration or lock. Fix: re-declare under v2 and regenerate the lock.
- **`propose-lock` exits 2 with `policy_violation`** — the destination root runtime carries an AICore/upstream/management-tool/reuse-guide/lineage reference or is missing a required `Project identity`/`Spec version`/`Local version` marker. Fix: rewrite the root to destination-only content, then regenerate the lock.
