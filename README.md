# AICore

A reusable, agnostic **agentic orchestration core** for [OpenCode](https://opencode.ai): a lead-orchestrator runtime, a role-separated specialist roster, a skill library, shared evidence rules, and an ODD feature-document lifecycle. Another project adopts it **atomically** — one AICore revision for the complete applicable unit set — and customizes it there; the core itself stays neutral.

## Find the owner for your task

| Task | Start here |
|---|---|
| Act on a request | [AGENTS.md](AGENTS.md) is the lead runtime; [knowledge/agent-workflow.md](knowledge/agent-workflow.md) is the single workflow router, including ODD classification and task-specific reads. |
| Check evidence, coordination or safety obligations | [knowledge/agents.md](knowledge/agents.md); runtime authority and automatic edit/release/PR gates remain in [AGENTS.md](AGENTS.md) and the assigned specialist runtime. |
| Work on a feature | `odd/tasks/<feature-name>.md`, created from [odd/tasks/_template.md](odd/tasks/_template.md) through `.opencode/skills/odd-workflow/SKILL.md`; Specs, Tasks and Log are the single feature record. |
| Select architecture or testing definitions | [architecture/README.md](architecture/README.md); [architecture/testing/architecture.md](architecture/testing/architecture.md) owns testing. Runtimes own procedures and gates; documentation acceptance is not implementation conformance. |
| Reuse research or read explanatory documentation | [docs/README.md](docs/README.md) → [research catalog](docs/research/README.md). Research and history are evidence, not execution authority. |
| Investigate an incident | `knowledge/symptoms.md`, `knowledge/problems.md`, and the register-first procedure in `knowledge/agents.md`; incident skills are `.opencode/skills/ticket-runbook/SKILL.md` and `.opencode/skills/query-verification/SKILL.md`. |
| Author skills/agents or change models | `.opencode/skills/op-skill-creator/SKILL.md`, `.opencode/skills/op-agent-creator/SKILL.md`, `.opencode/skills/op-model/SKILL.md`. |
| Prepare Git/release artifacts | `.opencode/skills/{git-branch-name,git-commit,git-pr}/SKILL.md`; Git execution belongs to Herald 📯 (Release Manager), under the runtime gates. |
| Adopt or update the core | [Adoption guide below](#using-it-in-another-project), [AGENTS.md → Reuse guide](AGENTS.md#reuse-guide-adopting-this-core), and `.opencode/skills/core-sync/SKILL.md`. |
| Inspect legacy plans | `plan-enforce` is migration-only, apart from user-confirmed legacy PR-merge cleanup. Historical `plans/` references do not imply a current directory. |

The safety policy and role-specific permissions live in [opencode.jsonc](opencode.jsonc): force-push, PR merge, `sudo`, system-path `rm -rf` and env-file reads are denied; the `plan` agent cannot edit. Irreversible actions remain User-Authority-Only. This map locates owners rather than replacing their instructions.

## Roster

| Agent | Team |
|---|---|
| Cipher 🔓 (Lead Orchestrator) | cross-cutting |
| Augur 🔮 (Research Analyst) | cross-cutting |
| Marshal 🎖️ (HR Director) | cross-cutting |
| Vault 🔐 (Catalog Steward) | cross-cutting |
| Investigator 🔍 (Incident Investigator) | incident |
| Ledger 📒 (Record Keeper) | incident |
| Quill 🪶 (Note Drafter) | incident |
| Scribe ✍️ (Docs & Problems Manager) | incident |
| Atrium 🏛️ (Frontend Architect) | dev |
| Bastion 🧱 (Backend & Scripts Architect) | dev |
| Crucible 🔥 (Test Architect) | dev |
| Forge 🔨 (Implementer) | dev |
| Herald 📯 (Release Manager) | dev |
| Inquisitor 🔎 (PR Reviewer) | dev |
| Lumen ✨ (Visual Director) | dev |
| Sentinel 🛡️ (Quality Guardian) | dev |
| Warden 🔒 (Dependency Warden) | dev |

Persona CVs live at `agents/<name>/profile.md`; runtime specs at `.opencode/agents/<name>.md` (Cipher's runtime spec is the root `AGENTS.md` by design). The spec carries workflow only, the CV carries personality — they never duplicate each other.

## Repository map

```
AGENTS.md                     Lead runtime: mandatory core + source-project bindings/reuse guide
opencode.jsonc                OpenCode V2 config: agent/model bindings, permission model, MCP servers
opencode.v1.jsonc             Distinct OpenCode V1 compatibility config, not a byte-identical V2 copy
magic-context.jsonc           magic-context disabled — native OpenCode compaction owns context
.opencode/agents/             Specialist runtimes: authority, procedures, scope, gates and reporting
.opencode/skills/             Skill-local SKILL.md, references/ and scripts/ (including nested tests)
agents/<name>/profile.md      Persona CVs, including the lead; no duplicated runtime workflow
knowledge/agent-workflow.md   Shared ODD workflow and task router
knowledge/agents.md           Shared rules; source-side extensions stay project-owned
knowledge/debt.md             Accepted-debt register: shared frame, project-owned filed entries
knowledge/symptoms.md         Shared symptom-class catalog
knowledge/problems.md         Shared known-problem register (empty of rows as shipped)
knowledge/diagnostic-system-design.md  Shared living design; source-local refinement state stays project
architecture/                 Shared common/shape/implementation and testing contracts/templates/guides
docs/README.md                Source-local documentation map, not a second workflow router
docs/research/                Durable research catalog, single template and domain/topic records
docs/architecture/            Source-local ADRs and historical accounting, not shared dependencies
odd/tasks/                    Current feature records and the canonical _template.md
distribution-clearance.json   Per-file distribution clearance; definition in distribution-clearance.definition.md
tests/                        Repository-level tests; skill tests stay with their scripts
conftest.py                   Repository-wide pytest temporary-directory policy
pyproject.toml  uv.lock       Python toolchain/dependencies and pytest discovery/worker configuration
output/                       Gitignored temporary audits, research drafts, design and test artifacts
```

## Using it in another project

The detailed adoption instructions below are retained alongside the runtime's reuse guide. The source operator must obey [AGENTS.md → Destination modification boundary](AGENTS.md#destination-modification-boundary-hard-rule): synchronization and report reading only. Destination reconciliation, `pending` and blocker mutations belong to the destination's agents; the instructions below do not authorize the source operator to perform them. Cleanup and Git actions retain their existing user-authorization gates.

### Existing project — atomic adoption via `core-sync`

1. Start only from a destination that is already clean and saved. `core-sync` performs no cleanliness check — confirming the destination is clean and saved is an operator pre-flight. Run `core-sync init --bind-cleared` from an AICore checkout after an approved source refresh. Inspect the selected revision's clearance and every applicable target precondition in `.opencode/skills/core-sync/SKILL.md` first — existing merge targets and raw-target parent requirements remain binding, and markerless or new region paths require enrollment before they can sync. It enrolls the **complete applicable unit set** at one AICore revision using the cleared modes: each file's `core` region gets the source core, and the file's previous body moves into the destination-owned `project` region. Review every `.aicore/reconciliation/` report under the core-wins rule, resolve the destination-root reconciliation blocker, and clear `pending`; `core-sync check` must exit `0` before the enrollment is accepted. Do not treat enrollment as an application build.
2. Keep the shared knowledge infrastructure. Copying follows each unit's cleared mode: a region-mode source delivers its `core` region while the destination's `project` bytes are preserved, a raw source is copied whole, and a merge source replaces the source-owned top-level keys (the `mcp` key alone merging by server name, core-wins on a same-named server while destination-only MCP servers survive). The clearance registry (`distribution-clearance.json`, format defined in `distribution-clearance.definition.md`) declares the cleared set. The register tables of the three shared registers (`knowledge/agents.md`, `knowledge/problems.md`, `knowledge/symptoms.md`) live in the core region and copy with it like every core region — no table declarations exist. The shared rules ship, with source-side extensions staying project (`knowledge/agents.md`). The shared workflow entry ships as `knowledge/agent-workflow.md`. New work uses `odd/tasks/` feature documents; plan adoption remains legacy migration. The shared catalogs ship in full: `knowledge/symptoms.md` (symptom-class catalog) and `knowledge/problems.md` (known-problem register, empty of rows as shipped). The debt register (`knowledge/debt.md`) ships its frame alone — the payload the retired 0-entry seed used to carry — and its filed entries are project-region content: AICore's filed debt is never copied into a destination, and no seed template ships. The living design ships its shared contract as `knowledge/diagnostic-system-design.md`, its local refinement state staying project. Destination-filed records live in the destination's project region, survive every sync, and are never substituted — distinguish filed history, which never ships, from the shared catalog, which does.
3. Select architecture through `architecture/README.md`: common contract, applicable shape(s), implementation guide, then `architecture/testing/architecture.md` and its testing guide. If your stack differs, adapt only destination-owned project extensions/configuration; copy `architecture/stacks/_template.md` for implementation mappings or `architecture/testing/stacks/_template.md` for testing mappings and obtain the applicable review. Runtime specs retain procedures and gates. Record destination reconciliation in its `.aicore/reconciliation/` records; do not replace mandatory bytes. Source-local ADRs are explanatory, not required shared dependencies.
4. Substitute your real tooling only in destination-owned project extensions or destination configuration. Do not edit protected mandatory text. The core ships neutral on purpose. The new architecture files have explicit per-file clearance and must arrive with their consumers; testing documents live only under `architecture/testing/`. They require destination-authorized `init --bind-cleared` enrollment at the selected revision; `apply` alone is insufficient for new or markerless paths. Destination agents alone reconcile displaced duplicates and local extensions; nonempty `pending` or a reconciliation blocker blocks acceptance until `check` exits `0`. This source update does not perform or claim destination migration.
5. Recurring updates run from an AICore checkout, after an approved refresh of the protected upstream tip, using the absolute path `.opencode/skills/core-sync/scripts/core_sync.py`:

   ```bash
   uv run --frozen python3 .opencode/skills/core-sync/scripts/core_sync.py apply \
     --source <source-dir> --destination <destination-dir> \
     --bindings <bindings-file> --source-revision <40-hex>
   uv run --frozen python3 .opencode/skills/core-sync/scripts/core_sync.py check \
     --source <source-dir> --destination <destination-dir> \
     --bindings <bindings-file> --source-revision <40-hex>
   ```

   `apply` splices each source `core` region into its destinations (and byte-copies raw bindings or merges a JSON/JSONC config's top-level keys, the `mcp` key by server name) and pins the revision; `check` verifies every destination core region against the pinned revision and requires `pending` empty, exiting `0` only when current. A failed `check` blocks acceptance until the drift is reconciled. A local branch that was not refreshed is not live remote truth.

### New project — start from this repository

Clone AICore, then remove only source-local state so the fresh project starts clean: historical `plans/` if present, `output/`, `docs/architecture/`, `docs/research/`, `docs/README.md` (remove or rewrite as the destination's own documentation map), `knowledge/debt.md` filed entries, AICore's git history, and each delivered file's source-local `project` content. ODD feature documents in `odd/tasks/` are the active record; `plans/` remain migration inputs. Keep destination-owned records, evidence, and history intact. Customize the project-extensions sections (stack rulebooks, `knowledge/`, MCP servers, models) to your stack, and keep the core regions untouched. Do not treat the clone as enrolled: future `core-sync apply` or `core-sync check` runs require an authorized enrollment first — `core-sync init --bind-cleared` from a **separate** AICore source checkout at the selected revision, under the same clearance and applicable-target-precondition review as any destination. Never run core-sync with an overlapping source and destination root, and never assemble the destination's `.aicore/core.yaml` bindings by hand; the enrollment writes the bindings and pins the revision.

## Development

- **Environment** — `python3` (not `python`), Python ≥ 3.13, managed with `uv`. Every Python command runs through the project environment: `uv run --frozen …`, never a bare or global interpreter.
- **Tests** — the reviewed whole-suite command is `uv run --frozen --group dev pytest -q`, dispatched to Crucible 🔥 (Test Architect) under `.opencode/agents/crucible.md`; this page is not execution authorization or a test result. `pyproject.toml` configures repository-wide `test_*.py` discovery and pytest-xdist workers. Scope includes core-sync, plan/runbook validators, query verification and other skill machinery. Repository tests live in `tests/`; skill tests stay throughout `.opencode/skills/<skill>/scripts/**/test_*.py`, including layered subpackages (e.g. `.opencode/skills/op-model/scripts/op_model_lookup/domain/test_catalog.py`). `conftest.py` owns the default in-repository temporary-root setup.
- **Authoring** — use the `op-skill-creator` and `op-agent-creator` skills to scaffold skills/agents, and `op-model` to change agent models deterministically.
- **Config changes** — the OpenCode TUI must be restarted after any `opencode.jsonc` permission change; active sessions do not reload it. AICore's `opencode.jsonc` targets the OpenCode V2 config definition, and `opencode.v1.jsonc` preserves the V1 config for an OpenCode V1 binary.
- **Workflow and runtime changes** — read `knowledge/agent-workflow.md` before acting; it owns classification, feature timing and the task router, with shared-resource rules in `knowledge/agents.md`. Synced spec versions follow `AGENTS.md` → Reuse guide, including destination-local version markers; local history and feature Log never replace that policy. Restart OpenCode after accepting runtime or skill changes; the active session does not hot-reload them.

## Notes

- Everything is OpenCode-native: agent specs in `.opencode/agents/`, skills in `.opencode/skills/` (`compatibility: opencode`), and feature documents in `odd/tasks/`. Historical `plans/` citations are migration provenance, not a claim that those paths still exist. Source-local architecture decisions/history and saved research are mapped by `docs/README.md` unless that map is removed or rewritten as the destination's own documentation map.
- `output/` is gitignored — it holds temporal artifacts (audit reports, research briefs, design briefs/audits); agents create it on first write.
- Skills `git-commit` and `git-pr` write `output/commit.txt` / `output/pr-draft.md` (covered by the `output/` ignore) and, with `git-branch-name`, assume git + pnpm and the GitHub CLI (`gh`) — the dev-team defaults.
- Each destination's adopted content is bound by its own `.aicore/core.yaml`: it maps each source file to its destination paths and pins the `core_revision` the destination was enrolled at. The bindings are destination-owned state — AICore keeps no adopter registry.
- This project uses the local memories.sh store via the `memories` MCP server as a **cache** of repo-derivable facts; durable knowledge belongs in repo surfaces (`knowledge/`, skill Troubleshooting), never memory-only.
