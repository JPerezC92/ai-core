# ODD upstream fidelity and first-party Python retirement

> **Status:** active
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-14
> **Objective:** Make AICore's ODD implementation follow the intent of the original ODD in five respects — Log authoring, Specs authoring, task closure consistency, a routine seven-day retention policy, and completion of the first-party Python migration — in one pull request.
> **Branch:** `refactor/odd/simplify-workflow-and-typescript-migration`, created by Herald 📯 (Release Manager) from `origin/main` at `0c786e9`; `main` is untouched.
> **Delivery:** One strategy, `single-pr`, as the user requires one pull request. Authored additions plus deletions forecast above the ~400 trigger, so the single-pull-request strategy applies from the first commit; slice boundaries are the work-unit tasks.
> **Runner:** `pnpm --dir tests exec vitest run`; `pnpm --dir .agents/skills/odd-workflow exec vitest run`; `node .agents/skills/odd-workflow/scripts/validate_feature.ts .aicore/core/odd/tasks`; `node .agents/skills/odd-workflow/scripts/validate_feature_file.ts .aicore/core/odd/features`.

Load and read the `odd-workflow` skill (`.agents/skills/odd-workflow/SKILL.md`) before creating or maintaining this record. Its creation, delivery, change and closure procedures are canonical; this template illustrates their layout, not another policy definition.

## Specs

- **S1 — Equivalent contract coverage in TypeScript**

  **Requirement:** "Finish the Python-to-TypeScript migration, preserving equivalent working test coverage."

  **Acceptance:** The contract suite runs 9 tests over 2 files with zero failures.

- **S2 — The first-party Python surface is gone**

  **Requirement:** "Complete the Python-to-TypeScript migration for first-party Python tooling that no longer has a justified consumer."

  **Acceptance:** A repository search for the removed Python paths returns zero live references outside the two MCP tooling projects.

- **S3 — The Log convention is concise and non-duplicating**

  **Requirement:** "Do not reproduce complete reviewer reports, investigation transcripts, repeated tool output, or PR bodies."

  **Acceptance:** The skill's log-evidence rule and the template both state the logbook purpose and that prohibition.

- **S4 — The Specs convention is readable and verifiable**

  **Requirement:** "Preserve all three, but separate them visually using multiline Markdown."

  **Acceptance:** The skill's specification rule and the template both show one bullet per spec with separate requirement and acceptance paragraphs, and the validator accepts that shape as one entry.
- **S5 — Historical records are read or deleted, never modified**

  **Requirement:** "Do not rewrite historical task Logs or Specs to make them eligible for deletion."

  **Acceptance:** The implementation diff contains no content change to a historical task record.

- **S6 — The validator reports a completed-but-active record**

  **Requirement:** "The validator must detect newly created task records that claim to be active despite all tasks being complete, unless a genuine pending closure obligation is explicitly recorded."

  **Acceptance:** Validating a record created on or after the effective date whose tasks are all done exits non-zero and names the defect.

- **S7 — A historical record is never invalidated**

  **Requirement:** "Do not modify historical task records just to satisfy new validation rules."

  **Acceptance:** The feature-document validator exits 0 over the whole corpus.

- **S8 — Retirement eligibility has exactly two conditions**

  **Requirement:** "A task record is eligible when BOTH conditions hold: 1. Status: closed. 2. At least seven complete calendar days have passed since its valid Closed date."

  **Acceptance:** The retention check excludes a record closed six days before the report date and reports one closed exactly seven days before it as a candidate.
- **S9 — Eligible records are deleted without per-record approval**

  **Requirement:** "No per-file approval is required for records satisfying this policy."

  **Acceptance:** The skill's retirement rule authorizes deletion by the policy itself and names Herald as the executor.

- **S10 — The retention rule adds no new system**

  **Requirement:** "Do not introduce additional eligibility conditions, exemptions, schedulers, services, or tracking systems."

  **Acceptance:** The retention rule names one command in the existing skill plus the ordinary Git workflow, and no new service, scheduler or store exists in the diff.

- **S11 — Every current rule is classified with its evidence**

  **Requirement:** "Do not automatically keep AICore-specific rules just because they already exist."

  **Acceptance:** The record's log contains one entry naming the rules placed in each classification category.

- **S12 — Original guarantees and Herald's authority are unchanged**

  **Requirement:** "Preserve ODD's seven-step protocol, verifiable requirements, durable evidence, independent review where genuinely required, and Herald's exclusive Git/GitHub authority."

  **Acceptance:** The changed rule surfaces still carry all seven protocol steps, the requirement rule, the evidence rule, the review duty and Herald's exclusive authority.

- **S13 — One branch, one pull request, no merge**

  **Requirement:** "Keep everything in this single ODD workstream." and "Do not merge. Merge authority remains mine."

  **Acceptance:** Exactly one open pull request exists for this branch, with zero merge commits authored by an agent.

## Tasks

- T1 | S1 | delegated (porting the contract suite is implementation work in a new package with a dependency change) — Forge 🔨 (Implementer) | in progress | commit: pending
- T2 | S2 | delegated (removing the Python surface and repointing its bindings is implementation and configuration work) — Forge 🔨 (Implementer) | in progress | commit: pending
- T3 | S3, S4 | delegated (the skill rule text and the template are documentation-owned prose) — Scribe ✍️ (Docs & Problems Manager) | in progress | commit: pending
- T4 | S5, S7 | inline (confirming the corpus is untouched and the rule is prospective is coordinator-owned verification) — Cipher 🔓 (Lead Orchestrator) | in progress | commit: pending
- T5 | S6, S8, S9, S10 | delegated (the validator rule, the retention check and their tests live in the skill's script package) — Forge 🔨 (Implementer) | in progress | commit: pending
- T6 | S9 | inline (executing the retention policy is coordinator verification plus Herald's deletion) — Cipher 🔓 (Lead Orchestrator) | in progress | commit: pending
- T7 | S1, S2 | delegated (risk trigger: the dependency surfaces change) — Warden 🔒 (Dependency Warden) | in progress | commit: pending
- T8 | S1, S6, S8 | delegated (risk trigger: a new suite and runner wiring) — Crucible 🔥 (Test Architect) | in progress | commit: pending
- T9 | S6, S8, S9 | delegated (risk trigger: a new runtime module in the skill package) — Bastion 🧱 (Backend & Scripts Architect) | in progress | commit: pending
- T10 | S3, S4, S5 | delegated (every change to the rule surfaces and the corpus is audited independently) — Sentinel 🛡️ (Quality Guardian) | in progress | commit: pending
- T11 | S11, S12, S13 | inline (classification, accounting, acceptance and delivery are coordinator-owned) — Cipher 🔓 (Lead Orchestrator) | in progress | commit: pending

## Log

- L1 — 2026-11-14 — Original request, verbatim: "Your task is to correct our existing ODD implementation, not redesign ODD." with the five issues, quoted verbatim: "1. Complete the Python-to-TypeScript migration for first-party Python tooling that no longer has a justified consumer. Preserve equivalent test coverage before removing Python files and dependencies." / "2. Restore the original purpose of ## Log: original request and material corrections verbatim, meaningful decisions, observed outcomes, and durable evidence references. Stop duplicating entire review transcripts, investigations, and PR bodies." / "3. Fix task-status consistency. The TypeScript validator currently enforces closed → all tasks done but not the reverse. Add appropriate detection of completed-but-active records and require Cipher to resolve genuine closure prerequisites before declaring work complete. Never fabricate independent acceptance or automatically close a feature with missing evidence." / "4. Correct ## Specs according to upstream ODD. Every S# must be one independently verifiable requirement, preserving the user's exact requirement-defining words and concrete acceptance checks. Remove unnecessary duplication and implementation transcripts from Specs." / "5. Implement a routine seven-day retention check: task records with Status: closed and at least seven complete calendar days since Closed are deletion candidates. Reconcile AICore's additional retirement conditions with this intended policy while preserving authoritative decisions and unresolved obligations." And its safeguards, verbatim: "Do not create another ODD implementation, additional agent, tracking system, audit framework, or complex validator." / "Preserve ODD's seven-step protocol, verifiable requirements, durable evidence, independent review where genuinely required, and Herald's exclusive Git/GitHub authority." / "Do not delete existing task files or merge a PR without my authorization." / "Use the current upstream and current AICore main as the factual basis." / "Classify each current rule as: Upstream ODD, preserved. AICore-specific rule, justified. AICore-specific rule, unnecessarily restrictive. Defective implementation requiring correction." / "Do not automatically keep AICore-specific rules just because they already exist." Follow-up, verbatim: "I want all five ODD improvements delivered together in ONE PR." / "One ODD workstream. One implementation branch. One coordinated test plan. One PR. One independent final review of the complete change." / "Do not create another workflow engine, agent, mirror implementation, or tracking database." / "Herald remains the sole Git/GitHub executor." / "I alone authorize the merge."
- L2 — 2026-11-14 — User correction, verbatim: "STOP retroactive ODD Log modifications. I did NOT authorize rewriting, shortening, reformatting, or normalizing historical ODD task Logs. The five-fix PR must improve the ODD workflow going forward, not perform a repository-wide historical documentation migration." with: "Leave ALL existing historical ODD task records unchanged, including their ## Log, ## Specs, task history, and original requests." / "Apply concise Log and correct Specs conventions to the authoritative ODD skill, template, and future authoring behavior." / "Adjust validators to enforce genuinely necessary structural and status-consistency rules without forcing historical records to be rewritten solely to meet new style conventions. If a new rule would invalidate legitimate historical records, design an appropriate prospective application rather than modifying history." / "Exclude unauthorized historical edits from the deliverable. Restore their exact pre-work contents using a safe, path-specific method after Herald verifies the original bytes. Preserve unrelated user changes; do not use blanket reset, clean, or destructive restoration."
- L3 — 2026-11-14 — Final scope correction and retention authorization, verbatim: "Do NOT rewrite, shorten, reformat, repair, normalize, or restore historical ODD Logs or Specs." / "The only authorized operations on historical task records are: Read them when necessary to test the new workflow. Delete them when they satisfy the new seven-day retention policy. Do not modify their contents." / "When both conditions are satisfied, delete the task file as part of the normal authorized Git workflow." / "No per-file user approval is required. This message authorizes retirement of qualifying task records, subject to verifying eligibility and preserving authoritative ODD feature specifications and required durable evidence." / "The rule applies to historical and future task records." / "Do not invent additional eligibility criteria." / "You are authorized to delete verified eligible task records within that PR, but NOT to merge the PR. Merge authority remains mine." / "Do not accept real blockers as debt merely to publish the PR."
- L4 — 2026-11-14 — Baseline and scope. Upstream ODD read from `docs/usage.md` and the `## Organic Driven Development` block of `internal/components/agentguidance/routing.go` at `Gentleman-Programming/gentle-ai@main`; AICore `main` at `0c786e9`. First-party Python scope: five modules and 587 lines — `conftest.py`, `tests/support/agent_spec_documents.py`, `tests/integration/test_agent_sources.py`, `test_agent_versions.py`, `test_agent_profiles_retired.py` — plus `pyproject.toml` and `uv.lock`. `scripts/git_preflight/` held only stale bytecode with no source and no consumer. Compatibility risk: the eleven pytest tests were the only mechanical enforcement of the agent runtime-specification region contract, the version pins and the effective harness permission boundaries, so removing them before an equivalent suite passed would have deleted that safety net. The replacement suite covers ten of the eleven rules; the eleventh is the pytest temporary-root rule, which has no counterpart because the new suite creates no scratch state.
- L5 — 2026-11-14 — Rule classification against the original ODD. **Upstream, preserved:** the seven protocol steps; the resume test as the only size classifier; one feature document per non-small feature in header, Specs, Tasks, Log order; verbatim requirement wording; one task line with stable id, linked spec, route, status and commit; the Log as a logbook with dated verbatim corrections and no exhaustive decision journal; work-unit commits; conditional test-first; the differential check for changed commands; resume from record and mirror; a per-spec verifier verdict; push, PR and merge as the user's decisions. **AICore-specific, justified:** the status, owner, created, objective, branch, delivery and runner header; recorded route with trigger evidence; the 7–64 hex commit reference; the closed date and Close entry; the durable feature file; the full-feature mirror; the three evidence classes; independent semantic review before close; Herald's exclusive Git authority; risk-triggered specialist review; the seven-day age floor. **AICore-specific, unnecessarily restrictive — two, both reconciled:** retirement required approval of each exact record, replaced by the policy-level authorization this record now states; the candidate inventory existed only on explicit request, replaced by a routine check. **Defective implementation:** first-party Python tooling with no consumer; a Log rule with no brevity or no-duplication obligation; an under-specified Specs rule; a validator enforcing closed implies done but not the converse; a retention policy with no check, no date-boundary evidence and no dry run; a validator with no notion of dates.
- L6 — 2026-11-14 — Decisions. The completed-but-active rule is prospective, gated by `CLOSURE_CONSISTENCY_EFFECTIVE_FROM`, because the user directed that a new rule must not invalidate a legitimate historical record; a record with no readable creation date stays in scope so the rule cannot be escaped by omission. The retention check decides eligibility from exactly two conditions and deletes nothing itself, because the user directed that no additional eligibility criteria be invented. Corpus rewrites are withdrawn: the conventions bind authoring from this change onward. The four records a durable surface still cites are retained until their indispensable decisions are reconciled into the durable owner, because the authorization preserves required durable evidence.
- L7 — 2026-11-14 — Verification outcomes at that point, historical and superseded by the final results recorded at L12. The contract suite then reported 10 passed over 3 files and the skill suite 53 passed; `pnpm typecheck` exit 0 across three packages; feature-document validator exit 0; feature-file validator exit 0; Markdown text policy exit 0 over every changed path. RED evidence for the new behaviours was observed by mutation before acceptance: forcing the closure condition false made the closure test fail with an empty finding list, and changing the retention threshold from seven to eight made six boundary tests fail for the intended reason. Retention dry run as of 2026-11-14: 72 candidates of 89 records.
- L8 — 2026-11-14 — Retention executed. Herald deleted 68 eligible records with one path-specific `git rm`, staged as 68 pure deletions of 3,417 lines, every staged path under `.aicore/core/odd/tasks/`; no record was modified. Four candidates were retained pending reconciliation of the durable evidence a surface still cites: `2026-11-02-odd-scope-readiness-and-ownership.md`, `2026-11-02-query-verification-debt.md`, `2026-11-03-odd-workflow-fidelity.md` and `2026-11-05-domain-architecture-definitions.md`. They were not permanent exemptions: once their citing surfaces were repointed to surviving authority — a research record, a diagnostic guidance note, two status-document pointers, and an amended ADR 0007 rather than a rewritten one — Herald deleted them as well, bringing the retired total to 72. Python cutover: eight tracked files removed and the replacement suite took their place; the reviewed whole-suite command moved to `pnpm --dir tests test` across the harness grant and the six runtime specifications that named the old one.
- L9 — 2026-11-14 — Independent assessments. Warden 🔒 (Dependency Warden) `[PASS]`, zero findings, staging authorized: the new package adds no dependency absent from the lockfile, declares no runtime dependency and no lifecycle script, and leaves no unaudited root Python surface. Bastion 🧱 (Backend & Scripts Architect) `[ADVISORY]` with five findings; Crucible 🔥 (Test Architect) `[BLOCK]` with seven; Sentinel 🛡️ (Quality Guardian) `[FAIL]` with nine. Dispositions are recorded at L10.
- L10 — 2026-11-14 — Finding dispositions, distinguishing real defects from preference. **Fixed as real defects:** an unreadable record aborting the whole report without naming it; an unvalidated as-of operand that made an operand error indistinguishable from a usage error; a prospective date gate that returned on the first creation field it found, so a decoy entry could exempt a record; a permanent rather than current-state closure-prerequisite exemption; a tautological assertion comparing two literals in the reviewed file; and an engine-dependent message pin. **Challenged and not implemented, with reasons:** the demand to extract shared pure helpers into a new module, and the demands to split modules by behaviour, move a CLI test to another level and build a generalized fixture layer — each is a structural preference with no functional consequence, and the user directed that unnecessary abstractions and additional modules not be introduced to satisfy reviewer preference. **Open:** obsolete Python references in `README.md`, `PROJECT-STRUCTURE.md`, `warden.md` and `forge.md`, and the orphan bytecode tree, which are being removed under T2; and the four retained records, whose reconciliation was completed and whose retirement is recorded at L8.
- L11 — 2026-11-14 — Relevance review of the migrated contract suite, on the user's correction that equivalence means preserving verification of current requirements rather than mirroring historical test counts. **Retained, each mapped to a live contract:** region placement, core-heading order, project-region shape and core/project separation protect the core-sync distribution contract that ships these specifications to destinations; the two permission tests protect the real defect class this repository has already hit, where a declared mandatory check or a deny row does not resolve as intended; the roster and pinned-version tests protect the agent-workforce requirement that every specification declares a SemVer version. **Removed:** the retired-profile test, whose subject — per-agent profile files under `agents/` — no longer exists anywhere in the repository and backs no active requirement, so it asserted the absence of a retired structure rather than a current behaviour. **Not consolidated:** the two version tests keep distinct assertions and merging them would be cosmetic. **Gaps:** the pinned-version map is not asserted to cover the whole roster, which no active requirement depends on; no test was added.
- L12 — 2026-11-14 — Delivery and final verification. Pull request #186 carries the workstream; prior evidence from a merged pull request was archived byte-verified rather than discarded, and the creation body was published without any review result or checked gate. Final state after the correction pass: the contract suite reports 9 passed over 2 files and the skill suite 54 passed, `pnpm typecheck` exits 0 across three packages, both feature validators exit 0, the Markdown text policy exits 0 over every changed path, and 72 task records stand retired. The Log's earlier counts at L7 and L8 are the observations at those points and are superseded here. No merge is authorized.
