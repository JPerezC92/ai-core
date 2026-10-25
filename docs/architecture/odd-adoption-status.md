# ODD adoption: source-local status

**Evidence checked:** 2026-10-25. This is an informational snapshot, not workflow authority, an adoption certificate, or a second task tracker. Requirements and delivery evidence remain in their owning feature documents; new work follows [knowledge/agent-workflow.md](../../knowledge/agent-workflow.md).

## Current position

The bounded core-workflow features below are closed. ODD governs new work: one feature document for authorized non-small changes, no durable feature artifact for read-only or small work, and retained authorization/review gates. This does **not** establish universal completion of every possible ODD adoption concern or exact fidelity to every upstream practice.

Publication baseline supplied by the coordinator: `main` includes PR #87 at merge `34dc5dc`. The PR numbers below identify the supplied delivery history, not a fresh live-host inspection. Individual feature Logs often end before publication; their historical “PR pending” or “OPEN” statements are not current PR-state evidence. No claim is made that all PRs are closed.

## Completed core-workflow delivery

All eleven non-template documents currently in `odd/tasks/` have closed headers, done tasks with commit references, and close evidence. This was a document inspection, not a new validator or test execution.

| Delivery | Scope and owning evidence |
|---|---|
| PR #78 — core | [ODD core reorganization](../../odd/tasks/odd-core-reorganization.md): protocol, single Specs/Tasks/Log record, template-first rule, and source-local boundary. [Legacy reference sweep](../../odd/tasks/legacy-reference-sweep.md): bounded operational-pointer cleanup. [Feature-document validator](../../odd/tasks/feature-document-validator.md): mechanical anatomy/lifecycle checks. These records cite delivery `ae234b2`. |
| PR #79 — commit-state validator | [Validator commit-state semantics](../../odd/tasks/validator-test-architecture.md): done tasks require delivery commits; closure requires all tasks committed. Delivery `3cf9cdc`, skill metadata follow-up `4e80c0d`. Semantic completion remains a review responsibility. |
| PR #80 — agent alignment | [Agent-spec ODD alignment](../../odd/tasks/agent-spec-odd-alignment.md): scoped implementation/review/coordination pointers, delivery `800d107`; its deferred T5 was subsequently resolved by the tool-ownership feature. |
| PR #84 — classification and feature scope | [ODD classification and feature scope](../../odd/tasks/odd-classification-and-feature-scope.md): understood/risk-contained/resumable classification, no count-based threshold, legacy-only plan/story routing, and coordinated shared-file scope. Delivery `802333c`. This supersedes the initial core feature's historical plan-enforce threshold. |

## Completed supporting improvements

These improvements support delivery, review, or architecture organization. Their inclusion is not a claim that every listed PR is an ODD adoption requirement.

| Delivery | Scope and owning evidence |
|---|---|
| PR #81 — exact attribution matcher | [Exact attribution matcher](../../odd/tasks/attribution-matcher.md): immutable-head snapshot scanner, repository-readable policy, ODD PR-intent lookup, and recorded DEBT-007 retirement. Implementation `461e96b`, scan/retirement `2d94423`, skill update `84c4864`. |
| PR #82 — branch updates | [Governed updates for published PR branches](../../odd/tasks/pr-branch-update-governance.md): authorized non-force base-into-head update, conflict reconciliation, invalidated old evidence and renewed gates; never permission to merge a PR into its base. Deliveries include `c6599d1`, `c47d707`, `d6d15e5`. |
| PR #83 — tool ownership | [Tool-binding ownership](../../odd/tasks/tool-binding-ownership.md): AICore's Python tooling is core-owned; destination application tooling is project-owned or a labeled reference. Delivery `f63df3f`; resolves agent alignment T5. |
| PR #85 — Unicode | Coordinator-supplied published history identifies the Unicode follow-up. The classification feature records DEBT-016's creation; the current debt register no longer lists it. The clearing PR's full resolution evidence was not inspected in this refresh, so no broader Unicode-conformance claim is made. |
| PR #86 — testing split | [Testing architecture layering](../../odd/tasks/testing-architecture-layering.md): agnostic test contract, separate template and reviewed TypeScript/Python guides, parity and reviewer routing. Delivery `70287c4`; its original root location was subsequently superseded by PR #87. |
| PR #87 — architecture consolidation | [Architecture documentation](../../odd/tasks/architecture-documentation.md): common contract, shapes, stack guides, runtime read-pointers, distribution wiring and documentation review; delivery `69365b0`. [ADR 0003](decisions/0003-architecture-documentation.md) records the accepted canonical `architecture/testing/` location and removal of obsolete root pointers. |

## Architecture: documented, not implementation-certified

[Architecture navigation](../../architecture/README.md) selects the [common contract](../../architecture/clean-architecture.md), applicable shapes and implementation guides, then the [testing contract](../../architecture/testing/architecture.md) and applicable testing guide. Runtime specs retain execution authority, procedures and review gates. Reference-guide acceptance and recorded passing suites establish neither existing-code conformance nor destination migration.

Python HTTP framework, repository library, error-registry layout and serializer/framework mappings remain unselected, as recorded in architecture navigation and ADR 0003. These are future decisions when applicable, not missing requirements blocking the completed documentation feature. Existing implementation adoption/remediation is unassessed here and requires separately authorized work. New destination architecture paths require authorized enrollment and reconciliation; source documentation completion does not prove any destination accepted them.

## Deliberate boundaries and remaining concerns

- **Legacy history is not an automatic migration backlog.** The core feature Log L12 and classification feature S3/L7 preserve old plans/stories without making their pending goals binding on new ODD work. The current [plan-enforce notice](../../.opencode/skills/plan-enforce/SKILL.md) and [user-story notice](../../.opencode/skills/user-story/SKILL.md) explicitly limit those skills to legacy handling/migration and applicable cleanup. Further migration requires a concrete authorized need, not blanket conversion for completeness.
- **Missing old adoption plan:** the core feature records the former `plans/odd-project-adoption-20261022/plan.md` as a preserved migration input. Its current availability, untracked history and eventual disposition are not established here; it is not labeled retired, completed, or safely deleted.
- **Deferred policy analysis:** agent alignment Log L5 leaves stash ownership/cleanup and the periodic-audit rubric for future analysis. Classification and tool ownership were subsequently addressed by their named closed features; that does not silently decide the other policies. No new implementation mandate is created by this snapshot.
- **Verified local exclusions:** the governing features explicitly exclude a second tracker, Engram mirror, per-request context injection, plugin/dependency/permission changes and destination mutation within their scopes. This is bounded source evidence, not an exhaustive upstream-ODD nonadoption catalogue. Other alleged nonadoptions remain unverified.
- **Accepted debts remain open:** [knowledge/debt.md](../../knowledge/debt.md) contains seven entries: DEBT-011 completion-review reliability, DEBT-012 root release artifacts, DEBT-013 false multiple-plan prohibition, DEBT-014 lifecycle stalls, DEBT-015 stale merge-order advice, DEBT-017 hypothetical compatibility constraints and DEBT-018 inconsistent PR evidence presentation. Their recorded resolution criteria remain authoritative; this dashboard resolves none. The register also retains the provisional-retirement warning for DEBT-008/009/010.
- **DEBT-017/018 are nonblocking deferred process concerns**, not reasons to reopen the accepted documentation feature. DEBT-017 requires evidenced constraints, reviewer checks and both consumer/no-consumer exercises; DEBT-018 requires a reviewed consistent evidence template and later demonstrated traceability. Neither authorizes immediate rule/template changes.

## Local follow-up versus published delivery

The coordinator reports the current follow-up branch contains committed DEBT-018 and mentor-related changes that are **not yet published**. They are not counted as merged adoption delivery here; DEBT-018 is visible in the current local register. Mentor delivery/conformance was not assessed in this refresh. This local dashboard is likewise not a publication claim. Current remote state, historical test reruns, commit-object verification and a complete upstream-source fidelity audit were outside this bounded inspection.
