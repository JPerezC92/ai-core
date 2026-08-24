# Phase 2 — Vault 🔐 (Catalog Steward): ticket-runbook self-verify tooling

> **Owner:** Vault 🔐 (Catalog Steward)
> **Pre:** active plan; stash gate clean; source template/validator read from the source project.
> **Reads:** `tismart-support/tickets/_template/` (`runbook/*.md`, `_ticket_template.md`, `response-draft.md`); `tismart-support/tickets/validate_runbook.py` + `test_validate_runbook.py`; `.opencode/skills/ticket-runbook/SKILL.md`
> **Writes:** `.opencode/skills/ticket-runbook/references/runbook/runbook.md` + `phase-01-triage.md` … `phase-06-respond.md` (7); `.opencode/skills/ticket-runbook/references/ticket-template.md`; `.opencode/skills/ticket-runbook/references/response-draft-template.md`; `.opencode/skills/ticket-runbook/references/_consistency-checklist.md`; `.opencode/skills/ticket-runbook/scripts/validate_runbook.py`; `.opencode/skills/ticket-runbook/scripts/test_validate_runbook.py`; `.opencode/skills/ticket-runbook/SKILL.md` (edit)

## Steps

1. Migrate + neutralize the runbook template: copy `runbook.md` + 6 phase files to `references/runbook/`; ticket template + response-draft to `references/`. Replace tismart-specific tokens (SDP/Activo/domain agents/`.claude` paths/session #s) with neutral wording; framework/headers English, response-facing prose Spanish.
2. Migrate + neutralize `scripts/validate_runbook.py` + `scripts/test_validate_runbook.py` (same neutralization: `CLAUDE.md` → `AGENTS.md`, `<ACTIVO>` → `<SYSTEM>`, SDP docstring refs → ticket-system).
3. Write `references/_consistency-checklist.md` — canonical runbook contract: header fields + phase sections + kill-switches + Replay-candidate enum (delegated to `validate_runbook.py` as helper); folder structure, screenshot `NN_` naming, phase-01 `Pre` populated while Step/Gate/Abort template-intact, Replay-candidate consistent with prior-art (analysis).
4. Run `uv run --locked --project .opencode/skills/ticket-runbook python .opencode/skills/ticket-runbook/scripts/test_validate_runbook.py` from the project root — must exit 0.
5. Edit `ticket-runbook/SKILL.md`: add the post-write loop; replace "the project's template/validator" with the local `references/` + `scripts/` paths; bump `version` to `1.1.0`.
6. Neutralization sweep: run `grep -riE --exclude-dir=.venv '\b(tismart|sdp|activo|belcorp|ember|atlas|ranger|lex)\b' .opencode/skills/ticket-runbook/` from the project root → no matches. Do not search the local runtime or generic `gate`: required `## Gate` headings are legitimate runbook-template structure.

## Output

- **Artifact:** 9 migrated+neutralized templates, `_consistency-checklist.md`, `validate_runbook.py`, `test_validate_runbook.py`, edited `SKILL.md`
- **Schema / shape:** runbook template keeps the 7-field header + 6 phases; `validate_runbook.py` passes its test; `SKILL.md` cites local paths + `version: 1.1.0`.

## Verify commands

- ⬜ `uv run --locked --project .opencode/skills/ticket-runbook python .opencode/skills/ticket-runbook/scripts/test_validate_runbook.py` → exit 0
- ⬜ `grep -riE --exclude-dir=.venv '\b(tismart|sdp|activo|belcorp|ember|atlas|ranger|lex)\b' .opencode/skills/ticket-runbook/` → no matches; required `## Gate` headings are legitimate template structure.

## Gate

- ⬜ `test_validate_runbook.py` exits 0
- ⬜ Neutralization grep clean (source-project/domain identifiers only; required `## Gate` headings are legitimate template structure)
- ⬜ Bastion 🧱 (Backend Architect) verifies `validate_runbook.py` (backend Python rules) — [PASS]
- ⬜ `SKILL.md` loop section present; `version: 1.1.0` set

## Abort conditions

- `test_validate_runbook.py` non-zero after neutralization → the migration broke the validator; fix before proceeding.
- Residual tismart/SDP/Activo content in any migrated file → halt, remove it; never ship domain-specific content in AICore.
