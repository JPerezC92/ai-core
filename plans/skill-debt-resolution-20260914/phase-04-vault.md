# Phase 4 — Audit skill quality

> **Owner:** Vault 🔐 (Catalog Steward)
> **Pre:** Phases 1-3 pass; both skill files are final for catalog review.
> **Reads:** `.opencode/skills/git-pr/SKILL.md`; `.opencode/skills/op-model/SKILL.md`; `.opencode/skills/op-model/scripts/models.py`; `.opencode/agents/vault.md`; `.opencode/skills/op-skill-creator/SKILL.md`; `plans/skill-debt-resolution-20260914/plan.md`
> **Writes:** none; return a read-only catalog gate response to Cipher 🔓 (Lead Orchestrator)

## Steps

1. Audit both complete modified skills against every applicable Core and OpenCode quality check.
2. Verify `git-pr` `1.3.1` and `op-model` `1.0.1` are correct patch bumps and descriptions/triggers remain aligned with behavior.
3. Verify `git-pr`'s dual-layout plan discovery and roster correction introduce no authority drift.
4. Verify the `op-model` script inventory and skill references remain accurate with no dependency declaration change.
5. Return `[PASS]` only when both skills pass every applicable check; otherwise return `[FAIL]` with exact evidence.

## Output

- **Artifact:** Vault gate response in the phase handoff.
- **Schema / shape:** Separate `[PASS]`/`[FAIL]` disposition for each skill, version judgment, checklist evidence, and any finding.

## Verify commands

| Executor | Command |
|---|---|
| Cipher 🔓 (Lead Orchestrator) | `python3 -c "from pathlib import Path; files=[Path('.opencode/skills/git-pr/SKILL.md'),Path('.opencode/skills/op-model/SKILL.md')]; required=('## What I do','## When to use me','## Examples','## Troubleshooting'); assert all(len(p.read_text().split())<5000 and len(p.read_text().splitlines())<500 and all(h in p.read_text() for h in required) for p in files)"` |

## Gate

- ⬜ Vault returns `[PASS]` for both skills with no unresolved finding.

## Abort conditions

- Halt if either skill needs a rename, new dependency, reference extraction, or behavioral expansion beyond G1/G2.
