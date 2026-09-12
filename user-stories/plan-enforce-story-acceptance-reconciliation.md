# User story — plan-enforce-story-acceptance-reconciliation

> **Created:** 2026-09-12
> **Title:** Plan-enforce story acceptance reconciliation
> **Status:** active
> **Epic:** plan-governance
> **Affected areas:** `.opencode/skills/plan-enforce/`, `.opencode/agents/sentinel.md`, `user-stories/`

## Persona

- A plan owner (Cipher 🔓 (Lead Orchestrator)) who completes and archives plans and must not leave a touched user story claiming work is unfinished when it is done.

## Goal

- **G:** A plan that touches a user story cannot complete or archive while that story carries a stale or undetermined acceptance criterion.
  - Done when: `plan-enforce` requires every criterion in a touched story to be `✅` (evidence-established), `❌` (explicitly unmet, blocking), or removed as out-of-scope — never left `⬜` — and Sentinel 🛡️ (Quality Guardian) reports any violation as a blocking finding without ever auto-checking a box.

## Scenario

- A plan finishes and Cipher 🔓 (Lead Orchestrator) is about to write `## Outcome` and archive it. If a story the plan touched still has an `⬜` criterion that the plan's verified goals prove is fulfilled, completion is blocked until the criterion is `✅` (or `❌`, or removed as out-of-scope). Release events such as "PR opened/merged" are not acceptance criteria; they are change-log history.

## Acceptance criteria

- ✅ AICore's `plan-enforce` skill states the canonical fail-closed reconciliation invariant: no `⬜` remains after a touching plan completes; each criterion is `✅`, `❌`, or removed. Evidence: `.opencode/skills/plan-enforce/SKILL.md` `1.11.0`, section `### Acceptance-criterion reconciliation (fail-closed)`; `_consistency-checklist.md` `## user-stories` bullet.
- ✅ `plan-enforce` blocks `## Outcome` and archival until every touched story is fully dispositioned. Evidence: completion bullet in `### Resume (completion)` and the analysis-pass clause in `## Post-write self-verification loop` (`SKILL.md` `1.11.0`).
- ✅ Sentinel 🛡️ (Quality Guardian) reports a stale `⬜`, fulfilled-but-unchecked, or release-event criterion in a touched story as a blocking finding, and never auto-checks a box. Evidence: `.opencode/agents/sentinel.md` `1.3.0`, `### Judgment calls (report only)` item 6.
- ✅ Release events are not feature acceptance criteria; release policy stays enforceable and actual events live in change-log/PR history. Evidence: `SKILL.md` `1.11.0` invariant sentence; `_consistency-checklist.md` bullet; `_template-user-story.md` `## Acceptance criteria` guidance.
- ✅ The story registry reflects this feature with a matching index row, and its own criteria are fully dispositioned under the new rule. Evidence: this file and `user-stories/index.md`.

## Change log

- 2026-09-12 — story-acceptance-reconciliation-20260912: created the fail-closed story-acceptance reconciliation feature definition.

## Resolved decisions

- 2026-09-12 — Enforcement is a fail-closed workflow gate (`plan-enforce` + Sentinel 🛡️ (Quality Guardian)), not a Python schema migration; a mechanical acceptance-criterion ID system is deferred.
- 2026-09-12 — There is no "left as pending" state for a criterion in a touched story; out-of-scope work is removed, never left unchecked.
