# AICore

A reusable, agnostic core of AI agents, personas, and skills. Another project adopts it **atomically** — one AICore revision for the complete applicable unit set — and customizes it there; the core itself stays neutral.

## What's inside

```
AGENTS.md                     Lead orchestrator (Cipher 🔓 (Lead Orchestrator)) + roster + reuse guide
.opencode/agents/             16 runtime agent specs (OpenCode subagents)
.opencode/skills/             11 skills (git-commit, git-branch-name, git-pr,
                              migrate-core-to-project, op-skill-creator, op-agent-creator, op-model,
                              plan-enforce, query-verification, sync-aicore-adoption, ticket-runbook)
agents/<name>/profile.md      17 persona CVs (incl. cipher)
knowledge/agents.md           Shared agent rules
knowledge/debt.md             Accepted-debt register
knowledge/symptoms.md         Diagnostic Symptom Catalog
knowledge/problems.md         Known Problem Pattern Register
knowledge/query-verification-design.md  Query-verification living design (incident pilot v1 implemented; broader design deferred)
plans/  user-stories/         Plan lifecycle (plan-enforce)
output/                       Temporal working space (audits, research, design — gitignored)
```

## How to use it in another project

1. Run `migrate-core-to-project` to enroll the **complete applicable unit set** atomically (see `AGENTS.md` → Reuse guide); it bootstraps `.aicore/adoption.yaml`, `.aicore/adoption-review.yaml`, and `.aicore/adoption.lock.yaml`.
2. Keep the shared infrastructure: `knowledge/agents.md`, `knowledge/debt.md`, `knowledge/symptoms.md`, `knowledge/problems.md`, `plans/`, `user-stories/`, and `output/` for temporal artifacts.
3. Adapt the stack-specific rulebooks (`atrium.md`, `bastion.md`, `crucible.md`, `lumen.md`) if your stack differs, and record the reconciliation in `.aicore/adoption-review.yaml`.
4. Substitute your real tooling wherever an agent says "the ticket system", "the primary database", "the docs/wiki", etc. The core ships neutral on purpose.
5. `sync-aicore-adoption check` verifies one adopter's compliance; `sync-aicore-adoption verify-all` checks every adopter registered in `.aicore/adopters.yaml`.

## Notes

- Everything is OpenCode-native: agent specs in `.opencode/agents/`, skills in `.opencode/skills/` (`compatibility: opencode`), plan lifecycle in `plans/` + `user-stories/`.
- `output/` is gitignored — it holds temporal artifacts (audit reports, research briefs, design briefs/audits); agents create it on first write.
- Skills `git-commit`, `git-branch-name`, `git-pr` assume git + pnpm and the GitHub CLI (`gh`) — the dev-team defaults.
- The authoritative inventory for adopted content is `.aicore/core-catalog-v2.yaml`: it lists the adopted units with machine `applicability` and deterministic config `assertions`, and excludes the 2 upstream-only management tools (`migrate-core-to-project` and `sync-aicore-adoption`), which run from an AICore checkout and are never copied into an adopter. `.aicore/adopters.yaml` is the single AICore surface that names external adopter repositories.
