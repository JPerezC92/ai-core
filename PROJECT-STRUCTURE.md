# Project structure

Explanatory map of this repository's tracked layout. Tree baseline generated from `git ls-files` at merged head `e70b3870796bfde92e2e1b31864e88e339585b7a`; the documentation entries noted below were manually updated on 2026-11-05, not regenerated from Git.

This file is navigation only. It is source-local, it ships to no destination, and it never overrides `AGENTS.md`, `knowledge/agent-workflow.md`, `architecture/`, or any runtime spec. When the tree changes, this map is stale until regenerated — treat the files themselves as truth.

## Repository tree

```text
ai-core/
├── AGENTS.md                      Cipher's runtime spec (lead orchestrator)
├── README.md                      Adoption guide, roster, repository map
├── opencode.jsonc                 V2 config: agents, models, permissions, MCP, instructions
├── distribution-clearance.json    What ships, and how (raw / region / merge)
├── distribution-clearance.definition.md
├── pyproject.toml  uv.lock        Python toolchain + pytest config
├── conftest.py                    Repository-wide temp-dir policy
│
├── .opencode/
│   ├── agents/                    16 specialist runtimes
│   │   atrium  augur  bastion  crucible  forge  herald  inquisitor
│   │   investigator  ledger  lumen  marshal  quill  scribe
│   │   sentinel  vault  warden
│   ├── skills/                    9 skills, each self-contained
│   │   ├── core-sync/             Distribution engine (package + tests)
│   │   ├── odd-workflow/          Feature-record lifecycle + validator
│   │   ├── incident-workflow/     Incident analysis + validator
│   │   ├── git-branch-name/  git-commit/  git-pr/
│   │   └── op-agent-creator/  op-model/  op-skill-creator/
│   └── tooling/                   astgrep/ · semgrep/ (own locked envs)
│
├── knowledge/                     Shared operating rules
│   ├── agent-workflow.md          ODD protocol + task router            [whole-file]
│   ├── agents.md                  Evidence, coordination, safety rules   [region]
│   ├── architecture-decision-workflow.md  ADR lifecycle + gates        [region]
│   ├── release.md                 PR readiness, post-review routing     [whole-file]
│   ├── debt.md                    Accepted-debt register                [region]
│   ├── unicode-policy.md  .json
│   └── diagnostics/
│       ├── symptoms.md            S-01…S-07 symptom catalog
│       ├── problems.md            P-NNN known-problem register
│       └── diagnostic-guidance.md Reusable queries + evidence bounds
│
├── architecture/                  Shared current rules (ships byte-identical)
│   ├── README.md                  Selection + content model
│   ├── implementation/
│   │   ├── architecture.md        Common contract C1–C10 (documentation candidate)
│   │   ├── shapes/                frontend.md · backend.md · scripts.md
│   │   └── stacks/                _template · python · typescript/{react,nestjs}
│   └── testing/
│       ├── architecture.md        Test contract T1–T36
│       └── stacks/                _template · python · typescript
│
├── docs/                          Source-local (AICore only, never shipped)
│   ├── README.md                  Source-local documentation map
│   ├── tooling.md
│   ├── architecture/
│   │   ├── README.md              Selections, ADR index, history routes
│   │   ├── decisions/            ADR 0001–0005, Accepted 0007 + _template
│   │   ├── history/               Extraction accounting
│   │   └── odd-adoption-status.md
│   └── research/
│       ├── README.md  _template.md
│       ├── agent-workflows/       ai-repository-navigation,
│       │                          odd-foundation-plan-fit,
│       │                          odd-gentleman-programming
│       └── architecture/          anemic-domain-model-and-use-case-naming,
│                                  domain-model-repositories-and-naming
│
├── odd/tasks/                     _template.md + 58 feature records
└── tests/test_pytest_temp_root.py
```

## Where authority lives

```text
        ┌──────────────────────────────────────────────┐
        │  AGENTS.md            runtime authority      │  ← Cipher
        │  .opencode/agents/     role authority        │
        └───────────────┬──────────────────────────────┘
                        │ reads
        ┌───────────────▼──────────────────────────────┐
        │  knowledge/            when + who + rules    │
        │  architecture/         what is correct       │
        └───────────────┬──────────────────────────────┘
                        │ explained by
        ┌───────────────▼──────────────────────────────┐
        │  docs/                 why (ADRs, research)  │
        │  odd/tasks/            what we are building  │
        └──────────────────────────────────────────────┘
```

## The distribution boundary

What an adopting project receives, per `distribution-clearance.json`:

| Travels | Mode | Stays source-local |
|---|---|---|
| `AGENTS.md` | region (core only) | `AGENTS.md` project extensions |
| `opencode.jsonc` | merge (by top-level key) | — |
| `knowledge/agent-workflow.md`, `knowledge/release.md` | raw, whole file | — |
| `knowledge/agents.md`, `debt.md`, `architecture-decision-workflow.md`, `diagnostics/*` | region | their `project` regions |
| `odd/tasks/_template.md`, `odd/features/_template.md`, `odd/evidence/_template.md` | raw, whole file | — |
| `architecture/` (whole directory) | raw | — |
| `.opencode/agents/` | region | runtime `project` regions |
| `.opencode/skills/` (each skill) | raw | — |
| — | — | `docs/`, ODD feature records and evidence instances, `output/`, this file |

Two consequences are visible in the tree:

- The diagnostic catalog, problem register and guidance live together under `knowledge/diagnostics/`, so the symptom → problem → guidance relationship sits in one place.
- `knowledge/agent-workflow.md` and `knowledge/release.md` carry no ownership markers. The local-commit and merged-branch-deletion authorizations sit in the `AGENTS.md` core region, so an adopting project inherits them as a deliberate shared grant on its next synchronization; the unused magic-context mechanism was removed rather than shipped.

## Where to start

| I need to… | Read |
|---|---|
| Act on a request | `AGENTS.md`, then `knowledge/agent-workflow.md` |
| Work on a feature | `odd/tasks/<YYYY-MM-DD>-<feature-name>.md` from `odd/tasks/_template.md` |
| Select architecture rules | `architecture/README.md` |
| Understand why a rule exists | `docs/architecture/decisions/` |
| Investigate an incident | `knowledge/diagnostics/` and `.opencode/skills/incident-workflow/SKILL.md` |
| Reuse research | `docs/research/README.md` |
| Adopt or update this core | `README.md`, `AGENTS.md` reuse guide, `.opencode/skills/core-sync/SKILL.md` |
