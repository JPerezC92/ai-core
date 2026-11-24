# Skills-first agent architecture

> **Status:** active
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-24
> **Objective:** Replace mandatory multi-agent orchestration with direct primary-agent execution plus on-demand skills, keeping Herald's Git boundary and the seven ODD steps intact.
> **Branch:** feat/core/skills-first-architecture
> **Delivery:** option C — one feature branch, coherent work-unit commits per task, one PR at the end. Forecast ~500–800 authored additions and ~3,100 deletions (13 agent specs plus superseded procedure inside modified files); generated files excluded. Running count maintained per work-unit commit; the ~400 advisory applies to task size only and never justifies compressing tests, documentation or evidence.
> **Runner:** `pnpm --dir cli/aicore test` · `pnpm --dir cli/aicore test:e2e` · `pnpm --dir .agents/skills/<skill> exec vitest run` · `pnpm lint` · `pnpm format:check` · `pnpm typecheck` · `node .agents/skills/odd-workflow/scripts/validate_feature.ts odd/tasks`

## Specs

- S1 — Cipher performs implementation directly as the primary execution agent. Exact requirement: "Cipher becomes the primary execution and implementation agent." Acceptance: read the root runtime and name the section that grants Cipher direct implementation authority; it states the authority rather than delegating it.
- S2 — Herald is the only retained custom subagent and remains the exclusive Git and GitHub executor. Exact requirement: "Herald remains the only custom subagent and the exclusive Git/GitHub executor." Acceptance: enumerate the runtime specifications under the agent directory and confirm exactly one remains; read Herald's authority section and confirm the exclusivity and refusal duties survive.
- S3 — The other thirteen custom subagents are removed. Exact requirement: "Remove the other 13 custom subagents." Acceptance: enumerate the agent directory and observe no runtime specification for any of the thirteen retired roles.
- S4 — Three review skills exist and cover code review, dependency security and visual design. Exact requirement: "Create code-review, dependency-review, and visual-review skills." Acceptance: read each skill's file and observe a procedure that is usable without any retired subagent.
- S5 — The authoring-quality checklist is preserved inside the skill-authoring skill. Exact requirement: "Preserve Vault's useful authoring-quality checklist within op-skill-creator." Acceptance: read the authoring skill and confirm it references a quality-checklist reference file that exists.
- S6 — The seven ODD protocol steps are unchanged in identity and order. Exact requirement: "Preserve all seven original ODD steps." Acceptance: read the workflow entry and observe authorize, explore, resolve uncertainty, classify, track before the first write, implement task by task, close, in that order.
- S7 — The canonical architecture and testing standards remain authoritative and unchanged. Exact requirement: "Preserve canonical architecture and testing standards." Acceptance: confirm the shared architecture tree is byte-identical to its pre-change state and that surviving instructions still name it as the standard.
- S8 — Mandatory delegation, per-mutation checkpoints, independent semantic acceptance and independent PR review no longer gate delivery. Exact requirement: "Remove mandatory specialist delegation, per-mutation checkpoints, independent semantic acceptance, and independent PR review." Acceptance: read the workflow, closure and PR procedure owners and observe no delivery prerequisite that requires a second agent's verdict.
- S9 — Independent review stays available on explicit user request and may be recommended on risk. Exact requirement: "Independent reviews remain available on explicit user request and may be recommended when justified by actual risk." Acceptance: read the review procedure and observe both the requestable route and the recommendation, with neither stated as a delivery prerequisite.
- S10 — Evidence-based judgment and challenges to unsupported assumptions are preserved without requiring another agent's acceptance. Exact requirement: "Preserve evidence-based technical judgment and challenges to unsupported assumptions, without requiring another agent to accept the challenge." Acceptance: read the shared conduct and decision-consultation rules and observe the challenge duty intact with no second-agent acceptance requirement.
- S11 — No receipt-driven development and no replacement governance mechanism is introduced. Exact requirement: "Do not introduce RDD or replacement governance mechanisms." Acceptance: inspect the changed instruction surfaces and observe no new approval layer, audit framework, receipt system, hook, script or agent-communication protocol.
- S12 — The transitional exception is recorded verbatim and bounded to this migration. Exact requirement: "This exception applies exclusively to this migration and remains effective through its final PR delivery. Record this authorization verbatim in the governing ODD record." Acceptance: read this record's Log and observe the authorization quoted verbatim with its scope and its explicitly non-waived obligations.
- S13 — Build permissions keep the documented commands reachable and portable, add no unsafe trailing wildcard, and keep dependency installation authorized rather than blocked. Exact requirement: "An AICore-specific command allowlist must not inadvertently prevent destination projects from executing their own legitimate commands." Acceptance: read the harness configuration and observe that no allowlist names project-specific command text, that dependency mutation is prompted rather than denied, and that no newly added shell row ends in a wildcard.
- S14 — The three new skills enter the distribution set under the existing clearance model. Exact requirement: "Register the three new shared skills using the existing clearance model and document their classification." Acceptance: read the distribution registry and its format definition and observe one cleared row per new skill plus its documented classification, with the schema unchanged.
- S15 — Every listed lifecycle topic is documented in its existing canonical owner. Exact requirement: "The entire redesigned execution lifecycle must be documented in its existing canonical owners." Acceptance: walk the enumerated topics against the owners this record names and observe each stated once, without a new manual.
- S16 — The canonical ODD diagram and explanatory references describe the executed workflow. Exact requirement: "Update the existing canonical Mermaid ODD diagram and every applicable explanatory reference." Acceptance: read the workflow entry's diagram and observe no branch or label that requires a retired agent or an independent acceptance gate.
- S17 — Executable validation and its tests no longer enforce retired reviewer requirements, while unrelated structural and evidence validation is intact. Exact requirement: "Update executable validators and affected tests where they enforce retired reviewer requirements." Acceptance: run the record validator over the existing records and observe it passes without any per-spec reviewer verdict being required, and observe the retained structural findings still fire.
- S18 — The PR publication contract keeps optional verdicts, real evidence attribution and truthful results, and a missing verdict never conceals a failed check. Exact requirement: "A PR without an independent verdict is valid, but missing verdicts must never be used to conceal failed required checks or unresolved blockers." Acceptance: read the evidence-format and publication-input references and observe the absent-verdict state accepted, the unchecked-item and open-blocker states still blocking, and the readiness basis required to name its evidence source.
- S19 — Core Sync behaviour is unchanged and destination reconciliation of retired definitions is documented. Exact requirement: "Existing Core Sync behavior remains unchanged." Acceptance: confirm the synchronization engine and its tests are byte-identical, and read the adoption guidance describing that retired region-mode agent definitions are preserved and require destination-side reconciliation.
- S20 — Historical records and previously accepted decision records are untouched, and no unrelated functional change is introduced. Exact requirement: "Do not alter historical records or previously accepted ADRs." Acceptance: inspect the changed-file set and observe no record under the task-record directory, no accepted decision record and no history file in it.
- S21 — Root specification version is 7.0.0. Exact requirement: "Root specification version 7.0.0." Acceptance: read the root runtime's version marker and observe 7.0.0.
- S22 — The affected tests and repository checks pass. Exact requirement: "The affected tests and repository checks pass." Acceptance: run each command named in the header Runner field and observe each in its reported result.

## Tasks

- T1 | S12, S15 | inline (governing record and decision record are the bootstrap artifacts) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending
- T2 | S6, S7, S8, S9, S10, S11 | inline (shared rule and workflow simplification is one coupled edit surface) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending
- T3 | S4, S5 | inline (knowledge preservation must precede any deletion) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending
- T4 | S17 | inline (validator and its own suite change together) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending
- T5 | S18 | inline (publication evidence documentation only) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending
- T6 | S1, S2, S15, S16, S21 | inline (root runtime rewrite plus remaining de-roster) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending
- T7 | S13, S14 | inline (permission and clearance registration is configuration only) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending
- T8 | S3, S4, S14, S19 | inline (high-risk unit: deletions, block removal and fixture repair in one revertible commit) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending
- T9 | S15, S19, S20, S22 | inline (documentation, records and full verification) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending

## Log

- L1 — 2026-11-24 — original request, verbatim:

> # AICore — Skills-First Architecture Redesign
>
> ## Context
>
> AICore's current multi-agent architecture has repeatedly caused operational problems, including:
>
> - Mandatory audits becoming execution bottlenecks.
> - Excessive context transfers between agents.
> - Reviewer session failures and recovery problems.
> - Repeated acceptance and remediation cycles.
> - Duplicated verification responsibilities.
> - Excessive token consumption and coordination overhead.
> - Tasks remaining blocked despite completed implementation and available verification evidence.
>
> These are recurring architectural problems, not isolated incidents requiring another patch to the existing orchestration mechanism.
>
> We are evaluating a transition from mandatory multi-agent orchestration to a skills-first architecture, where the primary agent performs specialized work directly using existing documentation, skills, and tools.
>
> ## Authorization
>
> This request authorizes **read-only investigation, architectural evaluation, and proposal preparation only**. Do not create, modify, delete, or move any repository files. Do not create an ODD task record, register a debt, create a branch, commit, push, or open a PR. Do not begin implementation. The primary agent must perform this investigation directly. Do not delegate this evaluation to specialist subagents or initiate independent audit and acceptance cycles. Herald's existing exclusive Git/GitHub authorization remains in effect.
>
> ## 1. Establish the current baseline
>
> Investigate the actual repository rather than relying on assumptions about its architecture. Inspect the relevant: AGENTS.md instructions; OpenCode agent definitions and configuration; existing shared and local skills; ODD workflow documentation and implementation; architecture and implementation standards; agent-specific permissions; Git and PR workflows; hooks, plugins, scripts, and validators related to agent orchestration; Core Sync distribution contracts; Cursor integration and compatibility rules; existing tests, specifications, and governing records affected by the proposed redesign. Identify all active dependencies on specialist subagents and distinguish them from historical references that do not require modification. Do not perform unrelated repository audits.
>
> ## 2. Compare AICore against official ODD
>
> Consult Alan Buscaglia's official Gentleman Programming / Gentle AI documentation: https://github.com/Gentleman-Programming/gentle-ai. Identify the exact source, version, and section used for the comparison. Verify the original ODD protocol, including: 1. Authorize. 2. Explore. 3. Resolve uncertainty. 4. Classify. 5. Track before the first write. 6. Implement task by task. 7. Close. Determine which requirements belong to official ODD and which were introduced by AICore. Pay particular attention to: direct execution by the primary agent; delegation criteria; task classification; risk-based verification; independent verification requirements; correction and review cycles; tracking and closure requirements; the distinction between ODD and optional RDD mechanisms. The intention is to preserve the original seven-step ODD protocol while simplifying AICore's execution architecture. Explicitly identify any proposed departure from official ODD guidance. Do not silently redefine the methodology.
>
> ## 3. Evaluate every current subagent
>
> For each existing subagent, identify: its actual responsibilities; its specialized knowledge; its permission boundaries; its mandatory and optional invocation points; its inputs and outputs; dependencies from other agents, skills, workflows, scripts, and configuration; responsibilities already covered by existing skills or documentation; responsibilities that genuinely require a separate execution context. Evaluate whether each responsibility should be: moved to an existing skill; moved to a new skill; retained in canonical architecture documentation; retained as a primary-agent responsibility; removed because it exists exclusively to support multi-agent orchestration; retained as an isolated subagent responsibility when technically necessary. Do not assume that each removed subagent requires a corresponding new skill. Avoid duplication and preserve canonical ownership of architectural knowledge. Herald is an explicit exception in the initial proposal because of the existing Git/GitHub security boundary. Do not propose removing or weakening that boundary without separately identifying the security implications and obtaining user authorization.
>
> ## 4. Design the skills-first architecture
>
> Evaluate an architecture with the following characteristics: the primary agent owns the complete task lifecycle; specialized skills are loaded on demand; the primary agent retains execution context; existing architecture standards remain authoritative; verification is proportional to the actual task and risk; tests and objective verification evidence remain mandatory where applicable; independent reviewer approval is no longer a universal prerequisite for progress or delivery; independent reviews remain available when explicitly requested; user authorization boundaries remain intact; Git/GitHub operations continue to respect Herald's exclusive responsibility. Evaluate how high-risk changes should be handled without recreating the current mandatory audit bottlenecks. Clearly distinguish self-review, automated verification, and genuinely independent review. Do not claim that skills provide independent execution contexts or permission isolation.
>
> ## 5. Simplify the ODD execution workflow
>
> Preserve the seven original ODD steps. Identify and evaluate the AICore-specific mechanisms that can be eliminated or simplified, particularly: mandatory specialist delegation; mandatory independent work-unit acceptance; mandatory independent semantic acceptance; mandatory independent PR review; inter-agent handoff protocols; reviewer session continuity requirements; reviewer session recovery procedures; repeated acceptance cycles; blocking PASS/FAIL verdicts that depend exclusively on separate agents; duplicated review or verification responsibilities; orchestration-specific instructions and status reporting. Determine which existing mechanical validations remain useful independently of the multi-agent architecture. Preserve the applicable: user authorization gates; task classification; ODD tracking requirements; specifications, tasks, and logs; testing and verification requirements; architecture standards; work-unit commit policy; PR publication and merge authorization rules; security restrictions; verified completion reporting. Explain the proposed lifecycle from the initial user request through final delivery, including the relationship between task verification, ODD closure, and PR publication. The redesigned workflow must not replace removed independent audits with an equivalent number of mandatory self-audits.
>
> ## 6. Evaluate distribution and editor compatibility
>
> Respect AICore's existing separation between shared and local capabilities: shared skills under `.agents/skills/`; origin-specific skills under `.opencode/skills/`; existing Core Sync responsibilities and distribution boundaries; editor-specific configuration for OpenCode and Cursor. Do not introduce unrelated functionality into `cli/aicore`, which is exclusively dedicated to Core Sync. Identify whether removing specialist agents simplifies editor compatibility and reduces editor-specific configuration. Do not authorize changes to downstream repositories as part of this investigation.
>
> ## 7. Architectural constraints
>
> The proposed solution must favor simplification over additional enforcement infrastructure. Do not introduce new: orchestration engines; audit frameworks; permission-reconciliation systems; hooks or plugins; governance scripts; receipt systems; agent communication protocols; mandatory approval layers. If an existing technical constraint makes additional infrastructure genuinely necessary, report that constraint and present alternatives for user evaluation. Do not silently expand the scope. Preserve existing functional behavior outside the explicitly proposed changes to agent orchestration and ODD execution. Do not propose synthetic end-to-end agent tasks merely to reproduce historical incidents.
>
> ## 8. Required deliverable
>
> Return one consolidated architectural proposal containing: A. Current architecture; B. Root causes; C. Official ODD comparison; D. Subagent disposition matrix; E. Proposed target architecture; F. Exact file impact inventory; G. Alternatives and trade-offs; H. Migration plan; I. Risks and open decisions.
>
> ## Completion criteria
>
> This investigation is complete when the primary agent can present a coherent, evidence-based proposal with a sufficiently precise file inventory and migration plan for the user to make an informed architectural decision. No independent subagent acceptance verdict is required for this investigation. Report repository evidence directly, disclose uncertainties, and stop after delivering the proposal. **Await explicit user authorization before implementation.**

- L2 — 2026-11-24 — correction, verbatim (excerpt of the requirement-bearing clauses; the full message is the revision request that produced the F1–F7 corrections):

> The preferred direction for evaluation is A1: direct primary-agent execution with on-demand skills. This remains a read-only design activity. Implementation is not authorized.
> - Cipher becomes the primary implementation agent.
> - Herald remains the exclusive Git/GitHub executor.
> - Warden's useful security and dependency-review procedures become a skill instead of a mandatory or dedicated specialist subagent.
> - Lumen's useful design and accessibility procedures become a skill.
> - Remove the remaining specialist subagents.
> - Preserve all seven original ODD steps. Preserve existing user authorization boundaries.
> - Remove mandatory independent semantic acceptance and mandatory independent PR review.
> - Preserve applicable automated verification and proportionate self-review.
> - Independent review remains available when explicitly requested, without becoming a universal delivery prerequisite.
> - Do not introduce RDD, new governance infrastructure, or replacement audit mechanisms.
> F1 — Correct the distinction between optional native RDD review and independent verification under ODD delegation rules. Removing mandatory independent verification for named high-risk changes may constitute an intentional local departure from upstream guidance. Document it accurately. Do not claim full upstream equivalence where it does not exist.
> F2 — Inspect the relevant existing validators, schemas, templates, fixtures, and tests. Identify precisely which rules enforce: independent acceptance; reviewer identities; reviewer verdicts; commit-bound acceptance evidence; mandatory review-related closure prerequisites. Propose removal or adjustment only where a rule depends on the retired orchestration model. Preserve unrelated structural and evidence validation. Do not introduce replacement acceptance machinery.
> F3 — Explicitly include `.opencode/agents/herald.md` in the impact inventory. Remove only orchestration-specific dependencies that conflict with the new execution model. Do not weaken Herald's security responsibilities.
> F4 — Do not simply copy Forge's pnpm permission block into the primary agent. Account for OpenCode's actual permission-rule ordering and the installed configuration format. Do not create a new permission-management mechanism. Do not execute dangerous commands to prove that they are blocked.
> F5 — Distinguish architectural standards from specialized execution procedures. Do not create one skill per removed agent by default. Do not copy entire agent definitions into skills. Do not silently discard useful knowledge. A skill must not be presented as an independent reviewer.
> F6 — Determine whether obsolete files are removed, preserved, or handled through an existing migration mechanism. Do not access or modify downstream repositories.
> F7 — Revise the migration sequence so useful specialist knowledge is preserved before, or atomically with, deletion of its original agent definition. Reconcile the exact file inventory with the proposed work units.
> A missing independent reviewer is not, by itself, a blocker. Do not convert the removed independent audits into an equivalent number of mandatory self-audits, verdict documents, or additional reporting steps. Keep existing historical records intact.

- L3 — 2026-11-24 — correction, verbatim (requirement-bearing clauses of the final design-corrections message):

> These remain proposed decisions, not implementation authorization.
> 1. `pnpm --dir .agents/skills/* exec vitest run*` — PR #205 deliberately narrowed this pattern to `pnpm --dir .agents/skills/* exec vitest run`. Do not undo that correction. Derive the final build permission configuration from the currently approved repository configuration and its existing security restrictions. Also explain the legitimate execution route for dependency installation after explicit user authorization. Do not introduce a permanent operational blocker for authorized dependency changes.
> 2. Remove dependencies on retired specialist agents, independent acceptance verdicts, and specialist gate packets. Do not make Herald responsible for auditing Cipher's implementation. Do not replace the retired specialist gate packet with a new gate packet.
> 3. The proposed replacement of `## Verdict` with `## Delivery readiness` must remain compatible with the existing PR publication contract. Include only genuinely affected files in the migration inventory.
> 4. Include concise migration guidance in the appropriate existing documentation explaining that previously distributed obsolete agent definitions require destination-side reconciliation. Do not claim that removed source files are automatically deleted from existing destinations. Update the CLI test fixtures to use valid retained or appropriate existing fixture paths. Warden is being removed, so it cannot be used as a retained source fixture.
> 5. Remove the separate synthetic OpenCode runtime probe. Do not perform additional real or artificial agent tasks solely to validate the redesign.
> 6. Correct the inconsistent modified-file counts and reconcile the inventory against the migration units.
> 7. Explicitly describe how this migration will execute under the existing governance rules before the new workflow becomes active. The transition must not become another prolonged multi-agent audit exercise.

- L4 — 2026-11-24 — implementation authorization, verbatim (requirement-bearing clauses):

> I approve the skills-first architecture redesign and delivery option C: one feature branch, coherent work-unit commits, and one PR at the end.
> ## 1. Approved architecture
> - Cipher becomes the primary execution and implementation agent.
> - Herald remains the only custom subagent and the exclusive Git/GitHub executor.
> - Remove the other 13 custom subagents.
> - Create code-review, dependency-review, and visual-review skills.
> - Preserve Vault's useful authoring-quality checklist within op-skill-creator.
> - Preserve all seven original ODD steps.
> - Preserve canonical architecture and testing standards.
> - Remove mandatory specialist delegation, per-mutation checkpoints, independent semantic acceptance, and independent PR review.
> - Independent reviews remain available on explicit user request and may be recommended when justified by actual risk.
> - Preserve evidence-based technical judgment and challenges to unsupported assumptions, without requiring another agent to accept the challenge.
> - Do not introduce RDD or replacement governance mechanisms.
>
> ## 2. Transitional authorization
> I explicitly authorize the bounded transitional exception for this migration. Cipher may perform the complete implementation directly without Forge authorship, per-mutation AWAITING_REVIEW checkpoints, mandatory specialist dispatches, Sentinel audits, Warden audits, independent semantic acceptance, or mandatory Inquisitor review. This exception applies exclusively to this migration and remains effective through its final PR delivery. Record this authorization verbatim in the governing ODD record. The exception does not waive: Herald's exclusive Git/GitHub authority; existing Git safety checks and refusal duties; user-only authorization boundaries; applicable automated verification; evidence integrity; work-unit commit discipline; closure-before-PR requirements; user-only merge authority; post-merge cleanup safeguards; effective runtime permission restrictions. Do not introduce a transition framework, flag, script, hook, or additional approval mechanism.
>
> ## 3. Correct the distribution inventory
> Include the following two additional files in the authorized scope: `distribution-clearance.json`, `distribution-clearance.definition.md`. Register the three new shared skills using the existing clearance model and document their classification. Select the appropriate existing ownership mode according to their actual content and established distribution conventions. Verify their inclusion in the existing OpenCode and Cursor delivery paths using existing mechanisms. Do not change the Core Sync engine, schema, ownership semantics, or downstream repositories.
>
> ## 4. Preserve permission compatibility and portability
> The final proposed build permissions omit several existing documented commands, including: pnpm format; pnpm lint:fix; pnpm verify; pnpm verify:full; pnpm test:cli; pnpm test:cli:e2e. The documented System One install root also requires an authorized provisioning route. Additionally, opencode.jsonc is distributed to OpenCode destinations. An AICore-specific command allowlist must not inadvertently prevent destination projects from executing their own legitimate commands. Resolve these compatibility issues using the existing configuration and project-owned customization mechanisms. Preserve: previously approved narrowed permission patterns, including PR #205; legitimate implementation, formatting, testing, and verification capabilities; explicit authorization for dependency installation; destination-project portability; Herald's existing exclusive Git/GitHub boundary. Do not silently widen permissions, restore unsafe trailing wildcards, introduce new security infrastructure, or execute dangerous commands to verify restrictions.
>
> ## 5. Complete documentation is a mandatory acceptance requirement
> Update all applicable documentation ... The documentation must clearly describe: 1. Cipher's new identity, responsibilities, and direct execution authority. 2. The seven-step ODD lifecycle. 3. Read-only, small, and non-small work. 4. Skill discovery, selection, and on-demand loading. 5. Architecture and testing standards. 6. Proportionate verification and self-review. 7. High-risk changes and optional independent reviews. 8. Failed checks, unresolved findings, and legitimate blockers. 9. User authorization and scope changes. 10. Incident investigation and related procedures. 11. Interrupted-task recovery and context continuity. 12. Work-unit commits. 13. ODD closure. 14. PR evidence preparation and publication without mandatory reviewer verdicts. 15. Herald's authority, safety refusals, and cleanup safeguards. 16. User-only merge. 17. OpenCode and Cursor compatibility, including actual enforcement limitations. 18. Destination-side reconciliation of retired agent definitions. 19. Explicit local departures from official ODD. 20. The distinction between removed orchestration requirements and retained correctness requirements. Keep every rule in its canonical owner. Do not create redundant manuals or duplicate workflow definitions. Do not alter historical records or previously accepted ADRs. Do not claim runtime enforcement or independent verification where only instructional compliance or self-review exists.
>
> ## 6. Implementation and verification
> Execute the proposed dependency-ordered work units, incorporating the corrections above. Preserve specialist knowledge before deleting its original definition. ... Do not create synthetic agent tasks or initiate independent audit cycles. Do not perform broad unrelated refactoring.
>
> ## 7. Delivery authorization
> I authorize: the final implementation proposal and the bounded corrections explicitly described above; one feature branch; coherent local work-unit commits through Herald; root specification version 7.0.0; one PR published through Herald after ODD closure. Any additional material scope expansion requires separate authorization. I do not authorize merging the PR, modifying downstream repositories, changing the Core Sync engine, installing unapproved dependencies, or weakening Herald's security boundary.
>
> ## 8. Final delivery report
> Once implementation and applicable verification are complete, report: PR URL and exact final head SHA; exact changed-file inventory and change counts; removed custom subagents; new and updated skills; canonical documentation updated; existing verification commands and observed results; ODD alignment and documented local departures; permission and editor compatibility implications; destination migration instructions; remaining risks, failures, or pending checks; any scope decisions requiring my attention. Do not claim independent review when none occurred. Do not make the absence of an independent reviewer a delivery blocker. Finish with an explicit FINALIZED status when the authorized work is complete, and await my merge decision.
