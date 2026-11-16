<!-- core:begin -->
# Known Problem Pattern Register

Chronological, evidence-backed recurring problem patterns shared by incident and dev work. Each row is a child instance of a symptom class in `.aicore/core/knowledge/diagnostics/symptoms.md`; when a row references several classes, the primary symptom class comes first.

## Entry format

One row per record; columns exactly `ID | Date | Team | Symptom | System | Module | Problem | Discriminators | Exclusions | Evidence | Root cause | Lifecycle | Allow_exact | Status`:

- **ID** — `P-NNN` (durable — never renumbered or reused)
- **Date** — when the problem was first confirmed
- **Team** — `incident` | `dev` (mandatory discriminator)
- **Symptom** — >=1 class identifiers from the shared baseline (`S-xx` in `.aicore/core/knowledge/diagnostics/symptoms.md`) or the project's local catalog (`LOCAL:S-xx`), comma-separated, primary first (e.g. `S-05, LOCAL:S-01`)
- **System** — system the problem belongs to
- **Module** — module / component / package / tool the problem belongs to
- **Problem** — one-liner
- **Discriminators** — `field=value` signals that must all be evidenced for an `exact` match
- **Exclusions** — conditions that disqualify a match even when the discriminators align
- **Evidence** — at least one durable `case:<durable-ticket-path>` pointer (repo-relative ticket-record path); optionally `pack:<destination-relative-pack-path>` for a reusable identification pack — a multi-statement or multi-result correlation stored at the destination's declared path. The shared core never defines the destination directory. Register rows carry pointers only — never SQL statements or result tables.
- **Root cause** — the actual cause, not the symptom
- **Lifecycle** — `candidate | active | mitigated | resolved | retired` (see below)
- **Allow_exact** — `yes | no`; the per-record gate for an `exact` verdict
- **Status** — `open | closed` (open = still under analysis or awaiting a confirming case; closed = no further action)

## Lifecycle

| Lifecycle   | Meaning                                                    | Eligible verdict                                                                                                      |
| ----------- | ---------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `candidate` | First confirmed case.                                      | `structural` only                                                                                                     |
| `active`    | A second independent confirmed case confirmed the pattern. | `structural`; `exact` only when `Allow_exact: yes` and every discriminator is already evidenced in the current ticket |
| `mitigated` | A fix is in place but the problem may recur.               | `structural` only                                                                                                     |
| `resolved`  | Confirmed fixed; retained for history.                     | none — never matched                                                                                                  |
| `retired`   | Permanently removed from matching.                         | none — never matched                                                                                                  |

**Admission:** the first confirmed case admits a row as `candidate`; a `candidate` row is never an `exact` match. A second independent confirmed case may promote a `candidate` to `active`, which makes it eligible for `exact` when `Allow_exact: yes`.

**Operational gate:** admission runs via the incident-workflow register-admission step when the root cause is confirmed — before destructive collapse, never waiting for `Close out now`. Admission requires the durable `case:` pointer and never blocks on a reusable `pack:`. If the proof path is a reusable identification pack (a multi-statement or multi-result correlation) and the destination has not declared storage, ask for the destination-relative path and record `pack:` with it; the destination chooses the pack layout, the shared core never names the directory, and a register row never receives SQL statements or result tables.

Only `Team: incident` rows participate in incident identification.

## Rules

- Every row MUST reference >=1 existing class from the shared baseline catalog or the project's local catalog.
- Team MUST be `incident` or `dev`.
- Evidence-backed only — no rows without cited evidence.
- Duplicates merge into the existing row, never re-filed.
- **An empty register is valid**, and identification then reports `no_match` without halting. A register that is **missing, unreadable or malformed is not empty**: it is reported as a defect and blocks the affected verdict rather than being read as `no_match`.
- The rows themselves are destination-owned and live in the project register described under **Register location**; this document states the model and its rules.

## Register location

This document is AICore-managed and ships without rows. The authoritative project register is `incidents/diagnostics/problems.md`, created by the incident workflow's authorized initialization and never overwritten by that initialization or by synchronization. The project's own symptom classes live in `incidents/diagnostics/symptoms.md` and use the `LOCAL:S-xx` namespace; baseline classes keep `S-xx`.
<!-- core:end -->
