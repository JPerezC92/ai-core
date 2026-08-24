# Phase 1 — Marshal 🎖️ (HR Director): Python dependency policy and governance repair

> **Owner:** Marshal 🎖️ (HR Director)
> **Pre:** active plan; user selected UV package management; Warden's conditional PyYAML review read in full.
> **Reads:** `AGENTS.md`; `.opencode/agents/forge.md`; `.opencode/agents/sentinel.md`; `.opencode/agents/marshal.md`; `.opencode/agents/vault.md`; `.opencode/agents/warden.md`; Warden's conditional PyYAML review; Augur's UV grant brief
> **Writes:** `AGENTS.md`; `.opencode/agents/forge.md`; `.opencode/agents/sentinel.md`; `.opencode/agents/marshal.md`; `.opencode/agents/vault.md`; `.opencode/agents/warden.md`

## Steps

1. Add Warden's Python-only dependency branch for a repository with no pnpm manifest but a skill-local `pyproject.toml` and `uv.lock`: review exact pins and source, run `uv lock --check` and `uv tree --frozen`, and audit a provisioned locked skill environment with `uvx pip-audit --path` plus `uv pip check`. Keep Warden 🔒 (Dependency Warden) non-mutating and require an upstream review before `uv lock` or dependency provisioning.
2. Reconcile Warden's gate definitions: PASS means no Critical, High, or Advisory finding; INFO observations do not prevent PASS; ADVISORY means no Critical/High but one or more evidence-backed advisory findings and requires explicit user acknowledgment before release; BLOCK means one or more Critical/High findings. The anticipated PyYAML unavailable-provenance observation is INFO only after all required integrity controls pass.
3. State that the ticket-runbook skill owns its own Python dependency manifest and lockfile; no root Python manifest is created solely for a skill. Require a fresh Warden 🔒 (Dependency Warden) review for any manifest or lockfile version change.
4. Replace Sentinel 🛡️ (Quality Guardian) SP-3's single OpenCode-heading sequence with two explicit, limited structures: `.opencode/agents/*.md` retains its canonical `Your Role` / `Roster Context` / final `Hard Rules` order; AGENTS.md requires its root H1, `## Identity & Role`, persona and runtime-spec declarations, Cipher 🔓 (L2 Lead) owns/does-NOT boundary, roster, shared rules, reuse guide, and conventions in their current root order.
5. State that AGENTS.md's structural mapping is an SP-3 format alternative only. SP-4 through SP-8 remain applicable, and SP-1/2 retain their existing frontmatter/mode exception only.
6. Change Marshal's Vault 🔐 (Catalog Steward) roster-context wording from "skill/agent governance" to the exact catalog-only responsibility: skills catalog quality and lifecycle across both teams.
7. Add a one-plan exception to Forge's Bash hard rule for exactly these commands and no variants: `uv lock --project .opencode/skills/ticket-runbook`; `uv run --locked --project .opencode/skills/ticket-runbook python .opencode/skills/ticket-runbook/scripts/test_validate_runbook.py`; and `uv run --locked --project .opencode/skills/ticket-runbook python .opencode/skills/ticket-runbook/scripts/validate_runbook.py --help`. Require the active `audit-remediation-20260821` manifest, Warden's conditional review, the exact PyYAML manifest, and Cipher 🔓 (L2 Lead) assignment. Explicitly forbid every other UV command, flag, project, dependency change, custom index, redirect, or shell chaining.
8. Normalize the general Herald 📯 (Release Manager) roster mention in AGENTS.md to `Herald 📯 (Release Manager)` without changing Herald's execution-only evidence-gate boundary.
9. Restore Vault's exact canonical persona-reference suffix and normalize every non-possessive roster mention in Vault's spec to the required first/subsequent form without changing catalog scope or handoffs.
10. Re-read all six inputs and verify the Warden 🔒 (Dependency Warden) branch does not require pnpm for Python-only skills; a known advisory cannot become PASS without user acknowledgment; the Forge 🔨 (Implementation Agent) exception is exact and cannot generalize; Sentinel's exception is no broader than root format; and Vault's agent-document boundary remains owned by Sentinel 🛡️ (Quality Guardian).

## Output

- **Artifact:** Warden 🔒 (Dependency Warden) Python-only dependency policy; one-plan Forge 🔨 (Implementation Agent) UV exception; satisfiable Sentinel 🛡️ (Quality Guardian) SP-3 root-spec contract; catalog-accurate Marshal 🎖️ (HR Director) roster wording
- **Schema / shape:** skill-local UV dependencies are reviewable without pnpm; Forge 🔨 (Implementation Agent) can execute only the three user-authorized ticket-runbook commands; AGENTS.md is evaluated against a concrete root structure, not OpenCode-only headings; no agent-document responsibility returns to Vault 🔐 (Catalog Steward).

## Gate

- ☑ Warden 🔒 (Dependency Warden) defines a Python-only, skill-local manifest/lockfile branch without editing or installing packages
- ☑ Warden 🔒 (Dependency Warden) requires `uv lock --check`, `uv tree --frozen`, `uvx pip-audit --path`, and `uv pip check` at the stated points
- ☑ Warden's PASS, ADVISORY, and BLOCK definitions are mutually exclusive; INFO is non-blocking and advisory release requires user acknowledgment
- ☑ Forge's one-plan UV exception permits only the three exact commands after all stated Warden 🔒 (Dependency Warden)/plan prerequisites
- ☑ Sentinel 🛡️ (Quality Guardian) SP-3 defines a concrete AGENTS.md structure and does not require absent OpenCode-only headings
- ☑ Sentinel 🛡️ (Quality Guardian) limits AGENTS.md exceptions to SP-1/2 frontmatter/mode and SP-3 root structure
- ☑ Marshal 🎖️ (HR Director) describes Vault 🔐 (Catalog Steward) as skills-catalog quality/lifecycle only
- ☑ Vault's spec has canonical persona-reference and roster-name formatting without changing its skills-only boundary

## Abort conditions

- Warden's policy would permit an unpinned dependency, a root manifest solely for one skill, or mutable lock generation without an upstream review → stop and ask.
- The policy would classify unavailable PyYAML provenance as PASS without all required integrity controls, or would downgrade a concrete provenance anomaly to INFO/PASS → stop and ask.
- The Forge 🔨 (Implementation Agent) exception permits any unlisted UV command, another skill/root project, a dependency change, a custom index, a redirect, or shell chaining → stop and ask.
- The SP-3 mapping would exempt AGENTS.md from naming, evidence, path, or imperative-rule checks → stop and ask.
- Marshal 🎖️ (HR Director) wording would assign any agent-document audit responsibility to Vault 🔐 (Catalog Steward) → stop and ask.
