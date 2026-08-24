# Phase 5 — Marshal 🎖️ (HR Director): Herald 📯 (Release Manager) execution-boundary refactor

> **Owner:** Marshal 🎖️ (HR Director)
> **Pre:** phase 4 complete; `AGENTS.md` and `herald.md` read in full.
> **Reads:** `AGENTS.md`; `.opencode/agents/herald.md`; `.opencode/agents/sentinel.md`
> **Writes:** `.opencode/agents/herald.md` (edit)

## Steps

1. Rewrite Herald 📯 (Release Manager)'s description, Your Role, upstream trigger, and evidence-related Hard Rules so the boundary is explicit: Cipher 🔓 (L2 Lead) evaluates applicable audit evidence and sends an evaluated gate packet; Herald 📯 (Release Manager) verifies the packet is present, reports a missing packet as a raw blocker to Cipher 🔓 (L2 Lead), and executes the authorized git operation. Herald 📯 (Release Manager) does not reassess audit-evidence quality or decide which specialist gate applies.
2. Preserve the release-executor safeguards: Herald 📯 (Release Manager) still evaluates raw git/release blockers, discovers/stages paths, and never asks the user to certify evidence. Do not move release authority to Cipher 🔓 (L2 Lead) or alter user-only merge authority.
3. Group the existing Hard Rules under clear `###` subheadings while keeping `## Hard Rules` final: at minimum Scope and authority; Git integrity; PR lifecycle; Stash safety; Plan lifecycle. Preserve every existing protection and imperative rule; do not delete, weaken, or duplicate a rule.
4. Update the Roster Context and Workflow wording so the Cipher 🔓 (L2 Lead) ↔ Herald 📯 (Release Manager) gate handoff is two-sided with `AGENTS.md`.

## Output

- **Artifact:** structured, execution-only `.opencode/agents/herald.md`
- **Schema / shape:** Herald 📯 (Release Manager) receives an evaluated gate packet from Cipher 🔓 (L2 Lead); presence validation and raw git blockers remain Herald's; Hard Rules are grouped beneath `###` subheadings and remain the final section.

## Gate

- ☑ herald.md contains no claim that Herald 📯 (Release Manager) evaluates audit-evidence quality or decides applicable specialist gates
- ☑ AGENTS.md and herald.md state the same handoff in which Cipher 🔓 (L2 Lead) evaluates and Herald 📯 (Release Manager) executes
- ☑ every pre-existing Herald 📯 (Release Manager) protection remains with equal or stronger imperative wording
- ☑ `## Hard Rules` is final and grouped into the specified subheadings

## Abort conditions

- A proposed wording would make Cipher 🔓 (L2 Lead) execute git or release operations, or make Herald 📯 (Release Manager) lose a raw git/release blocker check → stop and ask.
- A rule cannot be placed in exactly one group without duplicating or weakening it → stop and ask.
