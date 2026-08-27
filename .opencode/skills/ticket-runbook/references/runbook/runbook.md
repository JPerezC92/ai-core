---
Phase: "01"
SLA-due: "YYYY-MM-DDTHH:MM"
Updated: "YYYY-MM-DDTHH:MM"
Hypotheses-outstanding: "3/3"
Query-budget: "0/6"
Replay-candidate: "pending"
Same-query-reruns: "0/2"
---
<!-- Query-budget is used/limit: fresh scaffold 0/6; 6/6 is exhausted. -->
<!-- Replay-candidate valid values:
     pending    — initial value at scaffold; phase-02 replaces it
     yes        — exact match (same system + module + failure + identifying values); skip phases 03/04/05
     structural — pattern match (same failure chain, different country/entity); skip phase 03, run phase 04 with adapted queries
     no         — no match; full investigation phases 02-06
-->

# Runbook — Ticket <ID>

> State machine header for the incident analysis flow. Agents update this file at every phase transition.

## Phase index

| Phase | File | Owner | Status |
|---|---|---|---|
| 01 — Triage | `phase-01-triage.md` | Cipher 🔓 (Lead Orchestrator) | ⬜ |
| 02 — Prior art | `phase-02-priorart.md` | Investigator | ⬜ |
| 03 — Hypothesis | `phase-03-hypothesis.md` | Investigator | ⬜ |
| 04 — Validate | `phase-04-validate.md` | Investigator | ⬜ |
| 05 — Synthesis | `phase-05-synthesis.md` | Cipher 🔓 (Lead Orchestrator) | ⬜ |
| 06 — Respond | `phase-06-respond.md` | Quill 🪶 (Note Drafter) | ⬜ |

## Kill-switch status

| Kill-switch | Budget | Consumed | Remaining |
|---|---|---|---|
| Hypotheses | 3 | 0 | 3 |
| Queries | 6 | 0 | 6 |
| Same-query reruns | 2 | 0 | 2 |
| SLA warn at | 75% | — | — |

> **Warn-if-recent rule:** If `Updated` is within the last 10 minutes AND `Phase` matches the phase an agent is about to execute — halt and report: "runbook.md was updated less than 10 minutes ago. Another session may be active. Verify before proceeding."
