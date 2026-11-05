# Evidence file — general implementer scope

> **Record:** [odd/tasks/2026-11-04-general-implementer-scope.md](../tasks/2026-11-04-general-implementer-scope.md) — the sole authoritative intent, task and status record for this feature.
> **Owner:** Cipher 🔓 (Lead Orchestrator) — author of this extraction
> **Created:** 2026-11-04

## What this file is for

Hold the attestational evidence behind one feature record's `## Log`: obligation accounting, reviewer verdicts and identities, original/candidate identities, literal commands with observed results, and the preservation mapping for anything moved out of the record. Each `E#` section is referenced from a record entry as `E#`.

## What this file is not

Disposable working evidence. It is not a feature record, task tracker, status register, intent authority, approval, adoption proof or delivery evidence. A verdict, hash or observed result recorded here establishes only what its own entry states; anatomy validation, a green check or a copied reviewer verdict never certifies the feature.

## Three evidence classes

- **Decisive** — requests, corrections, approvals and their labels, decisions, obligations, acceptance limits and commits: permanent, always in the record, never here.
- **Attestational** — who verified what, with which input identity, literal command and observed result: lives here while the feature is active so the record stays readable.
- **Reproducible** — content a reader can regenerate or re-read from Git, a committed artifact, or a gitignored `output/` artifact: referenced by pointer, never copied.

Retention and close-time reconciliation are owned by `.opencode/skills/odd-workflow/SKILL.md` → `### Evidence retention`; the boundary against a durable surface citing a specific evidence file is owned by `knowledge/agent-workflow.md` → `### Feature document`. This template illustrates the layout, not another rule definition.

## E1 — obligation accounting

Source: Sentinel 🛡️ (Quality Guardian) independent comparison of the byte-exact HEAD originals against the candidates, plus Marshal 🎖️ (HR Director) authoring accounting. No silent loss found.

- **Retained unchanged in effect**: Forge `#### Feature Scope`, `#### Nonconforming feature files`, `#### Impact-bounded read scope`, `#### Blocker handling`, `#### Dependency proposal`, `#### Codebase Landmarks`, `### Output Format`, `### Stop and Report`, `#### Naming Convention`, warmup read order and change-based reuse, step gating and `AWAITING_REVIEW`, gate hierarchy, import completeness, Hard Rules on Bash, environment exception, autofix footprint, maintenance commands, Warden install gate, no Git, no adjacent config, no tests beyond assignment, no broken imports, plus both project regions; Bastion's snapshot/reuse/round-cap and dependency/error contract; Atrium's dependency ownership and binding rules.
- **Translated**: the two enumerated exception scopes became one `#### Assigned implementation scope`; the Python-path execution caveat became any assigned path; gate nouns became backend/tooling/script/repository-owned MCP; the Static Data Service pointer was scoped to React/TypeScript frontend application code with the universal caution retained; tool and testing-guide enumerations became mapping-selected with the approved guides named as the current set; "Destination TypeScript/TSX stack" became a project-owned reference example plus an "any other stack" bullet; "backend or Python gate" became "backend, tooling, script, or MCP gate" (strengthened).
- **Retired with authority**: the application-source-tree framing, the two standalone exception scopes, the clause limiting outside-application authority to Python skill scripts plus MCP, and "Other backend-tooling server implementation remains forbidden". Authority: the user's S1/S3 request recorded in the record Log. No safety restriction was retired.

## E2 — original and candidate identities

Captured by Herald 📯 (Release Manager) with `git archive` at HEAD plus unfiltered blob-hash equality; UTF-8, `i/lf w/lf`, no filters.

| File | Original (HEAD `ea0c5e1`) | Original blob | Captured file hash | Candidate version |
|---|---|---|---|---|
| `.opencode/agents/forge.md` | 2.0.0 | `fe74de590d62dbc59eca43d280ca18aa9a143ed7` | matches exactly | 3.0.0 |
| `.opencode/agents/bastion.md` | 1.13.0 | `37e4e82647f1dc82950bef740c7a462f3c3124c2` | matches exactly | 1.14.0 |
| `.opencode/agents/atrium.md` | 1.9.0 | `1149c16001c49cd337782c7aa01be760834895a1` | matches exactly | 1.10.0 |

Originals on disk: `output/general-implementer-original-forge.md`, `-bastion.md`, `-atrium.md` (gitignored).

## E3 — reviewer verdicts and identities

- **Round 1** — Sentinel 🛡️ (Quality Guardian), independent of authoring: `PLAN: FAIL` (F2, F3, F4, F5, F6), `IMPLEMENTATION: FAIL` (F1); per-spec S1–S5 each PASS; sweep found zero surviving contradicting statement; accounting found no silent loss; recommended Forge version class = major. Findings and dispositions recorded in the record Log L7 and L8.
- **Marshal 🎖️ (HR Director)** authored T1/T2 and, on accepted finding F1, superseded its own minor version ruling with `3.0.0`.

## E4 — literal commands and observed results

- `git archive --format=tar --output=output/general-implementer-head-agents.tar HEAD <3 paths>` then extraction and copy — captured originals at HEAD; `git hash-object --no-filters` matches each HEAD blob (E2).
- `git status --porcelain -uall` — three `M` entries under `.opencode/agents` plus the untracked feature record; nothing else modified.
- `uv run --frozen python3 .opencode/skills/odd-workflow/scripts/validate_feature.py odd/tasks` — mechanical anatomy check; result recorded in the record Log at close, not a semantic verdict.
- Bounded sweep for the retired wording — result recorded in L7.

## E5 — preservation mapping

- The retired statements' substantive duties survive as follows: application-tree limit → `#### Assigned implementation scope` covering every assigned implementation path; Python-plus-MCP enumerated limit → the same scope plus Warmup and Per-step routing; TypeScript-only tool binding → project-owned reference examples with an "any other stack" bullet; testing-guide enumeration → mapping-selected testing guide with existing references named.
- Nothing was moved outside the three runtime files; no path was added or removed, so distribution clearance is unchanged.
