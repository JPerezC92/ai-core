# Workflow obligation paths

> **Status:** closed
> **Closed:** 2026-11-17
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-17
> **Objective:** Make every mandatory workflow obligation an obligation some authorized role can actually execute, so a dependency review reaches a finite verdict and a routine pull request is not stopped by avoidable permission denials — without weakening any severity rule, integrity control, Git boundary or merge authority.
> **Branch:** `fix/agents/workflow-obligation-paths`, created by Herald 📯 (Release Manager) from verified `origin/main` at `c85fbc79d2450154403bd229dd6b907c0f1251c9`; `main` is untouched by this change.
> **Delivery:** one isolated pull request, three implementation commits plus a closing record commit, on a branch cut from `origin/main`. Authored additions + deletions **forecast** ≈ 190 lines (this record ≈ 150, two durable feature files ≈ 25, `.opencode/agents/warden.md` ≈ 45, `.opencode/opencode.jsonc` ≈ 14, `.opencode/agents/forge.md` ≈ 10); generated files excluded; on that forecast the advisory ~400-line strategy trigger did not apply, so no chained-slice strategy was planned. **Measured on delivery**, the range totals 506 insertions and 11 deletions across the eight paths, which exceeds the forecast; the excess is this record's own growth to 381 lines as runtime verification, review rounds, scope corrections and delivery evidence were recorded, and no implementation or configuration volume grew beyond the forecast. The strategy actually applied is the one isolated PR required by the user, with cross-workstream file coupling disclosed at L23 and L25 rather than hidden. Slice boundaries: (A) the Warden review contract and its permission envelope, (B) the agent execution permissions, (C) the durable requirements and this record.
> **Runner:** `node .agents/skills/odd-workflow/scripts/validate_feature.ts odd/tasks`; `node .agents/skills/odd-workflow/scripts/validate_feature_file.ts odd/features`; `pnpm format:check`; `pnpm lint`; `pnpm typecheck`. Permission behaviour is evidenced by literal per-agent command probes recorded in the Log, not by reading the configuration.

Load and read the `odd-workflow` skill (`.agents/skills/odd-workflow/SKILL.md`) before creating or maintaining this record. Its creation, delivery, change and closure procedures are canonical; this template illustrates their layout, not another policy definition.

## Specs

- S1 — Every check the Warden runtime declares mandatory for the default dependency audit can be executed by Warden under its effective permissions, or is reported unavailable with no clean gate signal. Exact requirement: "A mandatory workflow obligation must have a documented, authorized execution path—or clearly require an explicit user decision." Acceptance: compare each command the Warden runtime names as required for the default audit against the Warden agent's effective permission rows and run each from Warden's own shell; every one resolves to allow, or is explicitly reported unavailable with the control it discharges recorded as unverified.

- S2 — A dependency review of an unchanged dependency surface reuses accepted evidence instead of repeating repository-wide inspection. Exact requirement: "Reuse valid evidence when relevant inputs have not changed." / "Stop when the required verification is satisfied." Acceptance: re-review a manifest-and-lockfile surface whose recorded inputs are unchanged and read the returned report; it cites the accepted baseline and performs no new repository-wide inventory.

- S3 — Missing optional publisher-provenance evidence is recorded as an informational observation rather than a finding whenever every reachable integrity control passes, while a demonstrated vulnerability or integrity failure still blocks. Exact requirement: "Clearly distinguish missing optional evidence from actual findings." Acceptance: review a change whose only limitation is unverifiable optional publisher provenance and read the gate signal; it is clean with an INFO observation, and the same review with a high-severity advisory present returns BLOCK.

- S4 — A demonstrated risk still blocks and cannot be overridden by any agent. Exact requirement: "Escalate demonstrated risks appropriately." / "Preserve lockfile integrity and real security controls." Acceptance: read the gate-signal rules and the no-override rule; an integrity mismatch or a high-severity advisory yields BLOCK and no annotation, decision or instruction clears it.

- S5 — A documented user acknowledgment of a non-blocking advisory permits the authorized continuation without becoming a clean pass. Exact requirement: "Respect documented user acceptance of non-blocking advisories." Acceptance: read the gate-signal rules and the stopping condition; an acknowledged advisory permits staging, remains recorded as an acknowledged advisory, and is never restated as PASS.

- S6 — Forge can execute the repository's own read-only lint, format-check and typecheck verification, and no other package-manager operation gains authority. Exact requirement: "Normal lint, format-check, typecheck, and test verification." Acceptance: run `pnpm lint`, `pnpm format:check` and `pnpm typecheck` as Forge after a harness restart and observe a non-denied run of each, then run a package-manager mutation form as Forge and observe a denial.

- S8 — Provisioning an already-approved, lockfile-pinned dependency set for isolated verification has a named authorized executor. Exact requirement: "Provisioning already approved lockfile-pinned dependencies." Acceptance: in an isolated worktree the designated agent runs the lockfile-frozen install form and the project's reviewed suite then runs at the exact committed revision.

- S9 — No permission expansion weakens a standing boundary: restricted roles stay restricted, Herald remains the sole Git and GitHub executor, merge remains the user's, and no wrapper, alias, alternate executable or nested invocation widens a grant. Exact requirement: "No wildcard permission expansion merely for convenience." / "Herald remains the sole Git/GitHub executor." Acceptance: attempt one denied form per touched role and observe the denial, and attempt a `git` command from a non-Herald role and observe the denial.

- S10 — Warden inspects a changed dependency surface rather than the repository by default, and treats a successful ordinary vulnerability scan as satisfying the known-vulnerability check without claiming it proves unrelated supply-chain properties. Exact requirement: "Audit changed dependency surfaces rather than the entire repository by default." / "A successful `pnpm audit` should satisfy the ordinary known-vulnerability check. It does not automatically prove every possible supply-chain property." Acceptance: review a change touching one manifest and read the report scope; it names the changed surface and performs no repository-wide inventory, and a clean advisory scan is not reported as provenance verification.

## Tasks

- T1 | S1, S2, S4, S5, S10 | inline (Warden's runtime specification is coordinator-authored and independently audited by Sentinel 🛡️ (Quality Guardian) — `AGENTS.md` → roster ownership table) — Cipher 🔓 (Lead Orchestrator) | done | commit: ce81c02
- T2 | S6, S9 | inline (Forge's harness permission rows and its project-region reviewed-command list; the permission-boundary risk trigger is covered by T5) — Cipher 🔓 (Lead Orchestrator) | done | commit: eadaa22
- T3 | S3 | inline (the publisher-provenance classification sentences in Warden's runtime; no other surface owns them) — Cipher 🔓 (Lead Orchestrator) | done | commit: ce81c02
- T4 | S8 | inline (a lockfile-frozen provisioning form in shared configuration) — Cipher 🔓 (Lead Orchestrator) | done | commit: eadaa22
- T5 | S1, S4, S9 | delegated (risk trigger: a permission-boundary change requires Warden 🔒 (Dependency Warden)'s independent assessment of the exact permission diff — `AGENTS.md` → risk-triggered specialist review) — Warden 🔒 (Dependency Warden) | done | commit: edd8258
- T6 | S1, S2, S3, S4, S5, S6, S9, S10 | delegated (every agent-document change is audited independently by Sentinel 🛡️ (Quality Guardian) — `AGENTS.md` → roster ownership table) — Sentinel 🛡️ (Quality Guardian) | done | commit: edd8258
- T7 | S1, S2, S3, S4, S5, S6, S9, S10 | inline (ODD validators, the durable feature files and the record's own evidence are coordinator-owned) — Cipher 🔓 (Lead Orchestrator) | done | commit: edd8258

## Log

- L1 — 2026-11-17 — Original request, verbatim:

```text

# AICore — Fix recurring Warden review friction and agent permission failures

I want to address two recurring operational problems in AICore:

1. **Warden's excessive dependency verification and recurring review blockers.**
2. **Agent permission configurations that prevent legitimate, routine development and verification operations.**

These problems repeatedly delayed the Biome/Oxlint adoption and PR #192 review.

**The objective is to make AICore's agent workflow efficient, reliable, and secure—not to weaken security controls or build another layer of infrastructure.**

This is a new, independent workstream.

## 1. Mandatory repository-first investigation

Before recommending or implementing anything, inspect the actual current AICore repository.

Read the authoritative contracts and relevant implementation, including:

- `.opencode/agents/warden.md`
- `.opencode/opencode.jsonc`
- `.aicore/core/knowledge/agent-workflow.md`
- `.aicore/core/knowledge/debt.md`
- The actual agent specifications for Cipher, Herald, Crucible, Forge, Inquisitor, and Sentinel where relevant.
- The existing ODD feature and task contracts.
- Relevant permission tests, configuration validators, and existing review workflows.

Also inspect the current repository state and any uncommitted work that must be preserved.

Do not assume the published `main` state matches the current local checkout.

Do not invent repository rules or recommend changes without direct source evidence.

## 2. Problem A — Warden's excessive dependency reviews

### Observed behavior

During PR #192, Warden repeatedly requested additional evidence involving:

- Dependency provenance.
- Canonical-project mapping.
- Package registry and source correspondence.
- Compatibility of the locked environment.
- Dependency changes between revisions.

These investigations continued despite successful ordinary vulnerability auditing and previous verification evidence.

The final unresolved advisory concerned canonical-project mapping for:

- `@jridgewell/resolve-uri@3.1.3`
- `@rolldown/pluginutils@1.1.1`
- `postcss@8.5.33`

I explicitly accepted that residual advisory for PR #192.

The resulting repeated investigation and review delays have been recorded as **DEBT-057** in the working tree.

### Required analysis

Determine whether Warden's actual behavior matches its own documented contracts.

Specifically examine:

1. When a dependency audit is required.
2. Whether an unchanged dependency surface should trigger another audit.
3. Which checks are genuinely mandatory.
4. Which findings are INFO, ADVISORY, or BLOCK.
5. Whether clean transitive dependencies are being investigated unnecessarily.
6. Whether canonical-project mapping is being treated as a default requirement beyond its intended scope.
7. Whether accepted verification evidence can be reused.
8. Whether the process has a deterministic stopping condition.
9. Whether Warden distinguishes unavailable evidence from demonstrated security risk.
10. Whether its instructions contain contradictory or unnecessarily expensive obligations.

**Important distinction:**

A successful `pnpm audit` should satisfy the ordinary known-vulnerability check.
It does not automatically prove every possible supply-chain property.

However, additional checks must be justified by the applicable security contract and actual risk. Do not turn optional provenance research into an unlimited default review.

### Expected improvement

Warden should:

- Audit changed dependency surfaces rather than the entire repository by default.
- Reuse valid evidence when relevant inputs have not changed.
- Avoid repeatedly inspecting unchanged transitive dependencies without a concrete reason.
- Preserve lockfile integrity and real security controls.
- Escalate demonstrated risks appropriately.
- Clearly distinguish missing optional evidence from actual findings.
- Produce actionable, finite verdicts.
- Stop when the required verification is satisfied.
- Respect documented user acceptance of non-blocking advisories.

Do not automatically weaken existing integrity requirements.

If correcting Warden requires changing an established security acceptance policy, identify that policy change and request my explicit approval before applying it.

Do not add new dependency-auditing tools or services unless the existing mechanisms are demonstrably insufficient.

## 3. Problem B — Agent permission failures

### Observed behavior

PR #192 encountered repeated permission-related obstacles:

- Herald could inspect Git diffs but could not use a particular `git diff --output` form.
- Some agents lacked permission to execute necessary `pnpm lint` or `pnpm typecheck` commands.
- Verification in an isolated worktree required separate dependency provisioning and execution authorization.
- Normal review operations repeatedly stopped because the assigned executor lacked the required capability.
- Obtaining complete review evidence became unnecessarily difficult.

The problem is not necessarily that every denial was wrong.

**The problem is that recurring, legitimate workflows do not consistently have an authorized execution path.**

### Required analysis

Inspect the effective OpenCode permission configuration, not just individual allow/deny rules.

For each confirmed failure, determine:

1. Which agent owns the operation?
2. Which exact command or capability is required?
3. Which permission denied it?
4. Whether the denial was intentional and security-relevant.
5. Whether the agent was incorrectly assigned the operation.
6. Whether another existing authorized agent could perform it.
7. Whether the permission configuration contradicts the agent's documented responsibilities.
8. Whether the necessary capability can be granted safely at a narrower scope.
9. Whether the same issue will recur in future ordinary PRs.
10. Whether the problem belongs to AICore's shared configuration or a project-owned local configuration.

Focus on actual workflow failures rather than theoretical permission coverage.

### Security constraints

Preserve these boundaries:

- Herald remains the sole Git/GitHub executor.
- Merge remains user-controlled.
- Dangerous and destructive Git operations remain protected.
- No unrestricted shell access for restricted agents.
- No wildcard permission expansion merely for convenience.
- No automatic approval of dependency changes.
- No unrestricted package installation.
- No bypasses through wrappers, aliases, alternate executables, or nested subprocesses.

Do not remove restrictions simply because they caused a denial.

A safe solution may involve routing an operation to the correct agent instead of granting another agent additional permissions.

### Expected improvement

Legitimate, recurring workflows should have a clear authorized execution path for:

- Read-only Git and PR evidence collection.
- Normal lint, format-check, typecheck, and test verification.
- Safe isolated verification of an exact committed revision.
- Provisioning already approved lockfile-pinned dependencies.
- Producing complete review evidence without unnecessary context truncation.
- Deterministic review and publication procedures.

Prefer existing commands and established agent responsibilities.

Avoid introducing a new permission-management framework, shell wrapper, or custom execution service.

## 4. Review the interaction between Warden and permissions

These two problems may be related.

For example:

- Warden requires a check that no authorized executor can perform.
- A reviewer requires evidence that cannot be collected through an allowed command.
- An agent repeatedly requests permission for an operation that another agent already owns.
- A permitted installation procedure is incompatible with the isolated verification environment.

Identify these contradictions directly.

**A mandatory workflow obligation must have a documented, authorized execution path—or clearly require an explicit user decision.**

Do not make the security checks weaker just to eliminate operational friction.

## 5. Architecture and ODD ownership

Inspect existing ODD features before creating anything new.

Determine whether these improvements belong to existing durable capabilities, such as agent workforce, dependency review, or permission governance.

Follow AICore's actual update-before-create conventions.

Use the existing task and debt lifecycle.

Reconcile DEBT-057 with the current repository state. It was previously reported as uncommitted, so verify that it actually exists before modifying or referencing it as a persisted record.

Do not duplicate the same rules across Warden, other agent runtimes, global instructions, and feature files.

Keep the changes small and owned by their authoritative sources.

## 6. Implementation approach

Use two focused work units:

**A. Warden review behavior**

Correct demonstrated contradictions, unnecessary repeated work, and unclear stopping conditions in its existing authoritative instructions.

**B. Agent execution permissions**

Correct demonstrated permission/ownership mismatches using the smallest safe configuration or workflow changes.

Before editing, provide a concise evidence-based design decision that identifies:

- The confirmed failure.
- Its owning contract.
- The smallest proposed correction.
- Security implications.
- Relevant validation.
- Whether my approval is needed.

If a proposed correction materially changes security authority, installation privileges, or Git permissions, obtain explicit approval first.

If the changes are too large or require a substantial redesign, warn me about their scope and present the simpler alternative.

Do not perform a repository-wide refactor.

## 7. Validation and regression protection

Validate the actual changes, not just their syntax.

Use existing testing tools and validation conventions.

For Warden, verify representative scenarios:

- No dependency changes: no unnecessary new audit.
- New dependency: appropriate scoped review.
- Clean audit and complete mandatory evidence: correct terminal verdict.
- Missing optional provenance: classification consistent with the security contract.
- Confirmed high-severity vulnerability or integrity mismatch: BLOCK remains effective.
- Accepted ADVISORY: documented user acknowledgment permits the authorized continuation without changing the finding to PASS.

For permissions, verify:

- Legitimate authorized commands succeed for the correct agents.
- Restricted commands remain denied.
- Herald's Git ownership remains intact.
- Dangerous Git operations remain protected.
- Approved verification operations can be executed in the intended environment.
- No unintended permission escalation is introduced.

Test the effective permissions using AICore's real OpenCode behavior or existing suitable validation mechanisms where available.

Do not claim a permission works merely because its JSON configuration appears correct.

Avoid building a custom permission-testing framework unless actual evidence demonstrates that the existing infrastructure cannot verify the required behavior.

## 8. Strict scope and Git rules

Work only within the AICore source repository.

Do not modify downstream destinations or the TISMART reference repository.

Preserve all existing unrelated work, particularly:

- `2026-11-17-cheapest-test-boundary.md`
- DEBT-055 and DEBT-056
- Other uncommitted test, agent, and architecture changes belonging to that workstream

Do not modify PR #192 or merge it as part of this task.

Do not stash, reset, discard, overwrite, or relocate existing work without separate authorization.

Herald alone may perform Git/GitHub operations.

No commits, new branches, pushes, PRs, or merges without my explicit authorization.

## 9. Required final report

Provide:

1. The confirmed root causes of Warden's repeated review friction.
2. The confirmed root causes of recurring permission failures.
3. Exact repository contracts and source evidence.
4. Changes made, with affected files and rationale.
5. Security controls preserved.
6. Commands and workflows successfully validated.
7. Any limitations or remaining risks.
8. DEBT-057 status and whether its resolution criteria are satisfied.
9. Any newly confirmed issue that must remain deferred, following the existing debt conventions.
10. Whether all authorized work is complete or explicit approval is required for security-sensitive changes.

**Do not manufacture work just because a review was requested.**

**Do not weaken security to make the workflow faster.**

**Do not create new architecture or tooling where a small correction to existing contracts is sufficient.**

The desired outcome is straightforward:

**Warden performs proportional, conclusive dependency reviews, and AICore agents can execute their legitimate responsibilities without recurring avoidable permission failures.**

Finish all work that is safely authorized, and notify me definitively when complete. Do not stop with an ambiguous progress update.

```

- L2 — 2026-11-17 — Repository state and DEBT-057 reconciliation, established before any mutation. Herald 📯 (Release Manager)'s read-only inventory: branch `main`, HEAD `c85fbc79d2450154403bd229dd6b907c0f1251c9` (`feat(tooling): adopt biome formatting and oxlint linting (#192)`), 12 modified and 2 untracked paths, 2 pre-existing stashes. DEBT-057 is **uncommitted**: `git diff -- .aicore/core/knowledge/debt.md` shows `## DEBT-055`, `## DEBT-056`, `## DEBT-057` and the `DEBT-058` counter as `+` lines only, and the last commit touching that file is HEAD, which predates the edit. The committed file carries none of the three. Coupling disclosed: the untracked `odd/tasks/2026-11-17-cheapest-test-boundary.md` and DEBT-055's evidence cite each other, so debt.md and that record cannot ship separately. Two of the twelve modified paths — `.opencode/agents/forge.md` and `.opencode/agents/crucible.md` — belong to that other workstream; this change touches `forge.md` only additively in its `### Reviewed Test Commands` project region and its frontmatter version line, which are textually disjoint from the other workstream's extractions, and every other dirty path is left untouched.
- L3 — 2026-11-17 — Root cause of Problem A, established from the contract and a live permission probe rather than from the report alone. Three findings. **(a) An in-scope obligation has no authorized executor.** `.opencode/agents/warden.md:150` requires that "The candidate artifact's own registry metadata document for its exact pinned version — its declared license, its published integrity digest and any published attestation — is in scope for the default audit and is retrieved read-only", and `:208` requires "package-manager info queries for JavaScript registry metadata" in the per-task warmup. The Warden envelope in `.opencode/opencode.jsonc:211-226` authorizes only `pnpm audit --json`, `pnpm outdated --json`, `pnpm config get registry` and four `uv` forms; `pnpm info` and `pnpm list` are not granted and `warden.md:334` states "other package-manager commands remain denied". Probe: Warden's own shell ran `pnpm config get registry` → EXECUTED (exit 0, `https://registry.npmjs.org/`), `pnpm info postcss --json` → DENIED, `pnpm list --depth 0 --json` → DENIED, and Warden's returned conclusion was "the core default-audit retrieval step is unavailable to me as configured". This is the same defect class the `2026-11-14-scoped-dependency-admission` record fixed for `pnpm config get registry`, unextended to the other two required commands. **(b) The provenance informational classification is unreachable.** `warden.md:113-114` permits `unavailable`/`indeterminate` as INFO only when seven controls all "positively pass", among them "canonical-project mapping" and "compatible locked environment"; `:55` makes "incomplete non-provenance integrity evidence" an ADVISORY. Canonical-project mapping is decidable only inside Tier 1 attestation identity matching or the Tier 2 source-correspondence procedure that `:103` restricts to an explicit per-case grant and forbids as a default step, and `:120` scopes the high-assurance requirement to destinations that document one; the JavaScript branch has no environment-compatibility command at all. The precondition set was imported from the Python branch's per-artifact record at `:183`. Net effect: a clean vulnerability scan can never produce `[PASS]`, because a mandatory control is structurally undecidable, so every dependency review terminates in `[ADVISORY]` and re-requests the same evidence. That is the repetition mechanism, and it is why DEBT-057's own note — "unnecessary repetition and its cause are not independently established" — can now be answered. **(c) The triggering rule is already correct.** `warden.md:130` trigger 2 fires only on a lockfile diff in the changeset, `:148` forbids a session-start audit, and `:201` already carries an evidence-reuse clause; PR #192 did change the dependency surface, so the scoped review was legitimate. The friction was the unreachable exit, not re-triggering.
- L4 — 2026-11-17 — Root cause of Problem B, established from the effective configuration and two live probes. **B1 — Forge owns routine verification and cannot run it.** The root `package.json` scripts `lint` (`oxlint`), `format:check` (`biome format .`) and `typecheck` were added by the 2026-11-16 lint-and-format adoption; Forge's harness block, authored 2026-11-14, denies `pnpm *` and re-allows only the lockfile-only preparation form and the package-scoped `test`/`typecheck`/`vitest` forms, so all three root forms resolve to `deny`. Forge's project-region reviewed-command list does not name them either, so its runtime and its permissions agree with each other and both disagree with its core responsibility to run "the tests of your assigned slice" and its permitted linter and formatter. The mismatch is a sequencing defect introduced by the later adoption, not a bad deny. **B2 — Herald cannot produce a diff artifact.** Probe: `git diff --stat` → EXECUTED; `git diff --output=output/probe-denied.patch --stat` and `git diff --stat --output=output/probe-denied-2.patch` → both DENIED by `.opencode/opencode.jsonc:124` (`git diff *--output*`), and Herald's returned conclusion was that no authorized form can write a diff to a file in the gitignored `output/` directory. The deny is intentional and security-relevant — `--output` writes to an arbitrary filesystem path outside the edit-permission layer — so the correction is a narrower allow, not a removal. **B3 — Isolated verification has no provisioning path.** Forge may run only `pnpm install --lockfile-only --ignore-scripts`, which resolves metadata without populating `node_modules`; a Herald-created worktree carries no `node_modules`, so a reviewed suite cannot run at the exact revision. No role holds a lockfile-frozen install form. **B4 — No regression detector exists.** The effective-permission regression test introduced by the scoped-dependency-admission work lived in the root `tests/` workspace and was deleted with it in `2026-11-14-root-contract-suite-retirement` (L1 named "simulate permission enforcement" among the redundant guarantees, L5 removed the `test:contracts` script). S1 of that record is therefore unguarded today, which is why B1 could regress silently. No new framework is proposed: the replacement is a literal per-agent command probe recorded in this Log, which is real harness behaviour rather than a matcher that reproduces it.
- L5 — 2026-11-17 — Applied without approval, because each either restores a documented intent or closes a reachability gap and none alters a severity threshold, an integrity requirement, an installation privilege or a Git grant. **(i)** Warden's mandatory-check list and its live envelope are aligned by adding the narrow read-only registry-metadata form the contract already requires, so the obligation at `:150`/`:208` becomes executable instead of silently unavailable. **(ii)** Warden gains an explicit stopping condition: the review terminates when the default audit's mandatory checks for the touched surface have been executed and classified, an unchanged recorded input reuses its accepted evidence, and an acknowledged advisory is final for that head. **(iii)** Forge's harness block and its project-region reviewed-command list gain the three root read-only verification scripts. `pnpm verify` is deliberately not granted: it composes the same three, and Forge correctly refused to run a script whose body it had not audited.
- L6 — 2026-11-17 — Withheld, because each changes what the security gate can accept, or what a privileged role may do. **(P-A)** Removing canonical-project mapping and locked-environment compatibility from the `unavailable`/`indeterminate` INFO precondition, and scoping the Artifact-Integrity Controls table to the candidate artifact and any finding-bearing artifact, would make a clean `[PASS]` reachable for a change whose only limitation is undecidable optional provenance. That is a change to an established security acceptance policy, which the request requires be identified and approved before application. **(P-B)** Allowing Herald a `--output` form scoped to the gitignored output directory is a Git permission change. **(P-C)** Granting a lockfile-frozen install form so an isolated worktree can be verified is an installation privilege change. All three are recorded as open tasks T3 and T4 and are not applied.
- L7 — 2026-11-17 — Validation executed on the delivered bytes. `node .agents/skills/odd-workflow/scripts/validate_feature.ts odd/tasks` → all 25 records ok. `node .agents/skills/odd-workflow/scripts/validate_feature_file.ts odd/features` → exit 0 over all 11 feature files. `pnpm lint` → exit 0, no findings. `pnpm typecheck` → exit 0 across the six workspace projects and the two non-workspace roots. `node .agents/skills/op-skill-creator/scripts/check_markdown_text.ts --policy .aicore/core/knowledge/unicode-policy.json` over the five edited paths → no findings. `pnpm format:check` → exit 1 with three unformatted files: this record's fence delimiter, corrected here, plus the other workstream's `cli/aicore/tests/e2e/sync-opt-out.test.ts` and `odd/tasks/2026-11-17-cheapest-test-boundary.md`, which this change does not touch and must not touch. Converging evidence for this change's own paths only: `pnpm exec biome format` over the same six edited paths → "Checked 6 files in 5ms. No fixes applied." Per-agent permission probes are recorded at L3 and L4 and are the behavioural evidence for the envelope; no matcher or simulator was written, because a literal probe is harness behaviour and a matcher only reproduces it.
- L8 — 2026-11-17 — Blocked: this record cannot close. Open closure prerequisites, each with its owner. (a) The commit reference every task row requires does not exist and cannot exist: the request forbids commits without explicit authorization, so T1–T7 stay `commit: pending`. (b) T3 and T4 await the three approval decisions recorded at L6; until then S3, S7 and S8 are unimplemented and must not be reported as met. (c) The independent semantic review `### Close` requires has not run over these bytes. (d) The runtime observation that the new grants actually take effect requires an OpenCode restart, which this session cannot perform; the grants are configuration-verified only and are never reported as runtime-verified.
- L9 — 2026-11-17 — DEBT-057 disposition. Its evidence clause is now answered by L3 and its resolution criteria are partially satisfied: a finite, risk-based stopping and evidence-reuse process is established, and the informational/advisory/blocking distinction is stated in the reachable set, but the canonical-project-mapping classification that produced the residual advisory is exactly the item awaiting approval at L6 (P-A). The entry therefore stays open, its `Direct evidence` is extended with L3's mechanism, and it is not retired. One new debt entry is opened — **DEBT-058**, the absence of any mechanical check that a command an agent runtime declares mandatory has an authorized executor, which is the defect class behind both problems and the reason B1 could regress silently after the root contract suite was retired. It is deferred under section 9 of the request, not waived. The three withheld corrections remain tracked as T3/T4 in this record rather than as debt, because they await a decision rather than a deferral.
- L10 — 2026-11-17 — Durable-file accounting, as the skill's `### Create or update the feature file` requires. **`odd/features/agent-workforce.md`** — one requirement added, R7 (Warden's assurance ends in a stated verdict it can reach, reuses unchanged evidence, distinguishes missing optional evidence from a finding, and treats an acknowledged advisory as final). Outcome: R7 **unticked** — this change delivers the reuse and stopping half, but R7's own text also covers the missing-optional-evidence distinction, which is withheld at L6 (P-A), so the requirement is not yet true as written. R1–R6 were read, found unaffected and were not re-verified. Declared status corrected from `achieved` to the derived `partial`. **`odd/features/agent-execution-permissions.md`** — new durable capability, seven requirements. Outcome: R2 **ticked** (each new Forge grant lies inside Forge's documented responsibility, and no runtime mention is treated as authorization); R4 and R5 **ticked** (the global `git *` and `gh *` denies, Herald's exclusive rows and the `gh pr merge` deny were read and are unchanged by this edit); R1, R3, R6 and R7 **unticked** with reasons — R1 and R3 await the approval items at L6 and the harness restart at L8(d), R6 is only partly exercised because the withheld items were held for a decision rather than widened, and R7 is not satisfied because the new grants were configuration-verified only and the only observed harness behaviour was the denial this change removes. Derived status `partial`.
- L11 — 2026-11-17 — Independent reviews and their dispositions, both fix-first and applied in this work unit. Sentinel 🛡️ (Quality Guardian), edit-triggered audit of the five changed paths, returned **[FAIL]** with eight findings and no auto-fixes: F1 (no durable-file accounting) → L10; F2 (dangling `format:check` pointer) → L7 rewritten with literal results; F3 (stale `achieved` status) → L10 records the derived statuses; F4 (no full-mirror state) → L13; F5 (the terminal condition named no emitted signal) → the clause now states `[ADVISORY]`, never `[PASS]`; F6 (Forge's Hard Rules enumeration did not name reviewed verification commands) → the bullet now does; F7 (bare-name prose mentions in `odd/tasks`) → **not fixed by design**, a judgment call left to this decision: the same pattern is present at 1–75 occurrences in every sibling record, so correcting one record would not converge the corpus and the L1 verbatim block is untouchable — recorded as an INFO observation requiring no action; F8 (line references in L3 no longer resolve after the edit) → L3's citations are pre-edit line references and are read against the record's own quoted rule text. Warden 🔒 (Dependency Warden), permission-boundary review, returned **[ADVISORY]** with two actionable findings and two INFO observations: W-F1 (the `pnpm info` allow was not narrowed against a flag that redirects the metadata source) → two ordered `deny` rows now close `--registry` and `--config` after the allow, and the finding raised a real narrowing gap rather than a policy question; W-F2 (the repetition clause could suppress an unacknowledged advisory) → the clause is now scoped to acknowledged advisories and states that an unacknowledged one stays open. Warden's INFO observations confirm no severity threshold, integrity control, no-override rule, install, Git or staging prohibition was weakened, and that the three Forge allows add no capability Forge did not already reach through another executable. Neither reviewer required a user decision.
- L12 — 2026-11-17 — Second and third review rounds, and the loop cap. **Round 2** re-read the corrected bytes in the same reviewer sessions. Sentinel 🛡️ (Quality Guardian) confirmed F1–F6 and F8 addressed on the candidate and F7 closed by adjudication, ran both validators itself (exit 0; 25 records; 11 feature files with both in-scope files `partial`) and returned **[PASS]** with zero open findings. Warden 🔒 (Dependency Warden) confirmed W-F2 closed and W-F1 partly closed, and raised one residual: two further spellings satisfied the `pnpm info` allow without matching either deny — a scoped-registry key carrying no `--registry` substring, and a flag that relocates pnpm's config root so a different registry is read with no source flag at all — both labelled as hypotheses about pnpm 12.14.0's option handling rather than verified behaviour. **Round 3** applied Warden's own prescribed correction: three further ordered `deny` rows close the scoped-registry key, the config-root flag and its short form, and the comment now records the envelope as cooperative matching rather than a sandbox, consistent with how this file describes every other grant. Warden re-audited the changed block and returned **[PASS]**, verifying that each residual resolves to deny, that the plain `<spec> --json` form stays reachable, and that no new deny shadows `pnpm audit --json`, `pnpm config get registry`, `pnpm outdated --json` or the four `uv` forms. Both reviewers now hold zero open findings on these bytes; the three-round cap is reached and no fourth unattended round is dispatched.
- L13 — 2026-11-17 — Full feature mirror: pending recovery, not synchronized. The contract requires the entire current document to be stored with project/feature identity, locator and content revision, then independently read back and compared. This record is approximately 24 000 characters across 370 lines and contains log entries well over the 2000-character read-surface cap, so a faithful byte-complete copy cannot be written or its readback verified through the surface available here; an unverifiable write is not synchronization, and a locator or summary is not a mirror. The project binding also records that the memories backend exposes no exact feature-key upsert, no explicit read-scope selection and no compare-and-swap. The authoritative file is complete and unchanged in the repository; the mirror is recorded as pending, and the next bounded recovery action is to store and read back this record once a surface can reproduce its long entries byte-completely, before closure.
- L14 — 2026-11-17 — **P-A approved and applied, narrowed to the authorised scope.** The decision, verbatim: "P-A — APPROVED WITH STRICT LIMITS" / "You may correct Warden's treatment of **unavailable optional provenance evidence**." / "When all applicable mandatory security and integrity checks have positively passed, the inability to establish optional canonical-project mapping must not automatically force an ADVISORY." / "A check that is mandatory under the applicable security contract must remain mandatory." / "Before applying P-A, verify that the proposed change affects only the incorrect classification of optional, unavailable evidence." **Applied:** in `#### Publisher-Provenance Evidence Contract`, canonical-project mapping was removed from the `unavailable` and `indeterminate` positive-control lists, and both bullets now state that it is an input to provenance verification — required for `verified` status and for a destination documenting a high-assurance requirement, recorded as `not required` where no verification is attempted, never as an unverified control and never as a finding. The Artifact-Integrity Controls table's canonical-project-mapping cell gained `not required` as a value. Nothing else in that section changed. **Scope check, as required before applying.** Retained exactly as written: the vulnerability severity thresholds at `:51-56`; committed hash coverage, exact pin and approved index as INFO preconditions; acceptable license; clean vulnerability scan; **compatible locked environment** — kept deliberately, because the approval forbids "Skipping the required locked-environment checks", so the narrower correction supersedes the broader one I proposed at L6, which had also removed that control; the Tier 1 and Tier 2 definitions and the per-case restriction that forbids Tier 2 as a default step; the Tier 2 six-step procedure; the destination high-assurance clause; `#### No Override Mechanism`; the Hard NO-AUTOUPDATE rule; and the rule that a hash mismatch or any concrete provenance contradiction is a BLOCK. The earlier proposal's second half — scoping the Artifact-Integrity Controls table to the candidate and finding-bearing artifacts — was **not** applied; only the mapping cell's value domain changed, so the table still requires every control for every listed artifact. A failed or unverified integrity control still yields ADVISORY or BLOCK, and `[PASS]` still requires every remaining control to pass. The change therefore affects only the classification of optional, unavailable provenance evidence.
- L15 — 2026-11-17 — **P-B rejected and P-C deferred; requirements reconciled, not silently dropped.** Verbatim: "P-B — REJECTED" / "**Do not modify Herald's Git permissions.**" / "The `git diff --output` denial was intentional." / "Herald is not the problem being corrected." and "P-C is explicitly deferred. Do not repeatedly ask for the same approval in this task." Consequences: **S7 is retired** — the requirement is removed from `## Specs`, its obligation accounting is this entry plus L6, and the underlying `git diff *--output*` deny at `.opencode/opencode.jsonc` is unchanged. **S8 is retained and unmet**: no installation permission was added for any role, no lockfile-frozen form exists, and T4 stays `open` with this deferral recorded as its reason. The remaining repeatability limitation, stated plainly: verifying an exact committed revision in a Herald-created worktree still requires a narrowly scoped per-execution approval for the dependency provisioning, because the worktree has no `node_modules` and no role holds a permanent install form; that is a known limitation, not a defect to re-open, and it is recorded here as the task requires rather than as a new debt entry.
- L16 — 2026-11-17 — Durable-file accounting for the P-A delivery, superseding the outcomes recorded at L10 for the requirements P-A affected. **`odd/features/agent-workforce.md`** — R7 **ticked**: its three clauses are now true — the stopping section reuses unchanged evidence, the provenance contract distinguishes missing optional evidence from a finding, and an acknowledged advisory is final for that changeset; the requirement's "every check it declares mandatory is executable by that role" clause was **removed** from R7 as a duplication correction, because that obligation is stated once in the other durable file. Declared status returned from `partial` to the derived `achieved` (R1–R7 all ticked). **`odd/features/agent-execution-permissions.md`** — R1 **ticked**: every command the checked runtimes declare mandatory was enumerated against the effective rules and each resolves to an allow or is reported unavailable — Warden's advisory scan, approved-source read and registry-metadata read; Forge's reviewed suite, typecheck and root verification forms; Crucible's reviewed suite and install form; Herald's Git and GitHub families; Sentinel and Inquisitor declare no executable grant. R6 **ticked**: the two operations this change could not authorise were routed to a user decision rather than widened. R2, R4 and R5 stand unchanged and were not re-verified. R3 and R7 stay unticked: R3 because the root verification grants have not been observed working after a harness reload, and R7 because of the same limitation. Derived status `partial`. No requirement is duplicated between the two durable files after the R7 correction.
- L17 — 2026-11-17 — Focused validation pass, one pass as instructed, distinguishing what was read from what was observed. **Warden scenarios, verified against the delivered rule text.** (1) A review whose mandatory checks all pass and whose only limitation is unavailable optional canonical-project mapping now has a reachable terminal verdict: the INFO preconditions no longer include that control, so `[PASS]` is not structurally excluded. (2) The same review no longer re-raises the mapping question on unchanged input: the `#### Evidence Reuse and Stopping Condition` reuse clause requires matching recorded inputs, and the repetition clause makes a renewed request for already-supplied evidence a contract defect. (3) A genuine integrity mismatch is unchanged: the `[BLOCK]` definition still names a hash mismatch and concrete artifact-integrity failure, and `#### No Override Mechanism` is untouched — read, not modified. (4) Severity is unchanged: `:51-56` is byte-identical, so a confirmed high-severity advisory or CVE still yields `[BLOCK]`. (5) An accepted ADVISORY is final for that changeset and is never restated as `[PASS]`, while an advisory nobody acknowledged stays open. **Forge.** The three added rows are `pnpm lint`, `pnpm format:check` and `pnpm typecheck`, each read-only; `pnpm verify`, `pnpm format`, `pnpm lint:fix`, `pnpm install` and every other pnpm form still resolve to the Forge `pnpm *` deny. **Herald.** The herald block is unchanged in this work unit: `git diff *--output*` still denies, the force-push, reset, clean, reflog, gc, prune, repack and `gh pr merge` denies are intact, and the global `git *` and `gh *` denies still close every other role. **Runtime limitation, not a new investigation:** the Warden `pnpm info` grant and the three Forge grants are configuration-verified only. Observing them working requires an OpenCode reload, which this session cannot perform, so they are not reported as runtime-verified; the only harness behaviour observed in this work unit is the denial those grants remove.
- L18 — 2026-11-17 — **Runtime verification after the harness reload. All four previously configuration-only grants are now observed working, and both narrowing boundaries still hold.** Forge 🔨 (Implementer), from its own shell: `pnpm lint` → allowed, exit 0; `pnpm format:check` → allowed, exit 1 with `Found 2 errors.` naming the two paths owned by the other workstream (a content result, not a permission refusal); `pnpm typecheck` → allowed, exit 0. Warden 🔒 (Dependency Warden), from its own shell: `pnpm info postcss@8.5.33 --json` → allowed, exit 0, returning `name`, `version`, `license`, `dist` (with `integrity`, `tarball`, `shasum` and `attestations` including `provenance.predicateType`), `repository`, `engines`, `maintainers` and `_npmUser` with `trustedPublisher`. **Boundaries re-confirmed by denial:** Warden's `pnpm info postcss --registry https://registry.npmjs.org/ --json` → `permission.rejected`, and Forge's `pnpm install --frozen-lockfile --ignore-scripts` → `permission.rejected` under the Forge `pnpm *` deny. Corroboration for L14: the metadata document now supplies `repository`, `dist.integrity` and `dist.attestations`, so the candidate's provenance inputs are retrievable and the control that was permanently `unavailable` has an executor. One harness limitation observed and worth recording: the refusal payload is byte-identical for every denial and names no matched rule, so a denial's responsible rule must be established by comparing an allowed variant with a denied one, not from the message. No grant failed, so no configuration defect required correction.
- L19 — 2026-11-17 — **P-C resolved: the existing path could not provision, the mechanism can enforce the boundaries, and the smallest adjustment is applied.** Existing installation permissions inspected: Crucible 🔥 (Test Architect) holds a bare `pnpm install`, and Forge 🔨 (Implementer) holds `pnpm install --lockfile-only --ignore-scripts`. **Neither provisions an approved dependency set safely.** The bare form is neither frozen nor script-disabled — it may write the lockfile and it runs lifecycle scripts — so using it to materialise an approved lockfile would open a dependency-change path and a lifecycle-execution path that Warden's gate exists to close; the preparation form writes no `node_modules` and so cannot run a suite at all. **Mechanism capability, evidenced rather than assumed:** exact whole-value command-text matching distinguishes an allowed form from a redirected one, proven by L18's `pnpm info` pair; `--frozen-lockfile` fails rather than writing a disagreeing manifest or lockfile; `--ignore-scripts` executes no lifecycle script. The safety boundaries of the intended operation are therefore enforced by the mechanism and by pnpm, not by documentation. **Applied:** three literal forms, one per install root in `docs/tooling.md`, granted to Crucible 🔥 (Test Architect) only — `pnpm install --frozen-lockfile --ignore-scripts`, `pnpm --dir mcp-servers/system-one install --frozen-lockfile --ignore-scripts`, `pnpm --dir .opencode/plugins/odd-adviser install --frozen-lockfile --ignore-scripts` — with ownership and boundaries documented in that runtime's project region. No wildcard, no `pnpm add`, no update or upgrade form, no bare-form change, and no second role given an install family. **Two limits stated, not enforced:** the layer matches command text only and cannot bind the working directory or prove which checkout is provisioned — the assignment names the worktree and a stale or mismatched lockfile makes the frozen form fail closed — and a checkout outside the repository is reached through the already-permitted `external_directory`. **S8 remains unmet and unticked:** its acceptance requires the frozen install followed by the reviewed suite at an exact committed revision in an isolated checkout, which needs the next reload and an authorised disposable checkout; the two worktrees present include the PR #192 validation checkout, which is out of scope.
- L20 — 2026-11-17 — Durable accounting after the runtime verification. **`odd/features/agent-execution-permissions.md`** — R3 **ticked** on the L18 observations (the implementing role ran all three root read-only gates and gained no mutating package-manager operation), and R7 **ticked** because every grant in this change is now established by observed harness behaviour rather than by reading the configuration. R1, R2, R4, R5 and R6 stand as recorded at L16. All seven requirements ticked; declared status set to the derived `achieved`. **Stated clearly so the tick is not over-read:** this durable file's seven requirements do not include isolated-verification provisioning, so its `achieved` says nothing about S8. Isolated provisioning remains the task's deferred requirement, S8 is unticked and its task T4 stays `open`; the capability gap is disclosed here and in L19 rather than absorbed into the durable status. `odd/features/agent-workforce.md` is unchanged by this turn and remains `achieved` on R1–R7. DEBT-057 and DEBT-058 are unchanged and remain accurate: DEBT-057's remaining item is the PR #192 accepted advisory and its closure review, and DEBT-058 — no mechanical check that a declared mandatory command has an executor — is still true, so neither is retired.
- L21 — 2026-11-17 — **Consistency check on Crucible's two install families; one removal is proposed and not applied.** Consumers of the bare `pnpm install` grant enumerated by reading the runtime: the only one is `#### Test-Runner Dependency Installation` steps 1–3 together with `#### Bash Grant Scope`'s "the project's package-manager install command, only for test-runner dependencies after Warden 🔒 (Dependency Warden) APPROVE and Cipher 🔓 (Lead Orchestrator) dispatch". No repository document, skill or other runtime references Crucible's grant; `docs/tooling.md:35` describes the three install roots in prose, and the incident-workflow skill's install line addresses a skill directory that neither the bare root form nor Crucible covers. **Runtime evidence:** the frozen root form ran from Crucible's own shell → allowed, exit 0, `Lockfile is up to date, resolution step is skipped`; the bare form also still runs → allowed, exit 0, `Already up to date`, which is expected because the row is still configured and demonstrates that the layer cannot see dispatch context. **Conclusion:** the bare form is not required for any documented duty — once a test-runner dependency's manifest and lockfile are already updated and Warden-approved, the frozen form materialises exactly that set, whereas the bare form additionally permits rewriting a stale lockfile, which is the dependency-change path Warden's gate exists to close. It is therefore replaceable, with one consequence to state: a test-runner package whose setup needs a lifecycle script could not be provisioned by an `--ignore-scripts` form, and that case would need its own decision rather than a standing unfrozen grant. **The exact removal diff and its rationale were presented to the user and are not applied**, because altering a permission surface the user approved on 2026-11-14 requires their confirmation. **Enforceable boundary, answered precisely:** argument text only — exact whole-value command matching plus pnpm's own `--frozen-lockfile` and `--ignore-scripts`; the execution directory is not enforceable by the permission layer, and this probe demonstrates it. **S8 unchanged and unticked:** the frozen form is runtime-verified only at the repository root, the two `--dir` forms remain configuration-verified, and no isolated checkout is authorised — the only candidates present are the PR #192 validation worktree, which is out of scope.
- L22 — 2026-11-17 — **Scope correction: the proposed Crucible removal was an unjustified expansion and is not authorized.** Decision, verbatim: "**Do not remove or restrict Crucible's existing permissions.**" / "Crucible was not identified as the cause of the recurring problems in PR #192." / "My previous instruction to remove Crucible's bare `pnpm install` grant was an unjustified scope expansion." / "**That removal is NOT authorized.**" **Nothing was executed, so no rollback is required or performed.** Verified current state in the configuration rather than assumed: `agents.crucible.permissions` still carries `{ "action": "shell", "resource": "pnpm install", "effect": "allow" }` alongside the three frozen forms, and Crucible's project region still describes that bare grant as untouched and limited to test-runner dependency installation after Warden 🔒 (Dependency Warden) APPROVE. L21's removal diff was presented and never applied; its conclusion that the bare form is not required for any documented duty is analysis only, is not acted upon, and does not become a requirement of this task. Crucible is outside the confirmed failure set, whose members are Warden 🔒 (repeated reviews, provenance ADVISORY cycles, missing metadata-query capability, weak reuse and stopping), Forge 🔨 (missing read-only repository verification commands) and Cipher 🔓 (repeated coordination cycles); Herald 📯 followed an intentional restriction correctly and required no permission change. No installation permission is added or removed by this turn, no worktree is created, and no new audit, framework, feature, task or debt is opened. S8 remains unticked and pending for the reasons at L21, and DEBT-057 and DEBT-058 remain open with their resolution criteria unmet.
- L23 — 2026-11-17 — **Delivery-scope ownership and S8's single missing action, established from Herald 📯 (Release Manager)'s read-only inventory at HEAD `c85fbc79d2450154403bd229dd6b907c0f1251c9`.** Nineteen paths are dirty: this workstream owns `.opencode/opencode.jsonc` (55/0, all rows are this change's), `.opencode/agents/warden.md` (20/7), `odd/features/agent-workforce.md` (1/0), and the two new untracked records. Three files are shared with the `cheapest-test-boundary` workstream and were mapped hunk by hunk: `forge.md` carries one frontmatter `version:` line whose committed value becomes 3.6.0 (both workstreams' bumps collapse into it), the other workstream's step-5 T8 sentence (1/1), and this change's Hard Rules enumeration (1/1) plus the reviewed-verification paragraph and Local History entry (3/0); `crucible.md` carries one `version:` line landing on 1.20.0 (both bumps), the other workstream's T8 bullet (1/0), and this change's provisioning block (10/0); `debt.md` carries DEBT-055/056 and the pre-existing DEBT-057 text from the other workstream together with this change's DEBT-057 state field and DEBT-058. **Consequence, stated rather than worked around:** those three files cannot be isolated at file granularity, and hunk-level staging is not an authorized Herald 📯 (Release Manager) operation, so any commit that includes them carries both workstreams' content. The delivery proposal therefore discloses the coupling instead of claiming an isolation the tree cannot support. **S8's single missing action:** explicit authorization for Herald 📯 (Release Manager) to create one disposable worktree at an existing committed revision — HEAD qualifies, so no commit of this work is required — in which Crucible 🔥 (Test Architect) runs `pnpm install --frozen-lockfile --ignore-scripts`, the two `--dir` provisioning forms and the reviewed suite. The three grants already exist and the root form is runtime-verified, so no permission change is needed; the PR #192 validation worktree is not reused. Until that run happens S8 stays unticked.
- L24 — 2026-11-17 — **S8 satisfied, with evidence; delivery isolation planned.** Herald 📯 (Release Manager) created one disposable worktree, detached, at the exact revision `c85fbc79d2450154403bd229dd6b907c0f1251c9` — `G:\projects-personal\ai-core-s8-validation`, verified detached by a failing `git symbolic-ref` and by `git worktree list`, clean, resolved to a real directory with no reparse point, and the primary checkout left byte-identical in its dirty state. Crucible 🔥 (Test Architect) then ran, in that worktree: `pnpm install --frozen-lockfile --ignore-scripts` → exit 0, `Lockfile is up to date, resolution step is skipped`, `Packages: +47`; `pnpm --dir mcp-servers/system-one install --frozen-lockfile --ignore-scripts` → exit 0, `+52`; `pnpm --dir .opencode/plugins/odd-adviser install --frozen-lockfile --ignore-scripts` → exit 0, `+51`; and the reviewed suite `pnpm --dir cli/aicore test` → exit 0, `Test Files 35 passed (35)`, `Tests 153 passed | 4 skipped (157)`. The non-zero package counts establish that the checkout began without installed dependencies, so the run is a genuine isolated provisioning, not a reuse of the primary tree. **S8's acceptance is met:** a named authorized executor, the lockfile-frozen form, and the reviewed suite at an exact committed revision. Limitations recorded rather than glossed: Crucible 🔥 (Test Architect) cannot itself verify the commit identity because Git belongs to Herald 📯 (Release Manager), so the pin rests on Herald's evidence; absence of `node_modules` was checked at the checkout root only, with the two `--dir` counts taken as corroboration; pnpm emitted a store-location warning that is cosmetic. **Delivery isolation inventory.** Exclusive to this workstream: `.opencode/opencode.jsonc` (55/0), `.opencode/agents/warden.md` (20/7), `odd/features/agent-workforce.md` (1/0), `odd/features/agent-execution-permissions.md` (new), this record (new). Three files are shared and must be isolated by hunk: `forge.md` excludes the other workstream's step-5 T8 sentence (1/1); `crucible.md` excludes its T8 bullet (1/0); `debt.md` excludes the DEBT-055 and DEBT-056 entry blocks while keeping DEBT-057's state field, DEBT-058 and the counter line. The proposed mechanism is an index-only operation — stage each shared file, then reverse-apply the three narrow foreign hunks to the index — because Herald 📯 (Release Manager)'s contract authorizes explicit-path staging only, never hunk-level index writes; it therefore requires its own authorization. Its acceptance proof is mechanical: after staging, `git diff -- <path>` must show exactly the foreign hunks as the only unstaged residue, and `git diff --cached` must show only this change. Excluded from delivery in every case: the four skill tests, the four CLI tests, `.aicore/core/architecture/testing/architecture.md`, and the two untracked `cheapest-test-boundary` records.
- L25 — 2026-11-17 — **Delivered as one isolated PR.** Base verified before branching: local `main` and `origin/main` both at `c85fbc79d2450154403bd229dd6b907c0f1251c9`, zero divergence either way, and PR #192 confirmed **merged** — its merge commit is that very tip — so nothing stacks on a feature branch and no committed work depends on an absent commit. Three shared files were isolated in the index only, leaving the working tree untouched: `.opencode/agents/forge.md` and `.opencode/agents/crucible.md` each lost their other-workstream testing-guidance hunk, and `.aicore/core/knowledge/debt.md` lost the DEBT-055 and DEBT-056 entries while keeping DEBT-057, DEBT-058 and the counter. Two counts were corrected during staging and are recorded rather than glossed: `crucible.md` is 11/1, not the 11/0 originally forecast, because its frontmatter `version:` line is a 1/1 change exactly like `forge.md`'s, and the `DEBT-055`/`DEBT-056` strings that remain visible inside the staged diff are backticked prose citations in this record's own L2, not foreign entries. Staged and unstaged counts reconcile exactly with the working-tree totals, so no content was lost or duplicated. Three commits: `eadaa22` `fix(agents): restore authorized verification and provisioning paths` (`opencode.jsonc` 55/0, `forge.md` 5/2, `crucible.md` 11/1); `ce81c02` `fix(deps): make Warden's dependency review proportional and conclusive` (`warden.md` 20/7); `edd8258` `docs(odd): record the workflow-obligation corrections and their evidence` (this record, both durable files, `debt.md` 18/1). Pull request **#193** targets `main` with eight changed files and no other path; the `cheapest-test-boundary` tests, its testing-contract edit, its two records, DEBT-055 and DEBT-056 all remain uncommitted and intact.
- L26 — Close: 2026-11-17 — every requirement is delivered and evidenced. S1–S6, S8–S10 are met and S7 is retired by the user's rejection of the Herald 📯 (Release Manager) `--output` grant; S8 closed on the isolated run at `c85fbc79` recorded at L24, and no acceptance criterion was marked satisfied before its evidence existed. All seven task rows are `done` with commit references. Requirements: `agent-workforce` R1–R7 ticked, `agent-execution-permissions` R1–R7 ticked, and the latter states explicitly that its seven requirements do not cover isolated provisioning, so its `achieved` never stood in for S8. Debt: DEBT-057 and DEBT-058 stay open with their criteria unmet, neither retired nor renumbered. **Independent semantic acceptance is the PR-stage review at this head**, per the precedent recorded in `2026-11-14-scoped-dependency-admission` L70 and `.agents/skills/odd-workflow/SKILL.md` `### Close`; its verdict is published in the pull-request body rather than restated here, and this record makes no clean-completion claim on the reviewer's behalf. The ordering of record closure against PR review remains the ambiguity recorded as DEBT-048 and is not resolved here.
- L27 — 2026-11-17 — Review finding F1 closed. Inquisitor 🔎 (PR Reviewer) returned `[ADVISORY]` with one finding: the `> **Delivery:**` line asserted a ≈190-line basis below the advisory ~400-line trigger while the delivered range measures 506 insertions and 11 deletions, and no running count was recorded. The finding was fix-first eligible and is corrected here rather than deferred: the line now states the forecast, the measured range at `f15747d`, the reason the excess is this record's own growth rather than implementation volume, and the strategy actually applied. No evidence, requirement or status changed, and no other finding was open.
