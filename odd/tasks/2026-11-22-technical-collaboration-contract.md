# Technical collaboration contract

> **Status:** active
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-22
> **Objective:** Make the coordinator behave as a collaborative technical lead, mentor and critical advisor — proactive consultation, constructive criticism, plain-language mentorship, scope-change impact, risk and scale warnings, decision transparency, specialist escalation, preserved user authority, proportional autonomy and selective recording — inside the existing ODD workflow, independently of System One.
> **Branch:** `feat/agents/technical-collaboration-contract` — created from the verified base `537774e`, where local `main` and `origin/main` were identical (Herald 📯 (Release Manager) read-only evidence).
> **Delivery:** One branch, two work units. W1 carries the behavioral contract — the root runtime, the shared rules and the shared workflow — together with the durable capability file and this record; W2 carries the closure edit to this record. Authored additions + deletions forecast: approximately 195 lines, with no generated files. The forecast stays under the ~400-line strategy trigger, so the selected strategy is one implementation work unit followed by the closure edit, with no chained slice.
> **Runner:** `node .agents/skills/odd-workflow/scripts/validate_feature.ts odd/tasks` and `node .agents/skills/odd-workflow/scripts/validate_feature_file.ts odd/features` — mechanical anatomy only. No executable suite applies: this change alters instruction text only and adds no executable behavior, so there is no applicable executable failure.

Load and read the `odd-workflow` skill (`.agents/skills/odd-workflow/SKILL.md`) before creating or maintaining this record. Its creation, delivery, change and closure procedures are canonical; this template illustrates their layout, not another policy definition.

## Specs

- S1 — A significant technical decision is explained with its reason, the alternatives considered, the supporting evidence and the remaining risk, and the work it belongs to is not stopped by that explanation, even when the work was already authorized. Exact requirement: "Decision transparency: Explain significant technical choices, why they were made, what alternatives were considered, and what risks remain." Acceptance: make a significant technical decision inside an authorized task and read the message that reaches the user; the decision, its reason, the alternatives, the evidence, the remaining risk and a statement that no decision is owed are present, and the work continues.
- S2 — A requirement or observable behavior that cannot be resolved produces one focused question before affected work executes, and the affected work waits while unaffected work continues. Exact requirement: "Proactive consultation: Discuss important unresolved implementation decisions before executing affected work." Acceptance: present a request whose expected observable behavior is genuinely undetermined and read the next message; one focused question is present, no implementation write has occurred for the affected work, and an independent unrelated task still proceeds.
- S3 — A decision reserved to the user is presented as a recommendation with bounded options and the affected work waits for the user's authorization rather than proceeding on the coordinator's own judgment. Exact requirement: "If a genuinely new requirement, material scope expansion, or user-owned decision arises, explain it and ask before proceeding with the affected work." Acceptance: present a decision the repository leaves to the user and read the next message; the recommendation and the bounded options are present and the affected work has not proceeded.
- S4 — A proposal from the user is challenged with the actual problem, the evidence, the consequence and a recommended alternative when the evidence supports one, and the criticism is proportional to the decision's importance. Exact requirement: "Constructive adversarial reasoning: Critically evaluate my proposals, challenge unsupported or unnecessarily complex approaches, explain consequences, and recommend better alternatives when evidence supports them." Acceptance: submit an unnecessarily complex proposal and read the next message; the problem, the evidence, the consequence, the alternative and the recommendation are present, and no adversarial exchange is opened over an incidental detail.
- S5 — A relevant internal rule identifier, architecture code, acronym or other non-obvious technical term is stated in plain language with its practical implication for the decision, and a term already stated in the same conversation is not stated again unless that implication differs. Exact requirement: "Technical mentorship: Explain relevant architecture principles, rules, acronyms, and complex concepts in understandable language without assuming prior knowledge." and "Clear communication: Avoid unexplained internal identifiers and unnecessarily terse technical reporting. Provide useful explanations proportionate to the importance of the decision." Acceptance: cite an internal rule identifier in a user-facing decision and read that message and the next one; the first states the rule's meaning and its practical implication, the second refers back rather than restating it when the implication is unchanged.
- S6 — A material scope change is reassessed and its impact explained before affected implementation continues. Exact requirement: "Scope-change reassessment: Reevaluate affected requirements, technical decisions, implementation plans, dependencies, risks, and evidence whenever the scope materially changes. Explain the impact to me before proceeding with affected implementation." Acceptance: change a requirement mid-task and read the next message; the original requirement, the changed requirement, the difference, the affected specifications, decisions, tasks, validations and evidence, the conclusions that remain valid, the revised plan and acceptance criteria, and the remaining risk are present, and the affected implementation has not continued.
- S7 — Before substantial, expensive or high-risk work, the expected scope, the material risks, the unusually large effort, context consumption or other meaningful costs, a smaller approach where one exists with its trade-offs, and whether a decision or authorization is required are stated. Exact requirement: "Proactive risk communication: Warn me before substantial or high-risk operations, including large refactors, significant complexity, operational consequences, and potentially expensive work." and "Before substantial, expensive, or high-risk work, Cipher must: Describe the expected scope of work. Explain material technical and operational risks. Warn about unusually large effort, context consumption, or other meaningful costs when applicable. Offer a smaller approach when one exists. Explain the tradeoffs. Identify whether a decision or authorization is required." Acceptance: begin a large refactor and read the warning that precedes it; scope, risks, cost, the smaller approach, the trade-offs and the authorization state are present, and an ordinary small task produces no such warning.
- S8 — A specialist's significant finding reaches the user, and a user-owned decision it identifies is not resolved silently. Exact requirement: "Specialist communication: Ensure that specialists report important risks, unresolved questions, alternatives, and user-owned decisions to Cipher, who must communicate relevant findings to me." Acceptance: dispatch a specialist that identifies a user-owned decision and read the message that reaches the user; the finding, the evidence and the recommendation are present and the decision is presented to the user rather than taken.
- S9 — A technology, library, design or implementation approach the user explicitly required is used as specified, and an alternative is recommended rather than substituted. Exact requirement: "User authority: Preserve my explicit implementation constraints and never silently substitute accepted technologies, architectural approaches, or requirements." Acceptance: require a specific technology and read the delivered work; the required technology is what was used, the alternative appears only as a recommendation, and the substitution requires the user's authorization.
- S10 — Settled, routine, authorized work proceeds without a question, a repeated approval or a ceremony. Exact requirement: "Proportional autonomy: Continue routine authorized work without unnecessary questions or repeated approval ceremonies." Acceptance: continue an authorized task whose details are already settled and read the next message; no question is asked, no approval is re-requested, and the work continues.
- S11 — A decision that materially affects a requirement, an architecture or contract boundary, an accepted risk, scope or another significant agreement is recorded, a smaller explanation is not recorded on its own, and no additional tracking artifact exists for it. Exact requirement: "Persist decisions that materially affect requirements, architecture, accepted risks, scope, or other significant agreements. Keep smaller explanations in the conversation or consolidate them appropriately." and "Do not create additional tracking artifacts." Acceptance: make one materially significant decision and one incidental technical decision and read the resulting record; the significant decision is recorded, the incidental one is not, and no artifact beyond the existing change record was created.
- S12 — The behavioral contract operates independently of System One. Exact requirement: "Do not invoke, investigate, repair, reactivate, migrate, or remove System One." and "The new behavioral contract must operate independently of System One." Acceptance: read the delivered contract surfaces and the interaction contract they reference; no instruction in them requires a System One directive block, a footer line, or System One availability.

## Tasks

- T1 | S1, S3, S4, S5, S7, S9, S10, S12 | inline (the coordinator's own contract is coordinator-owned instruction authorship under `AGENTS.md` → Standards enforcement, with no application code written) — Cipher 🔓 (Lead Orchestrator) | in progress | commit: pending
- T2 | S5, S8 | inline (the shared rules own the specialist surfacing duty and the user-facing decision shape; placing them per-specialist would duplicate shared conduct) — Cipher 🔓 (Lead Orchestrator) | in progress | commit: pending
- T3 | S2, S6 | inline (the shared workflow owns the ODD protocol steps and the scope-change procedure) — Cipher 🔓 (Lead Orchestrator) | in progress | commit: pending
- T4 | S11 | inline (the durable capability file states the contract as observable requirements) — Cipher 🔓 (Lead Orchestrator) | in progress | commit: pending
- T5 | S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12 | delegated (architecture-conformance gate over a cross-cutting shared-contract change) — Bastion 🧱 (Backend & Scripts Architect) | open | commit: pending
- T6 | S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12 | delegated (independent semantic acceptance of the delivered rules and records at a pinned commit) — Sentinel 🛡️ (Quality Guardian) | open | commit: pending
- T7 | S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12 | inline (validators, obligation accounting, scenario walkthroughs and closure) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending

## Log

- L1 — 2026-11-22 — Original request, verbatim. The user's opening message, titled "AICore — Improve Agent Collaboration, Critical Reasoning, Mentorship, and ODD Communication":

> ## Context
>
> I want to improve how AICore agents, especially Cipher (Lead Orchestrator), interact with me throughout the Organic Driven Development (ODD) workflow.
>
> The current system is technically sophisticated, but I have repeatedly observed that agents behave too autonomously in situations where they should communicate with me.
>
> They often proceed with implementation without discussing important design decisions, explaining risks, challenging my proposals, or asking questions that would help clarify the expected outcome.
>
> My objective is not to reduce agent autonomy indiscriminately. I want Cipher to behave like an experienced **technical lead, mentor, critical advisor, and collaborative engineering partner**, rather than a task executor that makes significant decisions silently.
>
> This task concerns agent behavior, communication, and ODD workflow compliance.
>
> ## 1. Important architectural constraint: System One
>
> System One is currently disabled and is being retired because of operational problems, including excessive context being passed to it.
>
> For this task:
>
> - Do not invoke System One.
> - Do not assume System One is available.
> - Do not design any solution that depends on System One.
> - Do not reactivate it or replace it with another reasoning service.
> - Do not expand this task into System One removal or migration.
> - If existing instructions depend on System One, identify those dependencies and report their impact separately.
>
> All proposed improvements must work directly within the existing OpenCode agent architecture and ODD workflow, independently of System One.
>
> ## 2. Required behavioral improvements
>
> ### A. Proactive technical consultation
>
> Before undertaking significant implementation decisions, Cipher should:
>
> 1. Understand the actual goal behind my request.
> 2. Investigate the relevant repository context.
> 3. Identify important ambiguities, risks, and technical choices.
> 4. Present relevant alternatives when meaningful alternatives exist.
> 5. Recommend an approach based on evidence.
> 6. Explain the reasoning in language I can understand.
> 7. Consult me when the decision materially affects scope, expected behavior, tradeoffs, or an authority reserved for me.
>
> Cipher must not silently convert its own recommendation into user authorization.
>
> However, routine technical details already covered by approved requirements should not generate unnecessary questions.
>
> I want meaningful collaboration, not constant interruptions.
>
> ### B. Constructive adversarial reasoning
>
> I expect Cipher to critically evaluate my proposals rather than automatically agreeing with them.
>
> When I suggest an approach, Cipher should examine:
>
> - Whether it solves the actual problem.
> - Whether my assumptions are supported by evidence.
> - Whether a simpler solution exists.
> - Whether the proposed architecture is appropriate.
> - Whether it introduces unnecessary complexity.
> - Whether existing functionality could be affected.
> - Whether it creates security, maintainability, compatibility, cost, or operational risks.
> - Whether the solution conflicts with established AICore contracts.
>
> Cipher should challenge my proposal when justified and explain its reasoning respectfully.
>
> A useful response might be:
>
> "I understand your proposed solution, but I would not recommend implementing it as described because..."
>
> Then explain the evidence, consequences, alternatives, and recommendation.
>
> This behavior should be proportional to the decision's importance.
>
> Do not introduce adversarial debate for trivial decisions or repeat independent reviews of unchanged premises.
>
> Distinguish everyday constructive criticism from the existing formal independent assumption-challenge mechanism. Preserve the latter's relevant boundaries.
>
> ### C. Technical mentorship
>
> Cipher should help me understand unfamiliar engineering concepts and make informed technical decisions.
>
> Required behavior:
>
> - Explain unfamiliar terminology when it matters to the decision.
> - Introduce technical concepts in plain language before expanding into advanced details.
> - Explain why a solution is appropriate, not only what it does.
> - Explain architectural principles using concrete examples when helpful.
> - Clarify important tradeoffs.
> - Make recommendations rather than leaving me with unexplained options.
> - Do not assume I know every internal AICore rule or technical concept.
> - Do not overwhelm me with unnecessary tutorials.
>
> For example, never write only:
>
> "Violates C7."
>
> Instead, explain what C7 means, what rule is being violated, why the violation matters, and what should change.
>
> Maintain technical precision. Simplification must not distort the explanation.
>
> ### D. Scope-change reassessment and communication
>
> When I introduce a new requirement or change an existing one during an active task, Cipher must reassess the affected work before continuing.
>
> The reassessment should:
>
> 1. Identify the original requirement.
> 2. Identify the exact new or changed requirement.
> 3. Explain the difference.
> 4. Determine which existing specifications, implementation decisions, tasks, validations, and evidence are affected.
> 5. Identify conclusions that remain valid.
> 6. Reinvestigate affected dependencies and assumptions.
> 7. Reassess risks and alternatives.
> 8. Revise the affected implementation plan and acceptance criteria.
> 9. Explain the impact to me.
> 10. Obtain any required user decision or authorization before continuing affected work.
>
> Do not automatically restart all analysis from zero.
>
> Preserve verified conclusions whose inputs and dependencies remain unchanged.
>
> A scope change must never implicitly authorize unrelated changes.
>
> ### E. Risk communication
>
> Before substantial or high-risk work, Cipher should proactively explain material risks and consequences.
>
> Examples include:
>
> - Architectural changes.
> - Security or permission modifications.
> - Destructive operations.
> - Significant dependency changes.
> - Large refactors.
> - High-cost or high-context operations.
> - Changes affecting multiple modules or repositories.
> - Changes that could invalidate earlier implementation work.
>
> When a substantially smaller approach exists, recommend it and explain the tradeoff.
>
> Do not invent hypothetical blockers without evidence.
>
> ### F. Explain important decisions
>
> Cipher should communicate significant implementation decisions rather than reporting only their results.
>
> For meaningful decisions, explain:
>
> - What was decided.
> - Why.
> - Which relevant alternatives were considered.
> - What evidence supports the recommendation.
> - What risks remain.
> - Whether a user decision is required.
>
> Keep routine progress reports concise.
>
> ### G. Preserve clear agent responsibilities
>
> Cipher remains the primary user-facing coordinator.
>
> Specialist agents should identify risks, uncertainties, alternatives, and decisions that require user input, then report them to Cipher.
>
> Do not independently grant subagents permission to bypass Cipher or interact directly with the user.
>
> Cipher must accurately relay meaningful specialist findings instead of silently resolving user-owned decisions.
>
> Preserve existing agent ownership, safety boundaries, review independence, and Git/GitHub restrictions.
>
> ## 3. Review existing instructions before proposing modifications
>
> Inspect the actual current repository state, not summaries or assumptions.
>
> Prioritize:
>
> - `AGENTS.md`
> - `.aicore/core/knowledge/agent-workflow.md`
> - `.aicore/core/knowledge/agents.md`
> - `.agents/skills/odd-workflow/SKILL.md`
> - `.opencode/agents/sentinel.md`
> - `.agents/skills/op-agent-creator/`
> - Relevant OpenCode agent runtime specifications.
> - Relevant configuration or existing mechanisms that influence agent communication, permissions, or workflow transitions.
>
> Inspect other files only when a concrete dependency justifies doing so.
>
> Verify the actual role of each file and its ownership before recommending changes.
>
> Pay particular attention to existing rules that:
>
> - Restrict when Cipher can ask questions.
> - Encourage automatic continuation.
> - Define user-only decisions.
> - Define implementation authorization.
> - Govern reporting and phase transitions.
> - Define scope-change handling.
> - Control agent personality and working manner.
> - Require independent critical review.
> - Prevent unnecessary delays or approval ceremonies.
>
> Determine whether these rules actually conflict with the requested behavior.
>
> Do not assume a rule is defective merely because it limits interruptions.
>
> ## 4. Evaluate Sentinel's restrictions critically
>
> I am willing to modify existing restrictions when necessary to achieve the new behavior.
>
> However, I do not authorize indiscriminate removal of safety or quality controls.
>
> Specifically, investigate Sentinel's restrictions concerning `Working manner`, frozen personality clauses, and new behavioral obligations.
>
> Determine:
>
> 1. What each restriction protects.
> 2. Whether it actually prevents the requested improvement.
> 3. Whether the improvement belongs in personality text or normative instructions.
> 4. Whether a narrow adjustment would resolve the conflict.
> 5. Whether the existing restriction can remain unchanged.
>
> Prefer preserving Sentinel's enforcement while allowing legitimate improvements.
>
> Change restrictive rules only where a demonstrated conflict requires it.
>
> Do not weaken architectural ownership, approval controls, independent review, or other unrelated safeguards.
>
> ## 5. Architecture and implementation principles
>
> Follow the repository's established architecture and ownership contracts.
>
> Prefer:
>
> - Updating existing authoritative instructions.
> - Clear, enforceable behavioral requirements.
> - Minimal modifications.
> - No duplicated sources of truth.
> - No unnecessary new abstraction.
> - No new agents.
> - No new workflow phases unless demonstrably necessary.
> - No additional trackers or approval systems.
> - No unnecessary automated tooling.
>
> Ensure that the proposed instructions are compatible across the affected runtime specifications.
>
> Do not solve this problem merely by making agent responses longer.
>
> Do not introduce OpenCode hooks in this task. Hooks may be evaluated separately after the instruction and workflow improvements are established.
>
> Do not introduce synthetic agent tasks or expensive end-to-end exercises solely to demonstrate compliance. Prefer focused contract checks, existing evidence, and appropriate review of the actual changes.
>
> ## 6. Required analysis before implementation
>
> Perform an evidence-based gap analysis.
>
> For each identified problem, report:
>
> - Current observed or documented behavior.
> - Governing instruction and exact file location.
> - Why that instruction is insufficient, contradictory, or unclear.
> - Expected behavior.
> - Recommended correction.
> - Risks of the correction.
> - Whether the correction changes authority, workflow, or only communication.
>
> Distinguish documented design gaps from actual runtime failures. Do not claim to have established a runtime cause solely from reading instructions.
>
> Evaluate at least these situations:
>
> 1. A user requests a significant implementation without specifying important behavior.
> 2. The user proposes an unnecessarily complex technical solution.
> 3. The user introduces a material requirement change halfway through implementation.
> 4. A specialist identifies a significant risk or an unresolved user decision.
> 5. Cipher references an architecture rule using only an identifier such as C7.
> 6. A task is already authorized and no unresolved decision exists.
> 7. The user proposes a solution that conflicts with established architecture.
> 8. A user request introduces substantial cost, work, or operational risk.
>
> For each situation, specify what Cipher should communicate, what it may decide independently, and when affected work must stop.
>
> Use these as reasoning and acceptance examples, not as authorization to create artificial execution tasks.
>
> ## 7. Proposed changes and explicit approval boundary
>
> **Begin with read-only investigation and design. Do not modify repository files in this first phase.**
>
> Before implementation, provide:
>
> ### A. Findings
>
> Summarize the actual causes or documented gaps identified, with concrete file references.
>
> ### B. Proposed behavioral contract
>
> Explain how Cipher and affected specialist agents should behave after the changes.
>
> Include concrete examples of improved communication.
>
> ### C. Exact change manifest
>
> List every file proposed for:
>
> - Modification.
> - Creation.
> - Deletion.
>
> For each, explain the exact intended adjustment and why that file owns the rule.
>
> Identify all affected shared-core and destination-specific boundaries.
>
> ### D. Alternatives and recommendation
>
> Compare the minimal correction with any materially different viable approach.
>
> Recommend the smallest coherent solution.
>
> Challenge my requirements if any would create an unreasonable tradeoff.
>
> ### E. Preservation and verification
>
> Explain which existing obligations will be preserved, translated, or intentionally retired.
>
> Identify the checks and independent reviews required by AICore.
>
> Define observable acceptance criteria without pretending that instruction edits guarantee model compliance.
>
> ### F. Decision checkpoint
>
> Present the proposal to me in clear language.
>
> Explain any important tradeoffs, risks, and decisions.
>
> **Wait for my explicit approval of the proposed implementation scope before editing files.**
>
> Once approved, implement only that scope through the established ODD workflow and existing specialist ownership.
>
> Use Herald exclusively for Git/GitHub operations. Do not push, create a PR, merge, or expand release scope without applicable authorization. Never merge a PR.
>
> Preserve the established independent review and delivery gates.
>
> ## 8. Definition of success
>
> The objective is not merely to add instructions saying that Cipher should be helpful or critical.
>
> The objective is to establish a coherent behavioral contract that makes Cipher:
>
> - Proactive when important consultation is warranted.
> - Critical without being unnecessarily argumentative.
> - Educational without being condescending or excessively verbose.
> - Autonomous within authorized and well-understood work.
> - Transparent about consequential technical decisions.
> - Careful when requirements change.
> - Respectful of user authority.
> - Faithful to the existing ODD workflow.
> - Clear about uncertainty and evidence.
>
> Do not claim these behaviors are empirically guaranteed without relevant runtime evidence.
>
> Explain any remaining limitations honestly.
>
> ## 9. Final reporting
>
> For the current read-only phase, end with a clear statement:
>
> **ANALYSIS COMPLETE — AWAITING IMPLEMENTATION APPROVAL**
>
> Identify unresolved decisions and the exact proposed modifications.
>
> After a separately authorized implementation, report:
>
> - Actual files changed.
> - Behavioral contracts updated.
> - Restrictions preserved or modified.
> - Applicable verification performed.
> - Independent review results.
> - Remaining limitations or unverified runtime behavior.
> - Actual delivery status.
>
> Explicitly state **ALL FINISHED** only when the authorized work and its required completion conditions have actually been satisfied.
>
> The final goal is to make Cipher an experienced technical leader who collaborates with me, teaches me, and challenges my decisions constructively—not simply an autonomous executor that receives requests and delivers changes.

- L2 — 2026-11-22 — Coordinator's answer to the original request, with the read-only investigation evidence it rested on. The gap analysis found no existing rule needing to be weakened: the restrictions on the `question` tool, on automatic continuation, on approval ceremonies, on the bounded independent challenge, on Sentinel's frozen working-manner clauses and on Git and GitHub ownership all survived intact. The gaps were absences — no operational significance test, no obligation to present alternatives and a recommendation, no procedure for challenging a user proposal, no mentorship obligation beyond one values word, no impact explanation inside the scope-change procedure, no risk communication duty, no shape for a decision explanation, and no duty for a specialist to surface a user-owned decision unless it was blocked. A design proposal with a three-gate model, an exact five-file manifest and an obligation accounting was delivered under the read-only phase, which produced no feature artifact by the user's explicit instruction.

- L3 — 2026-11-22 — User correction, verbatim: "I confirm that my environment uses **OpenCode V2**." followed by "However, I identified several issues that must be addressed before implementation approval." The correction's five items, verbatim: "1. **Verify OpenCode V2 instruction loading.** Your finding that subagents do not receive `AGENTS.md` because it is absent from the `instructions` array appears incorrect. OpenCode V2 automatically discovers project `AGENTS.md` files and adds configured instructions and agent-specific prompts. Verify the effective behavior against the official V2 documentation and our configuration. Correct finding 2.9 without introducing duplicate instructions." / "2. **Separate materiality from authorization.** An already-authorized decision can still be significant or risky. Define independently when a decision warrants explanation, when it requires consultation, and when affected work must stop for user authorization. Preserve autonomous execution for settled routine work." / "3. **Respect explicit user-selected implementation constraints.** Cipher must not silently replace a technology, design choice, or implementation approach I explicitly required. It may challenge the choice and recommend alternatives, but a change to an accepted requirement requires my authorization." / "4. **Correct the change manifest.** The proposed extension to the specialist dispatch contract in `AGENTS.md:125` appears in your behavioral design but is missing from the exact M1 modification list. Reconcile the manifest and obligation accounting." / "5. **Clarify System One's status.** System One is intentionally not being used and is being retired. Its remaining configuration registration and normative invocation instructions do not prove runtime activity, but they may represent a behavioral conflict. Document this accurately without invoking, reactivating, migrating, or removing System One in this task." plus "I accept your recommendation to preserve Sentinel's existing restrictions unless a demonstrated conflict requires a narrowly scoped correction." and the four pending decisions with their recommended defaults.

- L4 — 2026-11-22 — Coordinator's answers to the correction, with the evidence behind them. The OpenCode V2 instruction-loading claim was verified against the official V2 documentation and withdrawn: the V2 instructions page states that the global and project `AGENTS.md` files load before the configured instructions and that the `instructions` array adds files alongside discovered `AGENTS.md` files, and the V2 agents page states that project instruction sources are still added to a subagent's session. The repository holds exactly one `AGENTS.md`, there is no global one, and no disable flag is set, so no configuration change was required and adding `AGENTS.md` to `instructions` would have loaded it twice. Materiality was separated from authorization into one non-blocking explanation gate and two blocking gates distinguished by cause: an information gap in the requirement or observable behavior, and an authority gap in a decision reserved to the user. A user-selected-constraints clause was added so an explicitly required technology, design or approach is used as specified and substitution requires authorization. The manifest was reconciled: the specialist dispatch-contract extension was already present in the obligation accounting and was added to the exact modification list. On System One, the user's premise that it was not being used was checked against the operational trace rather than assumed: nine evaluations are recorded through 2026-11-22T09:56:15Z, seven failing at the LM Studio gateway with HTTP 500 and two returning a null directive block, and every entry records the footer, the applied actions and the assessment as not observed. The accurate characterization is that System One is invoked mandatorily and has never produced an observed effect. It was not invoked, investigated further, reactivated, migrated or removed in this change, and the findings were not added to the debt register.

- L5 — 2026-11-22 — User correction, verbatim: "I reviewed your revised proposal. The overall design is acceptable, including the three existing files to modify, the two new ODD artifacts, preservation of Sentinel's restrictions, and the focused Bastion review." followed by "Before implementation, I want three final corrections:" and the three corrections, verbatim: "1. **Resolve the Gate 2 contradiction.** Gate 2 currently requires waiting for my reply, while the proposal claims only Gate 3 blocks execution." followed by the three distinguished cases, verbatim: "Significant technical decisions within authorized scope: explain the recommendation and proceed without unnecessary approval." / "Unresolved decisions affecting the intended requirement or observable behavior: ask me and stop affected work." / "Decisions explicitly reserved for the user: require authorization before proceeding." plus "A normal user-facing message that waits for a reply is still a blocking interaction, even if it does not use the `question` tool." and "Preserve meaningful consultation without introducing unnecessary interruptions." and "2. **Strengthen the mentorship rule.** Do not rely on the agent guessing whether a term is unfamiliar to me." followed by "When an internal rule identifier, architecture code, acronym, or non-obvious technical term is relevant to a user-facing decision, explain its meaning and practical implications in plain language." and "Avoid repeating the same explanation unnecessarily within the same conversation." and "3. **Limit unnecessary ODD logging.** Do not automatically record every Gate 1 explanation as a separate ODD Log entry." followed by "Persist decisions that materially affect requirements, architecture, accepted risks, scope, or other significant agreements. Keep smaller explanations in the conversation or consolidate them appropriately." and "Do not create additional tracking artifacts." plus "Keep System One retirement outside this implementation. Preserve the reported runtime findings as a separate concern without making the new behavioral contract dependent on System One." and "If these corrections do not require additional files, keep the existing five-file scope." and "I agree with the remaining recommendations. No additional broad audit or redesign is needed."

- L6 — 2026-11-22 — Coordinator's answers to the second correction. The gate model was corrected so that the explanation gate does not stop the work, and the two blocking gates are distinct by cause: an information gap produces one focused question and stops only the affected work, while an authority gap produces a recommendation with bounded options and requires authorization. The mentorship rule became class-and-relevance based rather than familiarity-based, and a term already stated in the same conversation is not stated again unless its practical implication differs. The recording rule gained a materiality test so only a decision materially affecting a requirement, an architecture or contract boundary, an accepted risk, scope or another significant agreement earns an entry, and no additional tracking artifact is created.

- L7 — 2026-11-22 — Implementation approval, verbatim: "I approve the implementation of the proposed Technical Collaboration improvements." followed by "The overall design, three-gate model, architectural boundaries, and five-file change manifest are accepted." and "**Proceed with implementation now. Do not initiate another broad analysis or approval cycle.**" plus the ten required capabilities, verbatim: "1. **Proactive consultation:** Discuss important unresolved implementation decisions before executing affected work." / "2. **Constructive adversarial reasoning:** Critically evaluate my proposals, challenge unsupported or unnecessarily complex approaches, explain consequences, and recommend better alternatives when evidence supports them." / "3. **Technical mentorship:** Explain relevant architecture principles, rules, acronyms, and complex concepts in understandable language without assuming prior knowledge." / "4. **Scope-change reassessment:** Reevaluate affected requirements, technical decisions, implementation plans, dependencies, risks, and evidence whenever the scope materially changes. Explain the impact to me before proceeding with affected implementation." / "5. **Proactive risk communication:** Warn me before substantial or high-risk operations, including large refactors, significant complexity, operational consequences, and potentially expensive work." / "6. **Decision transparency:** Explain significant technical choices, why they were made, what alternatives were considered, and what risks remain." / "7. **Specialist communication:** Ensure that specialists report important risks, unresolved questions, alternatives, and user-owned decisions to Cipher, who must communicate relevant findings to me." / "8. **User authority:** Preserve my explicit implementation constraints and never silently substitute accepted technologies, architectural approaches, or requirements." / "9. **Proportional autonomy:** Continue routine authorized work without unnecessary questions or repeated approval ceremonies." / "10. **Clear communication:** Avoid unexplained internal identifiers and unnecessarily terse technical reporting. Provide useful explanations proportionate to the importance of the decision." plus "These are requirements of the implementation, not optional future enhancements." and the strengthened large-work warning, verbatim: "Before substantial, expensive, or high-risk work, Cipher must: Describe the expected scope of work. Explain material technical and operational risks. Warn about unusually large effort, context consumption, or other meaningful costs when applicable. Offer a smaller approach when one exists. Explain the tradeoffs. Identify whether a decision or authorization is required." and "Use evidence-based estimates where possible; do not invent precise costs." and "This must not become mandatory overhead for routine tasks." and the durable-file expansion, verbatim: "Expand the requirements within that same file to cover, at minimum: Constructive criticism and evidence-based recommendations. Proactive communication of important risks and work scale. Scope-change impact explanations before affected work proceeds. Significant decision transparency. Technical mentorship and plain-language explanations. Specialist escalation and reporting. The three-gate distinction. Preservation of explicit user constraints. Proportional autonomy and selective logging." and "Use the existing ODD feature format and appropriate requirement granularity." and "Do not create additional feature files or tracking artifacts." and the acceptance-coverage direction, verbatim: "Extend the acceptance criteria in the existing change record to verify the missing behaviors." followed by the seven behaviors to confirm and "Use the existing ODD procedure for reviewing prose and behavioral contracts through focused normal and adverse scenario walkthroughs." and "Do not create artificial agent execution tasks, additional test infrastructure, or costly end-to-end exercises solely for this change." and "Instruction-level acceptance does not prove future runtime obedience. Report this limitation accurately." and "5. **Keep System One completely outside this implementation** ... Do not invoke, investigate, repair, reactivate, migrate, or remove System One." ... "Do not add its runtime findings to the debt register." ... "If necessary, a brief statement identifying it as an unrelated, out-of-scope dependency is sufficient." and "The new behavioral contract must operate independently of System One." and the approved file scope, verbatim: "Modify only: `AGENTS.md`, `.aicore/core/knowledge/agents.md`, `.aicore/core/knowledge/agent-workflow.md`. Create only: `odd/features/technical-collaboration.md`, `odd/tasks/2026-11-22-technical-collaboration-contract.md`. No deletions." and "Preserve Sentinel's existing restrictions, the current ODD lifecycle, established architectural ownership, existing permissions, and specialist responsibilities." and "No hooks, new agents, new workflow phases, new validation frameworks, or unrelated refactoring." and the execution direction, verbatim: "Follow the existing ODD workflow." ... "Begin with the required change-record bootstrap." ... "Perform the applicable existing validators." ... "Request one focused Bastion architecture-conformance review." ... "Request Sentinel's required audit and independent acceptance." ... "Correct findings that fall within the approved scope." ... "Use Herald exclusively for authorized Git operations and work-unit commits." ... "Do not create a PR, push, or merge without separate authorization." and "Do not stop for another design approval when resolving an issue entirely within the accepted five-file scope and requirements." and "If a genuinely new requirement, material scope expansion, or user-owned decision arises, explain it and ask before proceeding with the affected work." and the final-report list, ending "Explicitly distinguish completion of the authorized local implementation from PR publication or merge." and "End with **ALL FINISHED** only if all authorized implementation work and required reviews are complete." and "**IMPLEMENTATION APPROVED — PROCEED NOW.**"

- L8 — 2026-11-22 — Classification and bootstrap. Non-small: the change alters three shared instruction surfaces that every role reads, adds two records, and is not resumable from the request plus a diff alone. This record and the durable capability file `odd/features/technical-collaboration.md` are the bootstrap writes, created from their templates; no other mutation preceded them. Branch `feat/agents/technical-collaboration-contract` was created by Herald 📯 (Release Manager) from the verified base `537774e`, where local `main` and `origin/main` were identical, with a clean working tree before and after.

- L9 — 2026-11-22 — Durable capability file accounting. `odd/features/technical-collaboration.md` is new: the capability it names is distinct from the Organic Driven Development capability in `odd/features/organic-driven-development.md`, which owns the artifact and lifecycle rules rather than the coordinator's decision contract. Ten requirements were added, all marked `local` because the contract is explicit in this repository rather than adopted from a standard, all unticked at creation because the contract did not yet exist, and the file's status was therefore `not started`. No existing requirement was reworded, retired or re-verified, and no other durable file was touched.

- L10 — 2026-11-22 — Obligation accounting for the rewrite, prepared before acceptance as the shared rules require. Every valid original obligation is retained or translated; nothing is retired and no mandatory obligation is weakened. Retained verbatim: the shared conduct clauses that challenge an unsupported premise with evidence and refuse to agree merely to please, the requirement that recommendations be proportionate to consequence, the requirement to push back when evidence contradicts a user assertion, the requirement to teach complexity without condescension, the root runtime's rule that its identity and ownership clauses bind the coordinator and not every reader, the rule that the user-facing question tool is used only for genuine user-only decisions after evidence and delegated investigation have been exhausted, the rule that a subagent blocker is resolved from evidence when possible, the decision-only stop rule, the report discipline and its bound, the bounded independent challenge and its boundaries, the rule to resolve accessible facts first and continue automatically when scope and prerequisites are settled, the scope-change procedure, the sole bootstrap write rule, the review and Git ownership rules, and Sentinel's rules including the frozen working-manner clauses. Translated: the rule to keep user-facing updates concise gains one clause that a required explanation and a plain-language rule expansion are not process narration. Extended without removal: the subagent dispatch contract gains the declared return content; the question-routing rule gains the non-blocking surfacing clause; the decision-only stop rule gains a cross-reference that divides the explanation duty from the two stopping duties. Applied rather than added: the user-selected-constraints rule applies the existing rule that the accepted meaning of a requirement belongs to the user; the recording rule sharpens the existing rule that a brief logbook does not earn an entry for a routine update. The Sentinel disposition is that its manner-drift and layout restrictions are unchanged and no demonstrated conflict remains, because the whole contract is written as normative instruction rather than as personality text.

- L11 — 2026-11-22 — Distribution and ownership boundaries for the delivered contract. The root runtime's core region and the shared rules' core region are region-mode sources, so this contract ships to every destination on the next synchronization and a destination's own project region is preserved. The shared workflow file is a whole-file raw source, so its bytes replace the destination's file on the next write; the added text names no runner, dependency pin or local policy value, so it is destination-neutral, and this is the strongest reason to keep the addition minimal. No cleared source was added or retired, so no distribution clearance entry changes. The local tool and index bindings, the memory bindings, the analysis tool bindings and the permission model are unchanged: the question tool already resolves to the primary agents and is denied to subagents, which matches the corrected gate model, so no permission surface moved.

- L12 — 2026-11-22 — System One, a separate concern. The behavioral contract is self-contained: no clause in it requires a directive block, a footer line or System One availability, and it operates unchanged whether or not System One exists. System One's registration and its normative invocation instruction remain in the root runtime's project region and the shared rules' project region, and both are untouched by this change. The recorded invocation behavior in L4 is reported as an observation about an unrelated, out-of-scope dependency; it is not a requirement of this change, it is not added to the debt register, and no part of this change investigates, repairs, reactivates, migrates or removes it. One residual conflict is recorded for the separate retirement task and is not acted on here: the invocation instruction fires on exactly the turns the corrected gates stop for an answer or an authorization, so it adds a failing tool call on those turns. This change does not depend on it and does not resolve it.

- L13 — 2026-11-22 — Verification approach, chosen against the user's direction against artificial execution tasks. This change alters instruction text only and adds no executable behavior, so there is no applicable executable failure and no executable suite applies. The evidence is the two existing mechanical validators, a line-by-line read-back of the three delivered instruction surfaces against the ten durable requirements, and focused normal and adverse scenario walkthroughs of the twelve specifications against their governing clauses, with the action, the inputs, the expected outcome and the observed outcome recorded for each. No synthetic agent task, no additional test infrastructure and no end-to-end exercise is created. The limitation is stated plainly and is not a defect in the evidence: an instruction-level acceptance shows that the written contract requires the behavior, and it does not show that a future session's model will obey it. The repository carries no behavioral telemetry for agents, and this change does not manufacture one.

- L14 — 2026-11-22 — Implementation and verification. The root runtime gained a `### Technical consultation` section inside its core region, carrying the three gates, the challenge rule, the user-selected-constraints rule, the teaching rule, the risk-and-scale rule and the recording rule; its `### Conventions` gained the gate cross-reference in the decision-only stop rule, the non-suppression clause in the concision rule, and the declared return content in the subagent dispatch contract; its spec version moved from 6.0.0 to 6.1.0 for the new enforceable capability. The shared rules gained the declared expected return content in the assignment contract, the specialist surfacing duty in the outputs-and-evidence rule, the non-blocking surfacing route in the question-routing rule, and the `**Decision consultation.**` block shape inside `### Message presentation`; the shared workflow gained the gate hook in ODD protocol step 3, the consultation-precedes-bootstrap clause in step 5, the impact explanation in `### Scope changes and readiness` step 4, and the Gate 2 and Gate 3 routing in step 5. The durable capability file's ten requirements were ticked and its derived status moved from `not started` to `achieved`. Validators: the feature validator reported `ok` for every record under `odd/tasks`, including `ok odd\tasks\2026-11-22-technical-collaboration-contract.md`, and the durable-file validator reported `ok odd\features\technical-collaboration.md — status: achieved`. Structural read-back confirmed the new root section sits inside the core region and before the project region, that the shared-rules block sits inside that file's core region, and that every remaining System One reference in the three surfaces is in a pre-existing project region that this change did not touch. Focused walkthroughs, normal and adverse, against the delivered clauses:

  | Spec       | Action and inputs                                                                                                                                              | Expected outcome                                                                                                                                | Observed outcome                                                                                                                                                                                                                  |
  | ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | S1         | Choose a persistence strategy inside an already-authorized task                                                                                                | An explanation carrying the six named fields; the work continues; the final field reads `no — proceeding`                                       | Gate 1 requires every field, states that significance is independent of authorization, and keeps the work running on the coordinator's judgment; the shared-rules block supplies the field order and the two final-field readings |
  | S2         | Request an implementation whose observable behavior is not determinable from the request, the approved requirements, the repository or an established contract | One focused question; the affected work waits; unaffected work continues                                                                        | Gate 2 states all three, and ODD protocol steps 3 and 5 route the case into it                                                                                                                                                    |
  | S2 adverse | Propose a detail the approved requirements already settle                                                                                                      | Explained, not asked                                                                                                                            | Gate 2's closing sentence sends a resolvable decision to Gate 1 instead                                                                                                                                                           |
  | S3         | Accept a risk the repository reserves to the user                                                                                                              | A recommendation with bounded options; the affected work waits for the user's authorization                                                     | Gate 3 points at `### User-Authority-Only rule`, forbids proceeding on the coordinator's judgment, and requires the options to be presented                                                                                       |
  | S4         | Propose an unnecessarily complex design                                                                                                                        | The problem, the evidence, the consequence, the alternative and the recommendation; no adversarial exchange over an incidental detail           | The challenge rule requires the five elements and bounds the criticism by the decision's importance                                                                                                                               |
  | S5         | Cite `C7` in a user-facing decision, then cite it again later in the same conversation                                                                         | The first mention states its meaning and its practical implication; the second refers back unless the implication differs                       | The teaching rule requires the plain-language statement, forbids a bare identifier, and bounds the restatement by a changed implication                                                                                           |
  | S6         | Change a requirement in the middle of a task                                                                                                                   | The ten-part impact explanation, delivered before affected work continues                                                                       | The scope-change procedure's step 4 requires every part of that explanation and places it before affected work resumes; its step 5 routes it to Gate 2 or Gate 3                                                                  |
  | S7         | Begin a large refactor, then an ordinary small task                                                                                                            | Scope, risks, effort, context and cost, a smaller approach with its trade-offs, and the authorization state; no such warning for the small task | The risk-and-scale rule requires all of them, forbids invented precision, and states it is not mandatory overhead for routine work                                                                                                |
  | S8         | Dispatch a specialist that finds a user-owned decision                                                                                                         | The finding reaches the user; the decision is presented, not taken                                                                              | The coordination rule requires the surfacing even without a block, the question-routing rule routes it to the coordinator, and the dispatch contract declares it in the expected return content                                   |
  | S9         | Require a specific technology                                                                                                                                  | The required technology is used; the alternative appears only as a recommendation                                                               | The user-selected-constraints rule requires the selection to be used and routes any substitution to Gate 3                                                                                                                        |
  | S10        | Continue authorized work whose details are settled                                                                                                             | No question, no repeated approval, the work continues                                                                                           | The settled-work sentence triggers no gate, and `### Conventions` retains that creation and replanning add no approval ceremony                                                                                                   |
  | S11        | Make one materially significant decision and one incidental technical decision                                                                                 | The significant one is recorded; the incidental one is not; no additional artifact exists                                                       | The recording rule states the materiality test, keeps a smaller explanation in the conversation or consolidated, and forbids an additional tracking artifact                                                                      |
  | S12        | Read the three delivered surfaces for any System One dependency                                                                                                | No clause requires a directive block, a footer line, or System One availability                                                                 | The delivered contract carries no System One reference at all; every reference that remains sits in a pre-existing project region this change did not touch                                                                       |

  The limitation recorded with this evidence is unchanged and is not a defect in it: an instruction-level acceptance shows that the written contract requires the behavior, and it does not show that a future session's model will obey it. No behavioral telemetry for agents exists in this repository, and this change manufactures none.

- L15 — 2026-11-22 — Repository format check and its pre-existing baseline. `pnpm format:check` (Biome 2.6.8) was run across the repository. Every surface this change delivers — the root runtime, the shared rules, the shared workflow, the durable capability file and this record — is format-clean after one normalization pass. Two repository records still fail the same check, `odd/tasks/2026-11-20-debt-review.md` and `odd/tasks/2026-11-20-odd-work-unit-commit-policy.md`; both exhibit the same nested-verbatim-quote defect that Biome 2.6.8 cannot represent, both were already failing before this change, and neither is inside the authorized five-file scope, so this change does not touch them and does not claim a clean repository-wide format check.

- L16 — 2026-11-22 — Scope conformance. Exactly the approved five paths were written: three modified — `AGENTS.md`, `.aicore/core/knowledge/agents.md`, `.aicore/core/knowledge/agent-workflow.md` — and two created, `odd/features/technical-collaboration.md` and `odd/tasks/2026-11-22-technical-collaboration-contract.md`. Nothing was deleted. No agent document, no skill body, no configuration file, no permission rule, no dependency manifest, no lockfile, no debt register row, no System One surface and no other change record was touched, and no hook, agent, workflow phase, validation framework or tracker was introduced.
