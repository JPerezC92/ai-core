# `distribution-clearance.json` — format definition

**Source of truth** for the distribution-clearance registry format. The sync tool implementation (`core_sync_pkg`), its tests, and the registry file conform to this document; a format change updates this file first.

## Version policy

The document carries `"schema": 1`. The version stays **v1** through every compatible change — new optional fields, new record kinds that existing parsers accept, new cleared sources. It bumps **only** when a change breaks this design, i.e. when existing records or parsers become incompatible. Nothing else warrants a bump.

## Document shape

```json
{ "schema": 1, "cleared": { "<repo-relative path>": <record>, ... } }
```

`cleared` keys are unique repo-relative paths. A key ending in `/` is a **skill root**; every other key is a **file**.

## Record kinds

| Kind | Key | Record | Mode semantics |
|---|---|---|---|
| Root runtime | `AGENTS.md` | `{"mode": "region", "role": "root"}` | core region only; `role: root` is unique to this row |
| Harness config | `opencode.jsonc` | `{"mode": "merge"}` | top-level JSON(C) key merge, destination-only keys preserved; the `mcp` key merges by server name, keeping destination-only MCP servers and making a same-named entry core-wins |
| Story payload | `user-stories/<slug>.md` (portable) | `{"mode": "region"}` | core region only (shared contract); project region is destination-owned |
| Story payload (source-local) | `user-stories/<slug>.md` (source-only) | *(absent — not cleared)* | story exists in the source catalogue but is never delivered |
| Knowledge documents | `knowledge/*.md` | `{"mode": "region"}` | core region only (core/project markers) |
| Agent specs | `.opencode/agents/*.md` | `{"mode": "region"}` | core region only (core/project markers) |
| Persona profiles | `agents/*/profile.md` | `{"mode": "region"}` | core region only |
| Skill roots | `.opencode/skills/<name>/` | `{"mode": <default>, "region_files": [<paths>]?}` | see below |

Agent specs and persona profiles migrate as **per-file rows** — one row per file, one shared shape. They are not folded into root entries.

## Skill-root records

- `mode` is the default mode of every file under the root.
- `region_files` is optional (absent = empty subset) and names root-relative files that instead use **region** mode. Today the only member is `SKILL.md` — within a skill root, the only file type governed by active core/project ownership markers. Raw references may illustrate marker literals without interpreting them, as described under **Story distribution**.
- Current classification: the four workflow roots (`plan-enforce`, `query-verification`, `ticket-runbook`, `user-story`) declare `{"mode": "raw", "region_files": ["SKILL.md"]}`; the six tooling roots (`git-branch-name`, `git-commit`, `git-pr`, `op-agent-creator`, `op-model`, `op-skill-creator`) declare `{"mode": "raw"}`.
- **Expansion** — the sync tool identifies the files at every sync: every file under the root joins the sync set; `region_files` members deliver only their core region; all others copy byte-for-byte; interpreter caches (`__pycache__` path parts, `*.pyc` suffixes) never join. Files added under a root later join automatically. Clearance records durable ownership, not file inventories.

## Knowledge distribution classes

The five cleared `knowledge/` sources are region rows whose core/project split expresses their distribution class:

| Class | Files | Core ships |
|---|---|---|
| Shared rules | `knowledge/agents.md` | the shared rules; source-side extensions stay project |
| Record-bearing register (frame-only core) | `knowledge/debt.md` | the frame alone — the register carries no table; filed records never ship |
| Shared catalog (full core) | `knowledge/problems.md`, `knowledge/symptoms.md` | the full catalog |
| Living design (contract core, local refinement state) | `knowledge/diagnostic-system-design.md` | the shared contract; refinement state stays project |

- The debt register's core is frame-only and carries no table: its records are the source's own filed history, and the frame is the retired template seed's payload.
- Whatever the class, destination-owned records live in the destination's project region and are never substituted by a sync.

## Story distribution

Eleven shared story contracts use explicit per-file `region` rows. The core region holds the approved shared contract (H1/metadata, Persona, Goal, Scenario, Acceptance criteria with shared marks, portable Proof, Constraints). The project region holds source-local or destination-local evidence, approval records, revision tracking, and Change log. Three source-only stories (`core-sync`, `aicore-adoption-governance`, `python-pytest`) and the source `user-stories/index.md` are **not cleared** and never ship. Existence in the source catalogue alone is not clearance.

A literal region marker pair inside a raw template or fenced example is ordinary content: raw mode copies it byte-for-byte without interpreting it. Only region-mode rows carry active core/project markers.

## Scope rules

- Root entries cover **skill roots only** for now. Agent specs, persona profiles, and every other non-skill source stay per-file rows; the scope widens only with an explicit design change (which, being compatible, does not bump the version).
- The sync tool's own skill (`.opencode/skills/core-sync/`) is never a cleared key and reaches no destination.
- Only region-mode rows use active core/project ownership markers — `SKILL.md` within a skill root, and region file rows (the root runtime, agent specs, persona profiles, knowledge documents, shared stories). Raw and merge transport does not interpret ownership markers; marker literals in a raw reference or fenced example remain ordinary copied bytes, not a separate region binding.
- Modes: `region` (delivers only the source core region; the destination owns its project region), `raw` (byte-for-byte copy), `merge` (top-level key merge — config only; the `mcp` key merges by server name, keeping destination-only MCP servers and making a same-named entry core-wins).

## Validation

A document is valid when `core_sync_pkg.domain.clearance.parse_clearance` accepts it: schema exactly `1`; keys unique and repo-relative; skill-root keys end with `/`; `region_files` members are root-relative, stay inside the root, and contain no `..` or absolute paths; `role` appears at most once and only on a `region` record (this registry uses `role: root` on `AGENTS.md` only). Any other version label is rejected (exit 2) — there is no version migration.
