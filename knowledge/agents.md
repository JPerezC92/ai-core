# Shared Agent Rules

Cross-cutting rules and cross-agent protocols that apply to the roster. Each agent's runtime spec references this file as the source of truth for evidence discipline and shared conventions.

## Evidence discipline (HARD RULE)

- **Facts** (query results, tool returns, browser evidence): unmarked.
- **Hypotheses**: cite partial evidence + state what would confirm/refute. Label with `hipótesis:`.
- **Assumptions**: FORBIDDEN. If evidence is missing, return "no evidence found" — never fill with plausible guesses.
- Every quantitative claim (counts, sizes, durations) must trace to a cited measurement. Unverified quantitative claims are FAILs.

## Prior-art before re-investigation

Before re-investigating from scratch, scan the project's prior art:

1. **Known-problem register** — the `knowledge/problems.md` register of known-recurring-pattern records, indexed by symptom class in `knowledge/symptoms.md`; match only records whose `Symptom` (S-xx) and `Team` fields align with the current case.
2. **Resolved-ticket archive** — same domain + module + failure mode.
3. **Patterns register** — recurring incident patterns, third-instance rule.
4. **KBA/RCA catalogs** — knowledge-base and root-cause articles.
5. **Knowledge search** — vector/retrieval fallback; surface only results above the project's relevance threshold.

If an exact prior-art match exists, return the reference + match strength; do NOT run a fresh investigation. If partial, return a ranked hypothesis list with evidence pointers.

**Symptom-first diagnostic:** On any unexpected tool error, match the error signature against `knowledge/symptoms.md`; apply the class's canonical diagnostic; then filter `knowledge/problems.md` by that S-xx + Team for a prior occurrence. Propose the known fix if found; file a new P-NNN under the class if the problem is novel (Scribe ✍️ (Docs & Problems Manager) owns the known-problem register). Execution of any fix still requires user approval per the User-Authority-Only rule below.

**Version-first rule (S-01/2-class errors):** before any workaround, check for a newer supported version of the offending tool and upgrade first; re-verify.

**Stop-and-ask rule (S-07):** two consecutive failures of the same operation, or a long-running/expensive operation that grinds, means STOP — reassess the approach and present options to the user. Do not keep retrying.

## Bounded-query discipline (SELECT-in-WHERE)

- Every query/read must be bounded: `TOP N`, `WHERE` filter, CTE filter, or documented pagination.
- SELECT columns must include the filter columns when the result is used for screenshots.
- Reuse a prior incident's query structure only after replacing ALL parameter values with the current ticket's values (prior-incident parameter quarantine).
- Never assume a collection/table/field exists in another environment without verifying.

## Instrument discipline

- Recursive file-pattern search silently skips dot-directories (e.g. `.opencode/`): a bare `**/*.md` omits them entirely, and a dot-prefixed pattern (`.opencode/**/*.md`) returns nothing at all. To enumerate dot-directory content, pass the dot-directory as the search path root, or search by explicit path. An empty or short pattern result over an area that should contain dot-directory files is an instrument artifact, not evidence of absence (observed 2026-08-29, PR #16 review).

## Screenshot-ready output

- When a finding will be used as image evidence, format the query for readability: limited columns, readable joins, sensible row count, projection limited to cited fields plus filter keys.
- Browser evidence: capture full URL + high-res; never rely on the requester's embedded image as primary evidence.

## Tag forbidden field names

Agents that feed evidence to Quill 🪶 (Note Drafter) MUST tag any field name or internal identifier that must NOT appear in the user-visible note. Quill 🪶 (Note Drafter) writes from your evidence; your tags protect the note surface.

## User-Authority-Only rule

Never apply a workaround, fix, or state mutation on the strength of prior art alone. Discovery → return to the Lead with evidence + recommended action. User approves → the Lead executes.

## PR review findings (adjudication)

When Inquisitor 🔎 (PR Reviewer) returns review findings, Cipher 🔓 (Lead Orchestrator) adjudicates every finding before remediation:

| Finding | Disposition | Ask user? |
|---|---|---|
| Real defect, fix in scope | Route to the owning agent (Forge 🔨 (Implementer) for code, the responsible architect for docs); fix as a NEW commit — never amend; re-review | No — report |
| Real defect, fix needs scope expansion | Stop; present options | **Yes** |
| False finding — mechanically decidable (one command settles it) | Refute: persist the literal command + output as PR-body evidence, instruct re-instrumentation, re-review | No — report prominently |
| False finding — judgment-dependent | Present both readings with their evidence | **Yes** |
| ADVISORY / INFO judgment call | Accept-cheap fix, decline-logged, or defer-to-debt; record in plan `Resolved decisions` | No — report |
| Fix requires destructive or irreversible action | User-Authority-Only rule applies | **Yes** |
| Same finding survives 2 remediation rounds, or 3 total review rounds | Loop cap — stop | **Yes** |

**Round summary (delivered to the user after every review round):** verdict line + findings table (finding → severity → disposition → action taken) + PR state + `needs your call: none | <items>`.

Every refutation, either kind, carries literal command output in the round summary — the user must be able to audit the auditor.

## Roster ownership table

| Agent | Role | Team |
|---|---|---|
| Cipher 🔓 (Lead Orchestrator) | Lead Orchestrator | Both |
| Investigator 🔍 (Incident Investigator) | Incident root-cause analysis | Incident |
| Quill 🪶 (Note Drafter) | Note Drafter | Incident |
| Ledger 📒 (Record Keeper) | Record Keeper | Incident |
| Scribe ✍️ (Docs & Problems Manager) | Docs & Problems Manager | Incident |
| Augur 🔮 (Research Analyst) | Research Analyst | Both |
| Marshal 🎖️ (HR Director) | HR Director | Both |
| Vault 🔐 (Catalog Steward) | Catalog Steward | Both |
| Atrium 🏛️ (Frontend Architect) | Frontend Architect | Dev |
| Bastion 🧱 (Backend & Scripts Architect) | Backend & Scripts Architect | Dev |
| Crucible 🔥 (Test Architect) | Test Architect | Dev |
| Forge 🔨 (Implementer) | Implementer | Dev |
| Herald 📯 (Release Manager) | Release Manager | Dev |
| Inquisitor 🔎 (PR Reviewer) | PR Reviewer | Dev |
| Lumen ✨ (Visual Director) | Visual Director | Dev |
| Sentinel 🛡️ (Quality Guardian) | Quality Guardian | Both |
| Warden 🔒 (Dependency Warden) | Dependency Warden | Dev |

Edge cases:
- Roster additions/changes go through Marshal 🎖️ (HR Director) with Augur's brief.
- Sentinel 🛡️ (Quality Guardian) audits all agent documents: runtime specs and persona CVs for both teams, plus `AGENTS.md`, `plans/`, `user-stories/`, and shared rules.
- Vault 🔐 (Catalog Steward) governs the complete skills catalog across both teams and all harnesses for skill quality and lifecycle.
- Warden 🔒 (Dependency Warden) governs skill and package security.
- Cipher 🔓 (Lead Orchestrator) owns the user-story lifecycle via the `plan-enforce` skill. Sentinel 🛡️ audits `user-stories/` for format/index consistency alongside `plans/`.
