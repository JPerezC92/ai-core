---
name: migrate-core-to-project
description: Migrate the AICore reusable core (skills, subagents, persona CVs, and shared infrastructure) into a target project — deterministically. Detects the target's stacks via a manifest→stack map, computes an installed-set inventory from a structured manifest, presents a selectable list of only the missing eligible items, copies idempotently, merges config, runs a union consistency pass with a re-diff verification, and reports stack-mismatched rulebook bodies needing destination-side adaptation. Use when the user wants to install or migrate the agent core into another project, migrate just the remaining missing items incrementally, copy agents or skills from AICore, or scaffold a project with the core tooling.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.2.0
  domain: opencode
---

## What I do

Migrate AICore's reusable, agnostic core into a target project — deterministically. I detect the target's stacks mechanically via a manifest→stack map, compute an installed-set inventory from a structured manifest, present a selectable list of only the missing eligible items, copy idempotently, merge config, run a union consistency pass with a re-diff verification that fails closed on any still-missing item, and report stack-mismatched rulebook bodies that need destination-side adaptation. I never run git; shipping (branch/commit/PR) happens separately.

## When to use me

- User wants to install or migrate the core into another project ("install AICore in X", "migrate the core to project X")
- User asks to copy agents, skills, or infrastructure from AICore into a target project
- User wants to scaffold a new project with the agent tooling
- Before a fresh project starts, to seed it with the git/planning/agent skills

Do NOT use me to create or edit skills or agents themselves — those are `op-skill-creator` and `op-agent-creator` territory.

## Arguments

From the user's request, extract:

- **target** — path to the destination project (required).
- **scope** — coarse Kind-prefilter narrowing the selection step. Derived from the Kind column, never hand-written: `all` (default), or the plural of any selectable Kind (`skill`→`skills`, `agent`→`agents`, `infra`→`infra`). `config` has no scope value — it is a merge target, never selectable. Fine-grained selection happens in step 2, not here.
- **stack hints** — optional notes about the target (backend? TUI? ticket system?) that give context for the mismatch report. Markers and stacks are set by mechanical existence checks; hints never override them.

### Argument collection form

| name | type | validation | trigger |
|---|---|---|---|
| `target` | text | non-empty, points to a directory | not provided |
| `scope` | choice | all / skills / agents / infra (derived from selectable Kinds) | not provided |

Use one `question` call per missing argument. Do not add a manual "Other" option.

## Steps

### 1. Inventory (deterministic)

Read the target's structure to detect its stacks and the ticket marker mechanically — concrete existence checks, not judgments.

**Stack detection — manifest→stack map** (a manifest file at the target root maps to a stack label; multiple manifests may coexist):

| Manifest exists at target root | Stack detected |
|---|---|
| `Cargo.toml` | `rust` |
| `package.json` or `nest-cli.json` | `node` |
| `pyproject.toml` or `requirements.txt` | `python` |
| `go.mod` | `go` |

`node` and `python` count as backend stacks for include-rules (they are the languages of the backend rulebooks). The detected stack list feeds the step-5 mismatch report.

**Ticket marker** (target has a ticket/support folder or workflow).

Loop the manifest table. For every item, check destination presence:

- skill → `<target>/.opencode/skills/<name>/SKILL.md` exists?
- agent → every file in the item's Source exists? A normal agent has 2 files (spec + CV); `investigator` is spec-only (1 file); `cipher` is CV-only (1 file). present when ALL its files exist, partial when exactly one does, missing when none do.
- infra → each file in the item's Source exists? A multi-file item (e.g. symptom-problem-register) is present when ALL its files exist, partial when exactly one does, missing when none do.
- config → treated as merge targets (always eligible for the merge check), not presence-diffed.

Output three lists: `present` (skip), `missing` (eligible), `partial` (a present item with a missing pair-half, e.g. spec present but CV absent).

`partial` FAILS CLOSED: report it, do NOT auto-migrate or auto-repair it; ask the user how to proceed.

Apply the include-rules to filter `missing` down to `eligible`: skip `bastion` unless a backend stack (`node` or `python`) is detected OR any skill in the eligible set ships Python scripts (mechanical check: `scripts/*.py` exists under the skill's source directory — true today for `op-model`, `plan-enforce`, `ticket-runbook`); skip ticket-team agents + `ticket-runbook` unless ticket marker.

### 2. Select items

Present a multi-select list via the `question` tool with `multiple: true`, listing ONLY the `missing` eligible items from step 1, grouped by Kind:

- **skills** — each missing eligible skill
- **agents** — each missing eligible agent (`investigator` listed as spec-only, `cipher` as CV-only; `bastion` described as the Backend & Scripts Architect — it audits the plan-scoped Python scripts shipped by the Python-script skills, so it travels with them)
- **infra** — each missing infra file
  - a multi-file infra item (symptom-problem-register) is listed as ONE option, not one per file.

Config merge targets (`AGENTS.md`, `opencode.jsonc`, `.gitignore`) are NOT listed — they are always handled in step 5, never selectable.

- The first option is **"Migrate all missing eligible items"** (default).
- Each option's label is the manifest Item name; its description cites the Destination path from the manifest (never re-invented).
- Map the selection 1:1 to manifest entries → derive the exact write manifest from the selection. Never invent an item that is not in the manifest.

### 3. Copy (idempotent)

Copy ONLY the selected items. Never write beyond the derived write manifest.

- **`present` items are NEVER touched.** Re-copying an already-present item requires the user to explicitly override — never silent.
- **Agents copy as pairs:** `.opencode/agents/<name>.md` + `agents/<name>/profile.md`. Exceptions: `investigator` copies spec only; `cipher` copies CV only.
- **Skills:** copy `.opencode/skills/<name>/` directories, excluding `__pycache__/` and `*.pyc` (never copy bytecode caches into the target).
- **Infra:** copy every file in the item's Source (a multi-file item copies all its files as one unit).

### 4. Dependency union

For each selected skill, read its `SKILL.md` frontmatter `metadata.dependencies` (if the key exists). Compute the union of all declared dependency strings across the selected set.

**Conflict check:** if the same package name appears with different version pins across two or more selected skills, surface the conflict as a blocking mismatch to the user — list each conflicting name and the competing pins — and halt until the user resolves it. Never silently coalesce conflicting pins.

**Union emission:**

- **Non-empty union** — generate a `pyproject.toml` at the destination root using the same shape as AICore's: `[project]` table with `name` (destination project name), `version = "0.0.0"`, `requires-python = ">=3.9"`, and `dependencies` set to the union list; `[tool.uv]` table with `package = false`. Then print the lock instruction the user must run: `uv lock --project <target>`.
- **Empty union** (no selected skill declares `metadata.dependencies`) — skip; no file is generated.

### 5. Merge adapts

- **AGENTS.md** — if `<target>/AGENTS.md` exists, MERGE new roster lines into the existing file (append lines for newly selected agents; do NOT regenerate from scratch). If absent, write fresh.
- **opencode.jsonc** — append only the missing permission gates: grep for an existing gate before adding; never duplicate.
- **.gitignore** — append-if-missing entries `commit.txt`, `pr-draft.md`, `output/`, `plans/.completed/`.
- **Build approvals** — if the target uses pnpm ≥ 11, approve native build scripts (`sharp`, `@swc/core`, `agent-browser`, `@parcel/watcher`, `unrs-resolver`) via `pnpm approve-builds`.

### 6. Consistency pass (union)

Run against the UNION = the already-present set + the newly selected set. After every copy, verify and fix cross-references. Verbatim copies are never internally consistent.

1. **Broken file pointers** — grep every copied spec for `.opencode/agents/<name>.md` and `agents/<name>/profile.md` references; trim a reference ONLY to an agent that is NEITHER `present` NOR `selected` this run. A reference to an already-installed agent is valid and must NOT be trimmed (e.g. `forge.md` reading `bastion.md` when bastion was not copied this run but was already installed).
2. **Roster lists** — align every roster list (AGENTS.md, knowledge/agents.md ownership table, sentinel audit-scope lists, per-spec Roster Context) to the union (existing + new), merging new entries in rather than regenerating from scratch. Stale lists are the most common bug.
3. **Non-installed team references** — de-reference the non-installed team from copied specs/CVs (e.g. incident-team mentions in `augur.md`/`marshal.md` roster context, Cipher CV delegation lines).
4. **Frontmatter** — every spec must have `name` (matching the filename), `description`, and `mode: subagent`. Missing `name` is a common verbatim-copy defect.
5. **CV ↔ spec reconciliation** — persona CVs and runtime specs must agree (e.g. if the spec forbids posting GitHub comments, the CV must not claim it posts them).
6. **Grammar/emoji** — persona CV H1 headings use `# Name Emoji — Role`; fix "a agent" → "an agent".
7. **Stack-mismatch report** — for every copied agent with a stack-bound rulebook body, compare the body's bound stack against the detected stacks from step 1. Current bound bodies: `atrium` → React/web, `bastion` → NestJS-TS + Python, `crucible` → Vitest/Playwright, `lumen` → web. Every mismatch (bound stack not among the target's detected stacks) goes into the migration summary as a row: agent, rulebook body, bound stack, detected stacks, note `adapt destination-side`. Report only — never write an adaptation artifact into the target, never rewrite the rulebook during migration.

### 7. Verify (re-diff)

- **Re-diff** — re-run the step-1 inventory diff. Every selected item must now be `present`; present-count = previous-present + selected-count. If any selected item is still `missing`, or any item is now `partial`, **FAIL** — do not report success.
- **Pointer sweep** — loop `.opencode/agents/*.md` and `agents/*/profile.md` references; none may point to a non-installed agent.
- **Roster count** — AGENTS.md, knowledge/agents.md, and sentinel audit lists must name exactly the installed roster.
- **Frontmatter** — every spec has `name` = basename, `description`, `mode: subagent`.
- **Build** — run the target's build command (`pnpm build` or equivalent) — must pass.

## Kind vocabulary

Kind is a closed set of 4 values:

| Kind | Meaning | Selectable? |
|---|---|---|
| `skill` | a skill directory under `.opencode/skills/` | yes |
| `agent` | a roster member — `.opencode/agents/<name>.md` and/or `agents/<name>/profile.md` | yes |
| `infra` | a shared-infra file or dir (`knowledge/`, `plans/`, `user-stories/`) | yes |
| `config` | a merge target (`AGENTS.md`, `opencode.jsonc`, `.gitignore`) | no — merge-only, step 5 |

Hard corollaries:

- File count lives in the **Source** column, never in a new Kind. `investigator` (spec-only) and `cipher` (CV-only) are Kind `agent`; their reduced file set is expressed by Source.
- `config` has **no `scope` value** because it is not selectable.
- **No 5th Kind.** Any future special case is encoded via Source + Include-rule, not a new Kind value.

## Core manifest

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
| `bastion` | agent | `.opencode/agents/bastion.md` + `agents/bastion/profile.md` | `<target>/.opencode/agents/bastion.md` + `<target>/agents/bastion/profile.md` | backend stack OR any selected skill ships Python scripts |
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
| `cipher` | agent | `agents/cipher/profile.md` | `<target>/agents/cipher/profile.md` | always (CV-only, no runtime spec) |
| `knowledge/agents.md` | infra | `knowledge/agents.md` | `<target>/knowledge/agents.md` | always |
| `knowledge/debt.md` | infra | `knowledge/debt.md` | `<target>/knowledge/debt.md` | always |
| `symptom-problem-register` | infra | `knowledge/symptoms.md` + `knowledge/problems.md` | `<target>/knowledge/symptoms.md` + `<target>/knowledge/problems.md` | always |
| `plans/` | infra | `plans/.gitkeep` | `<target>/plans/.gitkeep` | always |
| `user-stories/` | infra | `user-stories/.gitkeep` | `<target>/user-stories/.gitkeep` | always |
| `AGENTS.md` | config | (generated) | `<target>/AGENTS.md` | merge, not copy |
| `opencode.jsonc` | config | (permission block) | `<target>/opencode.jsonc` | merge, not copy |
| `.gitignore` | config | (entries) | `<target>/.gitignore` | merge, not copy |

## Examples

### Example 1 — frontend portfolio (dev team + cross-cutting + lead)

Target: a Next.js frontend project, no ticket system. Scope: `all`. Detected stacks: `node` (package.json at root).

- Skills: all except `ticket-runbook`
- Agents: `atrium`, `bastion`, `crucible`, `forge`, `herald`, `lumen`, `sentinel`, `warden`, `inquisitor`, `augur`, `marshal`, `vault`, plus Cipher 🔓 (Lead Orchestrator) — bastion is included because `op-model` and `plan-enforce` (always-include skills) ship Python scripts it audits
- Consistency pass removes: incident-team references in `augur.md`/`marshal.md`/Cipher CV, sentinel audit lists trimmed to installed agents, missing `name:` frontmatter added — bastion references stay intact
- Stack-mismatch report flags all four bound bodies: `atrium` (React/web), `bastion` (NestJS-TS + Python), `crucible` (Vitest/Playwright), `lumen` (web) — detected stacks: `node`; no bound body's stack label is `node` → adapt destination-side

### Example 1b — Rust TUI tool (gitez class)

Target: a Rust TUI client (`Cargo.toml` at root), no ticket system. Scope: `all`. Detected stacks: `rust` — no backend stack.

- Skills: all except `ticket-runbook`
- Agents: the full dev team + cross-cutting set including `bastion` — eligible via the Python-script branch (`op-model`, `plan-enforce` ship `scripts/*.py`), not the backend branch
- Consistency pass removes: ticket-team references only; bastion references stay intact
- Stack-mismatch report flags all four bound bodies: `atrium` (React), `bastion` (NestJS-TS), `crucible` (Vitest/Playwright), `lumen` (web) → adapt destination-side

### Example 2 — skills and infra install

Target: any project that wants the git/planning workflows without the agent roster. Scope: `all` — in step 2, select the 7 applicable skills plus the infra files, leaving agents unselected.

- Copy the 7 applicable skills + `knowledge/agents.md`, `knowledge/debt.md`, the `symptom-problem-register` item (`knowledge/symptoms.md` + `knowledge/problems.md`), `plans/`, `user-stories/`
- Merge `.gitignore` and `opencode.jsonc`; no AGENTS.md roster, no subagents

### Example 3 — incremental migration

Target already has 12 agents + 6 skills (from a prior migration). User runs the skill.

- Inventory shows 2 missing eligible items (`op-model` skill, `warden` agent) and 1 `partial` (spec present, CV missing).
- The partial is reported and blocked. User selects only `op-model`.
- Result: only `op-model` copies; AGENTS.md/appends unchanged (no new agent); consistency pass runs on the union; re-diff shows present-count +1 and `op-model` now present → PASS. The remaining 1 missing item stays missing (deferred).

## Troubleshooting

- **Copied spec references an agent that was not installed** — e.g. `forge.md` reads `.opencode/agents/bastion.md`. Cause: verbatim copy of a spec written for the full roster. Fix: trim the reference (warmup read, gate, roster line) to the installed set.
- **Roster list names agents that were not installed after a later agent addition** — Cause: a trim became stale when the roster grew. Fix: re-run step 6, align every roster list to the current installed set.
- **Spec is missing `name:` frontmatter** — Cause: the source project shipped the spec without it. Fix: add lowercase `name` matching the filename, plus `description` and `mode: subagent`.
- **CV and runtime spec disagree** — e.g. the CV claims the agent posts GitHub comments, the spec forbids it. Cause: separate files drifting. Fix: align the CV to the spec's Hard Rules.
- **`pnpm build` fails after install** — Cause: native build scripts ignored by pnpm 11. Fix: run `pnpm approve-builds` and rebuild.
- **Item present but partial** — spec exists, CV missing (or vice versa). Cause: interrupted or manual prior copy. Fix: fail closed; ask the user whether to re-copy the pair or leave it; never auto-repair.
- **Item present but from an older core** — destination copy is stale vs current AICore. Cause: prior migration of an earlier core. Fix: offer explicit re-copy (user override), never silent overwrite.
- **Target has a custom item with a core name** — destination has its own `SKILL.md`/spec under a manifest name but it is not a core item. Cause: name collision. Fix: the manifest whitelist governs; the target's file is treated as `present` and skipped, reported to the user.
