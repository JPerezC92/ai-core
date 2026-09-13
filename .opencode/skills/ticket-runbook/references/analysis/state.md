---
Phase: "identify"
SLA-due: "YYYY-MM-DDTHH:MM"
Updated: "YYYY-MM-DDTHH:MM"
Hypotheses-outstanding: "3/3"
Query-budget: "0/6"
identification_verdict: "pending"
Same-query-reruns: "0/2"
---
<!-- Query-budget is used/limit: fresh scaffold 0/6; 6/6 is exhausted. -->
<!-- identification_verdict valid values:
     pending    — set at scaffold; the identify step replaces it
     exact      — exactly one active incident P-NNN with allow_exact: yes and every discriminator already evidenced
     structural — exactly one candidate or active incident P-NNN; its hypothesis still needs current-ticket validation
     no_match   — no eligible incident P-NNN (an empty register always yields no_match)
-->

# Working analysis — Ticket <ID>

> State header for the incident analysis flow. Agents update this file at every step transition. This file and the other `analysis/*.md` files are removed at close-out after the ticket record and cited evidence are verified.

## Step index

| Step | File | Owner | Status |
|---|---|---|---|
| identify | `01-identify.md` | Cipher 🔓 (Lead Orchestrator) | ⬜ |
| investigate | `02-investigate.md` | Investigator 🔍 (Incident Investigator) | ⬜ |
| synthesize | `03-synthesize.md` | Cipher 🔓 (Lead Orchestrator) | ⬜ |
| respond | `response-draft.md` | Quill 🪶 (Note Drafter) | ⬜ |

## Kill-switch status

| Kill-switch | Budget | Consumed | Remaining |
|---|---|---|---|
| Hypotheses | 3 | 0 | 3 |
| Queries | 6 | 0 | 6 |
| Same-query reruns | 2 | 0 | 2 |
| SLA warn at | 75% | — | — |

> **Warn-if-recent rule:** If `Updated` is within the last 10 minutes AND `Phase` matches the step an agent is about to execute — halt and report: "state.md was updated less than 10 minutes ago. Another session may be active. Verify before proceeding."
