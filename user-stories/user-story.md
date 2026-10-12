# User story — user-story

> **Created:** 2026-10-11
> **Title:** Collaborative user-story definition
> **Status:** active
> **version:** 1.0.0
> **Epic:** plan-governance
> **Affected areas:** `.opencode/skills/user-story/`, `.opencode/skills/plan-enforce/SKILL.md`, `.opencode/skills/plan-enforce/references/_template-user-story.md`, `.opencode/skills/plan-enforce/references/_consistency-checklist.md`, `AGENTS.md`, `.opencode/agents/sentinel.md`, `README.md`, `user-stories/`

## Persona

- A maintainer who wants to discuss a new or changed feature, agree on its behavior, and check its relationship to existing features before creating an implementation plan.

## Goal

- **G:** An independently invokable `user-story` skill helps the maintainer create or revise a durable, collision-reviewed feature contract that becomes the behavioral source for implementation planning.
  - Done when: the skill supports discussion, evidence-backed CREATE/UPDATE selection, complete catalogue review, explicit contract approval, and a handoff to `plan-enforce` without treating approval as implementation evidence or execution authorization.

## Scenario

- The maintainer describes a new behavior or a change. The skill reads the story catalogue, recommends the owning story or a new story, discusses persona/outcome/scenarios/acceptance criteria, previews the contract delta, and reports concrete collisions. After the maintainer approves the contract and any collision resolution, the selected story is saved consistently with its index entry. `plan-enforce` then derives its feature goals from an explicitly selected set of those approved criteria.

## Acceptance criteria

The skill is implemented (`.opencode/skills/user-story/SKILL.md`); each criterion below is evidenced by that file and the aligned template/checklist.

- ✅ **AC1 — Standalone discussion:** `user-story` can be invoked before any implementation plan exists to create a story or revise an existing one. It owns feature-contract discussion, while `plan-enforce` owns execution planning. Proving surface: `.opencode/skills/user-story/SKILL.md` purpose and workflow.
- ✅ **AC2 — Complete catalogue:** Each invocation reconciles `user-stories/index.md` with the actual story files and reads every story body, respecting draft/active/superseded status. Missing or ambiguous catalogue evidence is reported rather than interpreted as absence of a collision. Proving surface: the skill's catalogue-validation workflow.
- ✅ **AC3 — Evidence-backed ownership:** Before writing a contract, the skill presents the relevant existing persona/goals/scenarios and recommends UPDATE, CREATE, or an explicit supersession relationship. Common files alone do not prove duplicate ownership. Proving surface: the skill's selection and preview rules.
- ✅ **AC4 — Semantic collisions:** Validation distinguishes duplicate scenarios, contradictions, extension/supersession, dependencies, and shared affected files. A collision report cites the paired statements and a recommended disposition; unresolved contradictions block contract approval/handoff. Mechanical checks do not substitute for semantic reading. Proving surface: the skill's collision-analysis rules.
- ✅ **AC5 — Explicit revision approval:** Discussion can produce an authorized persisted draft, but a draft is not an approved planning contract. An existing approved contract is not silently overwritten while alternatives are discussed. New or revised behavior receives explicit user approval, and approval does not authorize code execution or establish implementation acceptance. Proving surface: the skill's draft/approval workflow and `plan-enforce` story handoff.
- ✅ **AC6 — Coherent durable artifact:** A saved story contains its persona, observable goal, scenarios, acceptance criteria, affected areas, and current governing decisions. Its index entry agrees on title/status/epic/areas; its bounded feature Change log supports a story-only revision without inventing a plan. Implementation phases, grants, scheduling, and private coding recipes remain in the plan. Proving surface: the canonical story template and consistency checklist.
- ✅ **AC7 — Approved planning handoff:** The skill hands the approved story, selected delivery criteria, governing constraints, and dependencies to `plan-enforce`. Remaining legitimate story commitments are preserved. `plan-enforce` owns goal traceability and completion reconciliation; this skill does not create a competing plan-completion policy or archive a plan. Proving surface: the story skill's handoff and `plan-enforce` story-input contract.
- ✅ **AC8 — Contract drift:** If planning or implementation discovers a needed behavior change, the proposed story delta is discussed, collision-reviewed, and approved before the plan is revised. Private implementation decisions within the approved contract do not require inventing new story behavior. Proving surface: the story skill's revision workflow and `plan-enforce` drift watch.
- ✅ **AC9 — Documentation consistency:** Changes to the story workflow update its skill guidance, template/checklist, orchestrator/reviewer references, and README together. A future change using this workflow identifies and updates its own affected documentation in the same plan. Proving surface: skill documentation-impact rules and the planning completion contract.
- ✅ **AC10 — Bounded feature:** The skill does not create implementation plans, change application code, grant execution permissions, or split the existing large stories. It changes other stories only after an explicit approved collision resolution. Read-only mechanical validation uses existing authorized facilities rather than a separate semantic-checker engine. Proving surface: the skill's scope and authority boundaries.

## Change log

- 2026-10-11 — planning-workflow-20261011: delivered the standalone skill (catalogue reconciliation, evidence-backed ownership, semantic collision analysis, draft-vs-approved, approved-criteria handoff); implemented in `.opencode/skills/user-story/SKILL.md`.
- 2026-10-11 — user-story: standalone collaborative contract discussion, catalogue-wide collision review, and approved-criteria planning handoff.

## Resolved decisions

- 2026-10-11 — Story definition is a standalone `user-story` skill so feature behavior can be settled before execution planning; the canonical story format is reused.
- 2026-10-11 — Plans deliver an explicit approved criterion scope rather than being forced to deliver an entire large story; remaining legitimate commitments are retained.
- 2026-10-11 — Existing story splitting is outside this feature; full-catalogue assessment does not authorize bulk rewriting.
- 2026-10-11 — A plan that includes a file not conforming to the approved design must include the necessary architectural rework and its affected documentation/tests; unrelated repository-wide migrations are not implied.
