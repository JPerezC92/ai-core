# Agent-spec ODD alignment

> **Status:** closed
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-10-23
> **Closed:** 2026-10-24

## Specs

- S1 — Active implementation, test, and PR-review specs use the ODD feature document and assigned `T#` as the new-work source; existing design, test, review, and safety gates are unchanged.
- S2 — Within the named files, remove old plan/story workflow fallbacks where they compete with ODD; retain unrelated PR test-plan, incident, and historical meanings, and do not expand into other files.
- S3 — Any edited `.opencode/agents/*.md` runtime spec advances its repository `version` by the Sentinel-defined class; no unrelated version or authority change is made.
- S4 — High-risk workflow decisions (stash ownership, plan-classification threshold, periodic audit lifecycle) are documented for future analysis, not changed in this feature.
- S5 — The changed clauses pass an independent read-only audit for ODD alignment and retained authority. Pre-existing source-specific tool/runner references outside the changed clauses are recorded as deferred, not expanded into this feature; no context injection, plugin, dependency, permission, or destination change occurs.

## Tasks

- T1 | S1, S2 | Retarget Atrium, Bastion, Forge, Crucible, and Inquisitor's active plan terminology to the ODD feature document while preserving legacy references | done | commit: 800d10742cc1e9ad8a28a431347694b8ab369ae4
- T2 | S1, S2 | Retarget shared coordination and PR-advisory recording from plan/Resolved decisions to feature/task and `## Log` | done | commit: 800d10742cc1e9ad8a28a431347694b8ab369ae4
- T3 | S3 | Apply the required patch version bumps to every edited agent runtime spec | done | commit: 800d10742cc1e9ad8a28a431347694b8ab369ae4
- T4 | S4 | Record deferred stash, classification-threshold, and periodic-audit decisions in this feature Log | done | commit: 800d10742cc1e9ad8a28a431347694b8ab369ae4
- T5 | S5 | Run Sentinel's changed-clause audit and bounded final re-sweep; record unchanged source-specific references as deferred | done | commit: f63df3fee0bd4505daa358991441af1d65ed84c5

Allowed status: open, in progress, done. `pending` is valid for open or in-progress work. A task marked done must cite its completed work-unit commit. A feature closes only when every task is done and committed.

## Log

- L1 — "maybe its a good momento for the next, we are taking ODD as main flow and we want to organize this project to achieve the most nearest to ODD. actually the agents definition are based on the old flow analyze waht agent can be easily be improved now and defer the other for future analysis"
- L2 — Analysis: easy retargets found in Atrium/Bastion/Forge, Crucible, Inquisitor, and `knowledge/agents.md`; safety/lifecycle redesigns deferred.
- L3 — Branch and delivery: feature document created before source edits. PR #79 remains separate; this feature must not alter its branch or body.
- L4 — Applied easy retargets: Atrium/Bastion nonconforming-file rule; Forge heading; Crucible required-case and task-authorization wording; Inquisitor goal source; shared assignment and PR-advisory log destinations. Patch-bumped each edited runtime spec.
- L5 — Deferred without edits: Herald stash ownership/cleanup authority; ODD versus legacy classification threshold; Marshal's quarterly plan audit rubric; Sentinel's explicitly legacy plan/story checks; broad story/catalogue migration.
- L6 — User clarified that removal applies to the files in this feature, not the whole project. Remove old workflow fallbacks in the scoped lines; do not preserve a legacy escape there or expand to unrelated files.
- L7 — User scope clarification: "i am telling about the files u are touching now, i dont want u to overscope all the project". The feature is limited to the named specs and shared rule clauses.
- L8 — Sentinel re-audit found pre-existing source-specific tool/runner references in unchanged sections of the five runtime specs. These are not old-workflow pointers and were not introduced by this feature. Sentinel returned [FAIL] because its source-neutrality rule applies to the full candidate files.
- L9 — User chose to defer the source-specific tool-binding reorganization for future discussion. The current retarget batch remains uncommitted and paused; no source-neutrality edits are authorized by this decision.
- L10 — Scoped re-sweep found no old plan/story workflow pointers in the edited clauses. PR-specific `test plan` terminology remains because it means the PR verification checklist, not the retired feature-planning flow. Mechanical feature validation passes all five ODD documents.
- L11 — User asked for a PR for the scoped alignment batch. The PR is a review candidate only; Sentinel's [FAIL] remains visible, this feature stays active, and no completion or merge claim is made.
- L12 — T1–T4 delivered in work-unit commit `800d10742cc1e9ad8a28a431347694b8ab369ae4`. T5 was previously pending because Sentinel's source-neutrality finding was deferred.
- L13 — Close: T5 resolved by `tool-binding-ownership` in work-unit `f63df3fee0bd4505daa358991441af1d65ed84c5`; the source-neutrality boundary now distinguishes AICore's core-owned Python toolchain from destination application bindings. Sentinel [PASS], fixture gates [PASS], and the 738-test suite passed. All tasks are done and committed.
