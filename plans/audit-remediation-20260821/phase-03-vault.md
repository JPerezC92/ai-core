# Phase 3 — Vault 🔐 (Catalog Steward): root command and validation-contract documentation

> **Owner:** Vault 🔐 (Catalog Steward)
> **Pre:** phase 2 passes its locked UV unittest and Bastion 🧱 (Backend Architect) gate; current skill files and the earlier self-verify plan read in full.
> **Reads:** `.opencode/skills/ticket-runbook/SKILL.md`; `.opencode/skills/ticket-runbook/references/_consistency-checklist.md`; `.opencode/skills/plan-enforce/SKILL.md`; `plans/self-verify-loops-20260820/plan.md`; `plans/self-verify-loops-20260820/phase-01-vault.md`; `plans/self-verify-loops-20260820/phase-02-vault.md`; phase-2 validator/test results
> **Writes:** `.opencode/skills/ticket-runbook/SKILL.md`; `.opencode/skills/ticket-runbook/references/_consistency-checklist.md`; `.opencode/skills/ticket-runbook/references/runbook/runbook.md`; `.opencode/skills/ticket-runbook/references/runbook/phase-01-triage.md`; `.opencode/skills/ticket-runbook/references/runbook/phase-04-validate.md`; `.opencode/skills/plan-enforce/SKILL.md`; `plans/self-verify-loops-20260820/plan.md`; `plans/self-verify-loops-20260820/phase-01-vault.md`; `plans/self-verify-loops-20260820/phase-02-vault.md`

## Steps

1. In ticket-runbook SKILL.md, replace every relative validator command with `uv run --locked --project .opencode/skills/ticket-runbook python .opencode/skills/ticket-runbook/scripts/validate_runbook.py`. Immediately after scaffolding use `--scaffold`; before advancing a completed phase use `--phase NN`; reserve default full validation for all completed phases through the header.
2. Align the ticket-runbook self-verification loop and canonical checklist with those modes: scaffold analysis verifies phase-01 ticket context while later template bodies remain intentional; completed phases have no unfilled tokens. Canonicalize `Query-budget` as used/limit: a fresh copied scaffold begins at `0/6`, while `6/6` means exhausted. Apply the same meaning to the runbook, triage, and validation templates. Preserve the requirement that semantic evidence analysis is not delegated to the script.
3. In plan-enforce SKILL.md, replace its relative mechanical-pass command with `python3 .opencode/skills/plan-enforce/scripts/validate_plan.py` from the project root. When the active plan creates or changes a user story, include `--stories user-stories` so the documented mechanical pass actually checks story/index mirroring; preserve the single-file argument form and all loop semantics.
4. In the earlier self-verify plan and its two Vault 🔐 (Catalog Steward) phase runbooks, replace ticket-runbook commands with the locked UV form and plan-enforce commands with root-resolvable `python3` forms. Replace the false-positive residue expression that includes generic `gate` with an expression limited to source-project/domain identifiers. Preserve the evidence that required `## Gate` headings are legitimate template structure.
5. Re-read all six files and confirm every validator command resolves from the repository root.

## Output

- **Artifact:** root-resolvable, mode-accurate skill instructions and templates; precise historical command and residue verification expressions
- **Schema / shape:** ticket-runbook command paths use locked UV plus `.opencode/skills/.../scripts/...`; plan-enforce command paths use `python3` and conditionally `--stories user-stories`; fresh runbooks start at `Query-budget: 0/6`; scaffold and completed-phase token contracts match phase 2 behavior; the earlier plan no longer classifies `Gate` headings as residue.

## Gate

- ☑ No `python scripts/validate_` invocation remains in either SKILL.md
- ☑ ticket-runbook uses its locked UV command with `--scaffold` only for fresh copied templates and `--phase NN` for completed-phase validation
- ☑ plan-enforce mechanical pass is root-resolvable with `python3`
- ☑ Historical ticket-runbook commands use locked UV and plan-enforce commands use root-resolvable `python3`
- ☑ Self-verify plan residue expression excludes generic `gate`
- ☑ Fresh ticket-runbook template, checklist, and phase guidance agree that `Query-budget: 0/6` is the initial used/limit value
- ☑ plan-enforce documents `--stories user-stories` whenever the active plan changes a story/index

## Abort conditions

- A documentation change would weaken strict validation of completed phase artifacts → stop and ask.
- A command differs from the implemented phase-1 CLI contract → stop and report the mismatch.
