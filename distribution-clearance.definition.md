# `distribution-clearance.json` — format definition

**Source of truth** for the distribution-clearance registry format. The sync tool implementation (`cli/aicore/src/`), its tests, and the registry file conform to this document; a format change updates this file first.

## Version policy

The document carries `"schema": 1`. The version stays **v1** through every compatible change — new optional fields, new record kinds that existing parsers accept, new cleared sources, and retired cleared sources or directory roots. It bumps **only** when a change breaks this design, i.e. when existing records or parsers become incompatible. Nothing else warrants a bump.

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
| Region knowledge documents | individually cleared `.aicore/core/knowledge/` files (`.aicore/core/knowledge/agents.md`, `.aicore/core/knowledge/debt.md`, `.aicore/core/knowledge/architecture-decision-workflow.md`, `.aicore/core/knowledge/escalation.md`) | `{"mode": "region"}` | core region only (core/project markers) |
| Whole-file workflows | `.aicore/core/knowledge/agent-workflow.md`, `.aicore/core/knowledge/release.md` | `{"mode": "raw"}` | whole-file byte-for-byte transport, no ownership regions; source-local grants stay in root-runtime project extensions |
| Canonical ODD templates | individually cleared `.aicore/core/odd/tasks/_template.md`, `.aicore/core/odd/features/_template.md` | `{"mode": "raw"}` | whole-file byte-for-byte transport of the templates only; feature records stay source-local |
| Architecture documents | `.aicore/core/architecture/` directory root | `{"mode": "raw"}` | whole-file byte-for-byte transport with no ownership markers and no project region; no reconciliation report and no `pending` entry; common/shape contracts, implementation and testing templates/guides, and navigation; tools remain destination-owned |
| Directory roots | e.g. `.aicore/core/architecture/`, `.aicore/core/knowledge/diagnostics/`, `.agents/skills/<name>/`, `.opencode/agents/` | `{"mode": <default>, "region_files": [<paths>]?}` | root `mode` is the default mode of every file under the root; `region_files` overrides selected files; see below |

Agent specs are covered by the `.opencode/agents/` directory root, `{"mode": "region"}`, so every file under it delivers only its core region between markers (it holds `<name>.md` runtimes, each carrying its own role manner; there is no separate persona tier).

The two canonical ODD templates are individual file entries, not an `.aicore/core/odd/`, `.aicore/core/odd/tasks/` or `.aicore/core/odd/features/` directory root. Other files under `.aicore/core/odd/` remain uncleared. These new cleared sources use the existing raw record kind, so `schema` remains `1`. The `odd/evidence/_template.md` entry was retired: a destination that already received it keeps both a stale copy and a stale binding entry, and `check` fails closed with `source not cleared for distribution` until it removes both — removing the copy alone is not sufficient — while destination reconciliation stays destination-owned.

## Directory-root records

- `mode` is the default mode of every file under the root.
- `region_files` is optional (absent = empty subset) and names root-relative files that instead use **region** mode. Today the only member is `SKILL.md` — within a skill directory root, the only file type governed by active core/project ownership markers. Raw references may illustrate marker literals without interpreting them, as described under **Scope rules**.
- Current classification: `.aicore/core/architecture/` and the six tooling skill roots (`.agents/skills/git-branch-name/`, `.agents/skills/git-commit/`, `.agents/skills/git-pr/`, `.agents/skills/op-agent-creator/`, `.agents/skills/op-model/`, `.agents/skills/op-skill-creator/`) declare `{"mode": "raw"}`; the three workflow skill roots (`.agents/skills/incident-workflow/`, `.agents/skills/odd-workflow/`, `.agents/skills/git-pr-workflow/`) declare `{"mode": "raw", "region_files": ["SKILL.md"]}`; the `.opencode/agents/` directory and `.aicore/core/knowledge/diagnostics/` declare `{"mode": "region"}` — their files are all region-mode sources, so they need no `region_files`.
- **Expansion** — the sync tool identifies the files at every sync: every file under the root joins the sync set; `region_files` members deliver only their core region; every other file uses the root's default `mode` — `region` delivers only that file's core region, `raw` copies it byte-for-byte (mode semantics under **Scope rules**); interpreter caches (`__pycache__` path parts, `*.pyc` suffixes) never join. Files added under a root later join automatically. Clearance records durable ownership, not file inventories.

## Knowledge distribution classes

The remaining `.aicore/core/knowledge/` files stay individually selected region or raw; `.aicore/core/knowledge/diagnostics/` is the region directory root:

| Class | Files | Payload ships |
|---|---|---|
| Shared rules | `.aicore/core/knowledge/agents.md` | the shared rules; source-side extensions stay project |
| Shared workflow (raw) | `.aicore/core/knowledge/agent-workflow.md` | the whole reusable entry sequence, without ownership regions |
| Shared release workflow (raw) | `.aicore/core/knowledge/release.md` | the whole packet, post-review routing, and execution-owner pointers; local grants belong in root-runtime project extensions, not this payload |
| Shared decision workflow (region) | `.aicore/core/knowledge/architecture-decision-workflow.md` | the decision lifecycle and its propagation gate; the source-local ADR location stays project, and its records do not ship |
| Escalation guidance (contract and sole template core, local routing bindings) | `.aicore/core/knowledge/escalation.md` | the generic routing contract and embedded matrix template; organizational routes, fields, IDs, teams, tools, and execution history stay project |
| Record-bearing register (frame-only core) | `.aicore/core/knowledge/debt.md` | the frame alone — the register carries no table; filed records never ship |
| Shared catalog (full core) | `.aicore/core/knowledge/diagnostics/problems.md`, `.aicore/core/knowledge/diagnostics/symptoms.md` | the full catalog |
| Diagnostic guidance (contract core, local historical context) | `.aicore/core/knowledge/diagnostics/diagnostic-guidance.md` | the shared contract; historical context stays project |

- The debt register's core is frame-only and carries no table: its records are the source's own filed history, and the frame is the retired template seed's payload.
- For region-mode classes, destination-owned records live in the destination's project region and are never substituted by a sync. Raw workflows have no project region: a write replaces all destination bytes, with no reconciliation report or `pending` entry. A pre-write `check` detects byte drift, but does not preserve it.
- Existing destination bindings require destination-owned migration planning: renamed or retired source keys become uncleared, and enrollment alone does not resolve existing mappings. A region-to-raw workflow transition overwrites former project bytes, so preserve local grants at their appropriate owner before an authorized migration. This source update performs no destination migration and authorizes no manual binding edits.

## Architecture distribution

`.aicore/core/architecture/` is a **family-first layout**: `.aicore/core/architecture/implementation/` and `.aicore/core/architecture/testing/` are peer shared-contract families, each carrying its own contract, optional shapes, and stack guides. The implementation family has all three today; the testing family has its contract and stack guides today and adds shapes only when one of its concerns needs them. `.aicore/core/architecture/README.md` owns navigation and selection across both. Together the families form a unified shared contract, not a knowledge register and not an extension surface. The `.aicore/core/architecture/` directory root clears current and future files recursively as `raw`, subject to the existing cache exclusions. This uses the generic directory-root expansion, not architecture-specific behavior, and introduces no new schema behavior.

Every destination receives identical bytes, and `core-sync check` fails on any byte difference. That is a distribution guarantee, not a conformance guarantee: a reference library, runner, or framework named in a guide remains a reference choice, adopted by the destination in its own configuration or its own guide. No file under `.aicore/core/architecture/` carries ownership markers or a project region, so nothing there produces a reconciliation report or a `pending` entry.

- `.aicore/core/architecture/README.md` owns navigation and selection; `.aicore/core/architecture/implementation/architecture.md` owns common semantics.
- `.aicore/core/architecture/implementation/shapes/frontend.md`, `.aicore/core/architecture/implementation/shapes/backend.md`, and `.aicore/core/architecture/implementation/shapes/scripts.md` own shape-specific responsibilities.
- `.aicore/core/architecture/implementation/stacks/_template.md` is the implementation-guide template; `.aicore/core/architecture/implementation/stacks/typescript/react.md`, `.aicore/core/architecture/implementation/stacks/typescript/nestjs.md`, and `.aicore/core/architecture/implementation/stacks/python.md` map the common/shape obligations without claiming application conformance.
- `.aicore/core/architecture/testing/architecture.md` carries the language-agnostic test contract and the stack-guide index.
- `.aicore/core/architecture/testing/stacks/_template.md` carries the single testing stack-guide template, distinct from the implementation-guide template.
- `.aicore/core/architecture/testing/stacks/typescript.md` and `.aicore/core/architecture/testing/stacks/python.md` preserve the reviewed testing implementations. Concrete runners and frameworks are reference implementations, not universal destination bindings.
- Testing documents ship only from `.aicore/core/architecture/testing/`; obsolete root compatibility files remain removed.
- A destination records a selected stack or framework binding in its own configuration or its own guide; it must not weaken the shared contract.
- Adding a new stack guide uses the template and requires an authorized ODD feature and parity review before it is treated as `reference`.

Because a write replaces the destination file byte-for-byte, a destination edit to a distributed architecture file is overwritten by the next write and never enters `pending`; no reconciliation report exists for it, and only a `check` run before that write reports the drift. Divergence is destination-owned, never an in-file region: a destination that needs a different stack adds a guide copied from `.aicore/core/architecture/implementation/stacks/_template.md` or `.aicore/core/architecture/testing/stacks/_template.md`, and an unbound path survives every sync.

New required documents ship with their consumers at one selected revision. A destination must authorize `core-sync init --bind-cleared` enrollment for the new paths; `apply` alone does not enroll absent or markerless files. Architecture rows are `raw`, so they never raise a reconciliation report, a `pending` entry, or the destination-root reconciliation blocker — reconciliation applies to region-mode rows alone, which are the only rows whose displaced duplicates and local extensions a destination resolves. `core-sync check` must exit `0`. This source registry authorizes neither manual binding edits nor destination mutation and does not claim migration completed. Source-local ADRs, review histories, and inventories stay outside distributed core; documentation review is not implementation-conformance proof.

## Scope rules

- Root entries are **directory roots**. A directory may be cleared as a root only when every file under it is intended for distribution; every other source stays an individually cleared file row. This is the explicit design change the earlier skill-root-only scope anticipated — it is compatible, so `schema` stays `1` and no version-migration path is introduced.
- The tradeoff of that rule: clearing a directory clears everything that later lands in it. Files appearing under a cleared root join the sync set automatically, so a root is cleared only when every file under it — not merely the files present today — is meant for distribution.
- The sync tool's own skill (`.opencode/skills/core-sync/`) is never a cleared key and reaches no destination.
- Only region-mode rows use active core/project ownership markers — `SKILL.md` within a skill directory root, region file rows (the root runtime and individually selected knowledge documents), and the files expanded from the `region` agent directory root (`.opencode/agents/`) and from the `.aicore/core/knowledge/diagnostics/` region directory root; architecture and whole-file workflow rows are `raw`, without ownership regions. Raw and merge transport does not interpret ownership markers; marker literals in a raw reference or fenced example remain ordinary copied bytes, not a separate region binding. Region mode remains for the root runtime, selected knowledge documents, the `.opencode/agents/` directory, and `.aicore/core/knowledge/diagnostics/` because their project regions carry records, evidence, operational bindings, and history — non-normative content the shared core cannot carry — whereas a project region inside a rulebook would carry a competing rule.
- Modes: `region` (delivers only the source core region; the destination owns its project region), `raw` (byte-for-byte copy), `merge` (top-level key merge — config only; the `mcp` key merges by server name, keeping destination-only MCP servers and making a same-named entry core-wins).

## Validation

A document is valid when `parseClearanceDocument` in `cli/aicore/src/domain/synchronization/clearance.ts` accepts it: schema exactly `1`; keys unique and repo-relative; directory-root keys end with `/`; `region_files` members are root-relative, stay inside the root, and contain no `..` or absolute paths; `role` appears at most once and only on a `region` record (this registry uses `role: root` on `AGENTS.md` only). Any other version label is rejected (exit 2) — there is no version migration.
