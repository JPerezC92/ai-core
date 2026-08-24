# Phase 4 — Cipher 🔓 (L2 Lead): lead-spec convention + release evidence gate

> **Owner:** Cipher 🔓 (L2 Lead)
> **Pre:** phase 3 complete; `AGENTS.md` and `herald.md` read in full.
> **Reads:** `AGENTS.md`; `.opencode/agents/herald.md`
> **Writes:** `AGENTS.md` (edit)

## Steps

1. `AGENTS.md` Identity & Role: add one convention line after the persona reference — Cipher 🔓 (L2 Lead) has no separate runtime-spec file by design; AGENTS.md itself is the lead's runtime spec.
2. `AGENTS.md` Cipher owns: make the evidence-gate responsibility explicit — Cipher 🔓 (L2 Lead) evaluates the applicable audit reports and passes Herald 📯 (Release Manager) an evaluated gate packet; Herald 📯 (Release Manager) verifies the packet is present and then executes release operations, but does not reassess evidence quality.

## Output

- **Artifact:** `AGENTS.md` with the lead-spec convention line and evidence-gate responsibility
- **Schema / shape:** the AGENTS.md line records where the lead's spec lives; the evidence-gate line makes Cipher's existing Standards enforcement / Synthesis boundary explicit without changing release authority.

## Gate

- ☑ AGENTS.md carries the convention line and explicitly names Cipher 🔓 (L2 Lead) as evidence-gate evaluator before Herald 📯 (Release Manager) execution
- ☑ AGENTS.md preserves Cipher's existing responsibilities and user-only authority for destructive/irreversible actions

## Abort conditions

- The AGENTS.md edit would move release-execution authority from Herald 📯 (Release Manager), or user-only destructive/irreversible authority from the user, to Cipher 🔓 (L2 Lead) → stop and ask.
