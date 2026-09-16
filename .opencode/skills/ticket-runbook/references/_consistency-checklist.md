# Working analysis — consistency checklist

> Canonical contract for artifacts written by the `ticket-runbook` skill. Applied at write-time by the skill's post-write self-verification loop (analysis) and mechanically by `scripts/validate_runbook.py` (repetitive subset). The script is a helper, not the authority — semantic correctness is the loop's analysis job.

## Validation modes

Run every command from the project root. The validator enforces only the mechanical/repetitive subset; this checklist's evidence analysis remains the agent's responsibility.

- **Fresh scaffold:** run `python3 .opencode/skills/ticket-runbook/scripts/validate_runbook.py <analysis-dir> --scaffold`. It requires the copied `analysis/` structure but intentionally permits template-body fill tokens. The analysis pass verifies `01-identify.md` `Pre` contains this ticket's context; later step bodies are intentionally still template content.
- **Completed step:** before advancing completed step `NAME` (`identify`, `investigate`, `synthesize`), run `python3 .opencode/skills/ticket-runbook/scripts/validate_runbook.py <analysis-dir> --step NAME`. That completed step must have no unfilled tokens.
- **Completed working state:** after the `Phase:` header advances, reserve `python3 .opencode/skills/ticket-runbook/scripts/validate_runbook.py <analysis-dir>` for full validation of all completed steps through that header.
- **Pre-close readiness (before collapse):** run `python3 .opencode/skills/ticket-runbook/scripts/validate_runbook.py <ticket-folder> --pre-close`. It is read-only and proves the durable record and complete working set are ready before any deletion.
- **Close-out postcondition (after collapse):** run `python3 .opencode/skills/ticket-runbook/scripts/validate_runbook.py <ticket-folder> --close-out`. It verifies the durable set and confirms the working set is gone.

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

## Pre-close readiness (before collapse)

- Exactly one `ticket_<id>.md` record exists — zero or multiple is a halt. *(delegated)*
- Working set complete and exact: `analysis/state.md`, `01-identify.md`, `02-investigate.md`, `03-synthesize.md` — nothing missing, nothing unexpected; `Phase: synthesize`. *(delegated)*
- `response-draft.md` and the `screenshots/` and `validations/` directories are present. *(delegated)*
- Every machine-addressable `path:` recorded in the ticket record is spelled ticket-folder-relative (`screenshots/<filename>`) and resolves inside the ticket folder to an existing file; repo-relative spellings fail. *(delegated)*
- Identification/register consistency holds for the cited `P-NNN`. *(delegated)*
- The mode is read-only: no ticket file is created, edited, renamed, or deleted. *(delegated — non-mutation)*

## Semantic close-out confirmation (before authorization)

- Register admission from the confirmed root cause is complete: `case:` pointer recorded, plus an optional `pack:` pointer for a reusable identification pack, and an optional `diagnostic:` sidecar pointer when the confirming query is reusable under protocol-v1. *(analysis)*
- Every executed query in `02-investigate.md` — manual `Query:` blocks and verifier-routed evidence — is preserved verbatim in `ticket_<id>.md` or a cited `validations/` artifact BEFORE collapse deletes the working file. *(analysis)*
- Every non-`path:` evidence citation (prose/backtick references) in the ticket record resolves to real evidence. *(analysis)*
- Each used image records `url:` when the ticket system returned one, and never records a fabricated `url:`. *(analysis)*
- Posted-response fidelity and content/completeness gates pass. *(analysis)*
- The exact phrase `Close out now` is obtained before any deletion. *(analysis)*

## Authorization and collapse

- Only `analysis/state.md`, every `analysis/*.md`, and `response-draft.md` are deleted — only after pre-close passes plus exact authorization. *(analysis)*
- `ticket_<id>.md`, `screenshots/`, `validations/`, and every other cited evidence file are never deleted at close. *(delegated)*

## Close-out postcondition (after collapse)

- Durable set: `ticket_<id>.md` plus `screenshots/`, `validations/`, and every other cited evidence file; the working set (including `response-draft.md`) is gone. *(delegated)*
- `--close-out` exits 0; exit 2 (no record) and exit 1 are both halts. *(delegated)*
- Failure after collapse halts without deleting durable evidence to satisfy a validator. *(analysis)*

## Query retention and register admission (close-out)

- Every executed query in `02-investigate.md` — manual `Query:` blocks and verifier-routed evidence — is preserved verbatim in `ticket_<id>.md` or a cited `validations/` artifact BEFORE collapse deletes the working file. *(analysis)*
- When the confirming query is reusable, it is persisted as parameterized SQL plus an adjacent `.verifier.yaml` sidecar at the destination project's declared query-storage path; the row's Evidence records `diagnostic:<destination-relative-sidecar-path>`. A reusable identification pack (a multi-statement or multi-result correlation) is instead persisted at the destination-chosen path and recorded as `pack:<destination-relative-pack-path>`; it is not a verifier and is never evaluated by `query_verification.py`. AICore never defines the destination directory. *(analysis)*
- A later `structural` ticket follows a recorded `pack:` pointer first — resolving the destination-relative path and replaying the correlation with current-ticket keys under destination-owned execution (AICore never executes or parses the pack) — then follows the `diagnostic:` pointer through protocol-v1 when present (one existing Query-budget slot), before framing a new query. *(analysis)*
- Register admission on a confirmed root cause happens before collapse and never waits for `Close out now`; collapse itself requires explicit user authorization. *(analysis)*

## Loop rule

The validator enforces only the mechanical/repetitive subset (field presence, fraction/enum parse, section/label presence, unfilled tokens, kill-switch caps, cited-`P-NNN`/lifecycle consistency, pre-close readiness, and close-out file presence). Every value that must match evidence — SLA, discriminator evidence, verdict rationale, counters, naming, folder contents, and step context — is verified by the analysis pass against this checklist; a value is never invented to satisfy a check.
