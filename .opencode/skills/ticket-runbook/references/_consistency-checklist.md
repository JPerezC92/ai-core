# Runbook — consistency checklist

> Canonical contract for artifacts written by the `ticket-runbook` skill. Applied at write-time by the skill's post-write self-verification loop (analysis) and mechanically by `scripts/validate_runbook.py` (repetitive subset). The script is a helper, not the authority — semantic correctness is the loop's analysis job.

## Validation modes

Run every command from the project root. The validator enforces only the mechanical/repetitive subset; this checklist's evidence analysis remains the agent's responsibility.

- **Fresh scaffold:** run `uv run --locked python .opencode/skills/ticket-runbook/scripts/validate_runbook.py <runbook-dir> --scaffold`. It requires the copied phase structure but intentionally permits template-body fill tokens. The analysis pass verifies phase-01 `Pre` contains this ticket's context; later phase bodies are intentionally still template content.
- **Completed phase:** before advancing completed phase `NN`, run `uv run --locked python .opencode/skills/ticket-runbook/scripts/validate_runbook.py <runbook-dir> --phase NN`. That completed phase must have no unfilled tokens.
- **Completed runbook state:** after the `Phase:` header advances, reserve `uv run --locked python .opencode/skills/ticket-runbook/scripts/validate_runbook.py <runbook-dir>` for full validation of all completed phases through that header.

## runbook/runbook.md

- Header has all 7 YAML fields: `Phase`, `SLA-due`, `Updated`, `Hypotheses-outstanding`, `Query-budget`, `Replay-candidate`, `Same-query-reruns`. *(delegated to `validate_runbook.py`)*
- `Phase` advances only after the previous phase's gate passes and the validator exits clean.
- `Replay-candidate` is one of `pending` / `yes` / `structural` / `no`, and matches the prior-art verdict. *(enum delegated; verdict-vs-prior-art is analysis)*
- `Query-budget` is `used/limit`: a fresh scaffold is `0/6`, and `6/6` is exhausted. The used value reflects actually consumed queries. *(delegated)*
- Other kill-switch counters reflect what was actually consumed: hypotheses ≤ 3 and same-query reruns ≤ 2. *(delegated)*
- `SLA-due` matches the ticket's real SLA deadline (not a placeholder). *(analysis — value must match evidence)*

## phase-NN-*.md

- Required `##` sections present: `Steps`, `Output`, `Gate`, `Abort conditions`. *(delegated)*
- Blockquote labels present: `Owner`, `Pre`, `Reads`, `Writes`. *(delegated)*
- No unfilled `<...>` placeholder tokens (except the five boilerplate tokens in `validate_runbook.py`). *(delegated)*
- `phase-01-triage.md` `Pre` is populated with THIS ticket's context; `Step`/`Gate`/`Abort` remain template-intact. *(analysis)*
- Every result value is verbatim (no paraphrase, no rounding). *(analysis)*

## Folder structure

- Ticket folder contains `screenshots/`, `validations/`, the ticket record, and `response-draft.md`. *(analysis)*
- Screenshots follow the `NN_<source>_<entity>[_<distinguisher>].png` convention; all referenced image paths exist on disk before the response phase. *(analysis)*

## Loop rule

The validator enforces only the mechanical/repetitive subset (field presence, fraction/enum parse, section/label presence, unfilled tokens, kill-switch caps). Every value that must match evidence — SLA, verdicts, counters, naming, folder contents, and phase-01 ticket context — is verified by the analysis pass against this checklist; a value is never invented to satisfy a check.
