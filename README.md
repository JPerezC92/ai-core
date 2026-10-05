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

1. Start only from a destination that is already clean and saved. A dirty or uncertain destination aborts `migrate-core-to-project`; the skill does not commit, stash, or clean it. Run it after an approved source refresh. Prepare the complete result outside the destination, freeze approval, then enroll the **complete applicable unit set** (see `AGENTS.md` → Reuse guide). It writes `.aicore/adoption.yaml` and `.aicore/adoption-review.yaml` before content, and installs `.aicore/adoption.lock.yaml` only after an external candidate check. Do not treat enrollment as an application build.
2. Keep shared rule infrastructure (`knowledge/agents.md`) and the destination's own `plans/` and `user-stories/`. Initialize destination registers from their structural headers. Do not copy AICore debt, symptom history, or problem records into the destination.
3. If your stack differs, adapt only the project-extensions sections of the stack-specific rulebooks (`atrium.md`, `bastion.md`, `crucible.md`, `lumen.md`) before enrollment, and record that review in `.aicore/adoption-review.yaml`. Do not replace mandatory bytes.
4. Substitute your real tooling only in destination-owned project extensions or destination configuration. Do not edit protected mandatory text. The core ships neutral on purpose.
5. Recurring updates run from an AICore checkout, after an approved refresh of the protected upstream tip. Invoke `python3 -B` on the absolute `sync-aicore-adoption` script with explicit upstream, adopter snapshot, declaration, review, and lock options. Save a candidate outside the destination. `check` verifies one explicit snapshot and does not authorize writes. `verify-all` checks every adopter in `.aicore/adopters.yaml`; it may clone into and remove its own temporary directory, and it does not clean a supplied checkout. A local branch that was not refreshed is not live remote truth.

## Notes

- Everything is OpenCode-native: agent specs in `.opencode/agents/`, skills in `.opencode/skills/` (`compatibility: opencode`), plan lifecycle in `plans/` + `user-stories/`.
- `output/` is gitignored — it holds temporal artifacts (audit reports, research briefs, design briefs/audits); agents create it on first write.
- Skills `git-commit`, `git-branch-name`, `git-pr` assume git + pnpm and the GitHub CLI (`gh`) — the dev-team defaults.
- The authoritative inventory for adopted content is `.aicore/core-catalog-v2.yaml`: it lists the adopted units with machine `applicability` and deterministic config `assertions`, and excludes the 2 upstream-only management tools (`migrate-core-to-project` and `sync-aicore-adoption`), which run from an AICore checkout and are never copied into an adopter. `.aicore/adopters.yaml` is the single AICore surface that names external adopter repositories.
