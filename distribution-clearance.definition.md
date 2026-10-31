# `distribution-clearance.json` — format definition

**Source of truth** for the distribution-clearance registry format. The sync tool implementation (`core_sync_pkg`), its tests, and the registry file conform to this document; a format change updates this file first.

## Version policy

The document carries `"schema": 1`. The version stays **v1** through every compatible change — new optional fields, new record kinds that existing parsers accept, new cleared sources. It bumps **only** when a change breaks this design, i.e. when existing records or parsers become incompatible. Nothing else warrants a bump.

## Document shape

```json
{ "schema": 1, "cleared": { "<repo-relative path>": <record>, ... } }
```

`cleared` keys are unique repo-relative paths. A key ending in `/` is a **directory root**; every other key is a **file**.

## Record kinds

| Kind | Key | Record | Mode semantics |
|---|---|---|---|
| Root runtime | `AGENTS.md` | `{"mode": "region", "role": "root"}` | core region only; `role: root` is unique to this row |
| Harness config | `opencode.jsonc` | `{"mode": "merge"}` | top-level JSON(C) key merge, destination-only keys preserved; the `mcp` key merges by server name, keeping destination-only MCP servers and making a same-named entry core-wins |
| Knowledge documents | `knowledge/*.md` | `{"mode": "region"}` | core region only (core/project markers) |
| Architecture documents | explicit files under `architecture/` | `{"mode": "raw"}` | whole-file byte-for-byte transport with no ownership markers and no project region; no reconciliation report and no `pending` entry; common/shape contracts, implementation and testing templates/guides, and navigation; tools remain destination-owned |
| Directory roots | `.opencode/skills/<name>/`, `.opencode/agents/`, `agents/` | `{"mode": <default>, "region_files": [<paths>]?}` | root `mode` is the default mode of every file under the root; `region_files` overrides selected files; see below |

Agent specs are covered by the `.opencode/agents/` directory root and persona profiles by the `agents/` directory root — both `{"mode": "region"}`, so every file under them delivers only its core region between markers (`.opencode/agents/` holds `<name>.md`; `agents/` holds `<name>/profile.md`).

## Directory-root records

- `mode` is the default mode of every file under the root.
- `region_files` is optional (absent = empty subset) and names root-relative files that instead use **region** mode. Today the only member is `SKILL.md` — within a skill directory root, the only file type governed by active core/project ownership markers. Raw references may illustrate marker literals without interpreting them, as described under **Scope rules**.
- Current classification (twelve roots): the seven tooling skill roots (`.opencode/skills/git-branch-name/`, `.opencode/skills/git-commit/`, `.opencode/skills/git-pr/`, `.opencode/skills/op-agent-creator/`, `.opencode/skills/op-model/`, `.opencode/skills/op-skill-creator/`, `.opencode/skills/verified-pr-cleanup/`) declare `{"mode": "raw"}`; the three workflow skill roots (`.opencode/skills/odd-workflow/`, `.opencode/skills/query-verification/`, `.opencode/skills/ticket-runbook/`) declare `{"mode": "raw", "region_files": ["SKILL.md"]}`; the two agent directories (`.opencode/agents/`, `agents/`) declare `{"mode": "region"}` — their files are all region-mode sources, so neither needs `region_files`.
- **Expansion** — the sync tool identifies the files at every sync: every file under the root joins the sync set; `region_files` members deliver only their core region; every other file uses the root's default `mode` — `region` delivers only that file's core region, `raw` copies it byte-for-byte (mode semantics under **Scope rules**); interpreter caches (`__pycache__` path parts, `*.pyc` suffixes) never join. Files added under a root later join automatically. Clearance records durable ownership, not file inventories.

## Knowledge distribution classes

The eight cleared `knowledge/` sources are region rows whose core/project split expresses their distribution class:

| Class | Files | Core ships |
|---|---|---|
| Shared rules | `knowledge/agents.md` | the shared rules; source-side extensions stay project |
| Shared workflow | `knowledge/agent-workflow.md` | the reusable entry sequence; source-side extensions stay project |
| Shared release workflow | `knowledge/release.md` | packet, post-review routing, and execution-owner pointers; source-side grants stay project |
| Shared decision workflow | `knowledge/decisions.md` | the decision lifecycle and its propagation gate; the source-local ADR directory and its records stay project |
| Record-bearing register (frame-only core) | `knowledge/debt.md` | the frame alone — the register carries no table; filed records never ship |
| Shared catalog (full core) | `knowledge/problems.md`, `knowledge/symptoms.md` | the full catalog |
| Living design (contract core, local refinement state) | `knowledge/diagnostic-system-design.md` | the shared contract; refinement state stays project |

- The debt register's core is frame-only and carries no table: its records are the source's own filed history, and the frame is the retired template seed's payload.
- Whatever the class, destination-owned records live in the destination's project region and are never substituted by a sync.

## Architecture distribution

`architecture/` is a unified shared contract, not a knowledge register and not an extension surface. Each cleared architecture file has an explicit per-file `raw` row; no directory under `architecture/` is cleared wholesale, and only the skill roots and the two agent directories remain directory roots. Root expansion itself introduces no new schema behavior.

Every destination receives identical bytes, and `core-sync check` fails on any byte difference. That is a distribution guarantee, not a conformance guarantee: a reference library, runner, or framework named in a guide remains a reference choice, adopted by the destination in its own configuration or its own guide. No file under `architecture/` carries ownership markers or a project region, so nothing there produces a reconciliation report or a `pending` entry.

- `architecture/README.md` owns navigation and selection; `architecture/clean-architecture.md` owns common semantics.
- `architecture/shapes/frontend.md`, `architecture/shapes/backend.md`, and `architecture/shapes/scripts.md` own shape-specific responsibilities.
- `architecture/stacks/_template.md` is the implementation-guide template; `architecture/stacks/typescript/react.md`, `architecture/stacks/typescript/nestjs.md`, and `architecture/stacks/python.md` map the common/shape obligations without claiming application conformance.
- `architecture/testing/architecture.md` carries the language-agnostic test contract and the stack-guide index.
- `architecture/testing/stacks/_template.md` carries the single testing stack-guide template, distinct from the implementation-guide template.
- `architecture/testing/stacks/typescript.md` and `architecture/testing/stacks/python.md` preserve the reviewed testing implementations. Concrete runners and frameworks are reference implementations, not universal destination bindings.
- Testing documents ship only from `architecture/testing/`; the obsolete root compatibility files and their four clearance rows are removed.
- A destination records a selected stack or framework binding in its own configuration or its own guide; it must not weaken the shared contract.
- Adding a new stack guide uses the template and requires an authorized ODD feature and parity review before it is treated as `reference`.

Because a write replaces the destination file byte-for-byte, a destination edit to a distributed architecture file is overwritten by the next write and never enters `pending`; no reconciliation report exists for it, and only a `check` run before that write reports the drift. Divergence is destination-owned, never an in-file region: a destination that needs a different stack adds a guide copied from `architecture/stacks/_template.md` or `architecture/testing/stacks/_template.md`, and an unbound path survives every sync.

New required documents ship with their consumers at one selected revision. A destination must authorize `core-sync init --bind-cleared` enrollment for the new paths; `apply` alone does not enroll absent or markerless files. Architecture rows are `raw`, so they never raise a reconciliation report, a `pending` entry, or the destination-root reconciliation blocker — reconciliation applies to region-mode rows alone, which are the only rows whose displaced duplicates and local extensions a destination resolves. `core-sync check` must exit `0`. This source registry authorizes neither manual binding edits nor destination mutation and does not claim migration completed. Source-local ADRs, review histories, and inventories stay outside distributed core; documentation review is not implementation-conformance proof.

## Scope rules

- Root entries are **directory roots**. A directory may be cleared as a root only when every file under it is intended for distribution; every other source stays an individually cleared file row. This is the explicit design change the earlier skill-root-only scope anticipated — it is compatible, so `schema` stays `1` and no version-migration path is introduced.
- The tradeoff of that rule: clearing a directory clears everything that later lands in it. Files appearing under a cleared root join the sync set automatically, so a root is cleared only when every file under it — not merely the files present today — is meant for distribution.
- The sync tool's own skill (`.opencode/skills/core-sync/`) is never a cleared key and reaches no destination.
- Only region-mode rows use active core/project ownership markers — `SKILL.md` within a skill directory root, region file rows (the root runtime and knowledge documents), and the files expanded from the two `region` agent directory roots (`.opencode/agents/`, `agents/`); architecture rows are `raw`, so no file under `architecture/` carries a marker or a project region. Raw and merge transport does not interpret ownership markers; marker literals in a raw reference or fenced example remain ordinary copied bytes, not a separate region binding. Region mode remains for the root runtime, `knowledge/`, and the two agent directories because their project regions carry records, evidence, operational bindings, and history — non-normative content the shared core cannot carry — whereas a project region inside a rulebook would carry a competing rule.
- Modes: `region` (delivers only the source core region; the destination owns its project region), `raw` (byte-for-byte copy), `merge` (top-level key merge — config only; the `mcp` key merges by server name, keeping destination-only MCP servers and making a same-named entry core-wins).

## Validation

A document is valid when `core_sync_pkg.domain.clearance.parse_clearance` accepts it: schema exactly `1`; keys unique and repo-relative; directory-root keys end with `/`; `region_files` members are root-relative, stay inside the root, and contain no `..` or absolute paths; `role` appears at most once and only on a `region` record (this registry uses `role: root` on `AGENTS.md` only). Any other version label is rejected (exit 2) — there is no version migration.
