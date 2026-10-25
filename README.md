# AICore

A reusable, agnostic **agentic orchestration core** for [OpenCode](https://opencode.ai): a lead-orchestrator runtime, a role-separated specialist roster, a skill library, shared evidence rules, and an ODD feature-document lifecycle. Another project adopts it **atomically** — one AICore revision for the complete applicable unit set — and customizes it there; the core itself stays neutral.

## What you get

- **One lead, many specialists** — Cipher 🔓 (Lead Orchestrator) triages every request, dispatches independent ready tasks concurrently — including multiple instances of the same role — and serializes work that shares a dependency, resource, gate, or capacity limit. Each assignment names its inputs, exclusive resources, and output. Results are accepted before dependent work continues. Subagents report to the lead; they do not address the user.
- **Evidence discipline** — facts vs. labeled `hipótesis:` vs. forbidden assumptions; every quantitative claim traces to a cited measurement, every report leads with a verdict and stays ≤ 60 lines (`knowledge/agents.md`).
- **Safety rails** — a least-privilege permission model in `opencode.jsonc`: force-push, PR merges, `sudo`, system-path `rm -rf`, and env-file reads are denied; the `plan` agent cannot edit files; irreversible actions are User-Authority-Only.
- **ODD workflow** — one feature document per feature at `odd/tasks/<feature-name>.md`, created from `odd/tasks/_template.md` with the `odd-workflow` skill. Specs, Tasks, and Log are the single record; tracking precedes the first write; close reports the verified outcome and every failed or pending check.
- **Automatic architecture gates** — after a frontend edit, Atrium 🏛️ (Frontend Architect); after a backend or script edit, Bastion 🧱 (Backend & Scripts Architect); after a test-file edit, Crucible 🔥 (Test Architect). The worker returns the edit for review and continues only after the lead accepts the current verdict and explicitly resumes it. Inquisitor 🔎 (PR Reviewer) reviews each PR head, and Warden 🔒 (Dependency Warden) reviews manifest changes before they are staged.
- **Skill library** — ODD workflow (`odd-workflow`), core distribution (`core-sync`), git workflow (`git-branch-name`, `git-commit`, `git-pr`), OpenCode authoring (`op-agent-creator`, `op-skill-creator`, `op-model`), and incident tooling (`ticket-runbook`, `query-verification`). `plan-enforce` handles existing legacy plans and user-confirmed legacy PR-merge cleanup; `user-story` remains migration-only.
- **Knowledge registers** — shared agent rules, an accepted-debt register, a diagnostic symptom catalog, a known-problem register, and a living design.
- **Tested tooling** — the pytest suite covers the Python machinery (core-sync, plan validators, runbook validators, query verification) and runs worker-parallel.
- **Atomic, versioned distribution** — `core-sync` splices protected `core` regions into destination projects, byte-copies whole files, or merges a JSON/JSONC config's top-level keys (source keys winning, destination keys and comments kept — the `mcp` key alone merges by server name, core-wins on a same-named server while destination-only MCP servers survive), pins the source revision in the destination's own bindings file, and keeps acceptance blocked on any drift.

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

## What's inside

```
AGENTS.md                     Cipher's runtime spec: mandatory core + roster + reuse guide
opencode.jsonc                OpenCode V2 config: agent/model bindings, permission model, MCP servers
opencode.v1.jsonc             OpenCode V1 config backup (byte-identical), for an OpenCode V1 binary
magic-context.jsonc           magic-context disabled — native OpenCode compaction owns context
.opencode/agents/             16 subagent runtime specs (OpenCode subagents)
.opencode/skills/             12 skills (odd-workflow, core-sync, git-branch-name, git-commit,
                              git-pr, op-agent-creator, op-model, op-skill-creator, plan-enforce,
                              query-verification, ticket-runbook, user-story) — each with SKILL.md + scripts/
agents/<name>/profile.md      17 persona CVs (incl. cipher)
knowledge/agents.md           Shared agent rules (evidence/report discipline, hard rules) —
                              shared rules ship, source-side extensions stay project
                              (register table copies with its core region)
knowledge/agent-workflow.md   Shared ODD entry — seven-step protocol, feature document, template rule
docs/architecture/            Source-local ADRs and historical decision records
knowledge/debt.md             Accepted-debt register — frame-only core (entry format and rules);
                              filed entries are project-region content and never ship
knowledge/symptoms.md         Diagnostic symptom-class catalog — shared catalog, ships in full
                              (register table copies with its core region)
knowledge/problems.md         Known-problem register — shared catalog, ships in full, empty of
                              rows as shipped (register table copies with its core region)
knowledge/diagnostic-system-design.md  Diagnostic-system living design (incident query
                                       verification implemented, broader design deferred); shared contract
                                       ships, local refinement state stays project
odd/tasks/                    ODD feature documents: one file per feature, created from
                              odd/tasks/_template.md; legacy plans/ and user-stories/ remain for migration
pyproject.toml  uv.lock       Python toolchain (uv; pytest + pytest-xdist in the dev group)
output/                       Temporal working space (audits, research, design — gitignored)
```

## Using it in another project

### Existing project — atomic adoption via `core-sync`

1. Start only from a destination that is already clean and saved. `core-sync` performs no cleanliness check — confirming the destination is clean and saved is an operator pre-flight. Run `core-sync init --bind-cleared` from an AICore checkout after an approved source refresh. Inspect the selected revision's clearance and every applicable target precondition in `.opencode/skills/core-sync/SKILL.md` first — existing merge targets and raw-target parent requirements remain binding, and markerless or new region paths require enrollment before they can sync. It enrolls the **complete applicable unit set** at one AICore revision using the cleared modes: each file's `core` region gets the source core, and the file's previous body moves into the destination-owned `project` region. Review every `.aicore/reconciliation/` report under the core-wins rule, resolve the destination-root reconciliation blocker, and clear `pending`; `core-sync check` must exit `0` before the enrollment is accepted. Do not treat enrollment as an application build.
2. Keep the shared knowledge infrastructure. Copying follows each unit's cleared mode: a region-mode source delivers its `core` region while the destination's `project` bytes are preserved, a raw source is copied whole, and a merge source replaces the source-owned top-level keys (the `mcp` key alone merging by server name, core-wins on a same-named server while destination-only MCP servers survive). The clearance registry (`distribution-clearance.json`, format defined in `distribution-clearance.definition.md`) declares the cleared set. The register tables of the three shared registers (`knowledge/agents.md`, `knowledge/problems.md`, `knowledge/symptoms.md`) live in the core region and copy with it like every core region — no table declarations exist. The shared rules ship, with source-side extensions staying project (`knowledge/agents.md`). The shared workflow entry ships as `knowledge/agent-workflow.md`. New work uses `odd/tasks/` feature documents; story and plan adoption remains legacy migration. The shared catalogs ship in full: `knowledge/symptoms.md` (symptom-class catalog) and `knowledge/problems.md` (known-problem register, empty of rows as shipped). The debt register (`knowledge/debt.md`) ships its frame alone — the payload the retired 0-entry seed used to carry — and its filed entries are project-region content: AICore's filed debt is never copied into a destination, and no seed template ships. The living design ships its shared contract as `knowledge/diagnostic-system-design.md`, its local refinement state staying project. Destination-filed records live in the destination's project region, survive every sync, and are never substituted — distinguish filed history, which never ships, from the shared catalog, which does. Shared story contracts move like every other cleared source: the twelve portable story contracts deliver their `core` region — shared metadata through Constraints and portable Proof — while local evidence, approval records, revision tracking, and Change log stay in the destination-owned `project` region, and source-local state never ships. The six non-cleared stories (`user-stories/core-sync.md`, `user-stories/aicore-adoption-governance.md`, `user-stories/python-pytest.md`, `user-stories/concise-skill-authoring.md`, `user-stories/pr-review-corrections.md`, `user-stories/response-note-drafting.md`) and the source `user-stories/index.md` are not delivered. The destination owns its `plans/`, its own stories and filed records, and one destination-owned `user-stories/index.md` reconciled against the actual shared and local files; reconciling an enrolled story keeps genuine destination-owned stories, records, evidence, and history and removes only duplicate shared text displaced into its project body.
3. If your stack differs, adapt only the project-extensions sections of the stack-specific rulebooks (`atrium.md`, `bastion.md`, `crucible.md`, `lumen.md`) before adopting the core, and record that review in the destination's `.aicore/reconciliation/` records. Do not replace mandatory bytes.
4. Substitute your real tooling only in destination-owned project extensions or destination configuration. Do not edit protected mandatory text. The core ships neutral on purpose.
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

Clone AICore, then remove only source-local state so the fresh project starts clean: `plans/`, `output/`, `docs/architecture/`, `knowledge/debt.md` filed entries, AICore's git history, each delivered file's source-local `project` content, and the six non-cleared stories (`user-stories/core-sync.md`, `user-stories/aicore-adoption-governance.md`, `user-stories/python-pytest.md`, `user-stories/concise-skill-authoring.md`, `user-stories/pr-review-corrections.md`, `user-stories/response-note-drafting.md`) and source `user-stories/index.md` that are never delivered. ODD feature documents in `odd/tasks/` are the active record; `plans/` and `user-stories/` are migration inputs. Retain the shared story cores — the twelve portable story contracts keep their shared contract in `core` and an empty `project` region — and keep any destination-owned stories, records, evidence, and history intact. Reconcile one destination-owned `user-stories/index.md` against the actual shared and local files. Customize the project-extensions sections (stack rulebooks, `knowledge/`, MCP servers, models) to your stack, and keep the core regions untouched. Do not treat the clone as enrolled: future `core-sync apply` or `core-sync check` runs require an authorized enrollment first — `core-sync init --bind-cleared` from a **separate** AICore source checkout at the selected revision, under the same clearance and applicable-target-precondition review as any destination. Never run core-sync with an overlapping source and destination root, and never assemble the destination's `.aicore/core.yaml` bindings by hand; the enrollment writes the bindings and pins the revision.

## Development

- **Environment** — `python3` (not `python`), Python ≥ 3.13, managed with `uv`. Every Python command runs through the project environment: `uv run --frozen …`, never a bare or global interpreter.
- **Tests** — `uv run --frozen --group dev pytest -q` runs the whole suite (worker-parallel via pytest-xdist; scope: core-sync, plan validators, runbook validators, query verification, and the other skill machinery). Skill tests live throughout each skill's `scripts/` tree, not only beside the entry script: `.opencode/skills/<skill>/scripts/**/test_*.py`, including layered subpackages (e.g. `.opencode/skills/op-model/scripts/op_model_lookup/domain/test_catalog.py`).
- **Authoring** — use the `op-skill-creator` and `op-agent-creator` skills to scaffold skills/agents, and `op-model` to change agent models deterministically.
- **Config changes** — the OpenCode TUI must be restarted after any `opencode.jsonc` permission change; active sessions do not reload it. AICore's `opencode.jsonc` targets the OpenCode V2 config definition, and `opencode.v1.jsonc` preserves the V1 config for an OpenCode V1 binary.
- **ODD discipline** — agents read `knowledge/agent-workflow.md` before acting. Small work is understood, risk-contained, and resumable from request plus diff; read-only and small work create no durable feature artifact. Non-small state-changing work tracks in `odd/tasks/<feature-name>.md` before the first write; copy `odd/tasks/_template.md` and use the `odd-workflow` skill. Feature scope is requirement/task-based, not a unique-file partition; shared resources follow the canonical owner and one-writer coordination rules. Specs never bump synced version numbers locally — destination-local changes live in git history and the feature document Log. Restart OpenCode after accepting runtime or skill changes; the active session does not hot-reload them.

## Notes

- Everything is OpenCode-native: agent specs in `.opencode/agents/`, skills in `.opencode/skills/` (`compatibility: opencode`), feature documents in `odd/tasks/`, and legacy plans/stories in `plans/` + `user-stories/` for migration. Source-local architecture decisions live in `docs/architecture/`.
- `output/` is gitignored — it holds temporal artifacts (audit reports, research briefs, design briefs/audits); agents create it on first write.
- Skills `git-commit` and `git-pr` write `output/commit.txt` / `output/pr-draft.md` (covered by the `output/` ignore) and, with `git-branch-name`, assume git + pnpm and the GitHub CLI (`gh`) — the dev-team defaults.
- Each destination's adopted content is bound by its own `.aicore/core.yaml`: it maps each source file to its destination paths and pins the `core_revision` the destination was enrolled at. The bindings are destination-owned state — AICore keeps no adopter registry.
- This project uses the local memories.sh store via the `memories` MCP server as a **cache** of repo-derivable facts; durable knowledge belongs in repo surfaces (`knowledge/`, skill Troubleshooting), never memory-only.
