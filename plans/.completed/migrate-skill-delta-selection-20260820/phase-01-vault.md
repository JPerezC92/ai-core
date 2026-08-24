# Phase 1 — Vault 🔐 (Catalog Steward): structured manifest + deterministic inventory

> **Owner:** Vault 🔐 (Catalog Steward)
> **Pre:** plan.md confirmed; `.opencode/skills/migrate-core-to-project/SKILL.md` exists and is the current prose-manifest version.
> **Reads:** `.opencode/skills/migrate-core-to-project/SKILL.md`
> **Writes:** `.opencode/skills/migrate-core-to-project/SKILL.md` (edited — manifest + step 1)

## Steps

1. Replace the prose "Core manifest" section (`## Core manifest (what AICore contains)` and its 5 bullet lines) with a structured table. Header exactly:
   `| Item | Kind | Source | Destination | Include-rule |`
   Rows (16 subagents + CVs listed as one pair each; cipher CV-only; investigator CV-less):

   | Item | Kind | Source | Destination | Include-rule |
   |---|---|---|---|---|
   | `git-branch-name` | skill | `.opencode/skills/git-branch-name/` | `<target>/.opencode/skills/git-branch-name/` | always |
   | `git-commit` | skill | `.opencode/skills/git-commit/` | `<target>/.opencode/skills/git-commit/` | always |
   | `git-pr` | skill | `.opencode/skills/git-pr/` | `<target>/.opencode/skills/git-pr/` | always |
   | `op-agent-creator` | skill | `.opencode/skills/op-agent-creator/` | `<target>/.opencode/skills/op-agent-creator/` | always |
   | `op-model` | skill | `.opencode/skills/op-model/` | `<target>/.opencode/skills/op-model/` | always |
   | `op-skill-creator` | skill | `.opencode/skills/op-skill-creator/` | `<target>/.opencode/skills/op-skill-creator/` | always |
   | `plan-enforce` | skill | `.opencode/skills/plan-enforce/` | `<target>/.opencode/skills/plan-enforce/` | always |
   | `ticket-runbook` | skill | `.opencode/skills/ticket-runbook/` | `<target>/.opencode/skills/ticket-runbook/` | only if ticket marker |
   | `atrium` | agent | `.opencode/agents/atrium.md` + `agents/atrium/profile.md` | `<target>/.opencode/agents/atrium.md` + `<target>/agents/atrium/profile.md` | always |
   | `augur` | agent | `.opencode/agents/augur.md` + `agents/augur/profile.md` | `<target>/.opencode/agents/augur.md` + `<target>/agents/augur/profile.md` | always |
   | `bastion` | agent | `.opencode/agents/bastion.md` + `agents/bastion/profile.md` | `<target>/.opencode/agents/bastion.md` + `<target>/agents/bastion/profile.md` | only if backend marker |
   | `crucible` | agent | `.opencode/agents/crucible.md` + `agents/crucible/profile.md` | `<target>/.opencode/agents/crucible.md` + `<target>/agents/crucible/profile.md` | always |
   | `forge` | agent | `.opencode/agents/forge.md` + `agents/forge/profile.md` | `<target>/.opencode/agents/forge.md` + `<target>/agents/forge/profile.md` | always |
   | `herald` | agent | `.opencode/agents/herald.md` + `agents/herald/profile.md` | `<target>/.opencode/agents/herald.md` + `<target>/agents/herald/profile.md` | always |
   | `inquisitor` | agent | `.opencode/agents/inquisitor.md` + `agents/inquisitor/profile.md` | `<target>/.opencode/agents/inquisitor.md` + `<target>/agents/inquisitor/profile.md` | always |
   | `investigator` | agent | `.opencode/agents/investigator.md` | `<target>/.opencode/agents/investigator.md` | only if ticket marker |
   | `ledger` | agent | `.opencode/agents/ledger.md` + `agents/ledger/profile.md` | `<target>/.opencode/agents/ledger.md` + `<target>/agents/ledger/profile.md` | only if ticket marker |
   | `lumen` | agent | `.opencode/agents/lumen.md` + `agents/lumen/profile.md` | `<target>/.opencode/agents/lumen.md` + `<target>/agents/lumen/profile.md` | always |
   | `marshal` | agent | `.opencode/agents/marshal.md` + `agents/marshal/profile.md` | `<target>/.opencode/agents/marshal.md` + `<target>/agents/marshal/profile.md` | always |
   | `quill` | agent | `.opencode/agents/quill.md` + `agents/quill/profile.md` | `<target>/.opencode/agents/quill.md` + `<target>/agents/quill/profile.md` | only if ticket marker |
   | `scribe` | agent | `.opencode/agents/scribe.md` + `agents/scribe/profile.md` | `<target>/.opencode/agents/scribe.md` + `<target>/agents/scribe/profile.md` | only if ticket marker |
   | `sentinel` | agent | `.opencode/agents/sentinel.md` + `agents/sentinel/profile.md` | `<target>/.opencode/agents/sentinel.md` + `<target>/agents/sentinel/profile.md` | always |
   | `vault` | agent | `.opencode/agents/vault.md` + `agents/vault/profile.md` | `<target>/.opencode/agents/vault.md` + `<target>/agents/vault/profile.md` | always |
   | `warden` | agent | `.opencode/agents/warden.md` + `agents/warden/profile.md` | `<target>/.opencode/agents/warden.md` + `<target>/agents/warden/profile.md` | always |
   | `cipher` | cv | `agents/cipher/profile.md` | `<target>/agents/cipher/profile.md` | always (CV-only, no runtime spec) |
   | `knowledge/agents.md` | infra | `knowledge/agents.md` | `<target>/knowledge/agents.md` | always |
   | `knowledge/debt.md` | infra | `knowledge/debt.md` | `<target>/knowledge/debt.md` | always |
   | `knowledge/symptoms.md` | infra | `knowledge/symptoms.md` | `<target>/knowledge/symptoms.md` | always |
   | `knowledge/problems.md` | infra | `knowledge/problems.md` | `<target>/knowledge/problems.md` | always |
   | `plans/` | infra | `plans/.gitkeep` | `<target>/plans/.gitkeep` | always |
   | `user-stories/` | infra | `user-stories/.gitkeep` | `<target>/user-stories/.gitkeep` | always |
   | `AGENTS.md` | config | (generated) | `<target>/AGENTS.md` | merge, not copy |
   | `opencode.jsonc` | config | (permission block) | `<target>/opencode.jsonc` | merge, not copy |
   | `.gitignore` | config | (entries) | `<target>/.gitignore` | merge, not copy |

2. Rewrite `### 1. Scope discovery (read-first)` → `### 1. Inventory (deterministic)`. New content:
   - Read the target's structure to set the two markers mechanically: **backend marker** (target has a backend manifest, e.g. `nest-cli.json`, `pyproject.toml`, `requirements.txt`, or a backend source dir) and **ticket marker** (target has a ticket/support folder or workflow). Markers are concrete existence checks, not judgments.
   - Loop the manifest table. For every item, check destination presence:
     - skill → `<target>/.opencode/skills/<name>/SKILL.md` exists?
     - agent → `<target>/.opencode/agents/<name>.md` AND `<target>/agents/<name>/profile.md` both exist?
     - cv-only (cipher) → `<target>/agents/cipher/profile.md` exists?
     - infra → `<target>/knowledge/<file>` (or the `.gitkeep`) exists?
     - config → treated as merge targets (always eligible for the merge check), not presence-diffed.
   - Output three lists: `present` (skip), `missing` (eligible), `partial` (a present item with a missing pair-half, e.g. spec present but CV absent).
   - `partial` FAILS CLOSED: report it, do NOT auto-migrate or auto-repair it; ask the user how to proceed.
   - Apply the include-rules to filter `missing` down to `eligible`: skip `bastion` unless backend marker, skip ticket-team agents + `ticket-runbook` unless ticket marker.

## Output

- **Artifact:** `.opencode/skills/migrate-core-to-project/SKILL.md` (edited)
- **Schema / shape:** structured manifest table with the exact 34 rows above; step 1 renamed to "Inventory (deterministic)" with marker checks, presence checks per Kind, and the present/missing/partial + fail-closed output.

## Gate

- ⬜ `grep -c '| Kind | Source | Destination | Include-rule |' .opencode/skills/migrate-core-to-project/SKILL.md` → 1.
- ⬜ `grep -c 'Inventory (deterministic)' .opencode/skills/migrate-core-to-project/SKILL.md` → 1.
- ⬜ `grep -c 'FAILS CLOSED' .opencode/skills/migrate-core-to-project/SKILL.md` → >=1 (partial handling).
- ⬜ `grep -cE 'present|missing|partial' .opencode/skills/migrate-core-to-project/SKILL.md` → >=3 (all three states named).
- ⬜ Old prose manifest gone: `grep -c '## Core manifest (what AICore contains)' .opencode/skills/migrate-core-to-project/SKILL.md` → 0.

## Abort conditions

- Halt if any manifest row's Destination path deviates from the table above (paths are the determinism guarantee — do not improvise them).
- Halt if the partial state would be auto-resolved instead of failing closed.

## Tool whitelist / blacklist

- Whitelist: read tools; edit on `.opencode/skills/migrate-core-to-project/SKILL.md`.
- Blacklist: edits to any other skill, agent spec, CV, or `knowledge/` file in this phase.
