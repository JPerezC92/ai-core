# CV Migration Map — Evidence-Backed Phase 8

## Scope and method

This map replaces the prior summary inventory. The prior Dev team, Incident team, and Cross-cutting team inventory rows were used only as leads. Each statement below was independently checked against the current CV and its current runtime authority: all 17 `agents/*/profile.md` files, all 16 `.opencode/agents/*.md` files, and `AGENTS.md` for Cipher 🔓 (L2 Lead).

**Disposition meanings**

- **existing authority** — the cited current runtime authority already owns the operation; remove it from the CV without changing the contract.
- **planned runtime move** — the operation is valid but has no current owner clause in the correct runtime authority; Phase 9 must add it there before the CV is normalized.
- **stale retirement** — the claim is unsupported or contradicted by the cited current authority; remove it and do not invent a replacement duty.

The map intentionally lists operations only. Persona observations and voice may be rewritten within the canonical CV sections, but no operational sentence below remains in a CV.

## Canonical CV H1s

| Agent | Required H1 |
|---|---|
| Atrium 🏛️ (Frontend Architect) | `# Atrium 🏛️ — Frontend Architect` |
| Bastion 🧱 (Backend Architect) | `# Bastion 🧱 — Backend Architect` |
| Crucible 🔥 (Test Architect) | `# Crucible 🔥 — Test Architect` |
| Forge 🔨 (Implementation Agent) | `# Forge 🔨 — Implementation Agent` |
| Herald 📯 (Release Manager) | `# Herald 📯 — Release Manager` |
| Inquisitor 🔎 (PR Reviewer) | `# Inquisitor 🔎 — PR Reviewer` |
| Lumen ✨ (Visual Director) | `# Lumen ✨ — Visual Director` |
| Sentinel 🛡️ (Quality Guardian) | `# Sentinel 🛡️ — Quality Guardian` |
| Warden 🔒 (Dependency Warden) | `# Warden 🔒 — Dependency Warden` |
| Investigator 🔍 (Incident Investigator) | `# Investigator 🔍 — Incident Investigator` |
| Ledger 📒 (record-keeper) | `# Ledger 📒 — record-keeper` |
| Quill 🪶 (note drafter) | `# Quill 🪶 — note drafter` |
| Scribe ✍️ (docs & problem management) | `# Scribe ✍️ — docs & problem management` |
| Cipher 🔓 (L2 Lead) | `# Cipher 🔓 — L2 Lead` |
| Augur 🔮 (Senior Research Analyst) | `# Augur 🔮 — Senior Research Analyst` |
| Marshal 🎖️ (HR Director) | `# Marshal 🎖️ — HR Director` |
| Vault 🔐 (Catalog Steward) | `# Vault 🔐 — Catalog Steward` |

## Quill 🪶 (note drafter) decision record

**User decision (2026-08-23):** “surgical patch by default; fresh complete draft only on explicit user request.” This is the sole correction contract.

| Live clause | Decision for the runtime canonicalization | Authority |
|---|---|---|
| `.opencode/agents/quill.md` — `## Your Role`, lines 14–17: first draft, then “Patch … apply ONE surgical Edit … MUST NOT regenerate the full draft from scratch” | **Retain.** This is the selected default contract. | `.opencode/agents/quill.md` — `## Your Role` |
| `.opencode/agents/quill.md` — `## Your Role`, lines 77–80: “any change … produces a FRESH complete draft … The fresh draft replaces `response-draft.md` in full.” | **Revise.** Retire the mandatory fresh-complete-draft and full-replacement requirements. Replace them with surgical edits by default; a complete regeneration is permitted only on an explicit user request. | `.opencode/agents/quill.md` — `## Your Role`; user decision recorded in `plans/audit-remediation-20260821/plan.md` — `## Resolved decisions` |
| `.opencode/agents/quill.md` — `## Your Role`, lines 81–85: mandatory two-pass draft/rewrite sequence for every change | **Revise.** Keep a post-edit self-audit, but do not require a fresh draft pass or full-file replacement for a surgical patch. | `.opencode/agents/quill.md` — `## Patch-not-rewrite (CRITICAL)` and `## Self-audit before return (CRITICAL)` |
| `.opencode/agents/quill.md` — `## Self-audit before return (CRITICAL)`, lines 89–108 | **Retain, with wording aligned to surgical patches.** The audit follows both a first draft and a patch; it does not authorize regeneration. | `.opencode/agents/quill.md` — `## Self-audit before return (CRITICAL)` |
| `.opencode/agents/quill.md` — `## Patch-not-rewrite (CRITICAL)`, lines 110–122 | **Retain.** It is consistent with the selected contract. | `.opencode/agents/quill.md` — `## Patch-not-rewrite (CRITICAL)` |

## Dev team migration entries

### Atrium 🏛️ (Frontend Architect)

| CV line / quoted operational statement | Disposition | Exact source authority |
|---|---|---|
| 10 — “Reports violations with file:line + exact fix — never patches the code itself” | existing authority | `.opencode/agents/atrium.md` — `## Your Role` and `## Output Format` |
| 13 — “components → hooks → services → types is sacred; reverse imports flagged on sight” | existing authority | `.opencode/agents/atrium.md` — `## Architecture Overview` |
| 14 — “every rule traces back to the runtime spec rulebook; no improvised judgments” | existing authority | `.opencode/agents/atrium.md` — `## Your Role` |
| 15 — “audits + reports; never edits application source code. May edit dependency manifests (`package.json`) and run `pnpm install` … after Warden 🔒 (Dependency Warden) approval” | existing authority | `.opencode/agents/atrium.md` — `## Your Role`, `## Dependency Ownership`, and `## Hard Rules` |
| 16 — “rulebook describes target architecture; current portfolio code may [FAIL] until migration” | existing authority | `.opencode/agents/atrium.md` — `## Hard Rules` |
| 17 — “owns `dependencies` and non-test `devDependencies` … Tiebreaker … with Crucible 🔥 (Test Architect)” | existing authority | `.opencode/agents/atrium.md` — `## Dependency Ownership` |
| 20 — “Cipher 🔓 (L2 Lead) … edits frontend code → auto-invokes Atrium 🏛️ (Frontend Architect) …” | planned runtime move | `AGENTS.md` — planned Phase 9 `## Identity & Role` automatic-dispatch clause for Atrium 🏛️ (Frontend Architect), as specified by `phase-09-marshal.md` — step 4 |
| 21 — “reads files, applies rulebook, returns [PASS]/[FAIL]/[UNCERTAIN] report” | existing authority | `.opencode/agents/atrium.md` — `## Your Role`, `## Output Format`, and `## When Uncertain` |
| 22 — “Cipher 🔓 (L2 Lead) … routes fixes to the implementing agent” | existing authority | `AGENTS.md` — `## Identity & Role` |
| 23 — parallel Atrium 🏛️ (Frontend Architect)/Lumen ✨ (Visual Director) post-implementation audit and independent reports | existing authority | `.opencode/agents/lumen.md` — `## Audit Gate and Severity Threshold` |
| 24 — “Marshal 🎖️ (HR Director) … maintains Atrium’s persona + runtime spec; Sentinel 🛡️ (Quality Guardian) … gates those edits” | existing authority | `.opencode/agents/marshal.md` — `## Maintenance`; `.opencode/agents/sentinel.md` — `## Audit Workflow` |
| 27 — “Never edits application source code — output is reports only. Dependency manifest changes (`package.json`, `pnpm install`) within the owned domain are explicitly permitted.” | existing authority | `.opencode/agents/atrium.md` — `## Dependency Ownership` and `## Hard Rules` |
| 28 — “Never makes hiring decisions” | existing authority | `.opencode/agents/marshal.md` — `## Your Role` and `## Hard Rules` |
| 29 — uncertainty handling and escalation to Cipher 🔓 (L2 Lead) | existing authority | `.opencode/agents/atrium.md` — `## When Uncertain` |
| 30 — “Never trims rules to match current code” | existing authority | `.opencode/agents/atrium.md` — `## Hard Rules` |

### Bastion 🧱 (Backend Architect)

| CV line / quoted operational statement | Disposition | Exact source authority |
|---|---|---|
| 10 — backend/Python rulebook selection, layer boundary, and “Reports violations … never patches” | existing authority | `.opencode/agents/bastion.md` — `## Your Role`, `## DOMAIN LAYER`, and `## PYTHON BACKEND` |
| 13 — NestJS dependency direction and Python zone-boundary isolation | existing authority | `.opencode/agents/bastion.md` — `## DOMAIN LAYER` and `## PYTHON BACKEND` → `### MODULE BOUNDARIES` |
| 14 — file-type branch by application TypeScript versus tooling Python | existing authority | `.opencode/agents/bastion.md` — `## Your Role` |
| 15 — “audits + reports; never edits … [PASS]/[FAIL]/[UNCERTAIN]” | existing authority | `.opencode/agents/bastion.md` — `## Your Role`, `## Output Format`, and `## Hard Rules` |
| 16 — aspirational target / current code may fail | existing authority | `.opencode/agents/bastion.md` — `## Hard Rules` |
| 19 — Cipher 🔓 (L2 Lead) routing of backend, tooling, and plan-scoped Python audit | existing authority | `AGENTS.md` — `## Identity & Role`; `.opencode/agents/bastion.md` — `## Your Role` |
| 20 — rulebook selection and report signal | existing authority | `.opencode/agents/bastion.md` — `## Your Role`, `## Output Format`, and `## When Uncertain` |
| 21 — Cipher 🔓 (L2 Lead) routes fixes to Forge 🔨 (Implementation Agent) | existing authority | `AGENTS.md` — `## Identity & Role` |
| 22 — Marshal 🎖️ (HR Director)/Sentinel 🛡️ (Quality Guardian) maintenance route | existing authority | `.opencode/agents/marshal.md` — `## Maintenance`; `.opencode/agents/sentinel.md` — `## Audit Workflow` |
| 25–28 — report-only, no hiring, uncertainty route, and no rule trimming | existing authority | `.opencode/agents/bastion.md` — `## Hard Rules` and `## When Uncertain` |

### Crucible 🔥 (Test Architect)

| CV line / quoted operational statement | Disposition | Exact source authority |
|---|---|---|
| 10 — test-pyramid and mock-boundary rules | existing authority | `.opencode/agents/crucible.md` — `## Test Pyramid Overview` |
| 13–15 — pyramid layers, shared mock tooling, and red-phase compatibility | existing authority | `.opencode/agents/crucible.md` — `## BACKEND UNIT TESTS`, `## FRONTEND UNIT TESTS`, and `## SHARED TESTING TOOL CONSISTENCY` |
| 16–17 — report-only source/test auditing plus test-dependency ownership and Warden 🔒 (Dependency Warden)-approved `pnpm install` | existing authority | `.opencode/agents/crucible.md` — `## Your Role`, `## Dependency Ownership`, `## Bash Grant Scope`, and `## Hard Rules` |
| 20 — auto-invocation after test edit | planned runtime move | `AGENTS.md` — planned Phase 9 `## Identity & Role` automatic-dispatch clause for Crucible 🔥 (Test Architect), as specified by `phase-09-marshal.md` — step 4 |
| 21–22 — test report and Cipher 🔓 (L2 Lead) fix routing | existing authority | `.opencode/agents/crucible.md` — `## Your Role` and `## Output Format`; `AGENTS.md` — `## Identity & Role` |
| 23 — Marshal 🎖️ (HR Director)/Sentinel 🛡️ (Quality Guardian) maintenance route | existing authority | `.opencode/agents/marshal.md` — `## Maintenance`; `.opencode/agents/sentinel.md` — `## Audit Workflow` |
| 26–29 — no source/test edits, dependency exception, no hiring, uncertainty route, and mock-boundary prohibition | existing authority | `.opencode/agents/crucible.md` — `## Hard Rules`, `## Bash Grant Scope`, and `## When Uncertain` |

### Forge 🔨 (Implementation Agent)

| CV line / quoted operational statement | Disposition | Exact source authority |
|---|---|---|
| 10 — minimum implementation, Atrium 🏛️ (Frontend Architect) findings, fresh rulebook read, and blocker escalation | existing authority | `.opencode/agents/forge.md` — `## Your Role`, `## Warmup (every task session)`, `## Workflow` → `### Blocker handling` |
| 13–17 — layer direction, rulebook-first, minimum scope, escalation, and [PASS] completion gate | existing authority | `.opencode/agents/forge.md` — `## Your Role`, `## Warmup (every task session)`, `## Workflow`, and `## Hard Rules` |
| 20–25 — one-step dispatch, Atrium 🏛️ (Frontend Architect)/Crucible 🔥 (Test Architect) gates, dependency proposal route, git ownership, and Marshal 🎖️ (HR Director)/Sentinel 🛡️ (Quality Guardian) route | existing authority | `.opencode/agents/forge.md` — `## Your Role`, `## Workflow`, and `## Dependency proposal`; `AGENTS.md` — `## Identity & Role`; `.opencode/agents/marshal.md` — `## Maintenance` |
| 28–35 — shell, install, git, ticket/artifact, architecture, test, and completion prohibitions | existing authority | `.opencode/agents/forge.md` — `## Hard Rules` |
| 36–45 — autofix allowlist, Python-maintenance command exception, and post-command Bastion 🧱 (Backend Architect) gate | existing authority | `.opencode/agents/forge.md` — `## Hard Rules` |

### Herald 📯 (Release Manager)

| CV line / quoted operational statement | Disposition | Exact source authority |
|---|---|---|
| 10 — “Never commits until all signals are in.” | existing authority | `.opencode/agents/herald.md` — `## Your Role`; `## Workflow` → `### Upstream trigger`; and `## Hard Rules` → `### Scope and authority` |
| 13 — “independently evaluates the supplied audit evidence” | stale retirement | `.opencode/agents/herald.md` — `## Your Role` explicitly says “do not reassess audit-evidence quality”; Cipher 🔓 (L2 Lead) owns evaluation in `AGENTS.md` — `## Identity & Role` |
| 14 — commit/PR prose, skills, `commit.txt`, and `pr-draft.md` | existing authority | `.opencode/agents/herald.md` — `## Execution steps`, `## Commit Message Standards`, and `## PR Description Standards` |
| 15 — `git status` discovery/classification and explicit staging | existing authority | `.opencode/agents/herald.md` — `## Execution steps` |
| 16 — immutable PR-head context retention | existing authority | `.opencode/agents/herald.md` — `## Execution steps` → `### PR-head handoff and retained checkout` and `## Hard Rules` → `### PR lifecycle` |
| 17 — squash strategy, user-only merge, non-PR `git merge` exception | existing authority | `.opencode/agents/herald.md` — `## Execution steps` and `## Hard Rules` → `### PR lifecycle` |
| 20–26 — evaluated gate packet, discovery/staging, skills, merge policy, PR handoff, hook-failure route, and Marshal 🎖️ (HR Director)/Sentinel 🛡️ (Quality Guardian) route | existing authority | `.opencode/agents/herald.md` — `## Roster Context`, `## Workflow`, `## Execution steps`, and `## Hook failure handling` |
| 29–38 — source/persona/hiring boundaries, invocation/gate restriction, branch/merge/review-context, bypass/amend/staging prohibitions | existing authority | `.opencode/agents/herald.md` — `## Hard Rules` → `### Scope and authority`, `### Git integrity`, and `### PR lifecycle` |

### Inquisitor 🔎 (PR Reviewer)

| CV line / quoted operational statement | Disposition | Exact source authority |
|---|---|---|
| 11 — evidence/line-citation/report-signal operating claims | existing authority | `.opencode/agents/inquisitor.md` — `## Your Role`, `## Gate Signal Protocol`, and `## Output Templates` |
| 13 — architecture, dependency, and markdown lane boundaries | existing authority | `.opencode/agents/inquisitor.md` — `## Roster Context` and `## Hard Rules` |
| 19 — post-PR test-plan coordinator loop and `gh pr edit --body-file` | existing authority | `.opencode/agents/inquisitor.md` — `## Test-Plan Verification Workflow` |
| 23 — `git diff main...HEAD` review range | stale retirement | `.opencode/agents/inquisitor.md` — `## Your Role`, `## Workflow`, and `## Hard Rules` require a live PR `headRefOid` and `git diff origin/main...<head-sha>`; `main...HEAD` is not a permitted substitute. |
| 24–26 — live-compatible cross-file boundary, evidence citation, and one gate signal | existing authority | `.opencode/agents/inquisitor.md` — `## Your Role`, `## Workflow`, and `## Gate Signal Protocol` |
| 27 — “posts a GitHub comment … [ADVISORY] or [BLOCK]” | stale retirement | `.opencode/agents/inquisitor.md` — `## Your Role` and `## Hard Rules` forbid GitHub comments and reviews for every signal. |
| 28 — test-plan coordination and verified checkbox body updates | existing authority | `.opencode/agents/inquisitor.md` — `## Test-Plan Verification Workflow` |
| 32 — AI-attribution scan | existing authority | `.opencode/agents/inquisitor.md` — `## HARD RULE — No Unsanctioned AI/Agent Attribution in Tracked Files or Git Artifacts` |
| 32 — Claude-trailer exception | stale retirement | `.opencode/agents/inquisitor.md` — the live matcher is tool-agnostic and treats any exact matcher hit in tracked files or Git/PR artifacts as BLOCK; no Claude-trailer exception exists. |
| 34 — severity protocol and evidence-only test-plan ticking/N-A rule | existing authority | `.opencode/agents/inquisitor.md` — `## Gate Signal Protocol` and `## Test-Plan Verification Workflow` |
| 34 — claim that BLOCK must be fixed before PR creation | stale retirement | `.opencode/agents/inquisitor.md` — `## Workflow` requires an open PR before review; a pre-PR gate is outside Inquisitor 🔎 (PR Reviewer)'s live authority. |
| 36 — claim that Inquisitor 🔎 (PR Reviewer) runs before Herald 📯 (Release Manager) | stale retirement | `.opencode/agents/inquisitor.md` — `## Your Role` and `## Workflow` require Herald 📯 (Release Manager) to open the PR and provide the immutable-head packet first. |
| 38 — post-PR evidence-only test-plan ticking/N-A rule | existing authority | `.opencode/agents/inquisitor.md` — `## Test-Plan Verification Workflow` |
| 42 — pre-PR parallel-review invocation | stale retirement | `.opencode/agents/inquisitor.md` — `## Workflow` permits only the post-PR-boundary invocation after Herald 📯 (Release Manager)'s immutable-head handoff. |
| 42–43 — post-PR invocation, return, and Cipher 🔓 (L2 Lead) fix routing | existing authority | `.opencode/agents/inquisitor.md` — `## Your Role` and `## Workflow` |
| 44 — claim that Herald 📯 (Release Manager) waits for Inquisitor 🔎 (PR Reviewer) before `gh pr create` | stale retirement | `.opencode/agents/inquisitor.md` — `## Your Role` and `## Workflow` require the PR to exist before Inquisitor 🔎 (PR Reviewer) acts. |
| 45 — claim that Sentinel 🛡️ (Quality Guardian) audits Inquisitor 🔎 (PR Reviewer)'s temporal PR-review output | stale retirement | `.opencode/agents/inquisitor.md` — `## Roster Context` says no agent audits temporal `output/audits/` reports. |
| 46 — Marshal 🎖️ (HR Director) maintenance route | existing authority | `.opencode/agents/inquisitor.md` — `## Roster Context` |
| 47 — prescribed Atrium 🏛️ (Frontend Architect)/Bastion 🧱 (Backend Architect) → Forge 🔨 (Implementation Agent) escalation chain | stale retirement | `.opencode/agents/inquisitor.md` — `## Roster Context` permits noting unresolved Atrium 🏛️ (Frontend Architect) findings, while `## Your Role` routes Inquisitor 🔎 (PR Reviewer)'s BLOCK findings to Cipher 🔓 (L2 Lead) only; no intermediary escalation chain exists. |
| 51 — source/spec/persona read-only boundary | existing authority | `.opencode/agents/inquisitor.md` — `## Hard Rules` |
| 52 — “posts review comments” | stale retirement | `.opencode/agents/inquisitor.md` — `## Your Role`, `## Bash Command Allowlist`, and `## Hard Rules` prohibit all GitHub comments and reviews. |
| 53–57, 59–60, 62–63 — package/Python, markdown, architecture, trigger, checkbox, N/A, hiring, and research prohibitions | existing authority | `.opencode/agents/inquisitor.md` — `## Bash Command Allowlist` and `## Hard Rules` |
| 58 — claim that comments are allowed for non-PASS signals | stale retirement | `.opencode/agents/inquisitor.md` — comments and reviews are forbidden for every signal. |
| 61 — `gh pr edit --body` exception | stale retirement | `.opencode/agents/inquisitor.md` — only `gh pr edit <number> --body-file <file>` is permitted for verified test-evidence updates. |

### Lumen ✨ (Visual Director)

| CV line / quoted operational statement | Disposition | Exact source authority |
|---|---|---|
| 11 — upstream briefs, downstream audits, and “two artifacts and nothing else” | existing authority | `.opencode/agents/lumen.md` — `## Your Role` |
| 27–31 — hierarchy, severity, lane, prose, and bootstrap gates | existing authority | `.opencode/agents/lumen.md` — `## Audit Gate and Severity Threshold`, `## Bootstrap Gate (first invocation only)`, and `## Hard Rules` |
| 35–39 — visual-tool/reference-catalog workflow and conflict rule | existing authority | `.opencode/agents/lumen.md` — `## Skill Invocation Patterns` |
| 43–52 — browser validation commands, Browser State report, and app-health escalation | existing authority | `.opencode/agents/lumen.md` — `## Skill Invocation Patterns` → `### Primary instrument` |
| 56–59 — `output/design/` artifact paths and first-write directory creation | existing authority | `.opencode/agents/lumen.md` — `## Your Role` |
| 63–65 — Atrium 🏛️ (Frontend Architect) parallel gate and severity blocking threshold | existing authority | `.opencode/agents/lumen.md` — `## Audit Gate and Severity Threshold` |
| 69–72 — upstream/downstream routing and Marshal 🎖️ (HR Director)/Sentinel 🛡️ (Quality Guardian) route | existing authority | `.opencode/agents/lumen.md` — `## Roster Context` and `## Trigger Conditions`; `.opencode/agents/marshal.md` — `## Maintenance` |
| 75–82 — source/git/architecture/test/build/UX/shell/prose prohibitions | existing authority | `.opencode/agents/lumen.md` — `## Hard Rules` and `## Skill Invocation Patterns` |

### Sentinel 🛡️ (Quality Guardian)

| CV line / quoted operational statement | Disposition | Exact source authority |
|---|---|---|
| 13–16 — line-by-line review, naming fixes, pattern detection, and mechanical-autofix/judgment-report behavior | existing authority | `.opencode/agents/sentinel.md` — `## Your Role`, `## Audit Rulebook`, and `## Audit Workflow` |
| 17 — “audits dev-side markdown files only; incident management files … explicitly out of scope” | stale retirement | `.opencode/agents/sentinel.md` — `## Audit Scope` includes Incident-team and Cross-cutting runtime specs/CVs and `knowledge/agents.md`. |
| 20–24 — Marshal 🎖️ (HR Director) trigger, Cipher 🔓 (L2 Lead) sweep, auto-fix/report route, Augur 🔮 (Senior Research Analyst) exception, and PRODUCT/DESIGN scope | existing authority | `.opencode/agents/sentinel.md` — `## Audit Workflow` and `## Audit Scope` |
| 27 — “Never reviews code — that’s the domain agents’ territory” | existing authority | `.opencode/agents/sentinel.md` — `## Hard Rules` |
| 28 — “Never audits incident management files — the incident agent specs, ticket system data, docs/wiki, problem records, or `knowledge/agents.md`” | stale retirement | `.opencode/agents/sentinel.md` — `## Audit Scope` includes incident agent specs and `knowledge/agents.md`; its Hard-out list, not a CV claim, excludes ticket data, docs/wiki, and problem records. |
| 29–32 — hiring/research/judgment-call/scope-skip prohibitions | existing authority | `.opencode/agents/sentinel.md` — `## Hard Rules` |

### Warden 🔒 (Dependency Warden)

| CV line / quoted operational statement | Disposition | Exact source authority |
|---|---|---|
| 11 — dependency surfaces, pre-stage audit, non-install/non-edit boundary, report evidence, and gate signals | existing authority | `.opencode/agents/warden.md` — `## Your Role` |
| 15–19 — change triggers, source/evidence precision, and no unsupported threat escalation | existing authority | `.opencode/agents/warden.md` — `## Trigger Conditions`, `## Per-Session Audit Cadence`, and `## Gate Signal Protocol` |
| 23–27 — evidence, severity, lane, gate, and prose rules | existing authority | `.opencode/agents/warden.md` — `## Gate Signal Protocol` and `## Your Role` |
| 31–39 — owned dependency/skill/vendor/env/CI surfaces and out-of-scope distinctions | existing authority | `.opencode/agents/warden.md` — `## Your Role`, `## Trigger Conditions`, and `## Skill-Install Audit Depth` |
| 43–47 — Cipher 🔓 (L2 Lead) route, signal types, Herald 📯 (Release Manager) staging gate, override, and Marshal 🎖️ (HR Director)/Sentinel 🛡️ (Quality Guardian) route | existing authority | `.opencode/agents/warden.md` — `## Roster Context`, `## Override Mechanism`, and `.opencode/agents/marshal.md` — `## Maintenance` |
| 50–55 — edit/install/git/threat/Bash/no-autoupdate prohibitions | existing authority | `.opencode/agents/warden.md` — `## Hard Rules` and `## Hard NO-AUTOUPDATE Rule` |

## Incident team migration entries

### Investigator 🔍 (Incident Investigator)

| CV line / quoted operational statement | Disposition | Exact source authority |
|---|---|---|
| 13–16 — fact/hypothesis/evidence, prior-art, out-of-domain boundary, and authoritative-source checks | existing authority | `.opencode/agents/investigator.md` — `## Evidence discipline (HARD RULE)`, `## Data-grounding discipline`, and `## Hard Rules` |
| 19 — root-cause return, screenshot-ready queries, and forbidden-field tags | existing authority | `.opencode/agents/investigator.md` — `## Your Role` |
| 22–24 — Cipher 🔓 (L2 Lead) dispatch, Quill 🪶 (note drafter) evidence handoff, and Scribe ✍️ (docs & problem management) prior-art relation | existing authority | `.opencode/agents/investigator.md` — `## Roster Context` |
| 27–30 — no prose, no mutation, no out-of-domain remediation, and no assumptions | existing authority | `.opencode/agents/investigator.md` — `## Your Role`, `## Evidence discipline (HARD RULE)`, and `## Hard Rules` |

### Ledger 📒 (record-keeper)

| CV line / quoted operational statement | Disposition | Exact source authority |
|---|---|---|
| 10 — “what’s posted and what’s in `tickets/.../*.md` must match exactly” and “just edits” | existing authority | `.opencode/agents/ledger.md` — `## Mission` and `## Multi-session ticket layout` |
| 13 — “copies approved text verbatim; never rewrites, never paraphrases” | existing authority | `.opencode/agents/ledger.md` — `## Mission` and `## Evidence discipline` |
| 14 — ticket validation after every edit | existing authority | `.opencode/agents/ledger.md` — `## Mission` and `## Incremental sync per phase` |
| 15 — status reply examples | existing authority | `.opencode/agents/ledger.md` — `## Mission` |
| 16 — leave missing fields blank rather than fabricate | existing authority | `.opencode/agents/ledger.md` — `## Evidence discipline` |
| 19 — “Cipher 🔓 (L2 Lead) dispatches Ledger 📒 (record-keeper) after every approved response → archive sync” | existing authority | `.opencode/agents/ledger.md` — `## Mission` |
| 20 — “Cipher 🔓 (L2 Lead) dispatches Ledger 📒 (record-keeper) on close → changelog row written” | existing authority | `.opencode/agents/ledger.md` — `## Mission` and `## Close-out completeness gate` |
| 21 — reads ticket record and posted-note source | existing authority | `.opencode/agents/ledger.md` — `## Close-out content gate` → `### Gate B` |
| 24–28 — incident/prose/docs/screenshot/no-fabrication boundaries | existing authority | `.opencode/agents/ledger.md` — `## Evidence discipline`, `## Image placeholders`, and `## Images scope` |

**Ledger 📒 (record-keeper) correction:** Ledger 📒 (record-keeper) owns incremental phase/archive sync, durable verbatim posted-response records in `## Responses`, and the close-out changelog row. These are current authorities at `.opencode/agents/ledger.md` — `## Incremental sync per phase`, `## Mission`, `## Multi-session ticket layout`, and `## Close-out completeness gate`. Ledger 📒 (record-keeper) does **not** own an automatic Scribe ✍️ (docs & problem management)-link handoff: no Ledger 📒 (record-keeper) runtime clause creates that duty, and the claimed handoff in Scribe's CV is retired below.

### Quill 🪶 (note drafter)

| CV line / quoted operational statement | Disposition | Exact source authority |
|---|---|---|
| 10 — “when the user corrects one phrase, Quill 🪶 (note drafter) doesn’t rewrite the paragraph” | existing authority | `.opencode/agents/quill.md` — `## Your Role` and `## Patch-not-rewrite (CRITICAL)` |
| 13–16 — concise/no-tables/no-field names, surgical edit, image numbering, and hypothesis labeling | existing authority | `.opencode/agents/quill.md` — `## Hard Rules` |
| 19–20 — Cipher 🔓 (L2 Lead) dispatch payloads, `tickets/{id}/response-draft.md`, and correction dispatch | existing authority | `.opencode/agents/quill.md` — `## Your Role` |
| 21 — “Ledger 📒 (record-keeper) archives `response-draft.md` into `tickets/{id}/responses/`” | planned runtime move | **Planned Phase 9 runtime revision:** retire Quill's contradictory live `.opencode/agents/quill.md` — `## Reference` draft-move clause; revise `.opencode/agents/ledger.md` — `## Mission`/`## Incremental sync per phase` to state Ledger 📒 (record-keeper)'s actual durable posted-response authority: after posting, copy the approved posted response verbatim into the ticket record's `## Responses` block. `response-draft.md` remains ephemeral under `.opencode/agents/ledger.md` — `## Multi-session ticket layout`; see `phase-09-marshal.md` — step 1. |
| 24–28 — visible-prose, table, correction, posting, and evidence boundaries | existing authority | `.opencode/agents/quill.md` — `## Hard Rules`, `## Your Role`, and `## Patch-not-rewrite (CRITICAL)` |

### Scribe ✍️ (docs & problem management)

| CV line / quoted operational statement | Disposition | Exact source authority |
|---|---|---|
| 10 — evidence-before-create/publish and long-lived docs/problem-record operation | existing authority | `.opencode/agents/scribe.md` — `## Mission` and `## Evidence discipline` |
| 13–17 — long-view, evidence/TODO, title pattern, draft-before-publish, and draft→approval→apply workflow | existing authority | `.opencode/agents/scribe.md` — `## Mission`, `## Evidence discipline`, and `## Hard rule: user approval gate` |
| 20–22 — Cipher 🔓 (L2 Lead) trigger, source-reading, and problem workflow | existing authority | `.opencode/agents/scribe.md` — `## Mission` |
| 23 — “Returns docs/wiki URL or problem record ID …; Ledger 📒 (record-keeper) then records the link in the ticket record” | stale retirement | `.opencode/agents/scribe.md` — `## Mission` owns the return to Cipher 🔓 (L2 Lead); `.opencode/agents/ledger.md` — `## Mission` and `## Incremental sync per phase` contain no automatic Scribe ✍️ (docs & problem management)-link handoff. |
| 26–29 — investigation/prose/evidence/no-fabrication boundaries | existing authority | `.opencode/agents/scribe.md` — `## Evidence discipline` and `## Hard rule: user approval gate` |

## Cross-cutting migration entries

### Cipher 🔓 (L2 Lead)

| CV line / quoted operational statement | Disposition | Exact source authority |
|---|---|---|
| 16–17 — evidence discipline and ownership/synthesis behavior | existing authority | `AGENTS.md` — `## Identity & Role` and `## Shared agent rules` |
| 20–24 — read/classify/parallel dispatch, synthesis, Quill 🪶 (note drafter)/Ledger 📒 (record-keeper)/Scribe ✍️ (docs & problem management) routing, user-confirmation threshold, and output audit | existing authority | `AGENTS.md` — `## Identity & Role` and `## Conventions` |
| 27, 30–34 — no direct queries/prose/records, no assumptions, evidence-based escalation, and User-Authority-Only | existing authority | `AGENTS.md` — `## Identity & Role` and `## Shared agent rules` |
| 28 — prior-art delegation | planned runtime move | `AGENTS.md` — planned Phase 9 `## Identity & Role` lead rule retaining delegation to Investigator 🔍 (Incident Investigator) before fresh investigation; no current Cipher 🔓 (L2 Lead) authority clause owns this operation. See `phase-09-marshal.md` — step 4. |
| 29 — failure-mode hypothesis delegation | planned runtime move | `AGENTS.md` — planned Phase 9 `## Identity & Role` lead rule retaining delegation of ranked hypotheses to Investigator 🔍 (Incident Investigator); no current Cipher 🔓 (L2 Lead) authority clause owns this operation. See `phase-09-marshal.md` — step 4. |
| 36–46 — grounding discipline and self-correction triggers | planned runtime move | `AGENTS.md` — planned Phase 9 `## Identity & Role` grounding rule; see `phase-09-marshal.md` — step 4. |
| 48–56 — mandatory `question`-tool discipline and trigger words | existing authority | `AGENTS.md` — `## Conventions` |

### Augur 🔮 (Senior Research Analyst)

| CV line / quoted operational statement | Disposition | Exact source authority |
|---|---|---|
| 13–16 — web/codebase/tool/ticket-history scope, citations, gaps, and dense brief format | existing authority | `.opencode/agents/augur.md` — `## Your Role`, `## Research Workflow`, and `## Standards` |
| 19 — “Cipher 🔓 (L2 Lead) requests research → Augur 🔮 (Senior Research Analyst) investigates → brief drops in `output/research/`” | existing authority | `.opencode/agents/augur.md` — `## Research Workflow` |
| 20 — Marshal 🎖️ (HR Director) consumes hiring briefs and produces files | existing authority | `.opencode/agents/augur.md` — `## Research Workflow`; `.opencode/agents/marshal.md` — `## Hiring Workflow` |
| 21 — “Team agents consult Augur 🔮 (Senior Research Analyst) briefs when investigating unfamiliar territory” | stale retirement | `.opencode/agents/augur.md` — `## Research Workflow` makes Cipher 🔓 (L2 Lead) the research-request router; no current runtime authority gives team agents direct brief-consultation workflow. |
| 24–27 — no hiring/code/ticket fixes, citations, and no assumptions | existing authority | `.opencode/agents/augur.md` — `## Hard Rules` and `## Standards` |

### Marshal 🎖️ (HR Director)

| CV line / quoted operational statement | Disposition | Exact source authority |
|---|---|---|
| 10 — works with Augur 🔮 (Senior Research Analyst) research to make hiring decisions | existing authority | `.opencode/agents/marshal.md` — `## Your Role` and `## Hiring Workflow` |
| 13–16 — profile structure, work with Augur 🔮 (Senior Research Analyst)/Cipher 🔓 (L2 Lead), practical role definition, and CV/runtime reference pattern | existing authority | `.opencode/agents/marshal.md` — `## Your Role`, `## CV Format`, and `## Runtime Spec Format` |
| 19–20 — Augur 🔮 (Senior Research Analyst) brief → agent files and Cipher 🔓 (L2 Lead) hire/refinement request | existing authority | `.opencode/agents/marshal.md` — `## Hiring Workflow` |
| 21 — “Existing team agents → Marshal 🎖️ (HR Director) updates their `## Learnings` section after Cipher 🔓 (L2 Lead) feedback” | planned runtime move | `.opencode/agents/marshal.md` — planned Phase 9 `## Maintenance` learning-update rule, as specified by `phase-09-marshal.md` — step 5; no current runtime clause names Cipher 🔓 (L2 Lead) feedback as the trigger. |
| 24–26 — research/code/ticket boundary and research-brief prerequisite | existing authority | `.opencode/agents/marshal.md` — `## Hard Rules` |

### Vault 🔐 (Catalog Steward)

| CV line / quoted operational statement | Disposition | Exact source authority |
|---|---|---|
| 11 — catalog checklist examples and block-until-clean behavior | existing authority | `.opencode/agents/vault.md` — `## Quality Checklist` and `## Workflow` → `### Onboarding audit (new skill)` |
| 15–18, 20 — checklist governance, SKILL.md discovery, registry checks, SQL validation, and recurring audits | existing authority | `.opencode/agents/vault.md` — `## Your Role`, `## Scope (in)`, `## Quality Checklist`, and `## Workflow` → `### Periodic audit (quarterly)` |
| 19 — “quarterly audit … should be scripted” automation preference | planned runtime move | `.opencode/agents/vault.md` — planned Phase 9 approval-gated automation-proposal rule; it must require Cipher 🔓 (L2 Lead) approval and must not authorize unplanned script implementation. See `phase-09-marshal.md` — step 5. |
| 24–29 — governance-layer collaboration, approval, Investigator 🔍 (Incident Investigator) proposal, Warden 🔒 (Dependency Warden) boundary, and Ledger 📒 (record-keeper) notification | existing authority | `.opencode/agents/vault.md` — `## Roster Context` and `## Workflow` |
| 30 — “Sentinel 🛡️ (Quality Guardian) owns dev-side docs; Vault 🔐 (Catalog Steward) owns the shared rules and incident-side files” | stale retirement | `.opencode/agents/vault.md` — `## Scope (out)` assigns all agent documents to Sentinel 🛡️ (Quality Guardian); `.opencode/agents/sentinel.md` — `## Audit Scope` includes incident/cross-cutting specs and `knowledge/agents.md`. |
| 36–40 — no application code, ticket handling, production queries, response notes, or personnel-file edits | existing authority | `.opencode/agents/vault.md` — `## Hard Rules` |
| 41 — “Never audits `knowledge/` subdirectories (`design/`, `research/`) — those are Sentinel 🛡️ (Quality Guardian)'s territory” | stale retirement | `.opencode/agents/sentinel.md` — `## Audit Scope` does not assign generic `knowledge/design` or `knowledge/research` ownership; `.opencode/agents/vault.md` — `## Scope (out)` has no such transfer. |

## Destination-resolution check

**Result: no unresolved destination remains.** Every operational CV statement above is either covered by a cited existing runtime heading, has a named owner-runtime heading for a planned Phase 9 move, or is explicitly retired because the cited live authority contradicts it or no live authority owns it. The planned moves include Cipher 🔓 (L2 Lead)-owned orchestration/grounding clauses in `AGENTS.md`, Ledger 📒 (record-keeper)'s durable posted-response authority, Marshal 🎖️ (HR Director)'s Cipher 🔓 (L2 Lead)-feedback learning rule, and Vault 🔐 (Catalog Steward)'s approval-gated automation-proposal rule; none authorizes a new unplanned duty.
