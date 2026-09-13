# Working analysis — consistency checklist

> Canonical contract for artifacts written by the `ticket-runbook` skill. Applied at write-time by the skill's post-write self-verification loop (analysis) and mechanically by `scripts/validate_runbook.py` (repetitive subset). The script is a helper, not the authority — semantic correctness is the loop's analysis job.

## Validation modes

Run every command from the project root. The validator enforces only the mechanical/repetitive subset; this checklist's evidence analysis remains the agent's responsibility.

- **Fresh scaffold:** run `python3 .opencode/skills/ticket-runbook/scripts/validate_runbook.py <analysis-dir> --scaffold`. It requires the copied `analysis/` structure but intentionally permits template-body fill tokens. The analysis pass verifies `01-identify.md` `Pre` contains this ticket's context; later step bodies are intentionally still template content.
- **Completed step:** before advancing completed step `NAME` (`identify`, `investigate`, `synthesize`), run `python3 .opencode/skills/ticket-runbook/scripts/validate_runbook.py <analysis-dir> --step NAME`. That completed step must have no unfilled tokens.
- **Completed working state:** after the `Phase:` header advances, reserve `python3 .opencode/skills/ticket-runbook/scripts/validate_runbook.py <analysis-dir>` for full validation of all completed steps through that header.
- **Close-out:** after the working set collapses, run `python3 .opencode/skills/ticket-runbook/scripts/validate_runbook.py <ticket-folder> --close-out`. It verifies the durable set and confirms the working set is gone.

## analysis/state.md

- Header has all 7 YAML fields: `Phase`, `SLA-due`, `Updated`, `Hypotheses-outstanding`, `Query-budget`, `identification_verdict`, `Same-query-reruns`. *(delegated to `validate_runbook.py`)*
- `Phase` is one of `identify` / `investigate` / `synthesize` and advances only after the previous step's gate passes and the validator exits clean. *(enum delegated)*
- `identification_verdict` is one of `pending` / `exact` / `structural` / `no_match`. *(enum delegated; verdict-vs-register is delegated for cited `P-NNN`/lifecycle consistency and is analysis for discriminator evidence)*
- `Query-budget` is `used/limit`: a fresh scaffold is `0/6`, and `6/6` is exhausted. The used value reflects actually consumed queries. *(delegated)*
- Other kill-switch counters reflect what was actually consumed: hypotheses ≤ 3 and same-query reruns ≤ 2. *(delegated)*
- `SLA-due` matches the ticket's real SLA deadline (not a placeholder). *(analysis — value must match evidence)*

## Register-first identification (`knowledge/problems.md` → verdict)

- A class matches only when every `Required signals` entry in `knowledge/symptoms.md` is present and no `Exclusions` entry is present. *(analysis)*
- Only `S-xx` → `Team: incident` `P-NNN` can produce `exact` or `structural`. Resolved-ticket archives, patterns registers, KBA/RCA catalogs, and knowledge search MUST NOT issue a verdict. *(analysis)*
- **An empty register is valid and yields `no_match`; never halt on an empty register.** *(delegated when `identification_verdict`/cited IDs are parsed)*
- `exact`: exactly one cited `P-NNN`, `Lifecycle: active`, `Allow_exact: yes`, and every discriminator already evidenced in the current ticket. *(cited-ID/lifecycle delegated; discriminator evidence is analysis)*
- `structural`: exactly one cited `P-NNN` with `Lifecycle: candidate` or `active`. *(delegated)*
- `no_match`: no cited `P-NNN`. `pending` is scaffold-only and must be replaced when the identify step closes. *(delegated)*
- Lifecycle `resolved` / `retired` rows are never matched; `mitigated` is `structural` only. *(analysis)*

## analysis/01-identify.md, 02-investigate.md, 03-synthesize.md

- Required `##` sections present: `Steps`, `Output`, `Gate`, `Abort conditions`. *(delegated)*
- Blockquote labels present: `Owner`, `Pre`, `Reads`, `Writes`. *(delegated)*
- No unfilled `<...>` placeholder tokens (except the boilerplate tokens in `validate_runbook.py`). *(delegated)*
- `01-identify.md` `Pre` is populated with THIS ticket's context; `Step`/`Gate`/`Abort` remain template-intact. *(analysis)*
- Every result value is verbatim (no paraphrase, no rounding). *(analysis)*

## Folder structure while open

- Ticket folder contains `screenshots/`, `validations/`, the ticket record, and `response-draft.md`. *(analysis)*
- Screenshots follow the `NN_<source>_<entity>[_<distinguisher>].png` convention; all referenced image paths exist on disk before the response phase. *(analysis)*

## Close-out collapse

- Durable set: `ticket_<id>.md` plus `screenshots/`, `validations/`, and every other cited evidence file. *(delegated)*
- Working set removed: `analysis/state.md` and every `analysis/*.md`, plus `response-draft.md`. *(delegated)*
- Every `path:` recorded in an Imagen block resolves to an existing repo-relative file. *(delegated)*
- Each used image records `url:` when the ticket system returned one, and never records a fabricated `url:`. *(analysis)*
- `screenshots/`, `validations/`, and other cited evidence files are never deleted at close. *(delegated)*

## Loop rule

The validator enforces only the mechanical/repetitive subset (field presence, fraction/enum parse, section/label presence, unfilled tokens, kill-switch caps, cited-`P-NNN`/lifecycle consistency, and close-out file presence). Every value that must match evidence — SLA, discriminator evidence, verdict rationale, counters, naming, folder contents, and step context — is verified by the analysis pass against this checklist; a value is never invented to satisfy a check.
