# AICore

A reusable, agnostic core of AI agents, personas, and skills. Copy any part of it into another project and customize it there — the core itself stays neutral.

## What's inside

```
AGENTS.md                     Lead orchestrator (Cipher) + roster + reuse guide
.opencode/agents/             16 runtime agent specs (OpenCode subagents)
.opencode/skills/             6 skills (git-commit, git-branch-name, git-pr,
                              op-skill-creator, op-agent-creator, plan-enforce,
                              ticket-runbook)
agents/<name>/profile.md      16 persona CVs (incl. cipher)
knowledge/agents.md           Shared agent rules
knowledge/debt.md             Accepted-debt register
knowledge/{design,audits,research}/   Output directories used by agents
plans/  user-stories/         Plan lifecycle (plan-enforce)
```

## How to use it in another project

1. Copy the agents, profiles, and skills you need (see `AGENTS.md` → Reuse guide).
2. Create the shared infrastructure: `knowledge/` subdirs, `plans/`, `user-stories/`.
3. Replace the stack-specific rulebooks (`atrium.md`, `bastion.md`, `crucible.md`, `lumen.md`) if your stack differs.
4. Substitute your real tooling wherever an agent says "the ticket system", "the primary database", "the docs/wiki", etc. The core ships neutral on purpose.

## Notes

- Everything is OpenCode-native: agent specs in `.opencode/agents/`, skills in `.opencode/skills/` (`compatibility: opencode`), plan lifecycle in `plans/` + `user-stories/`.
- Skills `git-commit`, `git-branch-name`, `git-pr` assume git + pnpm and the GitHub CLI (`gh`) — the dev-team defaults.
