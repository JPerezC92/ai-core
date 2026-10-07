# AICore

A reusable, agnostic core of AI agents, personas, and skills. Another project adopts it **atomically** — one AICore revision for the complete applicable unit set — and customizes it there; the core itself stays neutral.

## What's inside

```
AGENTS.md                     Lead orchestrator (Cipher 🔓 (Lead Orchestrator)) + roster + reuse guide
.opencode/agents/             16 runtime agent specs (OpenCode subagents)
.opencode/skills/             10 skills (core-sync, git-branch-name, git-commit,
                              git-pr, op-agent-creator, op-model, op-skill-creator,
                              plan-enforce, query-verification, ticket-runbook)
agents/<name>/profile.md      17 persona CVs (incl. cipher)
knowledge/agents.md           Shared agent rules
knowledge/debt.md             Accepted-debt register (destination-owned; seeded from debt.template.md, never mirrored)
knowledge/symptoms.md         Diagnostic Symptom Catalog (shared, shipped)
knowledge/problems.md         Known Problem Pattern Register (shared, ships empty)
knowledge/query-verification-design.md  Query-verification living design (incident pilot v1 implemented; broader design deferred)
plans/  user-stories/         Plan lifecycle (plan-enforce)
output/                       Temporal working space (audits, research, design — gitignored)
```

## How to use it in another project

1. Start only from a destination that is already clean and saved. `core-sync` performs no cleanliness check — confirming the destination is clean and saved is an operator pre-flight. Run `core-sync init` from an AICore checkout after an approved source refresh. It enrolls the **complete applicable unit set** at one AICore revision: each file's `core` region gets the source core, and the file's previous body moves into the destination-owned `project` region. Review every `.aicore/reconciliation/` report under the core-wins rule, resolve the destination-root reconciliation blocker, and clear `pending`; `core-sync check` must exit `0` before the enrollment is accepted. Do not treat enrollment as an application build.
2. Keep shared rule infrastructure (`knowledge/agents.md`). The destination owns its `plans/`, `user-stories/`, and `knowledge/debt.md`: seed an absent debt register from the shipped 0-entry `knowledge/debt.template.md` and preserve the destination's own entries — AICore's filed debt is never copied into a destination, and the debt unit cannot be declared `mirror`. The shared diagnostic catalog does ship: `knowledge/symptoms.md` (symptom-class catalog) and the empty `knowledge/problems.md` (problem-pattern register) are copied as shared infrastructure. Distinguish filed history, which is never copied, from the shared catalog, which is.
3. If your stack differs, adapt only the project-extensions sections of the stack-specific rulebooks (`atrium.md`, `bastion.md`, `crucible.md`, `lumen.md`) before adopting the core, and record that review in the destination's `.aicore/reconciliation/` records. Do not replace mandatory bytes.
4. Substitute your real tooling only in destination-owned project extensions or destination configuration. Do not edit protected mandatory text. The core ships neutral on purpose.
5. Recurring updates run from an AICore checkout, after an approved refresh of the protected upstream tip, using the absolute path `.opencode/skills/core-sync/scripts/core_sync.py`:

   ```bash
   uv run --frozen python3 .opencode/skills/core-sync/scripts/core_sync.py apply \
     --source <source-dir> --destination <destination-dir> \
     --bindings <bindings-file> --source-revision <40-hex>
   uv run --frozen python3 .opencode/skills/core-sync/scripts/core_sync.py check \
     --source <source-dir> --destination <destination-dir> \
     --bindings <bindings-file> --source-revision <40-hex>
   ```

   `apply` splices each source `core` region into its destinations and pins the revision; `check` verifies every destination core region against the pinned revision and requires `pending` empty, exiting `0` only when current. A failed `check` blocks acceptance until the drift is reconciled. A local branch that was not refreshed is not live remote truth.

## Notes

- Everything is OpenCode-native: agent specs in `.opencode/agents/`, skills in `.opencode/skills/` (`compatibility: opencode`), plan lifecycle in `plans/` + `user-stories/`.
- `output/` is gitignored — it holds temporal artifacts (audit reports, research briefs, design briefs/audits); agents create it on first write.
- Skills `git-commit`, `git-branch-name`, `git-pr` assume git + pnpm and the GitHub CLI (`gh`) — the dev-team defaults.
- Each destination's adopted content is bound by its own `.aicore/core.yaml`: it maps each source file to its destination paths and pins the `core_revision` the destination was enrolled at. The bindings are destination-owned state — AICore keeps no adopter registry.
