# Phase 4 — Cipher 🔓 (L2 Lead): independent final acceptance audit

> **Owner:** Cipher 🔓 (L2 Lead)
> **Pre:** phases 1 through 3 complete; full test output, UV lock, and changed-file list available.
> **Reads:** every source file written in phases 1 through 3; `AGENTS.md`; `.opencode/agents/vault.md`; `.opencode/agents/warden.md`; full unittest and UV dependency-audit output
> **Writes:** none — Vault 🔐 (Catalog Steward), Sentinel 🛡️ (Quality Guardian), and Warden 🔒 (Dependency Warden) return independent audit evidence to Cipher 🔓 (L2 Lead)

## Steps

1. Dispatch Vault 🔐 (Catalog Steward) for a read-only skill audit of both SKILL.md files, the runbook checklist, validator module documentation, copied-template tests, and the historical plan verification expression.
2. Dispatch Sentinel 🛡️ (Quality Guardian) for a read-only governance audit of AGENTS.md, Sentinel 🛡️ (Quality Guardian), Marshal 🎖️ (HR Director), and Vault 🔐 (Catalog Steward) contracts.
3. Dispatch Warden 🔒 (Dependency Warden) for downstream review of ticket-runbook's `pyproject.toml` and `uv.lock`, including the Python-only audit branch required by phase 1.
4. Run `uv run --locked --project .opencode/skills/ticket-runbook python .opencode/skills/ticket-runbook/scripts/test_validate_runbook.py` from the project root; require exit 0.
5. Run `python3 .opencode/skills/plan-enforce/scripts/test_validate_plan.py` from the project root; require exit 0.
6. Run `python3 .opencode/skills/plan-enforce/scripts/validate_plan.py plans/self-verify-loops-20260820`; require exit 0.
7. Run `python3 .opencode/skills/plan-enforce/scripts/validate_plan.py plans/roster-boundary-fixes-20260821`; require exit 0.
8. Run `python3 .opencode/skills/plan-enforce/scripts/validate_plan.py plans/audit-remediation-20260821`; require exit 0.
9. Run `uv run --locked --project .opencode/skills/ticket-runbook python .opencode/skills/ticket-runbook/scripts/validate_runbook.py --help` from the project root; require exit 0.
10. Run `git diff --check`; require exit 0.
11. Return PASS only when Vault 🔐 (Catalog Steward), Sentinel 🛡️ (Quality Guardian), and Warden 🔒 (Dependency Warden) pass and every command exits 0. Warden 🔒 (Dependency Warden) records the PyYAML provenance state as INFO only after all required integrity controls pass; concrete Warden 🔒 (Dependency Warden) findings reopen the responsible phase. Do not add a release action.

## Output

- **Artifact:** independent Vault 🔐 (Catalog Steward)/Sentinel 🛡️ (Quality Guardian) source evidence, Warden 🔒 (Dependency Warden) gate evidence, and command output returned to Cipher 🔓 (L2 Lead)
- **Schema / shape:** every G1-G5 source condition is independently checked; a known PyYAML provenance-unavailable observation is visible INFO after verified integrity; no commit, push, branch, or PR is created.

## Gate

- ☑ Vault 🔐 (Catalog Steward) returns no skill/validator finding
- ☑ Sentinel 🛡️ (Quality Guardian) returns no governance finding
- ☑ Warden 🔒 (Dependency Warden) returns PASS with a documented PyYAML INFO provenance state after required integrity controls pass
- ☑ All listed test, validator, help, and diff commands exit 0

## Abort conditions

- Any Vault 🔐 (Catalog Steward)/Sentinel 🛡️ (Quality Guardian) advisory or blocker, or any Warden 🔒 (Dependency Warden) ADVISORY or BLOCK with concrete evidence → reopen the responsible phase; do not declare the plan clean.
- Any command fails from the project root → stop and report the exact output.
